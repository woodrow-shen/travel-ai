import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.clients.amadeus_client import AmadeusClient
from app.config import settings
from app.db import async_session
from app.detector import detect_anomaly
from app.models import (
    PriceHistory,
    Subscription,
    SubscriptionType,
)
from app.notifier import check_and_notify_bug_fares, check_and_notify_price_drops

logger = logging.getLogger(__name__)


async def _get_active_routes(db: AsyncSession) -> list[dict]:
    """Aggregate unique routes from active subscriptions.

    Returns list of dicts with origin, destination keys.
    """
    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.subscription_email))
        .where(
            Subscription.is_active.is_(True),
            Subscription.type.in_([
                SubscriptionType.BUG_FARE,
                SubscriptionType.PRICE_DROP,
            ]),
        )
    )
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()

    routes: set[tuple[str, str]] = set()
    for sub in subscriptions:
        config = sub.config or {}
        # Price drop: explicit route
        origin = config.get("origin")
        dest = config.get("destination")
        if origin and dest:
            routes.add((origin.upper(), dest.upper()))
        # Bug fare: origins × destinations
        origins = config.get("origins", [])
        destinations = config.get("destinations", [])
        for o in origins:
            for d in destinations:
                routes.add((o.upper(), d.upper()))

    return [{"origin": o, "destination": d} for o, d in routes]


async def _get_price_history(
    db: AsyncSession,
    origin: str,
    destination: str,
) -> list[float]:
    """Get historical prices for a route from price_history table."""
    stmt = (
        select(PriceHistory.price_amount)
        .where(
            PriceHistory.origin == origin,
            PriceHistory.destination == destination,
        )
        .order_by(PriceHistory.created_at.desc())
        .limit(30)
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def _get_previous_price(
    db: AsyncSession,
    origin: str,
    destination: str,
) -> float | None:
    """Get the most recent price for a route."""
    stmt = (
        select(PriceHistory.price_amount)
        .where(
            PriceHistory.origin == origin,
            PriceHistory.destination == destination,
        )
        .order_by(PriceHistory.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    row = result.first()
    return row[0] if row else None


async def _store_price(
    db: AsyncSession,
    origin: str,
    destination: str,
    departure_date: str,
    airline: str | None,
    price: float,
    currency: str,
    source: str,
    stops: int | None = None,
    cabin_class: str | None = None,
) -> None:
    """Store a price data point in price_history."""
    record = PriceHistory(
        origin=origin,
        destination=destination,
        departure_date=date.fromisoformat(departure_date),
        airline=airline,
        price_amount=price,
        price_currency=currency,
        source=source,
        stops=stops,
        cabin_class=cabin_class,
    )
    db.add(record)


async def scan_prices():
    """Scan all active subscription routes for price changes."""
    logger.info("Starting price scan...")

    amadeus = AmadeusClient()

    try:
        async with async_session() as db:
            # 1. Aggregate unique routes from active subscriptions
            routes = await _get_active_routes(db)
            if not routes:
                logger.info("No active routes to scan.")
                return

            logger.info("Scanning %d routes", len(routes))

            # Limit routes to Amadeus quota
            routes = routes[: settings.MAX_ROUTES_STANDARD]

            # Search date: ~2 weeks out (typical booking window)
            search_date = (
                datetime.now(UTC) + timedelta(days=14)
            ).strftime("%Y-%m-%d")

            total_notifications = 0

            for route in routes:
                origin = route["origin"]
                destination = route["destination"]

                try:
                    # 2. Query Amadeus for current prices
                    offers = await amadeus.search_flights(
                        origin=origin,
                        destination=destination,
                        departure_date=search_date,
                        adults=1,
                        max_results=5,
                    )

                    if not offers:
                        continue

                    # Get previous price for price drop detection
                    previous_price = await _get_previous_price(
                        db, origin, destination
                    )

                    # Get price history for anomaly detection
                    history = await _get_price_history(
                        db, origin, destination
                    )

                    for offer in offers:
                        price_info = offer.get("price", {})
                        price = float(price_info.get("total", 0))
                        currency = price_info.get("currency", "EUR")
                        if price <= 0:
                            continue

                        # Extract airline from first segment
                        segments = (
                            offer.get("itineraries", [{}])[0]
                            .get("segments", [])
                        )
                        airline = (
                            segments[0].get("carrierCode")
                            if segments
                            else None
                        )
                        dep_date = (
                            segments[0]
                            .get("departure", {})
                            .get("at", search_date)[:10]
                            if segments
                            else search_date
                        )
                        stops = max(len(segments) - 1, 0)

                        # 3. Store in price_history
                        await _store_price(
                            db,
                            origin=origin,
                            destination=destination,
                            departure_date=dep_date,
                            airline=airline,
                            price=price,
                            currency=currency,
                            source="amadeus",
                            stops=stops,
                        )

                        # 4. Bug fare anomaly detection
                        alert = detect_anomaly(
                            origin=origin,
                            destination=destination,
                            current_price=price,
                            currency=currency,
                            history=history,
                            source=airline or "amadeus",
                        )
                        if alert:
                            n = await check_and_notify_bug_fares(
                                db, alert
                            )
                            total_notifications += n

                        # 5. Price drop detection
                        if previous_price and price < previous_price:
                            n = await check_and_notify_price_drops(
                                db,
                                origin=origin,
                                destination=destination,
                                current_price=price,
                                previous_price=previous_price,
                                currency=currency,
                                airline=airline,
                                stops=stops,
                            )
                            total_notifications += n

                except Exception:
                    logger.exception(
                        "Error scanning route %s→%s",
                        origin,
                        destination,
                    )

            await db.commit()
            logger.info(
                "Price scan complete. %d routes scanned, "
                "%d notifications sent.",
                len(routes),
                total_notifications,
            )

    except Exception:
        logger.exception("Price scan failed")
    finally:
        await amadeus.close()

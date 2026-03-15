import asyncio
import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.clients.amadeus_client import AmadeusClient
from app.clients.google_flights_client import GoogleFlightsClient
from app.clients.kiwi_client import KiwiClient
from app.clients.normalizer import (
    extract_google_flights_price,
    extract_kiwi_price,
    extract_skyscanner_price,
)
from app.clients.skyscanner_client import SkyscannerClient
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
        # Bug fare: origins x destinations
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


def _min_price_from_offers(offers: list[dict], source: str) -> float | None:
    """Extract minimum price from a list of offers/itineraries by source."""
    prices: list[float] = []
    if source == "amadeus":
        for offer in offers:
            price_info = offer.get("price", {})
            try:
                p = float(price_info.get("total", 0))
                if p > 0:
                    prices.append(p)
            except (ValueError, TypeError):
                continue
    elif source == "skyscanner":
        for itin in offers:
            extracted = extract_skyscanner_price(itin)
            if extracted:
                prices.append(extracted["price"])
    elif source == "kiwi":
        for itin in offers:
            extracted = extract_kiwi_price(itin)
            if extracted:
                prices.append(extracted["price"])
    elif source == "google_flights":
        for itin in offers:
            extracted = extract_google_flights_price(itin)
            if extracted:
                prices.append(extracted["price"])
    return min(prices) if prices else None


async def _search_skyscanner(
    client: SkyscannerClient, origin: str, destination: str, search_date: str
) -> list[dict]:
    """Search Skyscanner, returning empty list on any failure."""
    try:
        return await client.search_flights(origin, destination, search_date)
    except Exception:
        logger.debug("Skyscanner search failed for %s->%s", origin, destination)
        return []


async def _search_kiwi(
    client: KiwiClient, origin: str, destination: str, search_date: str
) -> list[dict]:
    """Search Kiwi, returning empty list on any failure."""
    try:
        return await client.search_flights(origin, destination, search_date)
    except Exception:
        logger.debug("Kiwi search failed for %s->%s", origin, destination)
        return []


async def _search_google_flights(
    client: GoogleFlightsClient, origin: str, destination: str, search_date: str
) -> list[dict]:
    """Search Google Flights, returning empty list on any failure."""
    try:
        return await client.search_flights(origin, destination, search_date)
    except Exception:
        logger.debug("Google Flights search failed for %s->%s", origin, destination)
        return []


async def _process_amadeus_offers(
    db: AsyncSession,
    offers: list[dict],
    origin: str,
    destination: str,
    search_date: str,
    history: list[float],
    previous_price: float | None,
    other_source_price: float | None,
) -> int:
    """Process Amadeus offers: store prices, detect anomalies. Returns notification count."""
    notifications = 0
    for offer in offers:
        price_info = offer.get("price", {})
        price = float(price_info.get("total", 0))
        currency = price_info.get("currency", "EUR")
        if price <= 0:
            continue

        segments = (
            offer.get("itineraries", [{}])[0].get("segments", [])
        )
        airline = segments[0].get("carrierCode") if segments else None
        dep_date = (
            segments[0].get("departure", {}).get("at", search_date)[:10]
            if segments
            else search_date
        )
        stops = max(len(segments) - 1, 0)

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

        alert = detect_anomaly(
            origin=origin,
            destination=destination,
            current_price=price,
            currency=currency,
            history=history,
            source=airline or "amadeus",
            other_source_price=other_source_price,
        )
        if alert:
            n = await check_and_notify_bug_fares(db, alert)
            notifications += n

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
            notifications += n

    return notifications


async def _process_rapidapi_itineraries(
    db: AsyncSession,
    itineraries: list[dict],
    source: str,
    extract_fn,
    origin: str,
    destination: str,
    search_date: str,
    history: list[float],
    other_source_price: float | None,
) -> int:
    """Process Skyscanner/Kiwi itineraries: store prices, detect anomalies."""
    notifications = 0
    for itin in itineraries:
        extracted = extract_fn(itin)
        if not extracted:
            continue

        await _store_price(
            db,
            origin=origin,
            destination=destination,
            departure_date=extracted["departure_date"] or search_date,
            airline=extracted["airline"],
            price=extracted["price"],
            currency=extracted["currency"],
            source=source,
            stops=extracted["stops"],
        )

        alert = detect_anomaly(
            origin=origin,
            destination=destination,
            current_price=extracted["price"],
            currency=extracted["currency"],
            history=history,
            source=extracted["airline"] or source,
            other_source_price=other_source_price,
        )
        if alert:
            n = await check_and_notify_bug_fares(db, alert)
            notifications += n

    return notifications


async def scan_prices():
    """Scan all active subscription routes for price changes.

    Queries Amadeus, Skyscanner, and Kiwi in parallel per route.
    Graceful degradation: if RapidAPI sources fail, Amadeus results
    are still processed.
    """
    logger.info("Starting price scan...")

    amadeus = AmadeusClient()
    skyscanner = SkyscannerClient() if settings.RAPIDAPI_KEY else None
    kiwi = KiwiClient() if settings.RAPIDAPI_KEY else None
    google_flights = GoogleFlightsClient() if settings.RAPIDAPI_KEY else None

    try:
        async with async_session() as db:
            routes = await _get_active_routes(db)
            if not routes:
                logger.info("No active routes to scan.")
                return

            logger.info("Scanning %d routes", len(routes))
            routes = routes[: settings.MAX_ROUTES_STANDARD]

            search_date = (
                datetime.now(UTC) + timedelta(days=14)
            ).strftime("%Y-%m-%d")

            total_notifications = 0

            for route in routes:
                origin = route["origin"]
                destination = route["destination"]

                try:
                    # Query all sources in parallel
                    tasks = [
                        amadeus.search_flights(
                            origin=origin,
                            destination=destination,
                            departure_date=search_date,
                            adults=1,
                            max_results=5,
                        )
                    ]
                    if skyscanner:
                        tasks.append(
                            _search_skyscanner(
                                skyscanner, origin, destination, search_date
                            )
                        )
                    if kiwi:
                        tasks.append(
                            _search_kiwi(
                                kiwi, origin, destination, search_date
                            )
                        )
                    if google_flights:
                        tasks.append(
                            _search_google_flights(
                                google_flights, origin, destination, search_date
                            )
                        )

                    results = await asyncio.gather(
                        *tasks, return_exceptions=True
                    )

                    # Unpack results (graceful: exceptions become empty)
                    idx = 0
                    amadeus_offers = (
                        results[idx]
                        if not isinstance(results[idx], BaseException)
                        else []
                    )
                    idx += 1
                    sky_itins = []
                    if skyscanner:
                        sky_itins = (
                            results[idx]
                            if not isinstance(results[idx], BaseException)
                            else []
                        )
                        idx += 1
                    kiwi_itins = []
                    if kiwi:
                        kiwi_itins = (
                            results[idx]
                            if not isinstance(results[idx], BaseException)
                            else []
                        )
                        idx += 1
                    gf_itins = []
                    if google_flights:
                        gf_itins = (
                            results[idx]
                            if not isinstance(results[idx], BaseException)
                            else []
                        )

                    if (
                        not amadeus_offers
                        and not sky_itins
                        and not kiwi_itins
                        and not gf_itins
                    ):
                        continue

                    previous_price = await _get_previous_price(
                        db, origin, destination
                    )
                    history = await _get_price_history(
                        db, origin, destination
                    )

                    # Compute min prices per source for cross-validation
                    amadeus_min = _min_price_from_offers(
                        amadeus_offers, "amadeus"
                    )
                    sky_min = _min_price_from_offers(sky_itins, "skyscanner")
                    kiwi_min = _min_price_from_offers(kiwi_itins, "kiwi")
                    gf_min = _min_price_from_offers(gf_itins, "google_flights")

                    # For cross-source validation, use the min from other sources
                    other_prices = [
                        p
                        for p in [amadeus_min, sky_min, kiwi_min, gf_min]
                        if p is not None
                    ]

                    def _other_min(exclude: float | None) -> float | None:
                        others = [p for p in other_prices if p != exclude]
                        return min(others) if others else None

                    # Process Amadeus offers
                    if amadeus_offers:
                        n = await _process_amadeus_offers(
                            db,
                            amadeus_offers,
                            origin,
                            destination,
                            search_date,
                            history,
                            previous_price,
                            _other_min(amadeus_min),
                        )
                        total_notifications += n

                    # Process Skyscanner itineraries
                    if sky_itins:
                        n = await _process_rapidapi_itineraries(
                            db,
                            sky_itins,
                            "skyscanner",
                            extract_skyscanner_price,
                            origin,
                            destination,
                            search_date,
                            history,
                            _other_min(sky_min),
                        )
                        total_notifications += n

                    # Process Kiwi itineraries
                    if kiwi_itins:
                        n = await _process_rapidapi_itineraries(
                            db,
                            kiwi_itins,
                            "kiwi",
                            extract_kiwi_price,
                            origin,
                            destination,
                            search_date,
                            history,
                            _other_min(kiwi_min),
                        )
                        total_notifications += n

                    # Process Google Flights itineraries
                    if gf_itins:
                        n = await _process_rapidapi_itineraries(
                            db,
                            gf_itins,
                            "google_flights",
                            extract_google_flights_price,
                            origin,
                            destination,
                            search_date,
                            history,
                            _other_min(gf_min),
                        )
                        total_notifications += n

                except Exception:
                    logger.exception(
                        "Error scanning route %s->%s",
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
        if skyscanner:
            await skyscanner.close()
        if kiwi:
            await kiwi.close()
        if google_flights:
            await google_flights.close()

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

    Returns list of dicts with origin, destination, departure_date,
    return_date, trip_type, and date_flexibility keys.
    Filters out subscriptions whose departure_date has already passed.
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

    today = date.today()
    # Dedup by (origin, dest, departure_date, return_date)
    routes: dict[tuple, dict] = {}
    for sub in subscriptions:
        config = sub.config or {}
        origin = config.get("origin")
        dest = config.get("destination")

        # Skip subscriptions without origin/destination
        if not origin or not dest:
            # Handle legacy bulk format (origins x destinations)
            origins = config.get("origins", [])
            destinations = config.get("destinations", [])
            dep_date_str = config.get("departure_date")
            ret_date_str = config.get("return_date")
            trip_type = config.get("trip_type", "roundtrip")
            flexibility = config.get("date_flexibility", 3)

            dep_date = dep_date_str if dep_date_str else None
            ret_date = ret_date_str if ret_date_str else None

            # Skip expired
            if dep_date and dep_date < today.isoformat():
                continue

            for o in origins:
                for d in destinations:
                    key = (o.upper(), d.upper(), dep_date, ret_date)
                    if key not in routes:
                        routes[key] = {
                            "origin": o.upper(),
                            "destination": d.upper(),
                            "departure_date": dep_date,
                            "return_date": ret_date,
                            "trip_type": trip_type,
                            "date_flexibility": flexibility,
                        }
            continue

        origin = origin.upper()
        dest = dest.upper()
        dep_date_str = config.get("departure_date")
        ret_date_str = config.get("return_date")
        trip_type = config.get("trip_type", "roundtrip")
        flexibility = config.get("date_flexibility", 3)

        dep_date = dep_date_str if dep_date_str else None
        ret_date = ret_date_str if ret_date_str else None

        # Skip expired subscriptions
        if dep_date and dep_date < today.isoformat():
            continue

        key = (origin, dest, dep_date, ret_date)
        if key not in routes:
            routes[key] = {
                "origin": origin,
                "destination": dest,
                "departure_date": dep_date,
                "return_date": ret_date,
                "trip_type": trip_type,
                "date_flexibility": flexibility,
            }

    return list(routes.values())


async def _get_price_history(
    db: AsyncSession,
    origin: str,
    destination: str,
    departure_date: str | None = None,
    return_date: str | None = None,
) -> list[float]:
    """Get historical prices for a route from price_history table."""
    conditions = [
        PriceHistory.origin == origin,
        PriceHistory.destination == destination,
    ]
    if departure_date:
        conditions.append(
            PriceHistory.departure_date == date.fromisoformat(departure_date)
        )
    if return_date:
        conditions.append(
            PriceHistory.return_date == date.fromisoformat(return_date)
        )

    stmt = (
        select(PriceHistory.price_amount)
        .where(*conditions)
        .order_by(PriceHistory.created_at.desc())
        .limit(30)
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def _get_previous_price(
    db: AsyncSession,
    origin: str,
    destination: str,
    departure_date: str | None = None,
    return_date: str | None = None,
) -> float | None:
    """Get the most recent price for a route."""
    conditions = [
        PriceHistory.origin == origin,
        PriceHistory.destination == destination,
    ]
    if departure_date:
        conditions.append(
            PriceHistory.departure_date == date.fromisoformat(departure_date)
        )
    if return_date:
        conditions.append(
            PriceHistory.return_date == date.fromisoformat(return_date)
        )

    stmt = (
        select(PriceHistory.price_amount)
        .where(*conditions)
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
    return_date: str | None = None,
) -> None:
    """Store a price data point in price_history."""
    record = PriceHistory(
        origin=origin,
        destination=destination,
        departure_date=date.fromisoformat(departure_date),
        return_date=date.fromisoformat(return_date) if return_date else None,
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
    client: SkyscannerClient,
    origin: str,
    destination: str,
    search_date: str,
    return_date: str | None = None,
) -> list[dict]:
    """Search Skyscanner, returning empty list on any failure."""
    try:
        return await client.search_flights(
            origin, destination, search_date, return_date=return_date
        )
    except Exception:
        logger.debug("Skyscanner search failed for %s->%s", origin, destination)
        return []


async def _search_kiwi(
    client: KiwiClient,
    origin: str,
    destination: str,
    search_date: str,
    return_date: str | None = None,
) -> list[dict]:
    """Search Kiwi, returning empty list on any failure."""
    try:
        return await client.search_flights(
            origin, destination, search_date, return_date=return_date
        )
    except Exception:
        logger.debug("Kiwi search failed for %s->%s", origin, destination)
        return []


async def _search_google_flights(
    client: GoogleFlightsClient,
    origin: str,
    destination: str,
    search_date: str,
    return_date: str | None = None,
) -> list[dict]:
    """Search Google Flights, returning empty list on any failure."""
    try:
        return await client.search_flights(
            origin, destination, search_date, return_date=return_date
        )
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
    return_date: str | None = None,
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
            return_date=return_date,
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
    return_date: str | None = None,
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
            return_date=return_date,
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


async def _scan_route(
    route: dict,
    fallback_date: str,
    amadeus: AmadeusClient,
    skyscanner: SkyscannerClient | None,
    kiwi: KiwiClient | None,
    google_flights: GoogleFlightsClient | None,
) -> int:
    """Scan a single route across all sources. Returns notification count.

    Each route gets its own DB session to allow safe concurrent execution.
    """
    origin = route["origin"]
    destination = route["destination"]
    search_date = route.get("departure_date") or fallback_date
    return_date = route.get("return_date")
    trip_type = route.get("trip_type", "oneway")

    # For oneway trips, don't pass return_date
    if trip_type == "oneway":
        return_date = None

    try:
        # Query all sources in parallel
        tasks = [
            amadeus.search_flights(
                origin=origin,
                destination=destination,
                departure_date=search_date,
                return_date=return_date,
                adults=1,
                max_results=5,
            )
        ]
        if skyscanner:
            tasks.append(
                _search_skyscanner(
                    skyscanner, origin, destination,
                    search_date, return_date=return_date,
                )
            )
        if kiwi:
            tasks.append(
                _search_kiwi(
                    kiwi, origin, destination,
                    search_date, return_date=return_date,
                )
            )
        if google_flights:
            tasks.append(
                _search_google_flights(
                    google_flights, origin, destination,
                    search_date, return_date=return_date,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

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
            return 0

        # Each route uses its own DB session for concurrent safety
        notifications = 0
        async with async_session() as db:
            previous_price = await _get_previous_price(
                db, origin, destination,
                departure_date=search_date,
                return_date=return_date,
            )
            history = await _get_price_history(
                db, origin, destination,
                departure_date=search_date,
                return_date=return_date,
            )

            # Compute min prices per source for cross-validation
            amadeus_min = _min_price_from_offers(amadeus_offers, "amadeus")
            sky_min = _min_price_from_offers(sky_itins, "skyscanner")
            kiwi_min = _min_price_from_offers(kiwi_itins, "kiwi")
            gf_min = _min_price_from_offers(gf_itins, "google_flights")

            other_prices = [
                p
                for p in [amadeus_min, sky_min, kiwi_min, gf_min]
                if p is not None
            ]

            def _other_min(exclude: float | None) -> float | None:
                others = [p for p in other_prices if p != exclude]
                return min(others) if others else None

            if amadeus_offers:
                n = await _process_amadeus_offers(
                    db, amadeus_offers, origin, destination,
                    search_date, history, previous_price,
                    _other_min(amadeus_min),
                    return_date=return_date,
                )
                notifications += n

            if sky_itins:
                n = await _process_rapidapi_itineraries(
                    db, sky_itins, "skyscanner",
                    extract_skyscanner_price,
                    origin, destination, search_date, history,
                    _other_min(sky_min),
                    return_date=return_date,
                )
                notifications += n

            if kiwi_itins:
                n = await _process_rapidapi_itineraries(
                    db, kiwi_itins, "kiwi",
                    extract_kiwi_price,
                    origin, destination, search_date, history,
                    _other_min(kiwi_min),
                    return_date=return_date,
                )
                notifications += n

            if gf_itins:
                n = await _process_rapidapi_itineraries(
                    db, gf_itins, "google_flights",
                    extract_google_flights_price,
                    origin, destination, search_date, history,
                    _other_min(gf_min),
                    return_date=return_date,
                )
                notifications += n

            await db.commit()

        return notifications

    except Exception:
        logger.exception(
            "Error scanning route %s->%s", origin, destination,
        )
        return 0


async def scan_prices():
    """Scan all active subscription routes for price changes.

    Uses fixed departure dates from subscription config instead of now+14d.
    Routes are scanned concurrently with a semaphore to bound parallelism
    (default: 10 concurrent routes, configurable via SCAN_CONCURRENCY).
    Each route queries Amadeus, Skyscanner, Kiwi, and Google Flights in parallel.
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

        logger.info("Scanning %d routes (concurrency=%d)",
                     len(routes), settings.SCAN_CONCURRENCY)
        routes = routes[: settings.MAX_ROUTES_PER_SCAN]

        # Fallback date for legacy subscriptions without departure_date
        fallback_date = (
            datetime.now(UTC) + timedelta(days=14)
        ).strftime("%Y-%m-%d")

        sem = asyncio.Semaphore(settings.SCAN_CONCURRENCY)

        async def _bounded_scan(route: dict) -> int:
            async with sem:
                return await _scan_route(
                    route, fallback_date,
                    amadeus, skyscanner, kiwi, google_flights,
                )

        results = await asyncio.gather(
            *[_bounded_scan(r) for r in routes],
            return_exceptions=True,
        )

        total_notifications = sum(
            r for r in results if isinstance(r, int)
        )

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

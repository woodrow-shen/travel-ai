import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.clients.amadeus_client import AmadeusClient
from app.db import async_session
from app.models import PriceHistory, Subscription, SubscriptionType
from app.notifier import DealItem, check_and_send_deal_digests

logger = logging.getLogger(__name__)

# Home airports to search deals from (Taiwan defaults)
DEFAULT_ORIGINS = ["TPE", "KHH"]


async def _gather_deals_from_history(db) -> list[DealItem]:
    """Find the best recent deals from price_history (last 24 hours)."""
    since = datetime.now(UTC) - timedelta(hours=24)
    stmt = (
        select(PriceHistory)
        .where(PriceHistory.created_at >= since)
        .order_by(PriceHistory.price_amount.asc())
        .limit(50)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    deals: list[DealItem] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row.origin, row.destination)
        if key in seen:
            continue
        seen.add(key)
        deals.append(
            DealItem(
                origin=row.origin,
                destination=row.destination,
                airline=row.airline or "",
                departure_date=str(row.departure_date),
                price=row.price_amount,
                currency=row.price_currency,
            )
        )
    return deals


async def _gather_deals_from_inspiration(
    amadeus: AmadeusClient,
) -> list[DealItem]:
    """Fetch inspiration deals from Amadeus for default origins."""
    deals: list[DealItem] = []

    for origin in DEFAULT_ORIGINS:
        try:
            results = await amadeus.search_inspiration(origin)
            for item in results[:10]:
                deals.append(
                    DealItem(
                        origin=origin,
                        destination=item.get("destination", ""),
                        airline="",
                        departure_date=item.get("departureDate", ""),
                        price=float(item.get("price", {}).get("total", 0)),
                        currency=item.get("price", {}).get(
                            "currency", "EUR"
                        ),
                        tags=["inspiration"],
                    )
                )
        except Exception:
            logger.exception(
                "Inspiration search failed for %s", origin
            )

    return deals


async def generate_deal_digest():
    """Generate and send daily/weekly deal digest emails."""
    logger.info("Generating deal digest...")

    amadeus = AmadeusClient()

    try:
        async with async_session() as db:
            # Check if there are any active deal_digest subscriptions
            stmt = (
                select(Subscription)
                .where(
                    Subscription.type == SubscriptionType.DEAL_DIGEST,
                    Subscription.is_active.is_(True),
                )
                .limit(1)
            )
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                logger.info("No active deal digest subscriptions.")
                return

            # Gather deals from two sources
            history_deals = await _gather_deals_from_history(db)
            inspiration_deals = await _gather_deals_from_inspiration(
                amadeus
            )

            # Merge and deduplicate, sort by price
            all_deals = history_deals + inspiration_deals
            all_deals.sort(key=lambda d: d.price)

            if not all_deals:
                logger.info("No deals found for digest.")
                return

            # Send digests
            sent = await check_and_send_deal_digests(db, all_deals)
            await db.commit()

            logger.info(
                "Deal digest complete. %d deals, %d digests sent.",
                len(all_deals),
                sent,
            )

    except Exception:
        logger.exception("Deal digest generation failed")
    finally:
        await amadeus.close()

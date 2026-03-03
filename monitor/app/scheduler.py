from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.tasks.cleanup import cleanup_expired_data
from app.tasks.deal_digest import generate_deal_digest
from app.tasks.price_scan import scan_prices


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        scan_prices,
        "interval",
        hours=settings.SCAN_INTERVAL_HOURS,
        id="price_scan",
        name="Scan active subscription routes",
    )

    scheduler.add_job(
        generate_deal_digest,
        "cron",
        hour=6,
        minute=0,
        id="deal_digest",
        name="Generate daily deal digest",
    )

    scheduler.add_job(
        cleanup_expired_data,
        "cron",
        hour=3,
        minute=0,
        id="cleanup",
        name="Clean up expired price data",
    )

    return scheduler

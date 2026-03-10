import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete

from app.db import async_session
from app.models import NotificationLog, PriceHistory

logger = logging.getLogger(__name__)

PRICE_HISTORY_RETENTION_DAYS = 180
NOTIFICATION_LOG_RETENTION_DAYS = 90


async def cleanup_expired_data():
    """Clean up expired price history and notification logs."""
    logger.info("Starting data cleanup...")

    try:
        async with async_session() as db:
            now = datetime.now(UTC)

            # 1. Delete price_history records older than 180 days
            price_cutoff = now - timedelta(days=PRICE_HISTORY_RETENTION_DAYS)
            price_stmt = delete(PriceHistory).where(
                PriceHistory.created_at < price_cutoff
            )
            price_result = await db.execute(price_stmt)
            price_deleted = price_result.rowcount

            # 2. Delete notification_log records older than 90 days
            notif_cutoff = now - timedelta(
                days=NOTIFICATION_LOG_RETENTION_DAYS
            )
            notif_stmt = delete(NotificationLog).where(
                NotificationLog.sent_at < notif_cutoff
            )
            notif_result = await db.execute(notif_stmt)
            notif_deleted = notif_result.rowcount

            await db.commit()

            logger.info(
                "Cleanup complete. Deleted %d price_history records "
                "(>%dd) and %d notification_log records (>%dd).",
                price_deleted,
                PRICE_HISTORY_RETENTION_DAYS,
                notif_deleted,
                NOTIFICATION_LOG_RETENTION_DAYS,
            )

    except Exception:
        logger.exception("Data cleanup failed")

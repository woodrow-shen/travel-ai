import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import delete, select, update

from app.db import async_session
from app.models import NotificationLog, PriceHistory, Subscription

logger = logging.getLogger(__name__)

PRICE_HISTORY_RETENTION_DAYS = 180
NOTIFICATION_LOG_RETENTION_DAYS = 90


async def _deactivate_expired_subscriptions(db) -> int:
    """Deactivate subscriptions whose departure_date has passed.

    Returns count of deactivated subscriptions.
    """
    today_str = date.today().isoformat()

    # Find active subscriptions with a departure_date in the past
    stmt = select(Subscription).where(
        Subscription.is_active.is_(True),
        Subscription.config["departure_date"].astext < today_str,
        Subscription.config["departure_date"].astext.isnot(None),
    )
    result = await db.execute(stmt)
    expired = result.scalars().all()

    if not expired:
        return 0

    expired_ids = [sub.id for sub in expired]
    await db.execute(
        update(Subscription)
        .where(Subscription.id.in_(expired_ids))
        .values(is_active=False)
    )

    logger.info(
        "Deactivated %d expired subscriptions (departure_date < %s).",
        len(expired_ids),
        today_str,
    )
    return len(expired_ids)


async def cleanup_expired_data():
    """Clean up expired price history, notification logs, and subscriptions."""
    logger.info("Starting data cleanup...")

    try:
        async with async_session() as db:
            now = datetime.now(UTC)

            # 1. Deactivate expired subscriptions
            expired_count = await _deactivate_expired_subscriptions(db)

            # 2. Delete price_history records older than 180 days
            price_cutoff = now - timedelta(days=PRICE_HISTORY_RETENTION_DAYS)
            price_stmt = delete(PriceHistory).where(
                PriceHistory.created_at < price_cutoff
            )
            price_result = await db.execute(price_stmt)
            price_deleted = price_result.rowcount

            # 3. Delete notification_log records older than 90 days
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
                "Cleanup complete. Deactivated %d expired subscriptions, "
                "deleted %d price_history records (>%dd) and "
                "%d notification_log records (>%dd).",
                expired_count,
                price_deleted,
                PRICE_HISTORY_RETENTION_DAYS,
                notif_deleted,
                NOTIFICATION_LOG_RETENTION_DAYS,
            )

    except Exception:
        logger.exception("Data cleanup failed")

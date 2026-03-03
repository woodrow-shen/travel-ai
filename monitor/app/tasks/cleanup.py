import logging

logger = logging.getLogger(__name__)


async def cleanup_expired_data():
    """Clean up expired price history and notification logs."""
    logger.info("Starting data cleanup...")

    # TODO: Implementation steps:
    # 1. Delete price_history records older than 180 days
    # 2. Delete notification_log records older than 90 days
    # 3. Deactivate subscriptions for deleted users

    logger.info("Data cleanup complete.")

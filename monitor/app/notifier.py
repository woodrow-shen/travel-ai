import logging

logger = logging.getLogger(__name__)


async def send_bug_fare_notification(alert, subscription, email_address: str) -> bool:
    # TODO: Integrate with email_service for actual sending
    logger.info(
        "Bug Fare Alert: %s→%s at %s %s (avg: %s) -> %s",
        alert.origin,
        alert.destination,
        alert.current_price,
        alert.currency,
        alert.average_price,
        email_address,
    )
    return True


async def send_price_drop_notification(
    origin: str,
    destination: str,
    current_price: float,
    previous_price: float,
    target_price: float,
    currency: str,
    subscription,
    email_address: str,
) -> bool:
    logger.info(
        "Price Drop: %s→%s dropped from %s to %s %s (target: %s) -> %s",
        origin,
        destination,
        previous_price,
        current_price,
        currency,
        target_price,
        email_address,
    )
    return True

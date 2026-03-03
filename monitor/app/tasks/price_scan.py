import logging

logger = logging.getLogger(__name__)


async def scan_prices():
    """Scan all active subscription routes for price changes."""
    logger.info("Starting price scan...")

    # TODO: Implementation steps:
    # 1. Query all active subscriptions, aggregate unique routes
    # 2. For each route, query Amadeus
    # 3. Store results in price_history
    # 4. Run anomaly detection for bug fares
    # 5. Check price drop conditions
    # 6. Send notifications for matches

    logger.info("Price scan complete.")

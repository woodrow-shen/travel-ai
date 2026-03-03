from app.tasks.price_scan import scan_prices
from app.tasks.deal_digest import generate_deal_digest
from app.tasks.cleanup import cleanup_expired_data


async def test_scan_prices_runs():
    """Smoke test: scan_prices should run without error."""
    await scan_prices()


async def test_generate_deal_digest_runs():
    """Smoke test: generate_deal_digest should run without error."""
    await generate_deal_digest()


async def test_cleanup_runs():
    """Smoke test: cleanup should run without error."""
    await cleanup_expired_data()

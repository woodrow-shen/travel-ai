
from app.clients.rate_limiter import TokenBucketRateLimiter


async def test_rate_limiter_allows_within_capacity():
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=5)
    # Should allow 5 immediate requests
    for _ in range(5):
        await limiter.acquire()
    # Tokens should be approximately depleted (allow small refill from elapsed time)
    assert limiter.tokens < 0.1


async def test_rate_limiter_refills():
    limiter = TokenBucketRateLimiter(rate=1000.0, capacity=10)
    # Exhaust tokens
    for _ in range(10):
        await limiter.acquire()
    # With high rate, tokens refill quickly
    import asyncio
    await asyncio.sleep(0.02)
    # Should be able to acquire again
    await limiter.acquire()

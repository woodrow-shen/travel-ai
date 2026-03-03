"""Currency conversion utilities using open exchange rate API."""

from __future__ import annotations

import json
import logging

import httpx

logger = logging.getLogger(__name__)

_CACHE_TTL = 6 * 60 * 60  # 6 hours


async def get_exchange_rates(base: str) -> dict[str, float]:
    """Fetch exchange rates for *base* currency, cached in Redis for 6 hours.

    Returns a dict like ``{"USD": 1.17, "TWD": 35.2, ...}`` on success,
    or an empty dict on any failure (API down, Redis down, etc.).
    """
    cache_key = f"exchange_rates:{base.upper()}"

    # Try Redis cache first
    try:
        from app.db.redis import redis_client

        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        logger.debug("Redis cache read failed for exchange rates", exc_info=True)

    # Fetch from API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"https://open.er-api.com/v6/latest/{base.upper()}")
            resp.raise_for_status()
            data = resp.json()

        if data.get("result") != "success":
            logger.warning("Exchange rate API returned non-success: %s", data.get("result"))
            return {}

        rates: dict[str, float] = data.get("rates", {})
    except Exception:
        logger.warning("Failed to fetch exchange rates for %s", base, exc_info=True)
        return {}

    # Cache in Redis
    try:
        from app.db.redis import redis_client

        await redis_client.setex(cache_key, _CACHE_TTL, json.dumps(rates))
    except Exception:
        logger.debug("Redis cache write failed for exchange rates", exc_info=True)

    return rates


def convert_price(
    amount: float,
    from_currency: str,
    to_currency: str,
    rates: dict[str, float],
) -> tuple[float, str]:
    """Convert *amount* from one currency to another using pre-fetched rates.

    The *rates* dict must be keyed by the **base** currency used when fetching
    (i.e. ``rates`` returned by ``get_exchange_rates(from_currency)``).

    Returns ``(converted_amount, to_currency)`` on success, or
    ``(amount, from_currency)`` if the target rate is missing (graceful fallback).
    """
    if from_currency == to_currency:
        return amount, to_currency

    rate = rates.get(to_currency)
    if rate is None:
        return amount, from_currency

    return round(amount * rate, 2), to_currency

"""IP geolocation → currency detection endpoint."""

import logging

import httpx
from fastapi import APIRouter, Request

from app.db.redis import redis_client

router = APIRouter()
logger = logging.getLogger(__name__)

_CACHE_TTL = 86400  # 24 hours

# Common country code → currency mapping (Asia-Pacific focus)
COUNTRY_TO_CURRENCY: dict[str, str] = {
    "TW": "TWD",
    "JP": "JPY",
    "KR": "KRW",
    "CN": "CNY",
    "HK": "HKD",
    "SG": "SGD",
    "TH": "THB",
    "MY": "MYR",
    "PH": "PHP",
    "VN": "VND",
    "ID": "IDR",
    "IN": "INR",
    "AU": "AUD",
    "NZ": "NZD",
    "US": "USD",
    "CA": "CAD",
    "GB": "GBP",
    "DE": "EUR",
    "FR": "EUR",
    "IT": "EUR",
    "ES": "EUR",
    "NL": "EUR",
    "AT": "EUR",
    "BE": "EUR",
    "PT": "EUR",
    "IE": "EUR",
    "FI": "EUR",
    "GR": "EUR",
}

_DEFAULT_CURRENCY = "TWD"
_DEFAULT_COUNTRY = "TW"


def _get_client_ip(request: Request) -> str:
    """Extract client IP from X-Forwarded-For or request.client."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


@router.get("/currency")
async def get_currency(request: Request):
    """Detect user's currency from IP geolocation."""
    ip = _get_client_ip(request)

    # Skip geolocation for local/private IPs
    if not ip or ip.startswith(("127.", "10.", "172.", "192.168.", "::1")):
        return {"currency": _DEFAULT_CURRENCY, "country": _DEFAULT_COUNTRY}

    # Check Redis cache
    cache_key = f"geo:currency:{ip}"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            parts = cached.split(":")
            return {"currency": parts[0], "country": parts[1] if len(parts) > 1 else ""}
    except Exception:
        logger.debug("Redis cache read failed for geo", exc_info=True)

    # Call ip-api.com (free, no key required)
    country_code = ""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,countryCode"},
            )
            data = resp.json()
            if data.get("status") == "success":
                country_code = data.get("countryCode", "")
    except Exception:
        logger.debug("ip-api.com lookup failed for %s", ip, exc_info=True)

    currency = COUNTRY_TO_CURRENCY.get(country_code, _DEFAULT_CURRENCY)
    country = country_code or _DEFAULT_COUNTRY

    # Cache result
    try:
        await redis_client.setex(cache_key, _CACHE_TTL, f"{currency}:{country}")
    except Exception:
        logger.debug("Redis cache write failed for geo", exc_info=True)

    return {"currency": currency, "country": country}

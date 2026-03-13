import logging
import time

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# How long to back off after a 429 (seconds). Default: 1 hour.
_BACKOFF_SECONDS = 3600


class RapidAPIBaseClient:
    """Base client for all RapidAPI services."""

    # Class-level 429 tracking: {host: resume_timestamp}
    _blocked_until: dict[str, float] = {}

    def __init__(self, base_url: str, host: str):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self._host = host
        self._headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": host,
        }

    def _is_blocked(self) -> bool:
        until = self._blocked_until.get(self._host, 0)
        if time.monotonic() < until:
            return True
        return False

    def _mark_blocked(self) -> None:
        self._blocked_until[self._host] = (
            time.monotonic() + _BACKOFF_SECONDS
        )
        logger.warning(
            "RapidAPI %s hit 429, backing off for %ds",
            self._host,
            _BACKOFF_SECONDS,
        )

    async def _get(self, path: str, params: dict | None = None) -> dict:
        if self._is_blocked():
            logger.debug("RapidAPI %s skipped (quota backoff)", self._host)
            return {}
        try:
            resp = await self._client.get(
                path, params=params, headers=self._headers
            )
            if resp.status_code == 429:
                self._mark_blocked()
                return {}
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError:
            logger.exception("RapidAPI GET %s failed", path)
            return {}
        except Exception:
            logger.exception("RapidAPI GET %s failed", path)
            return {}

    async def close(self):
        await self._client.aclose()

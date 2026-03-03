import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class RapidAPIBaseClient:
    """Base client for all RapidAPI services."""

    def __init__(self, base_url: str, host: str):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self._headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": host,
        }

    async def _get(self, path: str, params: dict | None = None) -> dict:
        try:
            resp = await self._client.get(path, params=params, headers=self._headers)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.exception("RapidAPI GET %s failed", path)
            return {}

    async def _post(self, path: str, json: dict | None = None) -> dict:
        try:
            resp = await self._client.post(path, json=json, headers=self._headers)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.exception("RapidAPI POST %s failed", path)
            return {}

    async def close(self):
        await self._client.aclose()

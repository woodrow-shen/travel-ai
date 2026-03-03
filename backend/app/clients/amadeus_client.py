import logging
from datetime import UTC, datetime, timedelta

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AmadeusClient:
    def __init__(self):
        self.base_url = settings.AMADEUS_BASE_URL.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        self._token: str | None = None
        self._token_expires: datetime | None = None

    async def _authenticate(self):
        resp = await self._client.post(
            "/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.AMADEUS_API_KEY,
                "client_secret": settings.AMADEUS_API_SECRET,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires = datetime.now(UTC) + timedelta(seconds=data["expires_in"])

    async def _ensure_auth(self):
        if self._token is None or (
            self._token_expires and datetime.now(UTC) >= self._token_expires
        ):
            await self._authenticate()

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None = None,
        adults: int = 1,
        cabin_class: str | None = None,
        max_stops: int | None = None,
        max_results: int = 20,
    ) -> list[dict]:
        await self._ensure_auth()

        params: dict = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
        }
        if return_date:
            params["returnDate"] = return_date
        if cabin_class:
            params["travelClass"] = cabin_class.upper()
        if max_stops is not None:
            params["nonStop"] = "true" if max_stops == 0 else "false"

        try:
            resp = await self._client.get(
                "/v2/shopping/flight-offers",
                params=params,
                headers={"Authorization": f"Bearer {self._token}"},
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception:
            logger.exception("Amadeus flight search failed")
            return []

    async def search_inspiration(
        self, origin: str, departure_date: str | None = None
    ) -> list[dict]:
        await self._ensure_auth()

        params: dict = {"origin": origin}
        if departure_date:
            params["departureDate"] = departure_date

        try:
            resp = await self._client.get(
                "/v1/shopping/flight-destinations",
                params=params,
                headers={"Authorization": f"Bearer {self._token}"},
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception:
            logger.exception("Amadeus inspiration search failed")
            return []

    async def close(self):
        await self._client.aclose()

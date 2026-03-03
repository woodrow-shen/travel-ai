import logging
from datetime import datetime, timezone

from app.clients.base_client import BaseAPIClient
from app.config import settings

logger = logging.getLogger(__name__)


class AmadeusClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.AMADEUS_BASE_URL)
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
        self._token_expires = datetime.now(timezone.utc).replace(
            second=datetime.now(timezone.utc).second + data["expires_in"]
        )

    async def _ensure_auth(self):
        if self._token is None or (
            self._token_expires and datetime.now(timezone.utc) >= self._token_expires
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
        max_results: int = 10,
    ) -> list[dict]:
        await self._ensure_auth()

        params = {
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

        try:
            data = await self.get(
                "/v2/shopping/flight-offers",
                params=params,
                headers={"Authorization": f"Bearer {self._token}"},
            )
            return data.get("data", [])
        except Exception:
            logger.exception("Amadeus flight search failed")
            return []

    async def search_inspiration(
        self, origin: str, departure_date: str | None = None, max_price: int | None = None
    ) -> list[dict]:
        await self._ensure_auth()

        params = {"origin": origin}
        if departure_date:
            params["departureDate"] = departure_date
        if max_price:
            params["maxPrice"] = max_price

        try:
            data = await self.get(
                "/v1/shopping/flight-destinations",
                params=params,
                headers={"Authorization": f"Bearer {self._token}"},
            )
            return data.get("data", [])
        except Exception:
            logger.exception("Amadeus inspiration search failed")
            return []

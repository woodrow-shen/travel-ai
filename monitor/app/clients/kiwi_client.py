import logging

from app.clients.rapidapi_base import RapidAPIBaseClient
from app.config import settings

logger = logging.getLogger(__name__)


class KiwiClient(RapidAPIBaseClient):
    """Simplified Kiwi client for price monitoring (flights only)."""

    def __init__(self):
        super().__init__(
            f"https://{settings.RAPIDAPI_KIWI_HOST}",
            settings.RAPIDAPI_KIWI_HOST,
        )

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None = None,
        adults: int = 1,
        currency: str = "TWD",
    ) -> list[dict]:
        params = {
            "originSkyId": origin,
            "destinationSkyId": destination,
            "adults": adults,
            "cabinClass": "ECONOMY",
            "currency": currency,
            "market": "TW",
            "locale": "zh-TW",
            "limit": 10,
            "stops": 0,
        }
        if return_date:
            params["departureDate"] = departure_date
            params["returnDate"] = return_date
            endpoint = "/flights/search-return"
        else:
            params["departureDate"] = departure_date
            endpoint = "/flights/search-oneway"

        data = await self._get(endpoint, params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("itineraries", [])

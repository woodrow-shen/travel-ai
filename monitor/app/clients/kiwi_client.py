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
        adults: int = 1,
        currency: str = "TWD",
    ) -> list[dict]:
        params = {
            "originSkyId": origin,
            "destinationSkyId": destination,
            "departureDate": departure_date,
            "adults": adults,
            "cabinClass": "ECONOMY",
            "currency": currency,
            "market": "TW",
            "locale": "zh-TW",
            "limit": 10,
            "stops": 0,
        }
        data = await self._get("/flights/search-oneway", params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("itineraries", [])

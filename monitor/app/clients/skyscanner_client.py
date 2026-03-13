import logging

from app.clients.rapidapi_base import RapidAPIBaseClient
from app.config import settings

logger = logging.getLogger(__name__)


class SkyscannerClient(RapidAPIBaseClient):
    """Simplified Skyscanner client for price monitoring (flights only)."""

    def __init__(self):
        super().__init__(
            f"https://{settings.RAPIDAPI_SKYSCANNER_HOST}",
            settings.RAPIDAPI_SKYSCANNER_HOST,
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
            "cabinClass": "economy",
            "currency": currency,
            "market": "TW",
            "locale": "zh-TW",
            "sort": "best",
        }
        data = await self._get("/v2/flights/search-one-way", params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("itineraries", [])

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
        return_date: str | None = None,
        adults: int = 1,
        currency: str = "TWD",
    ) -> list[dict]:
        params = {
            "originSkyId": origin,
            "destinationSkyId": destination,
            "adults": adults,
            "cabinClass": "economy",
            "currency": currency,
            "market": "TW",
            "locale": "zh-TW",
            "sort": "best",
        }
        if return_date:
            params["departureDate"] = departure_date
            params["returnDate"] = return_date
            endpoint = "/v2/flights/search-roundtrip"
        else:
            params["departureDate"] = departure_date
            endpoint = "/v2/flights/search-one-way"

        data = await self._get(endpoint, params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("itineraries", [])

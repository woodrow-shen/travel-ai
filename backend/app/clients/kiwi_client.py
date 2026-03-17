import logging

from app.clients.rapidapi_base import RapidAPIBaseClient
from app.config import settings

logger = logging.getLogger(__name__)


class KiwiClient(RapidAPIBaseClient):
    """Client for Kiwi (Flights Scraper Real-Time) API via RapidAPI."""

    def __init__(self):
        super().__init__(
            f"https://{settings.RAPIDAPI_KIWI_HOST}",
            settings.RAPIDAPI_KIWI_HOST,
        )

    async def autocomplete(self, query: str) -> list[dict]:
        data = await self._get("/flights/auto-complete", {"query": query})
        edges = (
            data.get("data", {})
            .get("metadata", {})
            .get("firstResultStations", {})
            .get("edges", [])
        )
        return [edge.get("node", {}) for edge in edges]

    async def search_flights(
        self,
        origin_sky_id: str,
        destination_sky_id: str,
        departure_date: str,
        return_date: str | None = None,
        adults: int = 1,
        cabin_class: str = "ECONOMY",
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
        limit: int = 20,
        stops: int = 0,
    ) -> list[dict]:
        params: dict = {
            "originSkyId": origin_sky_id,
            "destinationSkyId": destination_sky_id,
            "adults": adults,
            "cabinClass": cabin_class,
            "currency": currency,
            "market": market,
            "locale": locale,
            "limit": limit,
            "stops": stops,
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

    async def search_deals(
        self,
        query: str,
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
    ) -> list[dict]:
        params = {
            "query": query,
            "currency": currency,
            "market": market,
            "locale": locale,
        }
        data = await self._get("/deals/search", params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("deals", [])

    async def price_trends(
        self,
        origin_sky_id: str,
        destination_sky_id: str,
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
    ) -> dict:
        params = {
            "originSkyId": origin_sky_id,
            "destinationSkyId": destination_sky_id,
            "currency": currency,
            "market": market,
            "locale": locale,
        }
        data = await self._get("/flights/price-trends", params)
        if not data.get("status"):
            return {}
        return data.get("data", {})

    async def stays_autocomplete(
        self,
        location: str,
        language_code: str = "en-us",
    ) -> list[dict]:
        """Resolve a location name to Kiwi stays dest_id/dest_type."""
        data = await self._get(
            "/stays/autocomplete",
            {"location": location, "language_code": language_code},
        )
        return data.get("data", [])

    async def search_hotels(
        self,
        dest_id: str,
        dest_type: str,
        checkin: str,
        checkout: str,
        adults: int = 1,
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
    ) -> list[dict]:
        params = {
            "dest_id": dest_id,
            "dest_type": dest_type,
            "checkin": checkin,
            "checkout": checkout,
            "adults": adults,
            "currency": currency,
            "market": market,
            "locale": locale,
        }
        data = await self._get("/stays/search/by-dest", params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("hotels", [])

import logging

from app.clients.rapidapi_base import RapidAPIBaseClient
from app.config import settings

logger = logging.getLogger(__name__)


class SkyscannerClient(RapidAPIBaseClient):
    """Client for Skyscanner (Fly Scraper) API via RapidAPI."""

    def __init__(self):
        super().__init__(
            f"https://{settings.RAPIDAPI_SKYSCANNER_HOST}",
            settings.RAPIDAPI_SKYSCANNER_HOST,
        )

    async def autocomplete(self, query: str) -> list[dict]:
        data = await self._get("/flights/autocomplete", {"query": query})
        if not data.get("status"):
            return []
        return data.get("data", [])

    async def search_flights(
        self,
        origin_sky_id: str,
        destination_sky_id: str,
        departure_date: str,
        return_date: str | None = None,
        adults: int = 1,
        cabin_class: str = "economy",
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
        sort: str = "best",
    ) -> list[dict]:
        params: dict = {
            "originSkyId": origin_sky_id,
            "destinationSkyId": destination_sky_id,
            "adults": adults,
            "cabinClass": cabin_class,
            "currency": currency,
            "market": market,
            "locale": locale,
            "sort": sort,
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

    async def search_flights_incomplete(self, session_id: str) -> list[dict]:
        """Poll for more results when initial search returned status 'incomplete'."""
        data = await self._get(
            "/v2/flights/search-incomplete", {"sessionId": session_id}
        )
        if not data.get("status"):
            return []
        return data.get("data", {}).get("itineraries", [])

    async def search_everywhere(
        self,
        origin_sky_id: str,
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
    ) -> list[dict]:
        params = {
            "originSkyId": origin_sky_id,
            "currency": currency,
            "market": market,
            "locale": locale,
        }
        data = await self._get("/1.0/flights/search-roundtrip", params)
        if not data.get("status"):
            return []
        return data.get("data", [])

    async def price_calendar(
        self,
        origin_sky_id: str,
        destination_sky_id: str,
        from_date: str,
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
    ) -> list[dict]:
        params = {
            "originSkyId": origin_sky_id,
            "destinationSkyId": destination_sky_id,
            "fromDate": from_date,
            "currency": currency,
            "market": market,
            "locale": locale,
        }
        data = await self._get("/flights/price-calendar", params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("flights", {}).get("days", [])

    async def hotel_autocomplete(
        self,
        query: str,
        locale: str = "en-US",
        market: str = "TW",
    ) -> list[dict]:
        """Resolve a location name to hotel entityId(s)."""
        data = await self._get(
            "/hotels/autocomplete",
            {"query": query, "locale": locale, "market": market},
        )
        if not data.get("status", True):
            return []
        return data.get("data", [])

    async def search_hotels(
        self,
        entity_id: str,
        checkin: str,
        checkout: str,
        adults: int = 1,
        currency: str = "TWD",
        market: str = "TW",
        locale: str = "zh-TW",
    ) -> list[dict]:
        params = {
            "entityId": entity_id,
            "checkin": checkin,
            "checkout": checkout,
            "adults": adults,
            "currency": currency,
            "market": market,
            "locale": locale,
        }
        data = await self._get("/hotels/search", params)
        if not data.get("status"):
            return []
        return data.get("data", {}).get("hotels", [])

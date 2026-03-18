import logging

from app.clients.rapidapi_base import RapidAPIBaseClient
from app.config import settings

logger = logging.getLogger(__name__)


class GoogleFlightsClient(RapidAPIBaseClient):
    """Simplified Google Flights Data client for price monitoring."""

    def __init__(self):
        super().__init__(
            f"https://{settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST}",
            settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST,
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
            "departureId": origin,
            "arrivalId": destination,
            "departureDate": departure_date,
            "currency": currency,
        }
        data = await self._get("/flights/search-oneway", params)
        if not data.get("status"):
            return []

        inner = data.get("data", {})
        flights: list[dict] = []
        for flight in inner.get("topFlights", []):
            if flight.get("price") is not None:
                flights.append(flight)
        for flight in inner.get("otherFlights", []):
            if flight.get("price") is not None:
                flights.append(flight)
        return flights

    async def get_price_graph(
        self,
        origin: str,
        destination: str,
        departure_range: str,
        currency: str = "TWD",
    ) -> list[dict]:
        """Get daily lowest prices for a date range (oneway only for monitor).

        Returns list of {departureDate, arrivalDate, price} dicts.
        """
        params = {
            "departureId": origin,
            "arrivalId": destination,
            "departureRange": departure_range,
            "currency": currency,
        }
        data = await self._get("/price-graph/for-oneway", params)
        if not data.get("status"):
            return []

        points = data.get("data", [])
        return [p for p in points if p.get("price")]

import logging

from app.clients.rapidapi_base import RapidAPIBaseClient
from app.config import settings

logger = logging.getLogger(__name__)


class GoogleFlightsClient(RapidAPIBaseClient):
    """Client for Google Flights Data API via RapidAPI.

    Host: google-flights-data.p.rapidapi.com
    Response wraps flights in ``data.topFlights`` / ``data.otherFlights``.
    """

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
        return_date: str | None = None,
        adults: int = 1,
        cabin_class: str | None = None,
        currency: str = "TWD",
    ) -> list[dict]:
        """Search flights via Google Flights Data API.

        Returns a flat list of flight dicts (merged from topFlights + otherFlights).
        Flights with ``price: null`` are filtered out.
        """
        params: dict = {
            "departureId": origin,
            "arrivalId": destination,
            "currency": currency,
        }

        if return_date:
            endpoint = "/flights/search-roundtrip"
        else:
            endpoint = "/flights/search-oneway"

        data = await self._get(endpoint, params)
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
        return_date: str | None = None,
        currency: str = "TWD",
    ) -> list[dict]:
        """Get daily lowest prices for a date range.

        Args:
            departure_range: Comma-separated start,end dates e.g. "2026-04-01,2026-04-30".
            return_date: If set, uses roundtrip endpoint.

        Returns list of {departureDate, arrivalDate, price} dicts.
        Entries with null/zero price are filtered out.
        """
        params: dict = {
            "departureId": origin,
            "arrivalId": destination,
            "departureRange": departure_range,
            "currency": currency,
        }

        if return_date:
            endpoint = "/price-graph/for-roundtrip"
            params["arrivalDate"] = return_date
        else:
            endpoint = "/price-graph/for-oneway"

        data = await self._get(endpoint, params)
        if not data.get("status"):
            return []

        points = data.get("data", [])
        return [p for p in points if p.get("price")]

    async def get_booking_details(
        self,
        booking_token: str,
        currency: str = "TWD",
    ) -> list[dict]:
        """Resolve a booking token into airline booking URLs.

        Returns list of {airlineCode, flightNumber, airlineName, price, bookingLink}.
        """
        params = {
            "bookingToken": booking_token,
            "currency": currency,
        }
        data = await self._get("/flights/booking-details", params)
        if not data.get("status"):
            return []

        return data.get("data", {}).get("bookingOptions", [])

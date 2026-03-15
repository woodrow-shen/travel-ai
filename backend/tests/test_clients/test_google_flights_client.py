from unittest.mock import patch

import httpx
import pytest
import respx

from app.clients.google_flights_client import GoogleFlightsClient

GF_HOST = "google-flights-data.p.rapidapi.com"
BASE_URL = f"https://{GF_HOST}"


@pytest.fixture
def gf_client():
    from app.clients.rapidapi_base import RapidAPIBaseClient

    # Clear any backoff state from other tests
    RapidAPIBaseClient._blocked_until.pop(GF_HOST, None)
    with patch("app.clients.google_flights_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST = GF_HOST
        client = GoogleFlightsClient()
    yield client
    # Clean up after each test
    RapidAPIBaseClient._blocked_until.pop(GF_HOST, None)


# --- Mock response fixtures (matches actual google-flights-data API) ---

SEARCH_RESPONSE = {
    "status": True,
    "status_code": 200,
    "data": {
        "topFlights": [
            {
                "airlineCode": "CI",
                "airlineName": "China Airlines",
                "departureAirport": "TPE",
                "arrivalAirport": "NRT",
                "departureDate": "2026-04-01",
                "arrivalDate": "2026-04-01",
                "durationMinutes": 255,
                "hasStop": False,
                "stops": 0,
                "price": 6790,
                "segments": [
                    {
                        "departureAirportCode": "TPE",
                        "departureAirportName": "Taiwan Taoyuan International Airport",
                        "arrivalAirportCode": "NRT",
                        "arrivalAirportName": "Narita International Airport",
                        "departureTime": "08:30",
                        "arrivalTime": "12:45",
                        "departureDate": "2026-04-01",
                        "arrivalDate": "2026-04-01",
                        "airlineCode": "CI",
                        "flightNumber": "100",
                        "airlineName": "China Airlines",
                        "duration": 255,
                    }
                ],
                "departureTime": "08:30",
                "arrivalTime": "12:45",
            }
        ],
        "otherFlights": [
            {
                "airlineCode": "KE",
                "airlineName": "Korean Air",
                "departureAirport": "TPE",
                "arrivalAirport": "NRT",
                "departureDate": "2026-04-01",
                "arrivalDate": "2026-04-01",
                "durationMinutes": 435,
                "hasStop": True,
                "stops": 1,
                "price": 5200,
                "segments": [
                    {
                        "departureAirportCode": "TPE",
                        "arrivalAirportCode": "ICN",
                        "departureTime": "14:00",
                        "arrivalTime": "17:30",
                        "departureDate": "2026-04-01",
                        "arrivalDate": "2026-04-01",
                        "airlineCode": "KE",
                        "flightNumber": "186",
                        "airlineName": "Korean Air",
                        "duration": 150,
                    },
                    {
                        "departureAirportCode": "ICN",
                        "arrivalAirportCode": "NRT",
                        "departureTime": "19:00",
                        "arrivalTime": "21:15",
                        "departureDate": "2026-04-01",
                        "arrivalDate": "2026-04-01",
                        "airlineCode": "KE",
                        "flightNumber": "703",
                        "airlineName": "Korean Air",
                        "duration": 135,
                    },
                ],
                "departureTime": "14:00",
                "arrivalTime": "21:15",
            },
            {
                "airlineCode": "B6",
                "airlineName": "JetBlue",
                "departureAirport": "TPE",
                "arrivalAirport": "NRT",
                "departureDate": "2026-04-01",
                "arrivalDate": "2026-04-01",
                "durationMinutes": 400,
                "hasStop": False,
                "stops": 0,
                "price": None,
                "segments": [],
                "departureTime": "22:14",
                "arrivalTime": "09:30",
            },
        ],
    },
    "message": "Success",
}


# --- Tests ---


@respx.mock
async def test_search_flights_oneway(gf_client):
    route = respx.get(f"{BASE_URL}/flights/search-oneway").mock(
        return_value=httpx.Response(200, json=SEARCH_RESPONSE)
    )

    result = await gf_client.search_flights("TPE", "NRT", "2026-04-01")

    # 3 flights in response but 1 has price=None, so filtered to 2
    assert len(result) == 2
    assert result[0]["price"] == 6790
    assert result[0]["departureAirport"] == "TPE"
    assert result[1]["price"] == 5200
    assert route.called
    request = route.calls[0].request
    assert "departureId=TPE" in str(request.url)


@respx.mock
async def test_search_flights_roundtrip(gf_client):
    route = respx.get(f"{BASE_URL}/flights/search-roundtrip").mock(
        return_value=httpx.Response(200, json=SEARCH_RESPONSE)
    )

    result = await gf_client.search_flights(
        "TPE", "NRT", "2026-04-01", return_date="2026-04-05"
    )

    assert len(result) == 2
    assert route.called
    # Roundtrip uses different endpoint
    request = route.calls[0].request
    assert "/flights/search-roundtrip" in str(request.url)


@respx.mock
async def test_search_flights_empty(gf_client):
    respx.get(f"{BASE_URL}/flights/search-oneway").mock(
        return_value=httpx.Response(200, json={"status": False, "message": "error"})
    )

    result = await gf_client.search_flights("TPE", "NRT", "2026-04-01")

    assert result == []


@respx.mock
async def test_search_flights_429(gf_client):
    from app.clients.rapidapi_base import RapidAPIBaseClient

    respx.get(f"{BASE_URL}/flights/search-oneway").mock(
        return_value=httpx.Response(429, json={"error": "rate limited"})
    )

    result = await gf_client.search_flights("TPE", "NRT", "2026-04-01")

    assert result == []
    # Clean up class-level backoff state
    RapidAPIBaseClient._blocked_until.pop(GF_HOST, None)


@respx.mock
async def test_search_flights_filters_null_price(gf_client):
    """Flights with price=None should be filtered out."""
    response = {
        "status": True,
        "data": {
            "topFlights": [
                {"price": None, "airlineCode": "XX", "segments": []},
                {"price": 1000, "airlineCode": "CI", "segments": []},
            ],
            "otherFlights": [],
        },
    }
    respx.get(f"{BASE_URL}/flights/search-oneway").mock(
        return_value=httpx.Response(200, json=response)
    )

    result = await gf_client.search_flights("TPE", "NRT", "2026-04-01")

    assert len(result) == 1
    assert result[0]["price"] == 1000


# --- Price graph mock response ---

PRICE_GRAPH_RESPONSE = {
    "status": True,
    "status_code": 200,
    "data": [
        {"departureDate": "2026-04-01", "arrivalDate": None, "price": 10795},
        {"departureDate": "2026-04-02", "arrivalDate": None, "price": 11517},
        {"departureDate": "2026-04-03", "arrivalDate": None, "price": None},
        {"departureDate": "2026-04-04", "arrivalDate": None, "price": 0},
        {"departureDate": "2026-04-05", "arrivalDate": None, "price": 6538},
    ],
    "message": "Success",
}

BOOKING_DETAILS_RESPONSE = {
    "status": True,
    "status_code": 200,
    "data": {
        "bookingOptions": [
            {
                "airlineCode": "GK",
                "flightNumber": "14",
                "airlineName": "Jetstar",
                "price": 5138,
                "domain": "www.jetstar.com/...",
                "bookingLink": "https://www.google.com/travel/clk/f?u=example",
                "fareType": None,
            }
        ]
    },
    "message": "Success",
}


@respx.mock
async def test_get_price_graph_oneway(gf_client):
    route = respx.get(f"{BASE_URL}/price-graph/for-oneway").mock(
        return_value=httpx.Response(200, json=PRICE_GRAPH_RESPONSE)
    )

    result = await gf_client.get_price_graph("TPE", "NRT", "2026-04-01,2026-04-05")

    # 5 entries but price=None and price=0 filtered out → 3
    assert len(result) == 3
    assert result[0]["price"] == 10795
    assert result[0]["departureDate"] == "2026-04-01"
    assert route.called
    request = route.calls[0].request
    assert "departureRange=" in str(request.url)


@respx.mock
async def test_get_price_graph_roundtrip(gf_client):
    route = respx.get(f"{BASE_URL}/price-graph/for-roundtrip").mock(
        return_value=httpx.Response(200, json=PRICE_GRAPH_RESPONSE)
    )

    result = await gf_client.get_price_graph(
        "TPE", "NRT", "2026-04-01,2026-04-05", return_date="2026-04-10"
    )

    assert len(result) == 3
    assert route.called
    request = route.calls[0].request
    assert "/price-graph/for-roundtrip" in str(request.url)
    assert "arrivalDate=" in str(request.url)


@respx.mock
async def test_get_price_graph_empty(gf_client):
    respx.get(f"{BASE_URL}/price-graph/for-oneway").mock(
        return_value=httpx.Response(200, json={"status": False, "message": "error"})
    )

    result = await gf_client.get_price_graph("TPE", "NRT", "2026-04-01,2026-04-05")
    assert result == []


@respx.mock
async def test_get_booking_details(gf_client):
    route = respx.get(f"{BASE_URL}/flights/booking-details").mock(
        return_value=httpx.Response(200, json=BOOKING_DETAILS_RESPONSE)
    )

    result = await gf_client.get_booking_details("test-token-123")

    assert len(result) == 1
    assert result[0]["airlineCode"] == "GK"
    assert result[0]["price"] == 5138
    assert "bookingLink" in result[0]
    assert route.called


@respx.mock
async def test_get_booking_details_empty(gf_client):
    respx.get(f"{BASE_URL}/flights/booking-details").mock(
        return_value=httpx.Response(200, json={"status": False, "message": "error"})
    )

    result = await gf_client.get_booking_details("bad-token")
    assert result == []


def test_missing_api_key():
    with (
        patch("app.clients.google_flights_client.settings") as mock_gf,
        patch("app.clients.rapidapi_base.settings") as mock_base,
    ):
        mock_gf.RAPIDAPI_KEY = ""
        mock_gf.RAPIDAPI_GOOGLE_FLIGHTS_HOST = GF_HOST
        mock_base.RAPIDAPI_KEY = ""
        client = GoogleFlightsClient()
        assert client._headers["x-rapidapi-key"] == ""

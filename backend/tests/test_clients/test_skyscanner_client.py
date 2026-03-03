from unittest.mock import patch

import httpx
import pytest
import respx

from app.clients.skyscanner_client import SkyscannerClient

SKYSCANNER_HOST = "fly-scraper.p.rapidapi.com"
BASE_URL = f"https://{SKYSCANNER_HOST}"


@pytest.fixture
def skyscanner():
    with patch("app.clients.rapidapi_base.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_SKYSCANNER_HOST = SKYSCANNER_HOST
        client = SkyscannerClient()
    yield client


# --- Mock response fixtures ---

AUTOCOMPLETE_RESPONSE = {
    "status": True,
    "data": [
        {
            "presentation": {
                "title": "Taipei Taiwan Taoyuan",
                "suggestionTitle": "...(TPE)",
                "subtitle": "Taiwan",
            },
            "navigation": {
                "entityId": "128667054",
                "entityType": "AIRPORT",
                "relevantFlightParams": {
                    "skyId": "TPE",
                    "entityId": "128667054",
                    "flightPlaceType": "AIRPORT",
                },
            },
            "skyId": "TPE",
        }
    ],
}

SEARCH_ONEWAY_RESPONSE = {
    "status": True,
    "data": {
        "context": {"sessionId": "sess-123", "status": "complete"},
        "itineraries": [
            {
                "id": "itin-001",
                "price": {"formatted": "NT$7,121", "raw": "7121000", "unit": "PRICE_UNIT_MILLI"},
                "legs": [
                    {
                        "originPlaceId": "128667054",
                        "destinationPlaceId": "128668889",
                        "departureDateTime": {
                            "year": 2026, "month": 4, "day": 1,
                            "hour": 2, "minute": 40, "second": 0,
                        },
                        "arrivalDateTime": {
                            "year": 2026, "month": 4, "day": 1,
                            "hour": 10, "minute": 5, "second": 0,
                        },
                        "durationInMinutes": 385,
                        "stopCount": 1,
                        "segments": [
                            {
                                "marketingFlightNumber": "752",
                                "durationInMinutes": 155,
                                "originPlaceId": "128667054",
                                "destinationPlaceId": "128667080",
                                "departureDateTime": {
                                    "year": 2026, "month": 4, "day": 1,
                                    "hour": 2, "minute": 40, "second": 0,
                                },
                                "arrivalDateTime": {
                                    "year": 2026, "month": 4, "day": 1,
                                    "hour": 6, "minute": 15, "second": 0,
                                },
                                "carriers": {
                                    "marketing": {
                                        "name": "Jin Air",
                                        "iata": "LJ",
                                        "imageUrl": "https://logos.skyscnr.com/images/airlines/LJ.png",
                                    },
                                    "operating": {"name": "Jin Air", "iata": "LJ"},
                                },
                            }
                        ],
                    }
                ],
                "pricingOptions": [
                    {
                        "price": {"formatted": "NT$7,142"},
                        "items": [{"deepLink": "https://booking.example.com/flight1"}],
                    }
                ],
            }
        ],
    },
}

SEARCH_ROUNDTRIP_RESPONSE = {
    "status": True,
    "data": {
        "context": {"sessionId": "sess-456", "status": "complete"},
        "itineraries": [
            {
                "id": "itin-rt-001",
                "price": {"formatted": "NT$12,500", "raw": "12500000", "unit": "PRICE_UNIT_MILLI"},
                "legs": [
                    {
                        "originPlaceId": "128667054",
                        "destinationPlaceId": "128668889",
                        "departureDateTime": {
                            "year": 2026, "month": 4, "day": 1,
                            "hour": 8, "minute": 0, "second": 0,
                        },
                        "arrivalDateTime": {
                            "year": 2026, "month": 4, "day": 1,
                            "hour": 12, "minute": 0, "second": 0,
                        },
                        "durationInMinutes": 240,
                        "stopCount": 0,
                        "segments": [
                            {
                                "marketingFlightNumber": "100",
                                "durationInMinutes": 240,
                                "originPlaceId": "128667054",
                                "destinationPlaceId": "128668889",
                                "departureDateTime": {
                                    "year": 2026, "month": 4, "day": 1,
                                    "hour": 8, "minute": 0, "second": 0,
                                },
                                "arrivalDateTime": {
                                    "year": 2026, "month": 4, "day": 1,
                                    "hour": 12, "minute": 0, "second": 0,
                                },
                                "carriers": {
                                    "marketing": {"name": "China Airlines", "iata": "CI"},
                                    "operating": {"name": "China Airlines", "iata": "CI"},
                                },
                            }
                        ],
                    }
                ],
                "pricingOptions": [],
            }
        ],
    },
}

SEARCH_INCOMPLETE_RESPONSE = {
    "status": True,
    "data": {
        "context": {"sessionId": "sess-123", "status": "complete"},
        "itineraries": [
            {
                "id": "itin-incomplete-001",
                "price": {"raw": "8000000", "unit": "PRICE_UNIT_MILLI"},
                "legs": [],
                "pricingOptions": [],
            }
        ],
    },
}

SEARCH_EVERYWHERE_RESPONSE = {
    "status": True,
    "data": [
        {"destinationId": "NRT", "price": {"raw": "5000000"}},
        {"destinationId": "KIX", "price": {"raw": "6000000"}},
    ],
}

PRICE_CALENDAR_RESPONSE = {
    "status": True,
    "data": {
        "flights": {
            "days": [
                {"day": "2026-04-01", "price": 7121, "group": "low"},
                {"day": "2026-04-02", "price": 8500, "group": "medium"},
            ]
        }
    },
}

HOTELS_RESPONSE = {
    "status": True,
    "data": {
        "hotels": [
            {"hotelId": "h001", "name": "Tokyo Hotel", "price": {"amount": 3500}},
        ]
    },
}


# --- Tests ---


@respx.mock
async def test_autocomplete(skyscanner):
    respx.get(f"{BASE_URL}/flights/autocomplete").mock(
        return_value=httpx.Response(200, json=AUTOCOMPLETE_RESPONSE)
    )

    result = await skyscanner.autocomplete("taipei")

    assert len(result) == 1
    assert result[0]["skyId"] == "TPE"
    assert result[0]["navigation"]["entityId"] == "128667054"


@respx.mock
async def test_search_flights_oneway(skyscanner):
    route = respx.get(f"{BASE_URL}/v2/flights/search-one-way").mock(
        return_value=httpx.Response(200, json=SEARCH_ONEWAY_RESPONSE)
    )

    result = await skyscanner.search_flights("TPE", "NRT", "2026-04-01")

    assert len(result) == 1
    assert result[0]["id"] == "itin-001"
    assert result[0]["price"]["raw"] == "7121000"
    assert route.called
    request = route.calls[0].request
    # Verify one-way endpoint used (no return_date)
    assert "returnDate" not in str(request.url)
    # Verify sort param name is "sort" (not "sortBy")
    assert "sort=best" in str(request.url)


@respx.mock
async def test_search_flights_roundtrip(skyscanner):
    route = respx.get(f"{BASE_URL}/v2/flights/search-roundtrip").mock(
        return_value=httpx.Response(200, json=SEARCH_ROUNDTRIP_RESPONSE)
    )

    result = await skyscanner.search_flights("TPE", "NRT", "2026-04-01", return_date="2026-04-05")

    assert len(result) == 1
    assert result[0]["id"] == "itin-rt-001"
    assert route.called
    request = route.calls[0].request
    assert "returnDate=2026-04-05" in str(request.url)


@respx.mock
async def test_search_flights_incomplete(skyscanner):
    route = respx.get(f"{BASE_URL}/v2/flights/search-incomplete").mock(
        return_value=httpx.Response(200, json=SEARCH_INCOMPLETE_RESPONSE)
    )

    result = await skyscanner.search_flights_incomplete("sess-123")

    assert len(result) == 1
    assert result[0]["id"] == "itin-incomplete-001"
    assert route.called
    request = route.calls[0].request
    assert "sessionId=sess-123" in str(request.url)


@respx.mock
async def test_search_flights_incomplete_error(skyscanner):
    respx.get(f"{BASE_URL}/v2/flights/search-incomplete").mock(
        return_value=httpx.Response(500, json={"error": "fail"})
    )

    result = await skyscanner.search_flights_incomplete("bad-session")

    assert result == []


@respx.mock
async def test_search_everywhere(skyscanner):
    respx.get(f"{BASE_URL}/1.0/flights/search-roundtrip").mock(
        return_value=httpx.Response(200, json=SEARCH_EVERYWHERE_RESPONSE)
    )

    result = await skyscanner.search_everywhere("TPE")

    assert len(result) == 2
    assert result[0]["destinationId"] == "NRT"


@respx.mock
async def test_price_calendar(skyscanner):
    respx.get(f"{BASE_URL}/flights/price-calendar").mock(
        return_value=httpx.Response(200, json=PRICE_CALENDAR_RESPONSE)
    )

    result = await skyscanner.price_calendar("TPE", "NRT", "2026-04-01")

    assert len(result) == 2
    assert result[0]["day"] == "2026-04-01"
    assert result[0]["price"] == 7121


@respx.mock
async def test_search_hotels(skyscanner):
    respx.get(f"{BASE_URL}/hotels/search").mock(
        return_value=httpx.Response(200, json=HOTELS_RESPONSE)
    )

    result = await skyscanner.search_hotels("128668889", "2026-04-01", "2026-04-03")

    assert len(result) == 1
    assert result[0]["hotelId"] == "h001"


@respx.mock
async def test_api_error_handling(skyscanner):
    respx.get(f"{BASE_URL}/v2/flights/search-one-way").mock(
        return_value=httpx.Response(500, json={"error": "Internal Server Error"})
    )

    result = await skyscanner.search_flights("TPE", "NRT", "2026-04-01")

    assert result == []


@respx.mock
async def test_api_returns_status_false(skyscanner):
    respx.get(f"{BASE_URL}/flights/autocomplete").mock(
        return_value=httpx.Response(200, json={"status": False, "message": "rate limited"})
    )

    result = await skyscanner.autocomplete("taipei")

    assert result == []


def test_missing_api_key():
    with patch("app.clients.rapidapi_base.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = ""
        mock_settings.RAPIDAPI_SKYSCANNER_HOST = SKYSCANNER_HOST
        client = SkyscannerClient()
        assert client._headers["x-rapidapi-key"] == ""

from unittest.mock import patch

import httpx
import pytest
import respx

from app.clients.kiwi_client import KiwiClient

KIWI_HOST = "flights-scraper-real-time.p.rapidapi.com"
BASE_URL = f"https://{KIWI_HOST}"


@pytest.fixture
def kiwi():
    from app.clients.rapidapi_base import RapidAPIBaseClient

    RapidAPIBaseClient._blocked_until.pop(KIWI_HOST, None)
    with patch("app.clients.kiwi_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_KIWI_HOST = KIWI_HOST
        client = KiwiClient()
    yield client
    RapidAPIBaseClient._blocked_until.pop(KIWI_HOST, None)


# --- Mock response fixtures ---

AUTOCOMPLETE_RESPONSE = {
    "data": {
        "metadata": {
            "firstResultStations": {
                "edges": [
                    {
                        "node": {
                            "id": "Station:airport:TPE",
                            "legacyId": "TPE",
                            "name": "Taiwan Taoyuan International",
                            "type": "AIRPORT",
                            "code": "TPE",
                            "gps": {"lat": 25.0777778, "lng": 121.232778},
                            "city": {
                                "legacyId": "taipei_tw",
                                "name": "Taipei",
                                "country": {"legacyId": "TW", "name": "Taiwan"},
                            },
                        }
                    }
                ]
            }
        }
    }
}

SEARCH_ONEWAY_RESPONSE = {
    "status": True,
    "data": {
        "itineraries": [
            {
                "id": "kiwi-itin-001",
                "price": {"amount": "6790", "priceBeforeDiscount": "6790"},
                "duration": 21000,
                "sector": {
                    "id": "sector-001",
                    "duration": 21000,
                    "sectorSegments": [
                        {
                            "segment": {
                                "source": {
                                    "station": {
                                        "code": "TPE",
                                        "name": "臺灣桃園國際機場",
                                        "type": "AIRPORT",
                                        "city": {"name": "台北"},
                                        "country": {"code": "TW"},
                                    },
                                    "localTime": "2026-04-01T02:50:00",
                                    "utcTimeIso": "2026-03-31T18:50:00Z",
                                },
                                "destination": {
                                    "station": {
                                        "code": "NRT",
                                        "name": "成田國際機場",
                                        "type": "AIRPORT",
                                        "city": {"name": "東京"},
                                        "country": {"code": "JP"},
                                    },
                                    "localTime": "2026-04-01T10:15:00",
                                    "utcTimeIso": "2026-04-01T01:15:00Z",
                                },
                                "duration": 8400,
                                "type": "FLIGHT",
                                "code": "6154",
                                "carrier": {"name": "Jeju Air", "code": "7C"},
                                "operatingCarrier": {"name": "Jeju Air", "code": "7C"},
                                "cabinClass": "ECONOMY",
                            },
                            "layover": None,
                        }
                    ],
                },
                "provider": "kiwi",
                "bagsInfo": {"includedHandBag": True},
                "pnrCount": 1,
                "bookingOptions": [
                    {
                        "edges": [
                            {
                                "node": {
                                    "bookingUrl": "https://booking.kiwi.com/flight1",
                                    "price": {"amount": "6790"},
                                }
                            }
                        ]
                    }
                ],
            }
        ],
        "metadata": {},
    },
}

SEARCH_RETURN_RESPONSE = {
    "status": True,
    "data": {
        "itineraries": [
            {
                "id": "kiwi-rt-001",
                "price": {"amount": "12800", "priceBeforeDiscount": "12800"},
                "duration": 25200,
                "sector": {
                    "id": "sector-rt-001",
                    "duration": 25200,
                    "sectorSegments": [
                        {
                            "segment": {
                                "source": {
                                    "station": {"code": "TPE", "name": "TPE", "type": "AIRPORT"},
                                    "localTime": "2026-04-01T08:00:00",
                                },
                                "destination": {
                                    "station": {"code": "NRT", "name": "NRT", "type": "AIRPORT"},
                                    "localTime": "2026-04-01T12:00:00",
                                },
                                "duration": 14400,
                                "type": "FLIGHT",
                                "code": "100",
                                "carrier": {"name": "China Airlines", "code": "CI"},
                                "operatingCarrier": {"name": "China Airlines", "code": "CI"},
                                "cabinClass": "ECONOMY",
                            },
                            "layover": None,
                        }
                    ],
                },
                "pnrCount": 1,
                "bookingOptions": [],
            }
        ],
    },
}

DEALS_RESPONSE = {
    "status": True,
    "data": {
        "deals": [
            {"destination": "NRT", "price": 4999, "airline": "7C"},
            {"destination": "KIX", "price": 5500, "airline": "MM"},
        ]
    },
}

PRICE_TRENDS_RESPONSE = {
    "status": True,
    "data": {
        "trends": [
            {"date": "2026-04-01", "price": 6790},
            {"date": "2026-04-02", "price": 7100},
        ]
    },
}

HOTELS_RESPONSE = {
    "status": True,
    "data": {
        "hotels": [
            {"hotelId": "kiwi-h001", "name": "Tokyo Stay", "price": 4200},
        ]
    },
}


# --- Tests ---


@respx.mock
async def test_autocomplete(kiwi):
    respx.get(f"{BASE_URL}/flights/auto-complete").mock(
        return_value=httpx.Response(200, json=AUTOCOMPLETE_RESPONSE)
    )

    result = await kiwi.autocomplete("taipei")

    assert len(result) == 1
    assert result[0]["code"] == "TPE"
    assert result[0]["name"] == "Taiwan Taoyuan International"
    assert result[0]["city"]["name"] == "Taipei"


@respx.mock
async def test_search_flights_oneway(kiwi):
    route = respx.get(f"{BASE_URL}/flights/search-oneway").mock(
        return_value=httpx.Response(200, json=SEARCH_ONEWAY_RESPONSE)
    )

    result = await kiwi.search_flights("TPE", "NRT", "2026-04-01")

    assert len(result) == 1
    assert result[0]["id"] == "kiwi-itin-001"
    assert result[0]["price"]["amount"] == "6790"
    assert route.called
    # Verify stops=0 is sent by default (direct flights only)
    request = route.calls[0].request
    assert "stops=0" in str(request.url)


@respx.mock
async def test_search_flights_roundtrip(kiwi):
    route = respx.get(f"{BASE_URL}/flights/search-return").mock(
        return_value=httpx.Response(200, json=SEARCH_RETURN_RESPONSE)
    )

    result = await kiwi.search_flights("TPE", "NRT", "2026-04-01", return_date="2026-04-05")

    assert len(result) == 1
    assert result[0]["id"] == "kiwi-rt-001"
    assert route.called
    request = route.calls[0].request
    assert "returnDate=2026-04-05" in str(request.url)


@respx.mock
async def test_search_deals(kiwi):
    respx.get(f"{BASE_URL}/deals/search").mock(
        return_value=httpx.Response(200, json=DEALS_RESPONSE)
    )

    result = await kiwi.search_deals("tokyo")

    assert len(result) == 2
    assert result[0]["destination"] == "NRT"
    assert result[0]["price"] == 4999


@respx.mock
async def test_price_trends(kiwi):
    respx.get(f"{BASE_URL}/flights/price-trends").mock(
        return_value=httpx.Response(200, json=PRICE_TRENDS_RESPONSE)
    )

    result = await kiwi.price_trends("TPE", "NRT")

    assert "trends" in result
    assert len(result["trends"]) == 2
    assert result["trends"][0]["price"] == 6790


@respx.mock
async def test_search_hotels(kiwi):
    respx.get(f"{BASE_URL}/stays/search/by-dest").mock(
        return_value=httpx.Response(200, json=HOTELS_RESPONSE)
    )

    result = await kiwi.search_hotels("tokyo_jp", "CITY", "2026-04-01", "2026-04-03")

    assert len(result) == 1
    assert result[0]["name"] == "Tokyo Stay"


@respx.mock
async def test_api_error_handling(kiwi):
    respx.get(f"{BASE_URL}/flights/search-oneway").mock(
        return_value=httpx.Response(429, json={"error": "rate limited"})
    )

    result = await kiwi.search_flights("TPE", "NRT", "2026-04-01")

    assert result == []


@respx.mock
async def test_api_returns_status_false(kiwi):
    respx.get(f"{BASE_URL}/flights/search-oneway").mock(
        return_value=httpx.Response(200, json={"status": False, "message": "error"})
    )

    result = await kiwi.search_flights("TPE", "NRT", "2026-04-01")

    assert result == []


def test_missing_api_key():
    with (
        patch("app.clients.kiwi_client.settings") as mock_kiwi,
        patch("app.clients.rapidapi_base.settings") as mock_base,
    ):
        mock_kiwi.RAPIDAPI_KEY = ""
        mock_kiwi.RAPIDAPI_KIWI_HOST = KIWI_HOST
        mock_base.RAPIDAPI_KEY = ""
        client = KiwiClient()
        assert client._headers["x-rapidapi-key"] == ""

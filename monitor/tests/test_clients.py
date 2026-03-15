from unittest.mock import AsyncMock, patch

import httpx

from app.clients.rate_limiter import TokenBucketRateLimiter


async def test_rate_limiter_allows_within_capacity():
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=5)
    # Should allow 5 immediate requests
    for _ in range(5):
        await limiter.acquire()
    # Tokens should be approximately depleted (allow small refill from elapsed time)
    assert limiter.tokens < 0.1


async def test_rate_limiter_refills():
    limiter = TokenBucketRateLimiter(rate=1000.0, capacity=10)
    # Exhaust tokens
    for _ in range(10):
        await limiter.acquire()
    # With high rate, tokens refill quickly
    import asyncio
    await asyncio.sleep(0.02)
    # Should be able to acquire again
    await limiter.acquire()


# --- RapidAPI base client tests ---


def _mock_response(status_code: int, json_data: dict | None = None) -> httpx.Response:
    """Create an httpx.Response with a request set (needed for raise_for_status)."""
    resp = httpx.Response(
        status_code,
        json=json_data or {},
        request=httpx.Request("GET", "https://example.com/test"),
    )
    return resp


async def test_rapidapi_base_get_success():
    from app.clients.rapidapi_base import RapidAPIBaseClient

    client = RapidAPIBaseClient("https://example.com", "example.com")
    mock_response = _mock_response(200, {"status": True, "data": [1, 2]})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        result = await client._get("/test")
    assert result == {"status": True, "data": [1, 2]}
    await client.close()


async def test_rapidapi_base_get_429_backs_off():
    from app.clients.rapidapi_base import RapidAPIBaseClient

    client = RapidAPIBaseClient("https://example.com", "test-429.example.com")
    mock_429 = _mock_response(429)

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_429):
        result = await client._get("/test")
    assert result == {}
    assert client._is_blocked()
    # Subsequent calls should be skipped
    result2 = await client._get("/test2")
    assert result2 == {}
    # Clean up class-level state
    RapidAPIBaseClient._blocked_until.pop("test-429.example.com", None)
    await client.close()


async def test_rapidapi_base_get_http_error():
    from app.clients.rapidapi_base import RapidAPIBaseClient

    client = RapidAPIBaseClient("https://example.com", "example.com")
    mock_500 = _mock_response(500)

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_500):
        result = await client._get("/test")
    assert result == {}
    await client.close()


# --- Skyscanner client tests ---


async def test_skyscanner_search_flights():
    from app.clients.skyscanner_client import SkyscannerClient

    with patch("app.clients.skyscanner_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_SKYSCANNER_HOST = "fly-scraper.p.rapidapi.com"
        client = SkyscannerClient()

    mock_response = _mock_response(200, {
        "status": True,
        "data": {
            "itineraries": [
                {"price": {"raw": 5000}, "legs": [{"stopCount": 0}]}
            ]
        },
    })

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await client.search_flights("TPE", "NRT", "2026-04-01")
    assert len(results) == 1
    assert results[0]["price"]["raw"] == 5000
    await client.close()


async def test_skyscanner_search_flights_empty():
    from app.clients.skyscanner_client import SkyscannerClient

    with patch("app.clients.skyscanner_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_SKYSCANNER_HOST = "fly-scraper.p.rapidapi.com"
        client = SkyscannerClient()

    mock_response = _mock_response(200, {"status": False})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await client.search_flights("TPE", "NRT", "2026-04-01")
    assert results == []
    await client.close()


# --- Kiwi client tests ---


async def test_kiwi_search_flights():
    from app.clients.kiwi_client import KiwiClient

    with patch("app.clients.kiwi_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_KIWI_HOST = "flights-scraper-real-time.p.rapidapi.com"
        client = KiwiClient()

    mock_response = _mock_response(200, {
        "status": True,
        "data": {
            "itineraries": [
                {"price": {"raw": 3200}, "legs": [{"stopCount": 1}]}
            ]
        },
    })

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await client.search_flights("TPE", "BKK", "2026-04-01")
    assert len(results) == 1
    assert results[0]["price"]["raw"] == 3200
    await client.close()


# --- Normalizer tests ---


def test_extract_skyscanner_price():
    from app.clients.normalizer import extract_skyscanner_price

    itin = {
        "price": {"raw": 4500.0, "currency": "TWD"},
        "legs": [{
            "carriers": {"marketing": [{"alternateId": "CI"}]},
            "stopCount": 0,
            "departure": "2026-04-01T08:00:00",
        }],
    }
    result = extract_skyscanner_price(itin)
    assert result is not None
    assert result["price"] == 4500.0
    assert result["airline"] == "CI"
    assert result["stops"] == 0
    assert result["departure_date"] == "2026-04-01"


def test_extract_skyscanner_price_invalid():
    from app.clients.normalizer import extract_skyscanner_price

    assert extract_skyscanner_price({}) is None
    assert extract_skyscanner_price({"price": {"raw": 0}}) is None
    assert extract_skyscanner_price({"price": {"raw": -1}}) is None


def test_extract_kiwi_price():
    from app.clients.normalizer import extract_kiwi_price

    itin = {
        "price": {"raw": 3200.0, "currency": "TWD"},
        "legs": [{
            "carriers": {"marketing": [{"alternateId": "TG"}]},
            "stopCount": 1,
            "departure": "2026-04-01T10:30:00",
        }],
    }
    result = extract_kiwi_price(itin)
    assert result is not None
    assert result["price"] == 3200.0
    assert result["airline"] == "TG"
    assert result["stops"] == 1


def test_extract_kiwi_price_invalid():
    from app.clients.normalizer import extract_kiwi_price

    assert extract_kiwi_price({}) is None
    assert extract_kiwi_price({"price": {"raw": None}}) is None


# --- Google Flights client tests ---


async def test_google_flights_search_flights():
    from app.clients.google_flights_client import GoogleFlightsClient

    with patch("app.clients.google_flights_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST = "google-flights-data.p.rapidapi.com"
        client = GoogleFlightsClient()

    mock_response = _mock_response(200, {
        "status": True,
        "data": {
            "topFlights": [
                {
                    "airlineCode": "CI",
                    "airlineName": "China Airlines",
                    "departureAirport": "TPE",
                    "arrivalAirport": "NRT",
                    "price": 6790,
                    "stops": 0,
                    "segments": [],
                }
            ],
            "otherFlights": [],
        },
    })

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await client.search_flights("TPE", "NRT", "2026-04-01")
    assert len(results) == 1
    assert results[0]["price"] == 6790
    await client.close()


async def test_google_flights_get_price_graph():
    from app.clients.google_flights_client import GoogleFlightsClient

    with patch("app.clients.google_flights_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST = "google-flights-data.p.rapidapi.com"
        client = GoogleFlightsClient()

    mock_response = _mock_response(200, {
        "status": True,
        "data": [
            {"departureDate": "2026-04-01", "arrivalDate": None, "price": 10795},
            {"departureDate": "2026-04-02", "arrivalDate": None, "price": None},
            {"departureDate": "2026-04-03", "arrivalDate": None, "price": 6538},
        ],
    })

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await client.get_price_graph("TPE", "NRT", "2026-04-01,2026-04-03")
    # price=None filtered out
    assert len(results) == 2
    assert results[0]["price"] == 10795
    await client.close()


async def test_google_flights_get_price_graph_empty():
    from app.clients.google_flights_client import GoogleFlightsClient

    with patch("app.clients.google_flights_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST = "google-flights-data.p.rapidapi.com"
        client = GoogleFlightsClient()

    mock_response = _mock_response(200, {"status": False})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await client.get_price_graph("TPE", "NRT", "2026-04-01,2026-04-03")
    assert results == []
    await client.close()


async def test_google_flights_search_flights_empty():
    from app.clients.google_flights_client import GoogleFlightsClient

    with patch("app.clients.google_flights_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST = "google-flights-data.p.rapidapi.com"
        client = GoogleFlightsClient()

    mock_response = _mock_response(200, {"status": False})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await client.search_flights("TPE", "NRT", "2026-04-01")
    assert results == []
    await client.close()


# --- Google Flights normalizer tests ---


def test_extract_google_flights_price():
    from app.clients.normalizer import extract_google_flights_price

    itin = {
        "airlineCode": "CI",
        "airlineName": "China Airlines",
        "departureAirport": "TPE",
        "arrivalAirport": "NRT",
        "departureDate": "2026-04-01",
        "price": 6790,
        "stops": 0,
        "durationMinutes": 255,
    }
    result = extract_google_flights_price(itin)
    assert result is not None
    assert result["price"] == 6790.0
    assert result["airline"] == "CI"
    assert result["stops"] == 0
    assert result["departure_date"] == "2026-04-01"


def test_extract_google_flights_price_invalid():
    from app.clients.normalizer import extract_google_flights_price

    assert extract_google_flights_price({}) is None
    assert extract_google_flights_price({"price": 0}) is None
    assert extract_google_flights_price({"price": -1}) is None

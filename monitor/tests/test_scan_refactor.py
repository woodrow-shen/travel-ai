"""Tests for monitor scan refactoring: roundtrip clients, route extraction, concurrency, expired cleanup."""

import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tasks.price_scan import _get_active_routes, _scan_route, scan_prices


# ── Roundtrip client endpoint selection ──


async def test_skyscanner_roundtrip_uses_correct_endpoint():
    from app.clients.skyscanner_client import SkyscannerClient

    with patch("app.clients.skyscanner_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_SKYSCANNER_HOST = "fly-scraper.p.rapidapi.com"
        client = SkyscannerClient()

    calls = []

    async def mock_get(endpoint, params):
        calls.append({"endpoint": endpoint, "params": params})
        return {"status": True, "data": {"itineraries": []}}

    with patch.object(client, "_get", side_effect=mock_get):
        # Oneway
        await client.search_flights("TPE", "NRT", "2026-04-15")
        assert calls[-1]["endpoint"] == "/v2/flights/search-one-way"
        assert "returnDate" not in calls[-1]["params"]

        # Roundtrip
        await client.search_flights("TPE", "NRT", "2026-04-15", return_date="2026-04-22")
        assert calls[-1]["endpoint"] == "/v2/flights/search-roundtrip"
        assert calls[-1]["params"]["returnDate"] == "2026-04-22"

    await client.close()


async def test_kiwi_roundtrip_uses_correct_endpoint():
    from app.clients.kiwi_client import KiwiClient

    with patch("app.clients.kiwi_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_KIWI_HOST = "flights-scraper-real-time.p.rapidapi.com"
        client = KiwiClient()

    calls = []

    async def mock_get(endpoint, params):
        calls.append({"endpoint": endpoint, "params": params})
        return {"status": True, "data": {"itineraries": []}}

    with patch.object(client, "_get", side_effect=mock_get):
        await client.search_flights("TPE", "BKK", "2026-04-15")
        assert calls[-1]["endpoint"] == "/flights/search-oneway"

        await client.search_flights("TPE", "BKK", "2026-04-15", return_date="2026-04-22")
        assert calls[-1]["endpoint"] == "/flights/search-return"
        assert calls[-1]["params"]["returnDate"] == "2026-04-22"

    await client.close()


async def test_google_flights_roundtrip_uses_correct_endpoint():
    from app.clients.google_flights_client import GoogleFlightsClient

    with patch("app.clients.google_flights_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST = "google-flights-data.p.rapidapi.com"
        client = GoogleFlightsClient()

    calls = []

    async def mock_get(endpoint, params):
        calls.append({"endpoint": endpoint, "params": params})
        return {"status": True, "data": {"topFlights": [], "otherFlights": []}}

    with patch.object(client, "_get", side_effect=mock_get):
        await client.search_flights("TPE", "NRT", "2026-04-15")
        assert calls[-1]["endpoint"] == "/flights/search-oneway"

        await client.search_flights("TPE", "NRT", "2026-04-15", return_date="2026-04-22")
        assert calls[-1]["endpoint"] == "/flights/search-roundtrip"
        assert calls[-1]["params"]["returnDate"] == "2026-04-22"

    await client.close()


async def test_google_flights_price_graph_roundtrip():
    from app.clients.google_flights_client import GoogleFlightsClient

    with patch("app.clients.google_flights_client.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-key"
        mock_settings.RAPIDAPI_GOOGLE_FLIGHTS_HOST = "google-flights-data.p.rapidapi.com"
        client = GoogleFlightsClient()

    calls = []

    async def mock_get(endpoint, params):
        calls.append({"endpoint": endpoint, "params": params})
        return {"status": True, "data": []}

    with patch.object(client, "_get", side_effect=mock_get):
        await client.get_price_graph("TPE", "NRT", "2026-04-12,2026-04-18")
        assert calls[-1]["endpoint"] == "/price-graph/for-oneway"

        await client.get_price_graph(
            "TPE", "NRT", "2026-04-12,2026-04-18", return_date="2026-04-22"
        )
        assert calls[-1]["endpoint"] == "/price-graph/for-roundtrip"

    await client.close()


# ── Route extraction ──


def _make_subscription(config: dict, sub_type="bug_fare", is_active=True):
    sub = MagicMock()
    sub.config = config
    sub.is_active = is_active
    sub.type = MagicMock()
    sub.type.value = sub_type
    sub.subscription_email = MagicMock()
    return sub


async def test_get_active_routes_extracts_dates():
    today = date.today()
    dep = (today + timedelta(days=30)).isoformat()
    ret = (today + timedelta(days=37)).isoformat()

    subs = [
        _make_subscription({
            "origin": "TPE", "destination": "NRT",
            "departure_date": dep, "return_date": ret,
            "trip_type": "roundtrip", "date_flexibility": 3,
        }),
    ]

    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = subs
    db.execute = AsyncMock(return_value=result)

    routes = await _get_active_routes(db)
    assert len(routes) == 1
    assert routes[0]["departure_date"] == dep
    assert routes[0]["return_date"] == ret
    assert routes[0]["trip_type"] == "roundtrip"
    assert routes[0]["date_flexibility"] == 3


async def test_get_active_routes_skips_expired():
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    future = (date.today() + timedelta(days=30)).isoformat()

    subs = [
        _make_subscription({
            "origin": "TPE", "destination": "NRT",
            "departure_date": yesterday,
        }),
        _make_subscription({
            "origin": "TPE", "destination": "KIX",
            "departure_date": future,
        }),
    ]

    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = subs
    db.execute = AsyncMock(return_value=result)

    routes = await _get_active_routes(db)
    assert len(routes) == 1
    assert routes[0]["destination"] == "KIX"


async def test_get_active_routes_deduplicates():
    dep = (date.today() + timedelta(days=30)).isoformat()

    subs = [
        _make_subscription({
            "origin": "TPE", "destination": "NRT", "departure_date": dep,
        }),
        _make_subscription({
            "origin": "tpe", "destination": "nrt", "departure_date": dep,
        }),
    ]

    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = subs
    db.execute = AsyncMock(return_value=result)

    routes = await _get_active_routes(db)
    assert len(routes) == 1


# ── Concurrent scan ──


async def test_scan_route_returns_zero_when_no_results():
    """_scan_route returns 0 when all API sources return empty."""
    amadeus = AsyncMock()
    amadeus.search_flights = AsyncMock(return_value=[])

    route = {
        "origin": "TPE", "destination": "NRT",
        "departure_date": "2026-04-15", "return_date": "2026-04-22",
        "trip_type": "roundtrip", "date_flexibility": 3,
    }

    result = await _scan_route(
        route, "2026-04-15",
        amadeus, None, None, None,
    )
    assert result == 0


async def test_scan_prices_concurrent_execution():
    """scan_prices should process multiple routes concurrently."""
    dep = (date.today() + timedelta(days=30)).isoformat()
    mock_routes = [
        {"origin": "TPE", "destination": "NRT", "departure_date": dep,
         "trip_type": "oneway", "date_flexibility": 3},
        {"origin": "TPE", "destination": "KIX", "departure_date": dep,
         "trip_type": "oneway", "date_flexibility": 3},
        {"origin": "TPE", "destination": "ICN", "departure_date": dep,
         "trip_type": "oneway", "date_flexibility": 3},
    ]

    scan_count = 0

    async def mock_scan_route(route, *args, **kwargs):
        nonlocal scan_count
        scan_count += 1
        await asyncio.sleep(0.01)  # Simulate API call
        return 0

    # Create async-compatible mock clients
    mock_amadeus = AsyncMock()
    mock_amadeus.close = AsyncMock()

    # Mock async_session context manager
    mock_db = AsyncMock()
    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_db)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("app.tasks.price_scan._get_active_routes", new_callable=AsyncMock, return_value=mock_routes),
        patch("app.tasks.price_scan._scan_route", side_effect=mock_scan_route),
        patch("app.tasks.price_scan.AmadeusClient", return_value=mock_amadeus),
        patch("app.tasks.price_scan.async_session", return_value=mock_session_ctx),
        patch("app.tasks.price_scan.settings") as mock_settings,
    ):
        mock_settings.RAPIDAPI_KEY = ""
        mock_settings.MAX_ROUTES_PER_SCAN = 500
        mock_settings.SCAN_CONCURRENCY = 10

        await scan_prices()

    assert scan_count == 3


# ── Expired subscription cleanup ──


async def test_cleanup_deactivates_expired():
    from app.tasks.cleanup import _deactivate_expired_subscriptions

    yesterday = (date.today() - timedelta(days=1)).isoformat()

    sub = MagicMock()
    sub.id = "sub-1"
    sub.config = {"departure_date": yesterday}

    db = AsyncMock()
    select_result = MagicMock()
    select_result.scalars.return_value.all.return_value = [sub]
    update_result = MagicMock()
    db.execute = AsyncMock(side_effect=[select_result, update_result])

    count = await _deactivate_expired_subscriptions(db)
    assert count == 1
    # Verify update was called
    assert db.execute.call_count == 2

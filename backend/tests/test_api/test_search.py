from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.config import settings

requires_amadeus = pytest.mark.skipif(
    not settings.AMADEUS_API_KEY, reason="AMADEUS_API_KEY not set"
)


async def test_search_flights(client: AsyncClient, auth_headers):
    resp = await client.post(
        "/api/v1/search/flights",
        json={
            "origin": "TPE",
            "destination": "NRT",
            "date_from": "2026-04-01",
            "passengers": 1,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "flights" in data
    assert "total_results" in data
    assert "search_id" in data
    assert data["type"] == "flight"


async def test_search_hotels(client: AsyncClient, auth_headers):
    resp = await client.post(
        "/api/v1/search/hotels",
        json={
            "location": "Tokyo",
            "check_in": "2026-04-01",
            "check_out": "2026-04-05",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "hotel"
    assert "hotels" in data


async def test_search_direct_requires_premium(client: AsyncClient, auth_headers):
    resp = await client.post(
        "/api/v1/search/direct",
        json={
            "origin": "TPE",
            "destination": "NRT",
            "date_from": "2026-04-01",
            "date_to": "2026-04-10",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 403


MOCK_AMADEUS_OFFERS = [
    {
        "type": "flight-offer",
        "source": "GDS",
        "price": {"grandTotal": "150.00", "currency": "EUR"},
        "itineraries": [
            {
                "duration": "PT3H25M",
                "segments": [
                    {
                        "departure": {"iataCode": "TPE", "at": "2026-04-01T08:00:00"},
                        "arrival": {"iataCode": "NRT", "at": "2026-04-01T12:25:00"},
                        "carrierCode": "BR",
                        "number": "198",
                        "duration": "PT3H25M",
                        "numberOfStops": 0,
                    }
                ],
            }
        ],
    }
]


@patch(
    "app.services.search_service.AmadeusClient.search_flights",
    new_callable=AsyncMock,
    return_value=MOCK_AMADEUS_OFFERS,
)
async def test_search_direct_premium_ok(
    mock_amadeus, client: AsyncClient, premium_auth_headers
):
    resp = await client.post(
        "/api/v1/search/direct",
        json={
            "origin": "TPE",
            "destination": "NRT",
            "date_from": "2026-04-01",
            "date_to": "2026-04-10",
        },
        headers=premium_auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert "total_direct_flights" in data


@patch(
    "app.services.search_service.AmadeusClient.search_inspiration",
    new_callable=AsyncMock,
    return_value=[],
)
async def test_search_adventure(mock_amadeus, client: AsyncClient, auth_headers):
    resp = await client.post(
        "/api/v1/search/adventure",
        json={
            "origin": "TPE",
            "date_from": "2026-04-01",
            "date_to": "2026-04-10",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "adventures" in data
    assert data["origin"] == "TPE"


async def test_search_unauthenticated(client: AsyncClient):
    resp = await client.post(
        "/api/v1/search/flights",
        json={
            "origin": "TPE",
            "destination": "NRT",
            "date_from": "2026-04-01",
        },
    )
    assert resp.status_code == 401


@requires_amadeus
async def test_search_direct_premium_real_api(client: AsyncClient, premium_auth_headers):
    """Integration test: hits real Amadeus API. Skipped in CI."""
    resp = await client.post(
        "/api/v1/search/direct",
        json={
            "origin": "TPE",
            "destination": "NRT",
            "date_from": "2026-04-01",
            "date_to": "2026-04-10",
        },
        headers=premium_auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert "total_direct_flights" in data


@requires_amadeus
async def test_search_adventure_real_api(client: AsyncClient, auth_headers):
    """Integration test: hits real Amadeus API. Skipped in CI."""
    resp = await client.post(
        "/api/v1/search/adventure",
        json={
            "origin": "TPE",
            "date_from": "2026-04-01",
            "date_to": "2026-04-10",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "adventures" in data
    assert data["origin"] == "TPE"

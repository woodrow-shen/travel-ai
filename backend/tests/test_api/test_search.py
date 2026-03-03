from httpx import AsyncClient


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
    assert "results" in data


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


async def test_search_direct_premium_ok(client: AsyncClient, premium_auth_headers):
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


async def test_search_adventure(client: AsyncClient, auth_headers):
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

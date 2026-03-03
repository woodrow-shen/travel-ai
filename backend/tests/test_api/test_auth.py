from httpx import AsyncClient

from app.dependencies import create_refresh_token


async def test_get_me(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["tier"] == "basic"


async def test_get_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401  # no bearer token


async def test_get_me_invalid_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401


async def test_refresh_token(client: AsyncClient, test_user):
    refresh = create_refresh_token(test_user.id)
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_refresh_token_invalid(client: AsyncClient):
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid"})
    assert resp.status_code == 401


async def test_update_tier(client: AsyncClient, auth_headers):
    resp = await client.patch(
        "/api/v1/auth/me/tier", json={"tier": "premium"}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "premium"
    assert "updated_at" in data


async def test_update_tier_forbidden_in_production(client: AsyncClient, auth_headers):
    from app.config import settings

    original = settings.ALLOW_TIER_SWITCH
    settings.ALLOW_TIER_SWITCH = False
    try:
        resp = await client.patch(
            "/api/v1/auth/me/tier", json={"tier": "premium"}, headers=auth_headers
        )
        assert resp.status_code == 403
    finally:
        settings.ALLOW_TIER_SWITCH = original


async def test_logout(client: AsyncClient, auth_headers):
    resp = await client.post("/api/v1/auth/logout", headers=auth_headers)
    assert resp.status_code == 200

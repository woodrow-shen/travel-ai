
from httpx import AsyncClient


async def test_add_email_auto_verify(client: AsyncClient, auth_headers):
    """Email matching user's login email should auto-verify."""
    resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "test@example.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["is_verified"] is True


async def test_add_email_needs_verification(client: AsyncClient, auth_headers):
    """Different email should not auto-verify."""
    resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "other@example.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "other@example.com"
    assert data["is_verified"] is False


async def test_add_email_max_three(client: AsyncClient, auth_headers):
    """Users can have at most 3 emails."""
    for i in range(3):
        resp = await client.post(
            "/api/v1/subscriptions/emails",
            json={"email": f"email{i}@example.com"},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "email3@example.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


async def test_create_subscription(client: AsyncClient, auth_headers):
    # First add a verified email
    email_resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "test@example.com"},
        headers=auth_headers,
    )
    email_id = email_resp.json()["id"]

    resp = await client.post(
        "/api/v1/subscriptions",
        json={
            "email_id": email_id,
            "type": "bug_fare",
            "config": {"origins": ["TPE"]},
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "bug_fare"
    assert data["is_active"] is True


async def test_create_subscription_unverified_email(client: AsyncClient, auth_headers):
    email_resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "unverified@example.com"},
        headers=auth_headers,
    )
    email_id = email_resp.json()["id"]

    resp = await client.post(
        "/api/v1/subscriptions",
        json={"email_id": email_id, "type": "bug_fare"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


async def test_list_subscriptions(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/subscriptions", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_update_subscription(client: AsyncClient, auth_headers):
    # Create email + subscription
    email_resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "test@example.com"},
        headers=auth_headers,
    )
    email_id = email_resp.json()["id"]

    create_resp = await client.post(
        "/api/v1/subscriptions",
        json={"email_id": email_id, "type": "price_drop", "config": {}},
        headers=auth_headers,
    )
    sub_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/subscriptions/{sub_id}",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_delete_subscription(client: AsyncClient, auth_headers):
    email_resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "test@example.com"},
        headers=auth_headers,
    )
    email_id = email_resp.json()["id"]

    create_resp = await client.post(
        "/api/v1/subscriptions",
        json={"email_id": email_id, "type": "deal_digest", "config": {}},
        headers=auth_headers,
    )
    sub_id = create_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/subscriptions/{sub_id}", headers=auth_headers
    )
    assert resp.status_code == 204

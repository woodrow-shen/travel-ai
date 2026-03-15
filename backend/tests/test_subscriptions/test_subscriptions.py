from unittest.mock import patch

from email_validator import ValidatedEmail
from httpx import AsyncClient


def _mock_validate_email(email, **kwargs):
    """Skip DNS check in tests — return a valid ValidatedEmail."""
    result = ValidatedEmail()
    result.normalized = email
    result.local_part = email.split("@")[0]
    result.domain = email.split("@")[1]
    return result


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_add_email_auto_verify(mock_val, client: AsyncClient, auth_headers):
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


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_add_email_needs_verification(mock_val, client: AsyncClient, auth_headers):
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


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_add_email_max_three(mock_val, client: AsyncClient, auth_headers):
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


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_create_subscription(mock_val, client: AsyncClient, auth_headers):
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


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_create_subscription_unverified_email(
    mock_val, client: AsyncClient, auth_headers
):
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


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_update_subscription(mock_val, client: AsyncClient, auth_headers):
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


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_delete_subscription(mock_val, client: AsyncClient, auth_headers):
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


async def test_add_email_rejects_undeliverable_domain(client: AsyncClient, auth_headers):
    """Emails with invalid/undeliverable domains should be rejected."""
    resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "user@thisdomain-does-not-exist-xyz123.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "Invalid email" in resp.json()["detail"]


async def test_add_email_rejects_invalid_format(client: AsyncClient, auth_headers):
    """Emails with bad format should be rejected by Pydantic."""
    resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "not-an-email"},
        headers=auth_headers,
    )
    assert resp.status_code == 422

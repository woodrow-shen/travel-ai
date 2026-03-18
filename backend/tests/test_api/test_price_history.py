import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from email_validator import ValidatedEmail
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_history import PriceHistory


def _mock_validate_email(email, **kwargs):
    result = ValidatedEmail()
    result.normalized = email
    result.local_part = email.split("@")[0]
    result.domain = email.split("@")[1]
    return result


async def _create_subscription_for_route(
    client: AsyncClient, auth_headers: dict, origin: str, destination: str
):
    """Helper: create a verified email + subscription with origin/destination config."""
    with patch(
        "app.api.v1.subscriptions.validate_email",
        side_effect=_mock_validate_email,
    ):
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
                "type": "price_drop",
                "config": {"origin": origin, "destination": destination},
            },
            headers=auth_headers,
        )
        return resp.json()


async def _seed_price_history(db_session: AsyncSession, origin: str, destination: str, count: int):
    """Seed price_history rows."""
    now = datetime.now(UTC)
    for i in range(count):
        ph = PriceHistory(
            id=uuid.uuid4(),
            origin=origin,
            destination=destination,
            departure_date=(now + timedelta(days=30)).date(),
            price_amount=10000.0 + i * 100,
            price_currency="TWD",
            source="amadeus",
            created_at=now - timedelta(days=count - i),
        )
        db_session.add(ph)
    await db_session.commit()


async def test_price_history_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/price-history", params={"origin": "TPE", "destination": "NRT"})
    assert resp.status_code == 401


async def test_price_history_empty_without_subscription(client: AsyncClient, auth_headers):
    resp = await client.get(
        "/api/v1/price-history",
        params={"origin": "TPE", "destination": "NRT", "days": "30"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["origin"] == "TPE"
    assert data["destination"] == "NRT"
    assert data["days"] == 30
    assert data["points"] == []


async def test_price_history_returns_data_for_subscribed_route(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    await _create_subscription_for_route(client, auth_headers, "TPE", "NRT")
    await _seed_price_history(db_session, "TPE", "NRT", 5)

    resp = await client.get(
        "/api/v1/price-history",
        params={"origin": "TPE", "destination": "NRT", "days": "30"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["points"]) == 5
    assert data["points"][0]["source"] == "amadeus"
    assert data["points"][0]["price_currency"] == "TWD"


async def test_price_history_case_insensitive(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    await _create_subscription_for_route(client, auth_headers, "TPE", "NRT")
    await _seed_price_history(db_session, "TPE", "NRT", 2)

    resp = await client.get(
        "/api/v1/price-history",
        params={"origin": "tpe", "destination": "nrt", "days": "30"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["points"]) == 2


async def test_price_history_respects_days_filter(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    await _create_subscription_for_route(client, auth_headers, "TPE", "NRT")
    # Seed 10 points spanning 10 days
    await _seed_price_history(db_session, "TPE", "NRT", 10)

    resp = await client.get(
        "/api/v1/price-history",
        params={"origin": "TPE", "destination": "NRT", "days": "7"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    points = resp.json()["points"]
    assert len(points) <= 7


async def test_price_history_validates_params(client: AsyncClient, auth_headers):
    # origin too short
    resp = await client.get(
        "/api/v1/price-history",
        params={"origin": "TP", "destination": "NRT"},
        headers=auth_headers,
    )
    assert resp.status_code == 422

    # days out of range
    resp = await client.get(
        "/api/v1/price-history",
        params={"origin": "TPE", "destination": "NRT", "days": "200"},
        headers=auth_headers,
    )
    assert resp.status_code == 422

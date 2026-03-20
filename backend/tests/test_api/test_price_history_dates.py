"""Tests for price_history API departure_date/return_date query params."""

import uuid
from datetime import UTC, date, datetime, timedelta
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


async def _create_subscription(client: AsyncClient, auth_headers: dict):
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
        await client.post(
            "/api/v1/subscriptions",
            json={
                "email_id": email_id,
                "type": "price_drop",
                "config": {"origin": "TPE", "destination": "NRT"},
            },
            headers=auth_headers,
        )


async def _seed_prices(
    db: AsyncSession,
    origin: str,
    dest: str,
    dep_date: date,
    ret_date: date | None,
    count: int,
):
    now = datetime.now(UTC)
    for i in range(count):
        db.add(PriceHistory(
            id=uuid.uuid4(),
            origin=origin,
            destination=dest,
            departure_date=dep_date,
            return_date=ret_date,
            price_amount=10000.0 + i * 100,
            price_currency="TWD",
            source="amadeus",
            created_at=now - timedelta(days=count - i),
        ))
    await db.commit()


async def test_filter_by_departure_date(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    await _create_subscription(client, auth_headers)

    dep1 = date(2026, 4, 15)
    dep2 = date(2026, 5, 1)
    await _seed_prices(db_session, "TPE", "NRT", dep1, None, 3)
    await _seed_prices(db_session, "TPE", "NRT", dep2, None, 2)

    # Filter by dep1 only
    resp = await client.get(
        "/api/v1/price-history",
        params={
            "origin": "TPE", "destination": "NRT",
            "days": "30", "departure_date": dep1.isoformat(),
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["points"]) == 3
    assert data["departure_date"] == dep1.isoformat()
    assert all(p["departure_date"] == dep1.isoformat() for p in data["points"])


async def test_filter_by_return_date(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    await _create_subscription(client, auth_headers)

    dep = date(2026, 4, 15)
    ret1 = date(2026, 4, 22)
    ret2 = date(2026, 4, 25)
    await _seed_prices(db_session, "TPE", "NRT", dep, ret1, 4)
    await _seed_prices(db_session, "TPE", "NRT", dep, ret2, 2)

    resp = await client.get(
        "/api/v1/price-history",
        params={
            "origin": "TPE", "destination": "NRT",
            "days": "30",
            "departure_date": dep.isoformat(),
            "return_date": ret1.isoformat(),
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["points"]) == 4
    assert data["return_date"] == ret1.isoformat()


async def test_no_date_filter_returns_all(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    await _create_subscription(client, auth_headers)

    dep1 = date(2026, 4, 15)
    dep2 = date(2026, 5, 1)
    await _seed_prices(db_session, "TPE", "NRT", dep1, None, 3)
    await _seed_prices(db_session, "TPE", "NRT", dep2, None, 2)

    resp = await client.get(
        "/api/v1/price-history",
        params={"origin": "TPE", "destination": "NRT", "days": "30"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["points"]) == 5


async def test_date_filter_returns_empty_for_nonexistent_date(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    await _create_subscription(client, auth_headers)
    await _seed_prices(db_session, "TPE", "NRT", date(2026, 4, 15), None, 3)

    resp = await client.get(
        "/api/v1/price-history",
        params={
            "origin": "TPE", "destination": "NRT",
            "days": "30", "departure_date": "2026-12-25",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["points"]) == 0

import uuid
from datetime import UTC, datetime
from unittest.mock import patch

from email_validator import ValidatedEmail
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_log import NotificationLog, NotificationStatus


def _mock_validate_email(email, **kwargs):
    result = ValidatedEmail()
    result.normalized = email
    result.local_part = email.split("@")[0]
    result.domain = email.split("@")[1]
    return result


async def test_notifications_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/subscriptions/notifications")
    assert resp.status_code == 401


async def test_notifications_empty_without_subscriptions(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/subscriptions/notifications", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_notifications_returns_user_logs(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
    # Create subscription
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

        sub_resp = await client.post(
            "/api/v1/subscriptions",
            json={"email_id": email_id, "type": "bug_fare", "config": {}},
            headers=auth_headers,
        )
        sub_id = sub_resp.json()["id"]

    # Seed notification logs
    for i in range(3):
        log = NotificationLog(
            id=uuid.uuid4(),
            subscription_id=uuid.UUID(sub_id),
            email="test@example.com",
            subject=f"Bug Fare Alert #{i + 1}",
            sent_at=datetime.now(UTC),
            status=NotificationStatus.SENT if i < 2 else NotificationStatus.FAILED,
        )
        db_session.add(log)
    await db_session.commit()

    resp = await client.get("/api/v1/subscriptions/notifications", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    # Ordered by sent_at desc
    assert data[0]["subject"] == "Bug Fare Alert #3"
    assert data[0]["status"] == "failed"
    assert data[1]["status"] == "sent"


async def test_notifications_respects_limit(
    client: AsyncClient, auth_headers, db_session: AsyncSession
):
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

        sub_resp = await client.post(
            "/api/v1/subscriptions",
            json={"email_id": email_id, "type": "price_drop", "config": {}},
            headers=auth_headers,
        )
        sub_id = sub_resp.json()["id"]

    for i in range(5):
        log = NotificationLog(
            id=uuid.uuid4(),
            subscription_id=uuid.UUID(sub_id),
            email="test@example.com",
            subject=f"Alert #{i + 1}",
            sent_at=datetime.now(UTC),
            status=NotificationStatus.SENT,
        )
        db_session.add(log)
    await db_session.commit()

    resp = await client.get(
        "/api/v1/subscriptions/notifications",
        params={"limit": "2"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2

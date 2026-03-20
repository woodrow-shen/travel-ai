"""Tests for subscription config validation (departure_date, return_date, trip_type, etc.)."""

import uuid
from datetime import date, timedelta
from unittest.mock import patch

import pytest
from email_validator import ValidatedEmail
from httpx import AsyncClient
from pydantic import ValidationError

from app.models.subscription import SubscriptionType
from app.schemas.subscription import SubscriptionConfig, SubscriptionCreate

# ── Unit tests for SubscriptionConfig ──


def test_config_valid_roundtrip():
    cfg = SubscriptionConfig(
        origin="TPE",
        destination="NRT",
        departure_date=date(2026, 4, 15),
        return_date=date(2026, 4, 22),
        trip_type="roundtrip",
        date_flexibility=3,
    )
    assert cfg.trip_type == "roundtrip"
    assert cfg.date_flexibility == 3


def test_config_valid_oneway():
    cfg = SubscriptionConfig(
        origin="TPE",
        destination="KIX",
        departure_date=date(2026, 5, 1),
        trip_type="oneway",
    )
    assert cfg.return_date is None


def test_config_return_date_before_departure_fails():
    with pytest.raises(ValidationError, match="return_date must be on or after"):
        SubscriptionConfig(
            departure_date=date(2026, 4, 22),
            return_date=date(2026, 4, 15),
        )


def test_config_return_date_without_departure_fails():
    with pytest.raises(ValidationError, match="return_date requires departure_date"):
        SubscriptionConfig(return_date=date(2026, 4, 22))


def test_config_roundtrip_without_return_date_fails():
    with pytest.raises(ValidationError, match="roundtrip requires return_date"):
        SubscriptionConfig(
            departure_date=date(2026, 4, 15),
            trip_type="roundtrip",
        )


def test_config_flexibility_out_of_range():
    with pytest.raises(ValidationError, match="date_flexibility must be between"):
        SubscriptionConfig(date_flexibility=10)

    with pytest.raises(ValidationError, match="date_flexibility must be between"):
        SubscriptionConfig(date_flexibility=-1)


def test_config_flexibility_valid_range():
    for n in [0, 1, 3, 5, 7]:
        cfg = SubscriptionConfig(date_flexibility=n)
        assert cfg.date_flexibility == n


def test_config_defaults():
    cfg = SubscriptionConfig()
    assert cfg.date_flexibility == 3
    assert cfg.trip_type is None
    assert cfg.departure_date is None


# ── Unit tests for SubscriptionCreate trip_type defaults ──


def test_create_bug_fare_defaults_roundtrip():
    dep = date.today() + timedelta(days=30)
    ret = dep + timedelta(days=7)
    sub = SubscriptionCreate(
        email_id=uuid.uuid4(),
        type=SubscriptionType.BUG_FARE,
        config={
            "origin": "TPE",
            "destination": "NRT",
            "departure_date": dep.isoformat(),
            "return_date": ret.isoformat(),
        },
    )
    assert sub.config["trip_type"] == "roundtrip"


def test_create_deal_digest_defaults_roundtrip():
    dep = date.today() + timedelta(days=30)
    ret = dep + timedelta(days=7)
    sub = SubscriptionCreate(
        email_id=uuid.uuid4(),
        type=SubscriptionType.DEAL_DIGEST,
        config={
            "departure_date": dep.isoformat(),
            "return_date": ret.isoformat(),
        },
    )
    assert sub.config["trip_type"] == "roundtrip"


def test_create_price_drop_defaults_oneway():
    sub = SubscriptionCreate(
        email_id=uuid.uuid4(),
        type=SubscriptionType.PRICE_DROP,
        config={
            "origin": "TPE",
            "destination": "NRT",
            "departure_date": (date.today() + timedelta(days=30)).isoformat(),
        },
    )
    assert sub.config["trip_type"] == "oneway"


def test_create_config_validation_rejects_invalid():
    with pytest.raises(ValidationError):
        SubscriptionCreate(
            email_id=uuid.uuid4(),
            type=SubscriptionType.BUG_FARE,
            config={
                "departure_date": "2026-04-22",
                "return_date": "2026-04-15",  # before departure
                "trip_type": "roundtrip",
            },
        )


# ── API integration tests ──


def _mock_validate_email(email, **kwargs):
    result = ValidatedEmail()
    result.normalized = email
    result.local_part = email.split("@")[0]
    result.domain = email.split("@")[1]
    return result


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_create_subscription_with_dates_via_api(
    mock_val, client: AsyncClient, auth_headers
):
    # Add email
    email_resp = await client.post(
        "/api/v1/subscriptions/emails",
        json={"email": "test@example.com"},
        headers=auth_headers,
    )
    email_id = email_resp.json()["id"]

    dep = (date.today() + timedelta(days=30)).isoformat()
    ret = (date.today() + timedelta(days=37)).isoformat()

    resp = await client.post(
        "/api/v1/subscriptions",
        json={
            "email_id": email_id,
            "type": "bug_fare",
            "config": {
                "origin": "TPE",
                "destination": "NRT",
                "departure_date": dep,
                "return_date": ret,
                "date_flexibility": 3,
            },
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["config"]["departure_date"] == dep
    assert data["config"]["return_date"] == ret
    assert data["config"]["trip_type"] == "roundtrip"
    assert data["config"]["date_flexibility"] == 3


@patch(
    "app.api.v1.subscriptions.validate_email",
    side_effect=_mock_validate_email,
)
async def test_create_subscription_rejects_invalid_dates_via_api(
    mock_val, client: AsyncClient, auth_headers
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
            "type": "bug_fare",
            "config": {
                "origin": "TPE",
                "destination": "NRT",
                "departure_date": "2026-04-22",
                "return_date": "2026-04-15",
            },
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422

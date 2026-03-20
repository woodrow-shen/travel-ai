import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.models.subscription import SubscriptionType


class SubscriptionConfig(BaseModel):
    origin: str | None = None
    destination: str | None = None
    departure_date: date | None = None
    return_date: date | None = None
    trip_type: Literal["oneway", "roundtrip"] | None = None
    date_flexibility: int = 3
    target_price: float | None = None
    airline_override: list[str] | None = None
    # Legacy bulk format for bug_fare
    origins: list[str] | None = None
    destinations: list[str] | None = None

    @field_validator("date_flexibility")
    @classmethod
    def validate_flexibility(cls, v: int) -> int:
        if v < 0 or v > 7:
            raise ValueError("date_flexibility must be between 0 and 7")
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "SubscriptionConfig":
        if self.return_date and not self.departure_date:
            raise ValueError("return_date requires departure_date")
        if self.return_date and self.departure_date and self.return_date < self.departure_date:
            raise ValueError("return_date must be on or after departure_date")
        if self.trip_type == "roundtrip" and self.departure_date and not self.return_date:
            raise ValueError("roundtrip requires return_date")
        return self


def _apply_trip_type_defaults(sub_type: SubscriptionType, config: dict) -> dict:
    """Apply default trip_type based on subscription type."""
    if "trip_type" not in config or config["trip_type"] is None:
        if sub_type in (SubscriptionType.BUG_FARE, SubscriptionType.DEAL_DIGEST):
            config["trip_type"] = "roundtrip"
        else:
            config["trip_type"] = "oneway"
    return config


class SubscriptionCreate(BaseModel):
    email_id: uuid.UUID
    type: SubscriptionType
    config: dict = {}

    @model_validator(mode="after")
    def validate_config(self) -> "SubscriptionCreate":
        self.config = _apply_trip_type_defaults(self.type, self.config)
        SubscriptionConfig(**self.config)
        return self


class SubscriptionUpdate(BaseModel):
    config: dict | None = None
    is_active: bool | None = None


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    email_id: uuid.UUID
    type: SubscriptionType
    config: dict
    is_active: bool
    last_sent_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionEmailCreate(BaseModel):
    email: EmailStr


class SubscriptionEmailResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_verified: bool
    verified_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

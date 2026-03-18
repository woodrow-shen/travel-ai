import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.user import UserTier


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    avatar_url: str | None = None
    tier: UserTier
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPreferenceUpdate(BaseModel):
    preferred_airlines: list[str] | None = None
    excluded_airlines: list[str] | None = None
    preferred_alliances: list[str] | None = None
    cabin_classes: list[str] | None = None
    max_stops: int | None = None
    home_airports: list[str] | None = None
    preferred_language: str | None = None


class UserPreferenceResponse(BaseModel):
    preferred_airlines: list[str] | None = None
    excluded_airlines: list[str] | None = None
    preferred_alliances: list[str] | None = None
    cabin_classes: list[str] | None = None
    max_stops: int | None = None
    home_airports: list[str] | None = None
    preferred_language: str | None = None

    model_config = {"from_attributes": True}


class TierUpdateRequest(BaseModel):
    tier: UserTier


class TierUpdateResponse(BaseModel):
    tier: UserTier
    updated_at: datetime

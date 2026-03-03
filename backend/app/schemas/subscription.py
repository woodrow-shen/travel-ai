import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.subscription import SubscriptionType


class SubscriptionCreate(BaseModel):
    email_id: uuid.UUID
    type: SubscriptionType
    config: dict = {}


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
    email: str


class SubscriptionEmailResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_verified: bool
    verified_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

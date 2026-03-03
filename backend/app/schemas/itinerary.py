import uuid
from datetime import datetime

from pydantic import BaseModel


class ItineraryCreate(BaseModel):
    trip_id: uuid.UUID
    title: str | None = None
    description: str | None = None
    prompt: str | None = None


class ItineraryResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    title: str
    description: str | None = None
    schedule: dict
    created_at: datetime

    model_config = {"from_attributes": True}

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class TripCreate(BaseModel):
    title: str
    description: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class TripUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class TripResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

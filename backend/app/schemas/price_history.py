import uuid
from datetime import date, datetime

from pydantic import BaseModel


class PriceHistoryPoint(BaseModel):
    id: uuid.UUID
    origin: str
    destination: str
    departure_date: date
    return_date: date | None = None
    price_amount: float
    price_currency: str
    source: str
    airline: str | None = None
    cabin_class: str | None = None
    stops: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryResponse(BaseModel):
    origin: str
    destination: str
    departure_date: date | None = None
    return_date: date | None = None
    days: int
    points: list[PriceHistoryPoint]

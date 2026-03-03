from datetime import date

from pydantic import BaseModel

from app.schemas.search import FlightResult, HotelResult

# --- Unified compare schemas ---


class UnifiedCompareRequest(BaseModel):
    item_ids: list[str]
    item_type: str  # "flight" | "hotel"


class PricePoint(BaseModel):
    provider: str
    price: float
    currency: str = "TWD"
    url: str | None = None
    fetched_at: str


class CompareResult(BaseModel):
    item_id: str
    item_type: str
    label: str
    prices: list[PricePoint]
    lowest_price: float
    highest_price: float
    average_price: float


# --- Legacy compare schemas (backward compatible) ---


class FlightCompareRequest(BaseModel):
    origin: str
    destination: str
    date_from: date
    date_to: date | None = None
    passengers: int = 1
    cabin_class: str | None = None


class HotelCompareRequest(BaseModel):
    location: str
    check_in: date
    check_out: date
    guests: int = 1


class FlightCompareResponse(BaseModel):
    results: list[FlightResult]
    sources: list[str]
    cheapest: FlightResult | None = None
    fastest: FlightResult | None = None


class HotelCompareResponse(BaseModel):
    results: list[HotelResult]
    sources: list[str]
    cheapest: HotelResult | None = None
    best_rated: HotelResult | None = None

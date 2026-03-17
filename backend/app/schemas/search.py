import hashlib
from datetime import date

from pydantic import AliasChoices, BaseModel, Field

# --- Request schemas ---


class FlightSearchRequest(BaseModel):
    model_config = {"populate_by_name": True}

    origin: str
    destination: str
    date_from: date = Field(validation_alias=AliasChoices("date_from", "departure_date"))
    date_to: date | None = Field(
        default=None, validation_alias=AliasChoices("date_to", "return_date")
    )
    passengers: int = Field(
        default=1, validation_alias=AliasChoices("passengers", "adults")
    )
    cabin_class: str | None = None
    max_stops: int | None = None
    currency: str | None = None


class HotelSearchRequest(BaseModel):
    model_config = {"populate_by_name": True}

    location: str = Field(validation_alias=AliasChoices("location", "destination"))
    check_in: date
    check_out: date
    guests: int = Field(default=1, validation_alias=AliasChoices("guests", "adults"))
    rooms: int = 1
    stars_min: int | None = None


class DirectSearchRequest(BaseModel):
    origin: str
    destination: str
    date_from: date
    date_to: date
    passengers: int = 1
    cabin_class: str | None = None


class AdventureSearchRequest(BaseModel):
    origin: str
    date_from: date
    date_to: date
    passengers: int = 1
    cabin_class: str | None = None


# --- Shared models ---


class PriceInfo(BaseModel):
    amount: float
    currency: str


class FlightSegment(BaseModel):
    airline: str
    airline_logo: str = ""
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str  # ISO 8601
    arrival_time: str
    duration_minutes: int
    cabin_class: str = ""


class FlightResult(BaseModel):
    id: str  # stable hash of flight_number+departure_time
    provider: str  # e.g. "amadeus", "skyscanner", "kiwi"
    price: float
    currency: str = "TWD"
    outbound_segments: list[FlightSegment]
    return_segments: list[FlightSegment] | None = None
    total_duration_minutes: int
    stops: int = 0
    booking_url: str = ""
    booking_token: str = ""
    expires_at: str | None = None


# --- Helpers ---


def _stable_flight_id(flight_number: str, departure_time: str) -> str:
    """Generate deterministic ID from flight_number + departure_time."""
    return hashlib.md5(f"{flight_number}_{departure_time}".encode()).hexdigest()[:12]


def normalized_dict_to_flight_result(d: dict, expires_at: str = "") -> FlightResult:
    """Convert normalizer output dict -> FlightResult Pydantic model."""
    segments_raw = d.get("segments", [])
    outbound_segments = [
        FlightSegment(
            airline=seg.get("airline", ""),
            airline_logo="",
            flight_number=seg.get("flight_number", ""),
            departure_airport=seg.get("origin", ""),
            arrival_airport=seg.get("destination", ""),
            departure_time=seg.get("departure_time", ""),
            arrival_time=seg.get("arrival_time", ""),
            duration_minutes=seg.get("duration_minutes", 0),
            cabin_class="",
        )
        for seg in segments_raw
    ]

    # Fallback: if no segments parsed, create one from top-level fields
    if not outbound_segments:
        outbound_segments = [
            FlightSegment(
                airline=d.get("airline", ""),
                flight_number=d.get("flight_number", ""),
                departure_airport=d.get("origin", ""),
                arrival_airport=d.get("destination", ""),
                departure_time=d.get("departure_time", ""),
                arrival_time=d.get("arrival_time", ""),
                duration_minutes=d.get("duration_minutes", 0),
            )
        ]

    # Return segments (roundtrip)
    return_segments_raw = d.get("return_segments", [])
    return_segments = (
        [
            FlightSegment(
                airline=seg.get("airline", ""),
                airline_logo="",
                flight_number=seg.get("flight_number", ""),
                departure_airport=seg.get("origin", ""),
                arrival_airport=seg.get("destination", ""),
                departure_time=seg.get("departure_time", ""),
                arrival_time=seg.get("arrival_time", ""),
                duration_minutes=seg.get("duration_minutes", 0),
                cabin_class="",
            )
            for seg in return_segments_raw
        ]
        if return_segments_raw
        else None
    )

    flight_number = d.get("flight_number", "")
    departure_time = d.get("departure_time", "")

    return FlightResult(
        id=_stable_flight_id(flight_number, departure_time),
        provider=d.get("source", ""),
        price=float(d.get("price", 0)),
        currency=d.get("currency", "TWD"),
        outbound_segments=outbound_segments,
        return_segments=return_segments,
        total_duration_minutes=d.get("duration_minutes", 0),
        stops=d.get("stops", 0),
        booking_url=d.get("booking_url", ""),
        booking_token=d.get("booking_token", ""),
        expires_at=expires_at or None,
    )


# --- Response schemas ---


class HotelResult(BaseModel):
    id: str  # stable hash of name+location
    provider: str = ""  # "skyscanner" | "kiwi"
    name: str
    address: str = ""
    latitude: float | None = None
    longitude: float | None = None
    star_rating: int = 0
    user_rating: float | None = None
    review_count: int | None = None
    price_per_night: float = 0
    total_price: float = 0
    currency: str = "TWD"
    amenities: list[str] = []
    images: list[str] = []
    booking_url: str = ""
    cancellation_policy: str | None = None
    expires_at: str | None = None


def _stable_hotel_id(name: str, location: str) -> str:
    """Generate deterministic ID from hotel name + location."""
    key = f"{name.lower().strip()}_{location.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def normalized_dict_to_hotel_result(
    d: dict, expires_at: str = ""
) -> HotelResult:
    """Convert normalizer output dict -> HotelResult Pydantic model."""
    name = d.get("name", "")
    address = d.get("address", "")
    return HotelResult(
        id=_stable_hotel_id(name, address),
        provider=d.get("source", ""),
        name=name,
        address=address,
        latitude=d.get("latitude"),
        longitude=d.get("longitude"),
        star_rating=d.get("star_rating", 0),
        user_rating=d.get("user_rating"),
        review_count=d.get("review_count"),
        price_per_night=float(d.get("price_per_night", 0)),
        total_price=float(d.get("total_price", 0)),
        currency=d.get("currency", "TWD"),
        amenities=d.get("amenities", []),
        images=d.get("images", []),
        booking_url=d.get("booking_url", ""),
        cancellation_policy=d.get("cancellation_policy"),
        expires_at=expires_at or None,
    )


class HotelSearchResponse(BaseModel):
    search_id: str = ""
    results: list[HotelResult]
    total: int


class SearchResponse(BaseModel):
    search_id: str
    type: str  # "flight" | "hotel"
    flights: list[FlightResult] | None = None
    hotels: list[HotelResult] | None = None
    total_results: int
    search_params: dict
    created_at: str


class ForeignerDiscount(BaseModel):
    amount: float
    currency: str
    name: str


class DomesticFlightPrice(BaseModel):
    regular: PriceInfo
    foreigner_discount: ForeignerDiscount | None = None


class MultiSegmentLeg(BaseModel):
    leg: int
    type: str  # international / domestic
    flight: FlightResult
    price: PriceInfo | DomesticFlightPrice | None = None


class MultiSegmentResult(BaseModel):
    type: str = "multi_segment"
    segments: list[MultiSegmentLeg]
    total_price: PriceInfo
    layover: dict | None = None
    tags: list[str] = []


class DirectFlightRecommendation(BaseModel):
    rank: int
    score: int
    flight: FlightResult
    reasons: list[str]
    price: PriceInfo


class DirectSearchResponse(BaseModel):
    recommendations: list[DirectFlightRecommendation]
    total_direct_flights: int


class AdventureDestination(BaseModel):
    rank: int
    destination: dict  # city, airport, country
    best_flight: FlightResult
    price: PriceInfo
    tags: list[str] = []


class AdventureSearchResponse(BaseModel):
    adventures: list[AdventureDestination]
    search_coverage: str
    origin: str


class BookingDetailsRequest(BaseModel):
    booking_token: str
    currency: str = "TWD"


class BookingOption(BaseModel):
    airline_code: str = ""
    flight_number: str = ""
    airline_name: str = ""
    price: float | None = None
    booking_link: str = ""


class BookingDetailsResponse(BaseModel):
    options: list[BookingOption]


class PriceGraphRequest(BaseModel):
    origin: str
    destination: str
    departure_range: str  # "2026-04-01,2026-04-30"
    return_date: str | None = None
    currency: str = "TWD"


class PriceGraphPoint(BaseModel):
    departure_date: str
    arrival_date: str | None = None
    price: float


class PriceGraphResponse(BaseModel):
    points: list[PriceGraphPoint]
    origin: str
    destination: str

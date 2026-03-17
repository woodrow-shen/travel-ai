from fastapi import APIRouter, Depends

from app.clients.google_flights_client import GoogleFlightsClient
from app.dependencies import get_current_user, require_premium
from app.models.user import User
from app.schemas.search import (
    AdventureSearchRequest,
    AdventureSearchResponse,
    BookingDetailsRequest,
    BookingDetailsResponse,
    BookingOption,
    DirectSearchRequest,
    DirectSearchResponse,
    FlightSearchRequest,
    HotelSearchRequest,
    PriceGraphPoint,
    PriceGraphRequest,
    PriceGraphResponse,
    SearchResponse,
)
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/flights", response_model=SearchResponse)
async def search_flights(
    body: FlightSearchRequest,
    user: User = Depends(get_current_user),
):
    service = SearchService()
    return await service.search_flights(body, user)


@router.post("/hotels", response_model=SearchResponse)
async def search_hotels(
    body: HotelSearchRequest,
    user: User = Depends(get_current_user),
):
    service = SearchService()
    return await service.search_hotels(body, user)


@router.post("/direct", response_model=DirectSearchResponse)
async def search_direct(
    body: DirectSearchRequest,
    user: User = Depends(require_premium),
):
    service = SearchService()
    return await service.search_direct(body, user)


@router.post("/adventure", response_model=AdventureSearchResponse)
async def search_adventure(
    body: AdventureSearchRequest,
    user: User = Depends(get_current_user),
):
    service = SearchService()
    return await service.search_adventure(body, user)


@router.post("/booking-details", response_model=BookingDetailsResponse)
async def get_booking_details(
    body: BookingDetailsRequest,
    user: User = Depends(get_current_user),
):
    """Resolve a Google Flights booking token into airline booking URLs."""
    client = GoogleFlightsClient()
    try:
        raw = await client.get_booking_details(body.booking_token, body.currency)
    finally:
        await client.close()

    options = [
        BookingOption(
            airline_code=opt.get("airlineCode", ""),
            flight_number=opt.get("flightNumber", ""),
            airline_name=opt.get("airlineName", ""),
            price=opt.get("price"),
            booking_link=opt.get("bookingLink", ""),
        )
        for opt in raw
    ]
    return BookingDetailsResponse(options=options)


@router.post("/price-graph", response_model=PriceGraphResponse)
async def get_price_graph(
    body: PriceGraphRequest,
    user: User = Depends(get_current_user),
):
    """Get daily lowest prices for a date range from Google Flights."""
    client = GoogleFlightsClient()
    try:
        raw = await client.get_price_graph(
            origin=body.origin,
            destination=body.destination,
            departure_range=body.departure_range,
            return_date=body.return_date,
            currency=body.currency,
        )
    finally:
        await client.close()

    points = [
        PriceGraphPoint(
            departure_date=p.get("departureDate", ""),
            arrival_date=p.get("arrivalDate"),
            price=p.get("price", 0),
        )
        for p in raw
    ]
    return PriceGraphResponse(
        points=points,
        origin=body.origin,
        destination=body.destination,
    )

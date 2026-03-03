from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, require_premium
from app.models.user import User
from app.schemas.search import (
    AdventureSearchRequest,
    AdventureSearchResponse,
    DirectSearchRequest,
    DirectSearchResponse,
    FlightSearchRequest,
    HotelSearchRequest,
    HotelSearchResponse,
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


@router.post("/hotels", response_model=HotelSearchResponse)
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

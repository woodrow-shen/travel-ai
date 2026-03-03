from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.compare import (
    CompareResult,
    FlightCompareRequest,
    FlightCompareResponse,
    HotelCompareRequest,
    HotelCompareResponse,
    UnifiedCompareRequest,
)
from app.services.price_service import PriceService

router = APIRouter()


@router.post("", response_model=list[CompareResult])
async def unified_compare(
    body: UnifiedCompareRequest,
    user: User = Depends(get_current_user),
):
    service = PriceService()
    return await service.unified_compare(body, user)


@router.post("/flights", response_model=FlightCompareResponse)
async def compare_flights(
    body: FlightCompareRequest,
    user: User = Depends(get_current_user),
):
    service = PriceService()
    return await service.compare_flights(body, user)


@router.post("/hotels", response_model=HotelCompareResponse)
async def compare_hotels(
    body: HotelCompareRequest,
    user: User = Depends(get_current_user),
):
    service = PriceService()
    return await service.compare_hotels(body, user)

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.itinerary import ItineraryCreate, ItineraryResponse
from app.services.itinerary_service import ItineraryService

router = APIRouter()


@router.post("", response_model=ItineraryResponse)
async def create_itinerary(
    body: ItineraryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    return await service.create_itinerary(body, user)

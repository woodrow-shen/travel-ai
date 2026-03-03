
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.itinerary_agent import ItineraryAgent
from app.models.itinerary import Itinerary
from app.models.trip import Trip
from app.models.user import User
from app.schemas.itinerary import ItineraryCreate, ItineraryResponse


class ItineraryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.agent = ItineraryAgent()

    async def create_itinerary(
        self, request: ItineraryCreate, user: User
    ) -> ItineraryResponse:
        # Verify trip belongs to user
        result = await self.db.execute(
            select(Trip).where(Trip.id == request.trip_id, Trip.user_id == user.id)
        )
        trip = result.scalar_one_or_none()
        if trip is None:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # Generate schedule using the itinerary agent tool
        schedule_params = {
            "destination": trip.destination or "Unknown",
            "start_date": str(trip.start_date) if trip.start_date else "",
            "end_date": str(trip.end_date) if trip.end_date else "",
        }

        if request.prompt:
            schedule_params["interests"] = [request.prompt]

        schedule = await self.agent.execute_tool("create_itinerary", schedule_params)

        itinerary = Itinerary(
            trip_id=trip.id,
            title=request.title or f"Itinerary for {trip.title}",
            description=request.description,
            schedule=schedule,
        )
        self.db.add(itinerary)
        await self.db.flush()
        await self.db.refresh(itinerary)

        return ItineraryResponse.model_validate(itinerary)

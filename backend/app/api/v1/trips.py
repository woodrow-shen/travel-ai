import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripResponse, TripUpdate

router = APIRouter()


@router.get("", response_model=list[TripResponse])
async def list_trips(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trip).where(Trip.user_id == user.id).order_by(Trip.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    body: TripCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = Trip(user_id=user.id, **body.model_dump())
    db.add(trip)
    await db.flush()
    await db.refresh(trip)
    return trip


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: uuid.UUID,
    body: TripUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trip, key, value)
    await db.flush()
    await db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    await db.delete(trip)

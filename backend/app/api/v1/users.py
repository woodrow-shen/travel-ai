from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserPreference
from app.schemas.user import UserPreferenceResponse, UserPreferenceUpdate

router = APIRouter()


@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user.id)
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        return UserPreferenceResponse()
    return pref


@router.patch("/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    body: UserPreferenceUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user.id)
    )
    pref = result.scalar_one_or_none()

    if pref is None:
        pref = UserPreference(user_id=user.id)
        db.add(pref)

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pref, key, value)

    await db.flush()
    await db.refresh(pref)
    return pref

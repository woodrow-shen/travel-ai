from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.price_history import PriceHistory
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.price_history import PriceHistoryResponse

router = APIRouter()


@router.get("", response_model=PriceHistoryResponse)
async def get_price_history(
    origin: str = Query(..., min_length=3, max_length=4),
    destination: str = Query(..., min_length=3, max_length=4),
    days: int = Query(30, ge=7, le=90),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify user has an active subscription for this route
    sub_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active.is_(True),
        )
    )
    subscriptions = sub_result.scalars().all()

    origin_upper = origin.upper()
    destination_upper = destination.upper()

    has_route = any(
        sub.config.get("origin", "").upper() == origin_upper
        and sub.config.get("destination", "").upper() == destination_upper
        for sub in subscriptions
    )

    if not has_route:
        return PriceHistoryResponse(
            origin=origin_upper,
            destination=destination_upper,
            days=days,
            points=[],
        )

    cutoff = datetime.now(UTC) - timedelta(days=days)
    result = await db.execute(
        select(PriceHistory)
        .where(
            PriceHistory.origin == origin_upper,
            PriceHistory.destination == destination_upper,
            PriceHistory.created_at >= cutoff,
        )
        .order_by(PriceHistory.created_at.asc())
    )

    return PriceHistoryResponse(
        origin=origin_upper,
        destination=destination_upper,
        days=days,
        points=list(result.scalars().all()),  # type: ignore[arg-type]
    )

import logging
import uuid
from datetime import UTC

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.subscription import Subscription, SubscriptionEmail
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionEmailCreate,
    SubscriptionEmailResponse,
    SubscriptionResponse,
    SubscriptionUpdate,
)
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    return result.scalars().all()


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    body: SubscriptionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify email belongs to user and is verified
    result = await db.execute(
        select(SubscriptionEmail).where(
            SubscriptionEmail.id == body.email_id,
            SubscriptionEmail.user_id == user.id,
        )
    )
    email = result.scalar_one_or_none()
    if email is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    if not email.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified"
        )

    subscription = Subscription(
        user_id=user.id,
        email_id=body.email_id,
        type=body.type,
        config=body.config,
    )
    db.add(subscription)
    await db.flush()
    await db.refresh(subscription)
    return subscription


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: uuid.UUID,
    body: SubscriptionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(
            Subscription.id == subscription_id, Subscription.user_id == user.id
        )
    )
    subscription = result.scalar_one_or_none()
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(subscription, key, value)
    await db.flush()
    await db.refresh(subscription)
    return subscription


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(
            Subscription.id == subscription_id, Subscription.user_id == user.id
        )
    )
    subscription = result.scalar_one_or_none()
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )
    await db.delete(subscription)


@router.get("/emails", response_model=list[SubscriptionEmailResponse])
async def list_emails(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SubscriptionEmail).where(SubscriptionEmail.user_id == user.id)
    )
    return result.scalars().all()


@router.delete("/emails/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SubscriptionEmail).where(
            SubscriptionEmail.id == email_id,
            SubscriptionEmail.user_id == user.id,
        )
    )
    email_record = result.scalar_one_or_none()
    if email_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )
    await db.delete(email_record)


@router.post(
    "/emails",
    response_model=SubscriptionEmailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_email(
    body: SubscriptionEmailCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate email deliverability (DNS/MX check)
    try:
        validate_email(body.email, check_deliverability=True)
    except EmailNotValidError as e:
        logger.warning("Email validation failed for %s: %s", body.email, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email address: {e}",
        )

    # Check max 3 emails per user
    result = await db.execute(
        select(SubscriptionEmail).where(SubscriptionEmail.user_id == user.id)
    )
    existing = result.scalars().all()
    if len(existing) >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 email addresses allowed",
        )

    # Auto-verify if matches user's login email
    is_verified = body.email == user.email

    from datetime import datetime

    email_record = SubscriptionEmail(
        user_id=user.id,
        email=body.email,
        is_verified=is_verified,
        verified_at=datetime.now(UTC) if is_verified else None,
    )
    db.add(email_record)
    await db.flush()

    if not is_verified:
        service = SubscriptionService()
        await service.send_verification_email(email_record)

    await db.refresh(email_record)
    return email_record


@router.get("/emails/verify")
async def verify_email(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService()
    email_id = service.verify_token(token)
    if email_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    result = await db.execute(
        select(SubscriptionEmail).where(SubscriptionEmail.id == email_id)
    )
    email_record = result.scalar_one_or_none()
    if email_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    from datetime import datetime

    email_record.is_verified = True
    email_record.verified_at = datetime.now(UTC)
    return {"message": "Email verified successfully"}


@router.get("/unsubscribe")
async def unsubscribe(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService()
    subscription_id = service.verify_token(token)
    if subscription_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    if subscription is not None:
        subscription.is_active = False
    return {"message": "Unsubscribed successfully"}

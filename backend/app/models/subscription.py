import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SubscriptionType(enum.StrEnum):
    BUG_FARE = "bug_fare"
    PRICE_DROP = "price_drop"
    DEAL_DIGEST = "deal_digest"


class SubscriptionEmail(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "subscription_emails"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="subscription_emails")
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="subscription_email", cascade="all, delete-orphan"
    )


class Subscription(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscription_emails.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[SubscriptionType] = mapped_column(
        Enum(SubscriptionType, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    subscription_email: Mapped["SubscriptionEmail"] = relationship(
        back_populates="subscriptions"
    )
    notification_logs: Mapped[list["NotificationLog"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )


from app.models.notification_log import NotificationLog  # noqa: E402
from app.models.user import User  # noqa: E402

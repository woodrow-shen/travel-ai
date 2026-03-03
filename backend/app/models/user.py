import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserTier(enum.StrEnum):
    BASIC = "basic"
    PREMIUM = "premium"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    tier: Mapped[UserTier] = mapped_column(
        Enum(UserTier, values_callable=lambda e: [m.value for m in e]),
        default=UserTier.BASIC,
        nullable=False,
    )
    tier_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    preferences: Mapped["UserPreference | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    trips: Mapped[list["Trip"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    subscription_emails: Mapped[list["SubscriptionEmail"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserPreference(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    preferred_airlines: Mapped[list[str] | None] = mapped_column(ARRAY(String(10)))
    excluded_airlines: Mapped[list[str] | None] = mapped_column(ARRAY(String(10)))
    preferred_alliances: Mapped[list[str] | None] = mapped_column(ARRAY(String(50)))
    cabin_classes: Mapped[list[str] | None] = mapped_column(ARRAY(String(20)))
    max_stops: Mapped[int | None] = mapped_column()
    home_airports: Mapped[list[str] | None] = mapped_column(ARRAY(String(10)))

    user: Mapped["User"] = relationship(back_populates="preferences")


# Avoid circular import issues with string references
from app.models.chat_session import ChatSession  # noqa: E402
from app.models.subscription import Subscription, SubscriptionEmail  # noqa: E402
from app.models.trip import Trip  # noqa: E402

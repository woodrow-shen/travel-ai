import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserPreference(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    preferred_airlines: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(10))
    )
    excluded_airlines: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(10))
    )
    preferred_alliances: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(50))
    )
    cabin_classes: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(20))
    )
    max_stops: Mapped[int | None] = mapped_column()
    home_airports: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(10))
    )

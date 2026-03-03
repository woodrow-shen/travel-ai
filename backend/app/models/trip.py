import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Trip(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "trips"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    destination: Mapped[str | None] = mapped_column(String(255))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    user: Mapped["User"] = relationship(back_populates="trips")
    flights: Mapped[list["Flight"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    hotels: Mapped[list["Hotel"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    activities: Mapped[list["Activity"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    itineraries: Mapped[list["Itinerary"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )


from app.models.activity import Activity  # noqa: E402
from app.models.flight import Flight  # noqa: E402
from app.models.hotel import Hotel  # noqa: E402
from app.models.itinerary import Itinerary  # noqa: E402
from app.models.user import User  # noqa: E402

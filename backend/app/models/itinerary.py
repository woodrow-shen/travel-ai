import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Itinerary(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "itineraries"

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    schedule: Mapped[dict] = mapped_column(JSONB, nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="itineraries")


from app.models.trip import Trip  # noqa: E402

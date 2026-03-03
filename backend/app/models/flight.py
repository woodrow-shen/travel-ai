import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Flight(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "flights"

    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    airline: Mapped[str] = mapped_column(String(10), nullable=False)
    flight_no: Mapped[str] = mapped_column(String(20), nullable=False)
    origin: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    departure: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stops: Mapped[int] = mapped_column(Integer, default=0)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    cabin_class: Mapped[str | None] = mapped_column(String(20))
    price_amount: Mapped[float | None] = mapped_column(Float)
    price_currency: Mapped[str | None] = mapped_column(String(10))
    source: Mapped[str | None] = mapped_column(String(50))
    raw_data: Mapped[dict | None] = mapped_column(JSONB)

    trip: Mapped["Trip | None"] = relationship(back_populates="flights")


from app.models.trip import Trip  # noqa: E402

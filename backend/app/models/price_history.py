from datetime import date

from sqlalchemy import Date, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class PriceHistory(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "price_history"

    origin: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    return_date: Mapped[date | None] = mapped_column(Date)
    airline: Mapped[str | None] = mapped_column(String(10))
    price_amount: Mapped[float] = mapped_column(Float, nullable=False)
    price_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    cabin_class: Mapped[str | None] = mapped_column(String(20))
    stops: Mapped[int | None] = mapped_column()
    raw_data: Mapped[dict | None] = mapped_column(JSONB)

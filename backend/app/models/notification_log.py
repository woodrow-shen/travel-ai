import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class NotificationStatus(enum.StrEnum):
    SENT = "sent"
    FAILED = "failed"


class NotificationLog(UUIDMixin, Base):
    __tablename__ = "notification_log"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )

    subscription: Mapped["Subscription"] = relationship(back_populates="notification_logs")


from app.models.subscription import Subscription  # noqa: E402

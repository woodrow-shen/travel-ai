"""Minimal SQLAlchemy models for monitor service.

These mirror the backend models and map to the same database tables.
Only the models needed by the notifier are included.
"""

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.notification_log import NotificationLog, NotificationStatus
from app.models.subscription import Subscription, SubscriptionEmail, SubscriptionType

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "Subscription",
    "SubscriptionEmail",
    "SubscriptionType",
    "NotificationLog",
    "NotificationStatus",
]

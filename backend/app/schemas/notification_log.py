import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.notification_log import NotificationStatus


class NotificationLogResponse(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID
    email: str
    subject: str
    sent_at: datetime
    status: NotificationStatus

    model_config = {"from_attributes": True}

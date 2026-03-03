from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_log import NotificationLog, NotificationStatus
from app.models.subscription import Subscription
from app.services.email_service import EmailService


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailService()

    async def send_notification(
        self,
        subscription: Subscription,
        subject: str,
        template_name: str,
        context: dict,
    ) -> bool:
        email_address = subscription.subscription_email.email

        success = await self.email_service.send_email(
            to=email_address,
            subject=subject,
            template_name=template_name,
            context=context,
        )

        log = NotificationLog(
            subscription_id=subscription.id,
            email=email_address,
            subject=subject,
            sent_at=datetime.now(UTC),
            status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
        )
        self.db.add(log)

        if success:
            subscription.last_sent_at = datetime.now(UTC)

        return success

import logging
import uuid

from itsdangerous import URLSafeTimedSerializer

from app.config import settings
from app.models.subscription import SubscriptionEmail
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self):
        self._serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        self._email_service = EmailService()

    def generate_token(self, entity_id: uuid.UUID) -> str:
        return self._serializer.dumps(str(entity_id), salt="email-verify")

    def verify_token(self, token: str, max_age: int = 86400) -> uuid.UUID | None:
        try:
            entity_id = self._serializer.loads(
                token, salt="email-verify", max_age=max_age
            )
            return uuid.UUID(entity_id)
        except Exception:
            return None

    async def send_verification_email(self, email_record: SubscriptionEmail) -> bool:
        token = self.generate_token(email_record.id)
        verify_url = (
            f"{settings.BACKEND_URL}/api/v1/subscriptions/emails/verify"
            f"?token={token}"
        )
        sent = await self._email_service.send_email(
            to=email_record.email,
            subject="Travel-AI: Verify your email",
            template_name="verify_email.html",
            context={"verify_url": verify_url},
        )
        if sent:
            logger.info("Verification email sent to %s", email_record.email)
        else:
            logger.warning(
                "Failed to send verification email to %s",
                email_record.email,
            )
        return sent

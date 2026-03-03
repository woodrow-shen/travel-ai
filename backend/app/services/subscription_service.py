import uuid

from itsdangerous import URLSafeTimedSerializer

from app.config import settings
from app.models.subscription import SubscriptionEmail


class SubscriptionService:
    def __init__(self):
        self._serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

    def generate_token(self, entity_id: uuid.UUID) -> str:
        return self._serializer.dumps(str(entity_id), salt="email-verify")

    def verify_token(self, token: str, max_age: int = 86400) -> uuid.UUID | None:
        try:
            entity_id = self._serializer.loads(token, salt="email-verify", max_age=max_age)
            return uuid.UUID(entity_id)
        except Exception:
            return None

    async def send_verification_email(self, email_record: SubscriptionEmail) -> None:
        token = self.generate_token(email_record.id)
        verify_url = f"{settings.BACKEND_URL}/api/v1/subscriptions/emails/verify?token={token}"
        # TODO: Send actual email using email_service
        print(f"Verification email for {email_record.email}: {verify_url}")

import logging
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
from pydantic import SecretStr

from app.config import settings

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "emails"

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=SecretStr(settings.SMTP_PASSWORD),
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=bool(settings.SMTP_USER),
)

jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


class EmailService:
    def __init__(self):
        self.mailer = FastMail(mail_config)

    async def send_email(
        self, to: str, subject: str, template_name: str, context: dict
    ) -> bool:
        # Safety guard: never send real emails in test environment
        if getattr(settings, "ENV", "") == "test":
            logger.warning("EmailService.send_email blocked in test env (to=%s)", to)
            return False

        template = jinja_env.get_template(template_name)
        html = template.render(**context)

        message = MessageSchema(
            subject=subject,
            recipients=[to],  # type: ignore[list-item]
            body=html,
            subtype=MessageType.html,
        )
        try:
            await self.mailer.send_message(message)
            return True
        except Exception:
            return False

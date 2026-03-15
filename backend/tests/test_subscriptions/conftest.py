from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True)
def _no_real_emails():
    """Prevent subscription tests from sending real emails via SMTP."""
    with patch(
        "app.services.subscription_service.SubscriptionService.send_verification_email",
        new_callable=AsyncMock,
        return_value=True,
    ):
        yield

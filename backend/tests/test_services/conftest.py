import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models.user import User, UserTier


@pytest.fixture(autouse=True)
async def setup_database():
    """Override the root setup_database fixture — service tests mock their dependencies."""
    yield


@pytest.fixture
def test_user() -> User:
    """Create a mock User without requiring a database session."""
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.name = "Test User"
    user.google_id = "google_test_123"
    user.tier = UserTier.BASIC
    user.last_login = datetime.now(UTC)
    return user

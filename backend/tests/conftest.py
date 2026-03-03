import re
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.session import get_db
from app.dependencies import create_access_token
from app.main import app
from app.models.base import Base
from app.models.user import User, UserTier


def _resolve_db_url(url: str) -> str:
    """Replace Docker Compose internal hostnames with localhost for local test runs.

    .env uses POSTGRES_HOST=db (Docker DNS).  pydantic-settings does not expand
    shell variables, so it falls back to the Settings default which also uses 'db'.
    When pytest runs on the host machine, 'db' is unreachable — swap to localhost.
    """
    return re.sub(r"@db:", "@localhost:", url)


# Use a separate test database on the same PostgreSQL instance
_base_url = _resolve_db_url(settings.DATABASE_URL).rsplit("/", 1)[0]
TEST_DATABASE_URL = f"{_base_url}/travelai_test"

# Also patch settings so that any code importing settings.REDIS_URL during tests
# can reach the local Redis forwarded from Docker.
settings.REDIS_URL = re.sub(r"://redis:", "://localhost:", settings.REDIS_URL)


@pytest.fixture(autouse=True)
async def setup_database():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    await engine.dispose()


@pytest.fixture
def override_dependencies():
    app.dependency_overrides[get_db] = _override_get_db
    original_allow = settings.ALLOW_TIER_SWITCH
    settings.ALLOW_TIER_SWITCH = True
    yield
    app.dependency_overrides.clear()
    settings.ALLOW_TIER_SWITCH = original_allow


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        google_id="google_test_123",
        tier=UserTier.BASIC,
        last_login=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def premium_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="premium@example.com",
        name="Premium User",
        google_id="google_premium_123",
        tier=UserTier.PREMIUM,
        last_login=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def premium_auth_headers(premium_user: User) -> dict[str, str]:
    token = create_access_token(premium_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client(override_dependencies) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

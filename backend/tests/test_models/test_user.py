from datetime import UTC, datetime

from sqlalchemy import select

from app.models.user import User, UserPreference, UserTier


async def test_create_user(db_session):
    user = User(
        email="new@example.com",
        name="New User",
        google_id="google_new_123",
    )
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.email == "new@example.com"))
    found = result.scalar_one()
    assert found.name == "New User"
    assert found.tier == UserTier.BASIC
    assert found.google_id == "google_new_123"


async def test_read_user_by_google_id(db_session, test_user):
    result = await db_session.execute(
        select(User).where(User.google_id == "google_test_123")
    )
    found = result.scalar_one()
    assert found.id == test_user.id
    assert found.email == "test@example.com"


async def test_update_user_tier(db_session, test_user):
    test_user.tier = UserTier.PREMIUM
    test_user.tier_updated_at = datetime.now(UTC)
    await db_session.commit()
    await db_session.refresh(test_user)
    assert test_user.tier == UserTier.PREMIUM
    assert test_user.tier_updated_at is not None


async def test_user_preferences_crud(db_session, test_user):
    pref = UserPreference(
        user_id=test_user.id,
        preferred_airlines=["NH", "BR"],
        excluded_airlines=["XX"],
        preferred_alliances=["star_alliance"],
        cabin_classes=["economy", "business"],
        max_stops=1,
        home_airports=["TPE"],
    )
    db_session.add(pref)
    await db_session.commit()

    result = await db_session.execute(
        select(UserPreference).where(UserPreference.user_id == test_user.id)
    )
    found = result.scalar_one()
    assert found.preferred_airlines == ["NH", "BR"]
    assert found.max_stops == 1
    assert found.home_airports == ["TPE"]

    # Update
    found.max_stops = 0
    await db_session.commit()
    await db_session.refresh(found)
    assert found.max_stops == 0

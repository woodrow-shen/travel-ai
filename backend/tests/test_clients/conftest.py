import pytest


@pytest.fixture(autouse=True)
async def setup_database():
    """Override the root setup_database fixture — client tests don't need a database."""
    yield

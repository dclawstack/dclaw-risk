import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.main import app
from app.core.database import get_db
from app.models import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_risk_test",
    ),
)

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


async def override_get_db():
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


async def _postgres_available() -> bool:
    try:
        async with test_engine.connect() as conn:
            await conn.run_sync(lambda c: None)
        return True
    except OperationalError:
        return False
    except Exception:
        return False


@pytest_asyncio.fixture
async def setup_db():
    if not await _postgres_available():
        pytest.skip("Postgres not available at TEST_DATABASE_URL")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(setup_db):  # noqa: ARG001 - dependency only
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

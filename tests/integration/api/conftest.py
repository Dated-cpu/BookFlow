import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from src.infrastructure.config.settings import Settings
from src.infrastructure.database.base import Base
from src.infrastructure.database.engine import close_db, init_db
from src.presentation.main import create_app

TEST_DATABASE_URL = "postgresql+asyncpg://bookflow:bookflow@localhost:5432/bookflow"


@pytest_asyncio.fixture
async def app():
    settings = Settings()
    await init_db(settings.database_url)
    # Create tables for test isolation
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

    app = create_app()
    yield app

    # Cleanup tables
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    await close_db()


@pytest_asyncio.fixture
async def client(app) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

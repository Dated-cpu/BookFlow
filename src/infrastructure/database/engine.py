from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db(database_url: str) -> None:
    global engine, async_session_factory
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def close_db() -> None:
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def get_session() -> AsyncGenerator[AsyncSession]:
    if async_session_factory is None:
        raise RuntimeError("Database not initialized")
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

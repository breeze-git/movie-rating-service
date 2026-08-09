from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import settings

engine: AsyncEngine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_session_maker


async def close_db() -> None:
    await engine.dispose()

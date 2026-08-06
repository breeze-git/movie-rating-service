from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.settings import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)


async def get_session_maker():
    return async_sessionmaker(bind=engine, expire_on_commit=False)

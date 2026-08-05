from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.settings import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)

Session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session():
    async with Session() as session:
        yield session

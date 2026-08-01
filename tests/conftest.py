import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass

import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from alembic.config import Config
from app.core.settings import settings
from app.database.session import get_session
from app.main import app

pytest_plugins = [
    "tests.fixtures.users",
]


@dataclass
class URLPaths:
    register_user: str = app.url_path_for("register_user")
    login_user: str = app.url_path_for("login_user")
    refresh_token: str = app.url_path_for("refresh_token")


@pytest_asyncio.fixture(scope="session")
async def endp_urls() -> URLPaths:
    return URLPaths()


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(settings.test_database_url, echo=True)

    alembic_cfg = Config("alembic.ini")

    alembic_cfg.set_main_option("sqlalchemy.url", settings.test_database_url)

    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    try:
        yield engine
    finally:
        await asyncio.to_thread(command.downgrade, alembic_cfg, "base")
        await engine.dispose()


@pytest_asyncio.fixture
async def db_connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection]:
    async with engine.connect() as conn:
        transaction = await conn.begin()

        try:
            yield conn
        finally:
            await transaction.rollback()


@pytest_asyncio.fixture
async def db_session(db_connection) -> AsyncGenerator[AsyncSession]:
    Session = async_sessionmaker(bind=db_connection, expire_on_commit=False)

    async with Session() as session:
        yield session


@pytest_asyncio.fixture
async def session_override(db_session) -> AsyncGenerator[None]:
    async def _get_test_session():
        yield db_session

    app.dependency_overrides[get_session] = _get_test_session

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def api_client(session_override) -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://127.0.0.1:8000",
    ) as ac:
        yield ac

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from alembic import command
from alembic.config import Config
from app.core.settings import settings
from app.database.session import get_session_maker
from app.main import app

pytest_plugins = [
    "tests.fixtures.users",
    "tests.fixtures.movies",
    "tests.fixtures.directors",
]


@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        driver_url = postgres.get_connection_url(driver="asyncpg")

        settings.database_url = driver_url
        yield driver_url


@pytest.fixture(scope="session", autouse=True)
def redis_container():
    with RedisContainer("redis:7-alpine") as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)

        redis_url = f"redis://{host}:{port}/0"

        settings.redis_url = redis_url
        yield redis_url


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(settings.database_url, echo=settings.debug)

    alembic_cfg = Config("alembic.ini")

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


@pytest.fixture
def test_session_maker(
    db_connection: AsyncConnection,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


@pytest_asyncio.fixture
async def db_session(
    test_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def session_maker_override(
    db_session: AsyncSession,
) -> AsyncGenerator[None]:
    class SingleSessionMaker:
        def __call__(self):
            return db_session

    app.dependency_overrides[get_session_maker] = SingleSessionMaker

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def api_client(session_maker_override) -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://127.0.0.1:8000",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def user_client(api_client, user_tokens) -> AsyncGenerator[AsyncClient]:
    api_client.headers["Authorization"] = f"{user_tokens.token_type} {user_tokens.access_token}"
    yield api_client


@pytest_asyncio.fixture
async def admin_client(api_client, admin_tokens) -> AsyncGenerator[AsyncClient]:
    api_client.headers["Authorization"] = f"{admin_tokens.token_type} {admin_tokens.access_token}"
    yield api_client

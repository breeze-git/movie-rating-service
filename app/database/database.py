import asyncpg

from app.database.storage import config

DB_POOL: asyncpg.Pool | None = None


async def init_db() -> None:
    global DB_POOL

    DB_POOL = await asyncpg.create_pool(
        dsn=config.db.database_url,
        min_size=5,
        max_size=20,
    )


async def close_db() -> None:
    if DB_POOL:
        await DB_POOL.close()


async def get_session():
    if DB_POOL is None:
        raise RuntimeWarning("Database pool is not initialized")

    async with DB_POOL.acquire() as connection:
        yield connection

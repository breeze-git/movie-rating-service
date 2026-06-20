import asyncpg

from app.schemas.auth import UserInDB


async def get_user_from_db_by_email(
    email: str, session: asyncpg.Connection
) -> dict | None:
    user = await session.fetchrow(
        """
        SELECT id, username, first_name, 
               last_name, email, hashed_password 
        FROM users
        WHERE email = $1;
        """,
        email,
    )

    return user


async def get_user_from_db_by_id(
    user_id: str, session: asyncpg.Connection
) -> dict | None:
    user = await session.fetchrow(
        """
        SELECT id, username, first_name, 
               last_name, email, hashed_password 
        FROM users
        WHERE id = $1;
    """,
        user_id,
    )

    return user


async def add_user_to_db(user: UserInDB, session: asyncpg.Connection) -> None:
    await session.execute(
        """
        INSERT INTO users(id, username, first_name, last_name, email, hashed_password)
        VALUES($1, $2, $3, $4, $5, $6);

    """,
        user.id,
        user.username,
        user.first_name,
        user.last_name,
        user.email,
        user.hashed_password,
    )

    await session.execute(
        """
        INSERT INTO user_roles(user_id, role_id)
        VALUES($1, 2);
    """,
        user.id,
    )


async def get_reviews_from_db(session: asyncpg.Connection) -> list:
    reviews = await session.fetch("""
        SELECT id, user_id, message, created_at, updated_at
        FROM reviews
    """)

    return reviews


async def get_user_roles(user_id: str, session: asyncpg.Connection) -> set[str] | None:
    roles = await session.fetchrow(
        """
        SELECT ARRAY_AGG(r.name)
        FROM user_roles ur
        JOIN roles r ON r.id = ur.role_id
        WHERE ur.user_id = $1
        """,
        user_id,
    )

    user_roles = set(*roles)

    return user_roles


async def get_user_permissions(user_id: str, session: asyncpg.Connection) -> set[str]:
    perms = await session.fetchrow(
        """
        SELECT ARRAY_AGG(p.name)
        FROM user_roles ur
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE user_id = $1
    """,
        user_id,
    )

    user_perms = set(*perms)

    return user_perms


async def get_review_owner(review_id: str, session: asyncpg.Connection):
    review_data = await get_review_from_db(review_id, session)

    if review_data is not None:
        review = dict(review_data)

        return review["user_id"]

    return None


async def get_review_from_db(review_id: str, session: asyncpg.Connection):
    review_data = await session.fetchrow(
        """
        SELECT id, user_id
        FROM reviews
        WHERE id = $1
    """,
        review_id,
    )

    return review_data


async def add_review_to_db(review: dict, session: asyncpg.Connection):
    await session.execute(
        """
        INSERT INTO reviews(id, user_id, message, created_at) VALUES($1, $2, $3, $4)
    """,
        review["id"],
        review["user_id"],
        review["message"],
        review["created_on"],
    )

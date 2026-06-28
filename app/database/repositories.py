from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Permission, Review, Role, RolePermissions, User, UserRoles


async def get_user_by_email(session: AsyncSession, email: str):
    user = await session.scalar(select(User).where(User.email == email))

    return user


async def get_user_by_id(session: AsyncSession, id: str):
    user = await session.get(User, id)

    return user


async def get_default_role(session: AsyncSession):
    default_role = await session.get(Role, 2)

    return default_role


async def save_user(session: AsyncSession, user: User):
    session.add(user)
    await session.commit()


async def remove_user(session: AsyncSession, user: User):
    await session.delete(user)

    await session.commit()


async def get_user_roles(session: AsyncSession, user_id: str) -> set:

    query = (
        select(Role.name)
        .join(UserRoles, Role.id == UserRoles.role_id)
        .where(UserRoles.user_id == user_id)
    )

    roles = (await session.scalars(query)).all()

    return set(roles)


async def get_user_permissions(session: AsyncSession, user_id: str) -> set:

    query = (
        select(Permission.name)
        .join(RolePermissions, Permission.id == RolePermissions.permission_id)
        .join(UserRoles, RolePermissions.role_id == UserRoles.role_id)
        .where(UserRoles.user_id == user_id)
    )

    perms = (await session.scalars(query)).all()

    return set(perms)


async def get_reviews(session: AsyncSession):
    reviews = (await session.scalars(select(Review))).all()

    return reviews


async def save_review(session: AsyncSession, review: Review):
    session.add(review)
    await session.commit()


async def manage_review(session: AsyncSession, review: Review, message: str):
    review.message = message
    review.updated_at = datetime.now()

    await session.commit()


async def remove_review(session: AsyncSession, review: Review):
    await session.delete(review)

    await session.commit()


async def get_review_by_id(session: AsyncSession, review_id: str) -> Review | None:
    review = await session.get(Review, review_id)

    return review

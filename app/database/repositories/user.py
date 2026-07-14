from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.database.models import Permission, Role, RolePermissions, User, UserRoles

from .pg_error_codes import PostgresErrorCode as pg_err


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> User | None:
        query = select(User).where(User.id == id)

        user = await self.session.scalar(query)

        return user

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)

        user = await self.session.scalar(query)

        return user

    async def get_by_id_with_relations(self, id: UUID) -> User | None:
        query = select(User).where(User.id == id).options(selectinload(User.reviews))

        user = await self.session.scalar(query)

        return user

    async def save(self, user: User):
        self.session.add(user)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def update(self, user: User, user_data_dict: dict):
        for key, value in user_data_dict.items():
            setattr(user, key, value)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def get_roles(self, id: UUID) -> Sequence[str]:
        query = select(Role.name).join(UserRoles, Role.id == UserRoles.role_id).where(UserRoles.user_id == id)

        result = await self.session.scalars(query)

        return result.all()

    async def get_permissions(self, id: UUID) -> Sequence[str]:
        query = (
            select(Permission.name)
            .join(RolePermissions, Permission.id == RolePermissions.permission_id)
            .join(UserRoles, RolePermissions.role_id == UserRoles.role_id)
            .where(UserRoles.user_id == id)
        )

        result = await self.session.scalars(query)

        return result.all()

    async def get_default_roles(self) -> Sequence[Role]:
        roles_ids = [2]

        query = select(Role).where(Role.id.in_(roles_ids))

        result = await self.session.scalars(query)

        return result.all()

    async def delete(self, id: UUID) -> None:
        stmt = delete(User).where(User.id == id)

        result = await self.session.execute(stmt)

        if not result.rowcount:  # type: ignore
            raise EntityNotFoundError from None

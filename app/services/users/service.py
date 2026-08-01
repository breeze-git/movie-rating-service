import logging
from collections.abc import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.repository import RepoUniqueViolationError
from app.core.security import get_hash, verify_password
from app.database.models import User
from app.database.repositories.user import UserRepository
from app.database.session import get_session
from app.schemas.auth import UserRegister
from app.schemas.users import UserBrief, UserDetail, UserUpdate, UserWithReviews
from app.services.users.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

        self.users = UserRepository(session)

    async def get_user(self, user_id: UUID) -> UserWithReviews:
        db_user = await self.users.get_by_id_with_relations(user_id)

        if db_user is None:
            raise UserNotFoundError(search_by="id", value=user_id) from None

        user = UserWithReviews.model_validate(db_user)

        return user

    async def get_profile(self, user_id: UUID) -> UserDetail:
        db_user = await self.users.get_by_id_with_relations(user_id)

        if db_user is None:
            raise UserNotFoundError(search_by="id", value=user_id) from None

        user = UserDetail.model_validate(db_user)

        return user

    async def register_user(self, dto: UserRegister) -> UserBrief:
        if await self.users.exists_by_email(dto.email):
            raise UserAlreadyExistsError(conflict_reason="email", value=dto.email) from None

        hashed_password = get_hash(dto.password).decode("utf-8")

        default_roles = await self.users.get_default_roles()

        db_user = User(
            **dto.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
            roles=default_roles,
        )

        try:
            await self.users.save(db_user)
        except RepoUniqueViolationError as e:
            raise UserAlreadyExistsError(conflict_reason="username", value=dto.username) from e

        await self.session.commit()

        user = UserBrief.model_validate(db_user)

        logger.info(
            "User registered",
            extra={"id": user.id, "email": user.email, "username": user.username},
        )

        return user

    async def authenticate_user(self, email: str, password: str) -> UUID:
        db_user = await self.users.get_by_email(email)

        if db_user is None:
            raise InvalidCredentialsError(email=email) from None

        if not verify_password(password, db_user.hashed_password):
            raise InvalidCredentialsError(email=email) from None

        return db_user.id

    async def get_user_roles(self, user_id: UUID) -> Sequence[str]:
        roles = await self.users.get_roles(user_id)

        if not roles:
            raise UserNotFoundError(search_by="id", value=user_id) from None

        return roles

    async def get_user_permissions(self, user_id: UUID) -> Sequence[str]:
        perms = await self.users.get_permissions(user_id)

        if not perms:
            raise UserNotFoundError(search_by="id", value=user_id) from None

        return perms

    async def update_user(self, user_id: UUID, dto: UserUpdate) -> UserBrief:
        db_user = await self.users.get_by_id(user_id)

        if db_user is None:
            raise UserNotFoundError(search_by="id", value=user_id) from None

        update_data = dto.model_dump(exclude_unset=True)

        try:
            await self.users.update(db_user, update_data)
        except RepoUniqueViolationError as e:
            raise UserAlreadyExistsError(conflict_reason="username", value=update_data["username"]) from e

        await self.session.commit()

        user = UserBrief.model_validate(db_user)

        return user

    async def remove_user(self, user_id: UUID) -> None:
        result = await self.users.delete(user_id)

        if not result.scalar():
            raise UserNotFoundError(search_by="id", value=user_id) from None

        await self.session.commit()

        logger.info(
            "User deleted",
            extra={"id": user_id},
        )

from collections.abc import Sequence
from uuid import UUID

import bcrypt
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.repositories import RepositoryException
from app.core.exceptions.services import (
    AlreadyExistsError,
    InvalidCredentialsError,
    NotFoundError,
)
from app.core.security import get_hash
from app.database.models import User
from app.database.repositories.user import UserRepository
from app.database.session import get_session
from app.schemas.auth import UserRegister
from app.schemas.users import UserBrief, UserDetail, UserUpdate, UserWithReviews

from .base import BaseService
from .error_details import UserErrorDetails
from .integrity_maps import USER_INTEGRITY_MAP


class UserService(BaseService):
    _integrity_map = USER_INTEGRITY_MAP

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.users = UserRepository(session)

        super().__init__(session)

    async def get_user(self, user_id: UUID) -> UserWithReviews:
        db_user = await self.users.get_by_id_with_relations(user_id)

        if db_user is None:
            raise NotFoundError(**UserErrorDetails.not_found(id=user_id)) from None

        user = UserWithReviews.model_validate(db_user)

        return user

    async def get_profile(self, user_id: UUID) -> UserDetail:
        db_user = await self.users.get_by_id_with_relations(user_id)

        if db_user is None:
            raise NotFoundError(**UserErrorDetails.not_found(id=user_id)) from None

        user = UserDetail.model_validate(db_user)

        return user

    async def register_user(self, dto: UserRegister) -> UserBrief:
        existing_user = await self.users.get_by_email(dto.email)

        if existing_user is not None:
            raise AlreadyExistsError(**UserErrorDetails.already_exists(email=dto.email)) from None

        hashed_password = get_hash(dto.password).decode("utf-8")

        default_roles = await self.users.get_default_roles()

        db_user = User(
            **dto.model_dump(),
            hashed_password=hashed_password,
            roles=default_roles,
        )

        try:
            await self.users.save(db_user)
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, **dto.model_dump()) from None

        await self.session.commit()

        user = UserBrief.model_validate(db_user)

        return user

    async def authenticate_user(self, email: str, password: str) -> UUID:
        db_user = await self.users.get_by_email(email)

        if db_user is None:
            raise InvalidCredentialsError(**UserErrorDetails.invalid_credentials(email=email)) from None

        user_pass = password.encode("utf-8")
        hashed_pass = db_user.hashed_password.encode("utf-8")

        if not bcrypt.checkpw(user_pass, hashed_pass):
            raise InvalidCredentialsError(
                **UserErrorDetails.invalid_credentials(email=email, pass_mismatch=True)
            ) from None

        return db_user.id

    async def get_user_roles(self, user_id: UUID) -> Sequence[str]:
        roles = await self.users.get_roles(user_id)

        if not roles:
            raise NotFoundError(**UserErrorDetails.not_found(id=user_id)) from None

        return roles

    async def get_user_permissions(self, user_id: UUID) -> Sequence[str]:
        perms = await self.users.get_permissions(user_id)

        if not perms:
            raise NotFoundError(**UserErrorDetails.not_found(id=user_id)) from None

        return perms

    async def update_user(self, user_id: UUID, dto: UserUpdate) -> UserBrief:
        db_user = await self.users.get_by_id(user_id)

        if db_user is None:
            raise NotFoundError(**UserErrorDetails.not_found(id=user_id)) from None

        update_data = dto.model_dump(exclude_unset=True)

        try:
            await self.users.update(db_user, update_data)
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, user_id=user_id, **update_data) from None

        await self.session.commit()

        user = UserBrief.model_validate(db_user)

        return user

    async def remove_user(self, user_id: UUID) -> None:
        result = await self.users.delete(user_id)

        if not result.scalar():
            raise NotFoundError(**UserErrorDetails.not_found(id=user_id)) from None

        await self.session.commit()

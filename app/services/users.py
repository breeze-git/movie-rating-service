from collections.abc import Sequence
from uuid import UUID, uuid4

import bcrypt
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.error_messages import UserMessages
from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.core.exceptions.services import (
    AlreadyExistsError,
    InvalidCredentialsError,
    NotFoundError,
)
from app.core.security import get_hash
from app.database.models import User
from app.database.repositories.user import UserRepository
from app.database.session import get_session
from app.schemas.auth import UserRegisterRequest


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.users = UserRepository(session)

    async def get_user(self, user_id: UUID):
        user = await self.users.get_by_id_with_relations(user_id)

        if user is None:
            raise NotFoundError(detail=UserMessages.not_found(user_id=user_id)) from None

        return user

    async def register_user(self, user_data: UserRegisterRequest) -> UUID:
        existing_user = await self.users.get_by_email(user_data.email)

        if existing_user is not None:
            raise AlreadyExistsError(detail=UserMessages.already_exists(email=user_data.email)) from None

        id = uuid4()
        hashed_password = get_hash(user_data.password).decode("utf-8")

        default_roles = await self.users.get_default_roles()

        new_user = User(
            id=id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
            roles=default_roles,
        )

        try:
            await self.users.save(new_user)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(UserMessages.already_exists(username=user_data.username)) from None

        await self.session.commit()

        return id

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)

        if user is None:
            raise NotFoundError(detail=UserMessages.not_found(email=email)) from None

        user_pass = password.encode("utf-8")
        hashed_pass = user.hashed_password.encode("utf-8")

        if not bcrypt.checkpw(user_pass, hashed_pass):
            raise InvalidCredentialsError() from None

        return user

    async def get_user_roles(self, user_id: UUID) -> Sequence[str]:
        roles = await self.users.get_roles(user_id)

        if not roles:
            raise NotFoundError(detail=UserMessages.not_found(user_id=user_id)) from None

        return roles

    async def get_user_permissions(self, user_id: UUID) -> Sequence[str]:
        perms = await self.users.get_permissions(user_id)

        if not perms:
            raise NotFoundError(detail=UserMessages.not_found(user_id=user_id)) from None

        return perms

    async def update_user(self, user_id: UUID, user_data) -> None:
        user = await self.users.get_by_id(user_id)

        if user is None:
            raise NotFoundError(detail=UserMessages.not_found(user_id=user_id)) from None

        user_data_dict = user_data.model_dump()

        try:
            await self.users.update(user, user_data_dict)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=UserMessages.already_exists(username=user_data.username)) from None

        await self.session.commit()

    async def partial_update_user(self, user_id: UUID, user_data) -> None:
        user = await self.users.get_by_id(user_id)

        if user is None:
            raise NotFoundError(detail=UserMessages.not_found(user_id=user_id)) from None

        user_data_dict = user_data.model_dump(exclude_unset=True)

        try:
            await self.users.update(user, user_data_dict)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=UserMessages.already_exists(username=user_data.username)) from None

        await self.session.commit()

    async def remove_user(self, user_id: UUID) -> None:
        try:
            await self.users.delete(user_id)
        except EntityNotFoundError:
            raise NotFoundError(detail=UserMessages.not_found(user_id=user_id)) from None

        await self.session.commit()

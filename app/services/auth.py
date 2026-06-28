from uuid import UUID, uuid4

import bcrypt
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.repositories as repo
from app.core.exceptions.services import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import get_hash
from app.database.models import Role, User
from app.database.session import get_session
from app.schemas.auth import UserCreateRequest, UserLoginRequest


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def create_new_user(self, user_data: UserCreateRequest) -> UUID:
        existing_user = await repo.get_user_by_email(self.session, user_data.email)

        if existing_user is not None:
            raise UserAlreadyExistsError

        id = uuid4()
        hashed_password = get_hash(user_data.password).decode("utf-8")

        default_role = await repo.get_default_role(self.session)

        new_user = User(
            id=id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
            roles=[default_role],
        )

        try:
            await repo.save_user(self.session, new_user)
        except IntegrityError:
            raise UsernameAlreadyExistsError from None

        return id

    async def authenticate_user(self, user_data: UserLoginRequest) -> User:

        user = await repo.get_user_by_email(self.session, user_data.email)

        if user is None:
            raise UserNotFoundError

        user_pass = user_data.password.encode("utf-8")
        hashed_pass = user.hashed_password.encode("utf-8")

        if not bcrypt.checkpw(user_pass, hashed_pass):
            raise InvalidCredentialsError

        return user

    async def remove_user(self, user_id: str):
        user = await repo.get_user_by_id(self.session, user_id)

        if user:
            await repo.remove_user(self.session, user)

    async def get_user_roles(self, user_id: str) -> set:
        roles = await repo.get_user_roles(self.session, user_id)

        if not roles:
            raise UserNotFoundError

        return roles

    async def get_user_permissions(self, user_id) -> set:

        perms = await repo.get_user_permissions(self.session, user_id)

        return perms

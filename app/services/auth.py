from uuid import uuid4

import asyncpg
import bcrypt
from asyncpg.exceptions import UniqueViolationError
from fastapi import Depends

from app.core.exceptions import UsernameAlredyExistsError
from app.core.security import get_hash
from app.database.database import get_session
from app.database.repositories import add_user_to_db, get_user_from_db_by_email
from app.schemas.auth import CreateUser, LoginUser, UserInDB


async def create_user(data: CreateUser, session: asyncpg.Connection) -> None:
    user_id = uuid4()

    hashed_password = get_hash(data.password).decode("utf-8")

    user = UserInDB(
        id=user_id,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        hashed_password=hashed_password,
    )
    try:
        await add_user_to_db(user, session)
    except UniqueViolationError:
        raise UsernameAlredyExistsError from None


async def authenticate_user(user: LoginUser, session: asyncpg.Connection = Depends(get_session)) -> UserInDB | None:
    data = await get_user_from_db_by_email(user.email, session)

    if data is not None:
        user_in_db = UserInDB(**data)

        user_pass = user.password.encode("utf-8")
        hashed_pass = user_in_db.hashed_password.encode("utf-8")

        is_correct = bcrypt.checkpw(user_pass, hashed_pass)

        if is_correct:
            return user_in_db

    return None

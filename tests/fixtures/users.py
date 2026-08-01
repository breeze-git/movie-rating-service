from collections.abc import Callable

import pytest
from httpx2 import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_hash
from app.database.models import Role, User
from app.main import app
from app.schemas.auth import Tokens, UserRegister
from tests.factories.users import UserRegisterFactory


@pytest.fixture
def register_payload():
    return UserRegisterFactory.build()


@pytest.fixture
def create_user_in_db(db_session: AsyncSession) -> Callable:
    async def _create_user(payload: UserRegister, roles: tuple[str] = ("user",)) -> User:
        hashed_password = get_hash(payload.password).decode("utf-8")

        query = select(Role).where(Role.name.in_(roles))

        default_roles = (await db_session.scalars(query)).all()

        user = User(
            **payload.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
            roles=default_roles,
        )

        db_session.add(user)

        await db_session.commit()

        return user

    return _create_user


@pytest.fixture
async def registered_user(create_user_in_db: Callable, register_payload: UserRegister) -> UserRegister:
    await create_user_in_db(register_payload)
    return register_payload


@pytest.fixture
async def user_tokens(
    api_client: AsyncClient,
    registered_user: UserRegister,
) -> Tokens:
    login_data = {
        "username": registered_user.email,
        "password": registered_user.password,
    }

    endpoint_url = app.url_path_for("login_user")

    response = await api_client.post(endpoint_url, data=login_data)

    tokens_raw = response.json()["data"]

    return Tokens.model_validate(tokens_raw)

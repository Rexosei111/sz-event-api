import contextlib
import uuid
from typing import Union

from config import get_logger, get_settings
from database import get_async_session
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .models import Admins, Organisers, get_user_db, get_user_manager
from .schemas import AdminsCreate, AdminsUpdate, NewAdminsCreate

logger = get_logger()

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(**kwargs):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(NewAdminsCreate(**kwargs))
                    return user
    except UserAlreadyExists:
        logger.warning(f"User {kwargs.get('email')} already exists")
        return None


async def create_organiser(**kwargs) -> Union[Organisers, None]:
    try:
        async with get_async_session_context() as session:
            organiser = Organisers(**kwargs)
            session.add(organiser)
            await session.commit()
            await session.refresh(organiser)
            return organiser
    except SQLAlchemyError:
        logger.error(
            f"Unable to create organisation of name {organiser.name}", exc_info=True
        )
        await session.rollback()
        return None


async def update_user(user_id, **kwargs):
    try:
        async with get_async_session_context() as session:
            user = await session.scalar(
                statement=select(Admins).where(Admins.id == user_id)
            )

            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    updated_user = await user_manager.update(
                        user=user,
                        user_update=AdminsUpdate(**kwargs),
                    )
                    logger.info(f"User updated - {updated_user.email}")
                    return updated_user
    except SQLAlchemyError:
        logger.error("Unable to set user organisation", exc_info=True)
        return None


settings = get_settings()


bearer_transport = BearerTransport(tokenUrl="/admins/auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt_secret, lifetime_seconds=settings.jwt_expire_time
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[Admins, uuid.UUID](get_user_manager, [auth_backend])

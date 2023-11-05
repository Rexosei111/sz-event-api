import contextlib
from typing import Union

from config import get_logger
from database import get_async_session
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy.exc import SQLAlchemyError

from .models import Organisers, get_user_db, get_user_manager
from .schemas import AdminsCreate, AdminsUpdate

logger = get_logger()

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(*kwargs):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(AdminsCreate(**kwargs))
                    print(f"User created - {user.email}")
                    return user
    except UserAlreadyExists:
        print(f"User {kwargs.get('email')} already exists")
        return None


async def create_organiser(*kwargs) -> Union[Organisers, None]:
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


async def set_user_organisation(user, organiser_id):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.update(
                        user=user,
                        user_update=AdminsUpdate({"organiser_id": organiser_id}),
                    )
                    print(f"User updated - {user.email}")
                    return user
    except SQLAlchemyError:
        logger.error("Unable to set user organisation", exc_info=True)
        return None

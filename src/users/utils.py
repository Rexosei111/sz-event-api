import contextlib
import uuid

from config import get_logger, get_settings
from utils import send_sms
from database import get_async_session
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists
from httpx_oauth.clients.google import GoogleOAuth2

from .models import User, get_user_db, get_user_manager
from .schemas import UserCreate

settings = get_settings()

# google_oauth_client = GoogleOAuth2(
#     settings.google_client_id, settings.google_client_secret
# )
logger = get_logger()

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(*kwargs):
    logger.info(f"User details: {kwargs}")
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(UserCreate(**kwargs))
                    print(f"User created - {user.email}")
                    return user
    except UserAlreadyExists:
        print(f"User {kwargs.get('email')} already exists")
        return None


settings = get_settings()


bearer_transport = BearerTransport(tokenUrl="/users/auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt_secret, lifetime_seconds=settings.jwt_expire_time
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

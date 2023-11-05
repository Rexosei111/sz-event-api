import uuid
from datetime import datetime
from typing import List, Optional, Union

from config import get_settings
from database import Base, get_async_session
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin
from fastapi_users.db import SQLAlchemyBaseOAuthAccountTableUUID, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from .schemas import UserCreate

settings = get_settings()


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass

    @declared_attr
    def user_id(cls) -> Mapped[GUID]:
        return mapped_column(
            GUID, ForeignKey("users.id", ondelete="cascade"), nullable=False
        )


class User(Base):
    __tablename__ = "users"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    phone_number = Column(String(length=15))
    first_name = Column(String(length=30))
    last_name = Column(String(length=30))
    following_count = Column(Integer, default=0)

    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    createdAt = Column(DateTime, nullable=True, default=datetime.utcnow)
    updatedAt = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Following(Base):
    __tablename__ = "Following"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"))
    organiser_id = Column(GUID, ForeignKey("organisers.id"))
    organiser = relationship(
        "Organisers", back_populates="followers", lazy="selectin", viewonly=False
    )


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)  # type: ignore


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):  # type: ignore
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        print(f"User {user.email} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

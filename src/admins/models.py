import uuid
from datetime import datetime
from typing import Optional, Union

from config import get_logger, get_settings
from database import Base, get_async_session
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from .schemas import AdminsCreate

settings = get_settings()
logger = get_logger()


class Admins(Base):
    __tablename__ = "admins"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    phone_number = Column(String(length=15))
    first_name = Column(String(length=30))
    last_name = Column(String(length=30))
    organiser_id = Column(GUID, ForeignKey("organisers.id"))
    organiser = relationship(
        "Organisers",
        back_populates="admins",
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    createdAt = Column(DateTime, nullable=True, default=datetime.utcnow)
    updatedAt = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Organisers(Base):
    __tablename__ = "organisers"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(length=100))
    summary = Column(String(length=500))
    admins = relationship("Admins", back_populates="organiser")
    description = Column(Text)
    logo = Column(String(length=100))
    followers_count = Column(Integer, default=0)
    events = relationship("Events", back_populates="organiser")
    followers = relationship("Following", back_populates="organiser")
    createdAt = Column(DateTime, nullable=True, default=datetime.utcnow)
    updatedAt = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, Admins)  # type: ignore


class UserManager(UUIDIDMixin, BaseUserManager[Admins, uuid.UUID]):  # type: ignore
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    async def on_after_register(
        self,
        user: Admins,
        request: Optional[Request] = None,
    ):
        if user.organiser_id is None:
            organiser = await create_organiser()
            organiser_id = organiser.__dict__.get("id")
            await update_user(user_id=user.id, organiser_id=organiser_id)
        logger.info(f"User {user.email} has registered.")

    async def on_after_forgot_password(
        self, user: Admins, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: Admins, token: str, request: Optional[Request] = None
    ):
        logger.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )

    async def validate_password(
        self,
        password: str,
        user: Union[AdminsCreate, Admins],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


from events.models import Events

from .utils import create_organiser, update_user

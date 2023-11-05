from typing import Optional

from admins.schemas import OrganiserRead
from fastapi_users import models
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, EmailStr, Field


class UserRead(BaseModel):
    id: models.ID  # type: ignore
    email: EmailStr
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)


class UserUpdate(CreateUpdateDictModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)


class UserCredentialsRead(BaseModel):
    email: str
    password: str


class FollowingRead(BaseModel):
    id: models.ID
    # organiser_id:
    organiser: OrganiserRead

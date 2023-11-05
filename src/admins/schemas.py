from datetime import datetime
from typing import Optional

from fastapi_users import models
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator


class AdminsRead(BaseModel):
    id: models.ID  # type: ignore
    email: EmailStr
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminsCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    is_superuser: Optional[bool] = True

    @validator("is_superuser", pre=True, always=True)
    def set_is_superuser_status(cls, is_superuser, values):
        if not is_superuser:
            return True


class NewAdminsCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    organiser_id: Optional[models.ID] = None
    is_superuser: Optional[bool] = True
    is_verified: Optional[bool] = True
    is_active: Optional[bool] = True


class AdminsUpdate(CreateUpdateDictModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    organiser_id: Optional[models.ID] = None


class AdminsCredentialsRead(BaseModel):
    email: str
    password: str


class OrganiserRead(BaseModel):
    id: Optional[models.ID]
    name: Optional[str] = Field(description="Name of organiser")
    followers_count: Optional[int] = Field(description="Number of followers")
    summary: Optional[str] = Field(description="A little information about organiser")
    description: Optional[str] = Field(default=None, description="About organiser")
    logo: Optional[HttpUrl] = Field(default=None, description="Url of organisers logo")


class OrganiserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of organiser")
    summary: Optional[str] = Field(
        default=None, description="A little information about organiser"
    )
    description: Optional[str] = Field(default=None, description="About organiser")
    logo: Optional[str] = Field(default=None, description="Url of organisers logo")

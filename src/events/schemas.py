from datetime import date, datetime
from typing import List, Optional, Union

from admins.schemas import OrganiserRead
from fastapi_users import models
from pydantic import BaseModel, validator


class EventImagesCreate(BaseModel):
    url: str


class EventImagesRead(BaseModel):
    id: models.ID
    url: str


class EventListingRead(BaseModel):
    id: models.ID
    name: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[Union[datetime, str]] = None
    organiser: OrganiserRead


class EventReadWithOrganiser(BaseModel):
    id: models.ID
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[datetime] = None
    address: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    published: Optional[bool] = False
    images: Optional[List[EventImagesRead]] = None
    organiser: OrganiserRead


class EventRead(BaseModel):
    id: models.ID
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[datetime] = None
    address: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    published: Optional[bool] = False

    images: Optional[List[EventImagesRead]] = None

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[Union[str, datetime]] = None
    address: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    published: Optional[bool] = False
    images: Optional[List[EventImagesCreate]] = None

    @validator("start_date", pre=True, always=True)
    def convert_str_datetime(cls, start_date: str, values):
        if start_date and start_date.endswith("Z"):
            start_date = datetime.fromisoformat(start_date[:-1])
        else:
            start_date = datetime.fromisoformat(start_date)
        return start_date


class EventUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[Union[str, datetime]] = None
    address: Optional[str] = None
    longitude: Optional[str] = None
    published: Optional[bool] = False

    latitude: Optional[str] = None

    @validator("start_date", pre=True, always=True)
    def convert_str_datetime(cls, start_date: str, values):
        if start_date and start_date.endswith("Z"):
            start_date = datetime.fromisoformat(start_date[:-1])
        else:
            start_date = datetime.fromisoformat(start_date)
        return start_date

from typing import Optional

from fastapi_users import models
from pydantic import BaseModel


class EventAttendanceRead(BaseModel):
    id: models.ID
    email: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    present: Optional[bool] = False


class EventAttendanceCreate(BaseModel):
    email: str
    phone_number: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    location: Optional[str] = None
    present: Optional[bool] = False


class EventAttendanceUpdate(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    present: Optional[bool] = False

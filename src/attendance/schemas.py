from typing import Optional

from fastapi_users import models
from pydantic import BaseModel


class EventAttendanceReadWithoutId(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    present: Optional[bool] = False
    occupation: Optional[str] = None
    level: Optional[str] = None
    school: Optional[str] = None
    profession: Optional[str] = None
    other: Optional[str] = None
    by_friend: Optional[bool] = None
    by_member: Optional[bool] = None
    via_whatsapp: Optional[bool] = None
    via_instagram: Optional[bool] = None
    friend_name: Optional[str] = None
    first_time: Optional[bool] = None
    


class EventAttendanceRead(BaseModel):
    id: models.ID
    email: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    present: Optional[bool] = False
    occupation: Optional[str] = None
    level: Optional[str] = None
    school: Optional[str] = None
    profession: Optional[str] = None
    other: Optional[str] = None
    by_friend: Optional[bool] = None
    by_member: Optional[bool] = None
    via_whatsapp: Optional[bool] = None
    via_instagram: Optional[bool] = None
    friend_name: Optional[str] = None
    first_time: Optional[bool] = None
    


class EventAttendanceCreate(BaseModel):
    email: str
    phone_number: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    location: Optional[str] = None
    present: Optional[bool] = False
    occupation: Optional[str] = None
    level: Optional[str] = None
    school: Optional[str] = None
    profession: Optional[str] = None
    other: Optional[str] = None
    by_friend: Optional[bool] = None
    by_member: Optional[bool] = None
    via_whatsapp: Optional[bool] = None
    via_instagram: Optional[bool] = None
    friend_name: Optional[str] = None
    first_time: Optional[bool] = None


class EventAttendanceUpdate(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    present: Optional[bool] = False
    occupation: Optional[str] = None
    level: Optional[str] = None
    school: Optional[str] = None
    profession: Optional[str] = None
    other: Optional[str] = None
    by_friend: Optional[bool] = None
    by_member: Optional[bool] = None
    via_whatsapp: Optional[bool] = None
    via_instagram: Optional[bool] = None
    friend_name: Optional[str] = None
    first_time: Optional[bool] = None
    

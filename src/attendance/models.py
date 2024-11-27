import uuid
from datetime import datetime

from database import Base
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship


class EventAttendance(Base):
    __tablename__ = "event_attandance"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(length=320), index=True, nullable=False)
    phone_number = Column(String(length=15))
    first_name = Column(String(length=30))
    last_name = Column(String(length=30))
    location = Column(String(200))
    present = Column(Boolean, default=False)
    occupation = Column(String(200))
    level = Column(String(200))
    school = Column(String(200))
    profession = Column(String(200))
    other = Column(String(200))
    by_friend = Column(Boolean, default=False)
    by_member = Column(Boolean, default=False)
    via_whatsapp = Column(Boolean, default=False)
    via_instagram = Column(Boolean, default=False)
    first_time = Column(Boolean, nullable=True)
    friend_name = Column(String(200))
    event_id = Column(GUID, ForeignKey("events.id"))
    event = relationship("Events", back_populates="attendance")
    createdAt = Column(DateTime, nullable=True, default=datetime.utcnow)
    updatedAt = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )

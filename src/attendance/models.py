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
    event_id = Column(GUID, ForeignKey("events.id"))
    event = relationship("Events")
    createdAt = Column(DateTime, nullable=True, default=datetime.utcnow)
    updatedAt = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )

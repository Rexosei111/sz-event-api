import uuid
from datetime import datetime

from database import Base
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship


class EventImages(Base):
    __tablename__ = "event_images"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID, ForeignKey("events.id"))
    event = relationship("Events", back_populates="images", lazy="selectin")
    url = Column(String(300), nullable=False)
    createdAt = Column(DateTime, nullable=True, default=datetime.utcnow)
    updatedAt = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Events(Base):
    __tablename__ = "events"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(length=100))
    summary = Column(String(length=500))
    description = Column(Text)
    cover_image = Column(String(length=200))
    start_date = Column(DateTime)
    address = Column(String(300))
    longitude = Column(String(40))
    latitude = Column(String(40))
    published = Column(Boolean, default=False)
    images = relationship("EventImages", back_populates="event", lazy="selectin")
    organiser_id = Column(GUID, ForeignKey("organisers.id"))
    organiser = relationship("Organisers", back_populates="events", lazy="selectin")
    attendance = relationship(
        "EventAttendance", back_populates="event", cascade="all, delete-orphan"
    )
    createdAt = Column(DateTime, nullable=True, default=datetime.utcnow)
    updatedAt = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )


from admins.models import Organisers

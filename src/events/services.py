from typing import List, Optional

from events.models import Events
from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils import remove_none

from .models import EventImages
from .schemas import EventCreate
from .schemas import EventImagesCreate as EventImageSchema


async def get_organisation_events(
    session: AsyncSession,
    organiser_id: str,
    query: Optional[str],
):
    try:
        return await paginate(
            conn=session,
            query=select(Events)
            .where(Events.organiser_id == organiser_id)
            .where(Events.name.ilike(f"%{query}%")),
        )
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def create_event_images(
    session: AsyncSession,
    images: List[EventImageSchema],
    event: Optional[Events] = None,
    event_id: Optional[str] = None,
    commit: Optional[bool] = False,
):
    extra_params = remove_none({"event_id": event_id, "event": event})
    for image in images:
        new_image = EventImages(url=image.url, **extra_params)
        session.add(new_image)

    if commit:
        await session.commit()
    return True


async def delete_event_image(
    session: AsyncSession,
    image_ids: List[str],
):
    for id in image_ids:
        db_image = await session.execute(
            select(EventImages).where(EventImages.id == id)
        )
        image = db_image.scalar_one_or_none()
        if image:
            await session.delete(image)
    await session.commit()
    return True


async def create_new_organisation_event(
    session: AsyncSession, data: EventCreate, organiser_id: str
):
    images = data.images
    data_dict = data.model_dump()
    data_dict.pop("images")
    new_event = Events(**data_dict, organiser_id=organiser_id)
    await create_event_images(session=session, images=images, event=new_event)
    session.add(new_event)
    await session.commit()
    return new_event


async def update_organisation_event(
    session: AsyncSession, event_id: str, data: EventCreate, organiser_id: str
):
    data_dict = data.model_dump(exclude_unset=True)
    event = await get_event_by_id(
        session=session, event_id=event_id, organiser_id=organiser_id
    )
    for key, value in data_dict.items():
        setattr(event, key, value)

    await session.commit()
    return event


async def get_event_by_id(session: AsyncSession, event_id: str, organiser_id: str):
    try:
        db_result = await session.execute(
            select(Events).where(
                Events.id == event_id, Events.organiser_id == organiser_id
            )
        )
        event = db_result.scalar_one_or_none()
        if event is None:
            raise HTTPException(404, detail="Event not found")
        return event
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def delete_organiser_event(
    session: AsyncSession, event_id: str, organiser_id: str
):
    event = await get_event_by_id(
        event_id=event_id, organiser_id=organiser_id, session=session
    )
    await session.delete(event)
    await session.commit()
    return True


async def user_get_all_events(
    session: AsyncSession,
    query: Optional[str],
):
    try:
        return await paginate(
            conn=session,
            query=select(Events).where(Events.name.ilike(f"%{query}%")),
        )
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def user_get_event_by_id(session: AsyncSession, event_id: str):
    try:
        db_result = await session.execute(select(Events).where(Events.id == event_id))
        event = db_result.scalar_one_or_none()
        if event is None:
            raise HTTPException(404, detail="Event not found")
        return event
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def get_event_name_by_id(session: AsyncSession, event_id: str):
    try:
        db_result = await session.execute(
            select(Events.name).where(Events.id == event_id)
        )
        event_name = db_result.scalar_one_or_none()
        if event_name is None:
            raise HTTPException(404, detail="Event not found")
        return event_name
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")

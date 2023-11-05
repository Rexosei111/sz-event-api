from typing import List, Optional

from admins.main import get_current_active_user
from admins.models import Admins
from database import get_async_session
from fastapi import Depends, FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.links import Page
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    EventCreate,
    EventImagesCreate,
    EventListingRead,
    EventRead,
    EventUpdate,
)
from .services import (
    create_event_images,
    create_new_organisation_event,
    delete_event_image,
    delete_organiser_event,
    get_event_by_id,
    get_organisation_events,
    update_organisation_event,
)

event_app = FastAPI(title="Event API")


@event_app.get("/mini", response_model=Page[EventListingRead])
async def get_organiser_events_mini(
    query: Optional[str] = "",
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),  # noqa: F821
):
    return await get_organisation_events(
        session=session, organiser_id=admin.organiser_id, query=query
    )


@event_app.get("/", response_model=Page[EventRead])
async def get_organiser_events(
    query: Optional[str] = "",
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),  # noqa: F821
):
    return await get_organisation_events(
        session=session, organiser_id=admin.organiser_id, query=query
    )


@event_app.post("/", response_model=EventRead)
async def create_new_event(
    data: EventCreate,
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),  # noqa: F821
):
    return await create_new_organisation_event(
        session=session, organiser_id=admin.organiser_id, data=data
    )


@event_app.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: str,
    data: EventUpdate,
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),  # noqa: F821
):
    return await update_organisation_event(
        event_id=event_id, session=session, organiser_id=admin.organiser_id, data=data
    )


@event_app.delete("/{event_id}")
async def delete_event(
    event_id: str,
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),
):
    return await delete_organiser_event(
        session=session, organiser_id=admin.organiser_id, event_id=event_id
    )


@event_app.get("/{event_id}", response_model=EventRead)
async def get_event(
    event_id: str,
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),
):
    return await get_event_by_id(
        session=session, organiser_id=admin.organiser_id, event_id=event_id
    )


@event_app.post("/{event_id}")
async def add_new_images_to_event(
    event_id: str,
    images: List[str],
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),
):
    event_images = [EventImagesCreate(url=image) for image in images]
    return await create_event_images(
        session=session, images=event_images, event_id=event_id, commit=True
    )


@event_app.delete("/{event_id}/images")
async def delete_images(
    images: List[str],
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),
):
    return await delete_event_image(session=session, image_ids=images)


add_pagination(event_app)

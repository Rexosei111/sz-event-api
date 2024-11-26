from typing import Annotated, List, Optional, Union

from admins.main import get_current_active_user
from admins.models import Admins
from database import get_async_session
from events.services import get_event_name_by_id
from fastapi import BackgroundTasks, Depends, FastAPI, Query
from fastapi.responses import FileResponse
from fastapi_pagination import add_pagination
from fastapi_pagination.links import Page
from sqlalchemy.ext.asyncio import AsyncSession
from utils import delete_file, send_sms
from fastapi import BackgroundTasks

from .schemas import (
    EventAttendanceCreate,
    EventAttendanceRead,
    EventAttendanceReadWithoutId,
)
from .services import (
    create_attenances,
    delete_attendance,
    get_event_attendances,
    get_event_attendances_download,
    get_event_summary,
    mark_attendance,
)

attendance_app = FastAPI(title="Attendance API")


@attendance_app.get("/{event_id}", response_model=Page[EventAttendanceRead])
async def get_event_attandances(
    event_id: str,
    query: Optional[str] = "",
    present: Optional[bool] = None,
    occupations: Annotated[List[str] | None, Query()] = None,
    invitations: Annotated[List[str] | None, Query()] = None,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await get_event_attendances(
        session=session,
        event_id=event_id,
        query=query,
        present=present,
        occupations=occupations,
        invitations=invitations,
    )


@attendance_app.get(
    "/{event_id}/download",
    response_model=List[EventAttendanceReadWithoutId],
)
async def download_event_attandances(
    *,
    event_id: str,
    query: Optional[str] = "",
    present: Optional[bool] = None,
    occupations: Annotated[List[str] | None, Query()] = None,
    invitations: Annotated[List[str] | None, Query()] = None,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    attendees = await get_event_attendances_download(
        session=session,
        event_id=event_id,
        query=query,
        present=present,
        invitations=invitations,
        occupations=occupations,
    )
    return attendees


@attendance_app.get("/{event_id}/summary")
async def get_event_attandances_summary(
    event_id: str,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await get_event_summary(session=session, event_id=event_id)


@attendance_app.post("/{event_id}")
async def create_event_attendance(
    event_id: str,
    data: EventAttendanceCreate,
    background_tasks: BackgroundTasks,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    attendee = await create_attenances(session=session, event_id=event_id, data=data)
    # background_tasks.add_task(send_sms, phone_numbers=[attendee.phone_number])
    return attendee


@attendance_app.patch("/{event_id}", response_model=EventAttendanceRead)
async def mark_event_attendance(
    event_id: str,
    attendee_id: str,
    present: bool,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await mark_attendance(
        session=session, event_id=event_id, attendance_id=attendee_id, present=present
    )


@attendance_app.delete("/{event_id}")
async def delete_event_attendance(
    event_id: str,
    attendee_id: str,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await delete_attendance(
        session=session, event_id=event_id, attendance_id=attendee_id
    )


add_pagination(attendance_app)

import os
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils import generate_unique_filename

from .models import EventAttendance
from .schemas import EventAttendanceCreate


async def get_event_attendances(
    session: AsyncSession, event_id: str, query: str, present: Optional[bool] = None
):
    statement = (
        select(EventAttendance)
        .where(EventAttendance.event_id == event_id)
        .where(
            or_(
                EventAttendance.email.ilike(f"%{query}%"),
                EventAttendance.first_name.ilike(f"%{query}%"),
                EventAttendance.last_name.ilike(f"%{query}%"),
            ),
        )
    )

    if present is not None:
        statement = statement.where(EventAttendance.present == present)

    try:
        return await paginate(conn=session, query=statement)
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def get_event_attendances_download(
    session: AsyncSession, event_id: str, query: str, present: Optional[bool] = None
):
    statement = (
        select(EventAttendance)
        .where(EventAttendance.event_id == event_id)
        .where(
            or_(
                EventAttendance.email.ilike(f"%{query}%"),
                EventAttendance.first_name.ilike(f"%{query}%"),
                EventAttendance.last_name.ilike(f"%{query}%"),
            ),
        )
    )

    if present is not None:
        statement = statement.where(EventAttendance.present == present)

    try:
        db_results = await session.execute(statement=statement)
        attendees = db_results.scalars().all()
        return attendees
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def get_total_event_attendance(session: AsyncSession, event_id: str):
    try:
        count = await session.scalar(
            select(func.count())
            .select_from(EventAttendance)
            .where(EventAttendance.event_id == event_id)
        )
        return count
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def get_total_present_attendees(
    session: AsyncSession, event_id: str, present: bool
):
    try:
        count = await session.scalar(
            select(func.count())
            .select_from(EventAttendance)
            .where(
                EventAttendance.event_id == event_id, EventAttendance.present == present
            )
        )
        return count
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def get_event_summary(session: AsyncSession, event_id: str, present: bool = True):
    total_attendance = await get_total_event_attendance(
        session=session, event_id=event_id
    )
    total_present = await get_total_present_attendees(
        session=session, event_id=event_id, present=present
    )
    total_absent = await get_total_present_attendees(
        session=session, event_id=event_id, present=False
    )
    return {"total": total_attendance, "present": total_present, "absent": total_absent}


async def get_event_attendance_by_id(
    session: AsyncSession, event_id: str, attendance_id: str
):
    try:
        db_result = await session.execute(
            select(EventAttendance).where(
                EventAttendance.id == attendance_id,
                EventAttendance.event_id == event_id,
            )
        )
        attendance = db_result.scalar_one_or_none()
        if attendance is None:
            raise HTTPException(404, detail="Attendee not found")
        return attendance
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def create_attenances(
    session: AsyncSession, event_id: str, data: EventAttendanceCreate
):
    new_attendance = EventAttendance(**data.model_dump(), event_id=event_id)
    session.add(new_attendance)
    await session.commit()
    return new_attendance


async def delete_attendance(session: AsyncSession, event_id: str, attendance_id: str):
    attendee = await get_event_attendance_by_id(
        event_id=event_id, attendance_id=attendance_id, session=session
    )
    await session.delete(attendee)
    await session.commit()
    return True


async def mark_attendance(
    session: AsyncSession, event_id: str, attendance_id: str, present: bool
):
    attendee = await get_event_attendance_by_id(
        event_id=event_id, attendance_id=attendance_id, session=session
    )
    attendee.present = present
    await session.commit()
    return attendee


ATTENDANCE_ROOT_FOLDER = os.path.join(os.getcwd(), "attendance")


def create_excel_file_with_attendees(
    attendees: List[Dict[str, Any]], event_name: str = ""
):
    df = pd.DataFrame(attendees)
    file_name = generate_unique_filename(f"{event_name}_attendees", 30)
    excel_file = os.path.join(ATTENDANCE_ROOT_FOLDER, f"{file_name}.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    for row in dataframe_to_rows(df, index=False, header=True):
        ws.append(row)

    wb.save(excel_file)
    return excel_file, file_name

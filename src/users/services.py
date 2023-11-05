from datetime import datetime
from typing import Optional

from admins.services import get_organiser_by_id
from attendance.models import EventAttendance
from attendance.schemas import EventAttendanceCreate
from events.models import Events
from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Following, User


async def get_all_events(
    session: AsyncSession,
    query: Optional[str],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    statement = select(Events).filter(
        Events.name.ilike(
            f"%{query}%",
        ),
        Events.published == True,  # noqa: E712
    )
    if start_date and end_date:
        statement = statement.filter(
            Events.start_date >= start_date, Events.start_date <= end_date
        )

    try:
        return await paginate(conn=session, query=statement)
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def get_event_by_id(session: AsyncSession, event_id: str):
    try:
        db_result = await session.execute(select(Events).where(Events.id == event_id))
        event = db_result.scalar_one_or_none()
        if event is None:
            raise HTTPException(404, detail="Event not found")
        return event
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")


async def create_attenances(
    session: AsyncSession, event_id: str, data: EventAttendanceCreate
):
    new_attendance = EventAttendance(**data.model_dump(), event_id=event_id)
    session.add(new_attendance)
    await session.commit()
    return new_attendance


async def create_following(session: AsyncSession, organiser_id: str, user: User):
    new_following = Following(organiser_id=organiser_id, user_id=user.id)
    session.add(new_following)
    await session.flush()
    organiser = await get_organiser_by_id(session=session, organiser_id=organiser_id)
    organiser.followers_count = organiser.followers_count + 1
    user.following_count = user.following_count + 1
    session.add(organiser)
    session.add(user)
    await session.commit()
    return True


async def check_user_following_organiser(
    session: AsyncSession, organiser_id: str, user: User
):
    try:
        count = await session.scalar(
            select(func.count())
            .select_from(Following)
            .where(Following.organiser_id == organiser_id, Following.user_id == user.id)
        )
        return bool(count)
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(500, detail="Something went wrong")


async def get_all_followings(*, session: AsyncSession, query: str = "", user: User):
    statement = select(Following).filter(
        # Following.organiser.name.ilike(
        #     f"%{query}%",
        # ),
        Following.user_id
        == user.id,
    )

    try:
        return await paginate(conn=session, query=statement)
    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")

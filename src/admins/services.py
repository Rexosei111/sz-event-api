from typing import Optional

from config import get_logger
from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Admins, Organisers
from .schemas import AdminsCreate, OrganiserUpdate
from .utils import create_user

logger = get_logger()


async def check_organiser_existence(session: AsyncSession, organiser_id):
    statement = select(Organisers.id).where(Organisers.id == organiser_id)
    try:
        db_results = await session.scalar(statement=statement)
        logger.info(db_results)
        return bool(db_results)
    except SQLAlchemyError:
        logger.error("Unable to check organisation existence", exc_info=True)
        return False


async def get_organiser_by_id(session: AsyncSession, organiser_id):
    statement = select(Organisers).where(Organisers.id == organiser_id)
    try:
        db_results = await session.execute(statement=statement)
        organiser = db_results.scalar_one_or_none()
        if organiser is None:
            raise HTTPException(
                404, detail=f"Organiser with id {organiser_id} not found"
            )
        return organiser
    except SQLAlchemyError:
        logger.error("Unable to check organisation existence", exc_info=True)
        raise HTTPException(404, detail=f"Organiser with id {organiser_id} not found")


async def add_admin_to_organisation(
    session: AsyncSession, user_data: AdminsCreate, organiser_id: str
):
    organiser_exists = await check_organiser_existence(
        session=session, organiser_id=organiser_id
    )
    if organiser_exists:
        admin = await create_user(**user_data.model_dump(), organiser_id=organiser_id)
        if admin is None:
            raise HTTPException(400, detail="User with this email already exist")
        return admin

    else:
        raise HTTPException(404, detail=f"Organiser with id {organiser_id} not found!")


async def update_organiser_data(
    session: AsyncSession, organiser_id: str, data: OrganiserUpdate
):
    organiser = await get_organiser_by_id(session=session, organiser_id=organiser_id)
    for key, value in data.model_dump().items():
        setattr(organiser, key, value)

    await session.commit()
    return organiser


async def organization_admin_count(session: AsyncSession, organiser_id: str):
    try:
        count = await session.scalar(
            select(func.count())
            .select_from(Admins)
            .where(Admins.organiser_id == organiser_id)
        )
        return count
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(500, detail="Something went wrong")


async def get_admin_by_id(session: AsyncSession, admin_id: str):
    try:
        db_result = await session.execute(select(Admins).where(Admins.id == admin_id))
        admin = db_result.scalar_one_or_none()
        if admin is None:
            raise HTTPException(404, detail="Admin not found")
        return admin
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(500, detail="Something went wrong")


async def delete_admin_user_from_organisation(
    session: AsyncSession, organiser_id: str, admin_id: str
):
    admins_count = await organization_admin_count(
        session=session, organiser_id=organiser_id
    )
    if admins_count < 2:
        raise HTTPException(403, detail="You are the only admin")
    admin = await get_admin_by_id(session=session, admin_id=admin_id)
    await session.delete(admin)
    await session.commit()
    return True


async def get_organisation_admins(
    session: AsyncSession, organiser_id: str, admin_id: str, query: Optional[str]
):
    statement = (
        select(Admins)
        .where(Admins.organiser_id == organiser_id)
        .where(Admins.id != admin_id)
        .where(
            or_(
                Admins.first_name.ilike(f"%{query}%"),
                Admins.last_name.ilike(f"%{query}%"),
                Admins.email.ilike(f"{query}%"),
            )
        )
    )
    try:
        return await paginate(conn=session, query=statement)

    except SQLAlchemyError:
        raise HTTPException(500, detail="Something went wrong")

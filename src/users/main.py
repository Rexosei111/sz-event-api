from datetime import datetime
from typing import Optional, Union

from admins.schemas import OrganiserRead
from admins.services import get_organiser_by_id
from attendance.schemas import EventAttendanceCreate, EventAttendanceRead
from config import get_settings
from database import get_async_session
from events.schemas import EventListingRead, EventRead, EventReadWithOrganiser
from fastapi import Depends, FastAPI, HTTPException
from fastapi_pagination import add_pagination
from fastapi_pagination.links import Page
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import (
    FollowingRead,
    UserCreate,
    UserRead,
    UserUpdate,
)
from .services import (
    check_user_following_organiser,
    create_attenances,
    create_following,
    get_all_events,
    get_all_followings,
    get_event_by_id,
)
from .utils import auth_backend, fastapi_users, google_oauth_client

settings = get_settings()
users_app = FastAPI(title="Users API", version="0.1.0")

auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
verify_router = fastapi_users.get_verify_router(UserRead)
# reset_password_router = fastapi_users.get_reset_password_router()
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)

users_router.routes = [route for route in users_router.routes if route.path != "/{id}"]

users_app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
users_app.include_router(register_router, prefix="/auth", tags=["Authentication"])
users_app.include_router(verify_router, prefix="", tags=["Authentication"])
users_app.include_router(users_router, prefix="", tags=["Users"])
users_app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client, auth_backend, settings.jwt_secret, associate_by_email=True
    ),
    prefix="/auth/google",
    tags=["Google Auth"],
)
get_current_active_user = fastapi_users.current_user(active=True, optional=True)


@users_app.get("/events/mini", tags=["Events"], response_model=Page[EventListingRead])
async def get_events_mini(
    query: Optional[str] = "",
    start_date: Optional[Union[datetime, None]] = None,
    end_date: Optional[Union[datetime, None]] = None,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    return await get_all_events(
        session=session, query=query, start_date=start_date, end_date=end_date
    )


@users_app.get("/events", tags=["Events"], response_model=Page[EventRead])
async def get_events(
    query: Optional[str] = "",
    session: AsyncSession = Depends(get_async_session),
    start_date: Optional[Union[datetime, None]] = None,
    end_date: Optional[Union[datetime, None]] = None,
    user: User = Depends(get_current_active_user),
):
    return await get_all_events(
        session=session, query=query, start_date=start_date, end_date=end_date
    )


@users_app.get(
    "/events/{event_id}", response_model=EventReadWithOrganiser, tags=["Events"]
)
async def get_an_event(
    event_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    return await get_event_by_id(session=session, event_id=event_id)


@users_app.get(
    "/events/{event_id}/mini", response_model=EventListingRead, tags=["Events"]
)
async def get_an_event_mini(
    event_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    return await get_event_by_id(session=session, event_id=event_id)


@users_app.post(
    "/event/{event_id}", response_model=EventAttendanceRead, tags=["Attendance"]
)
async def rsvp_an_event(
    event_id: str,
    data: Optional[EventAttendanceCreate] = None,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    if data is None and user is None:
        try:
            val = EventAttendanceCreate()
        except ValidationError as e:
            raise HTTPException(400, detail=e.errors())
    if data is not None:
        pass
    if data is None and user is not None:
        data = EventAttendanceCreate(**user.__dict__)
    return await create_attenances(session=session, event_id=event_id, data=data)


@users_app.get(
    "/organisers/{organiser_id}", response_model=OrganiserRead, tags=["Organisers"]
)
async def get_an_organiser(
    organiser_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    return await get_organiser_by_id(session=session, organiser_id=organiser_id)


@users_app.post("/me/following/{organiser_id}", tags=["Organisers"])
async def follow_organiser(
    organiser_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    if user is None:
        raise HTTPException(401)
    return await create_following(session=session, organiser_id=organiser_id, user=user)


@users_app.get("/me/following/{organiser_id}", tags=["Organisers"])
async def check_following(
    organiser_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    if user is None:
        raise HTTPException(401)
    return await check_user_following_organiser(
        session=session, organiser_id=organiser_id, user=user
    )


@users_app.get("/me/following", tags=["Organisers"], response_model=Page[FollowingRead])
async def get_my_following(
    query: Optional[str] = "",
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_active_user),
):
    if user is None:
        raise HTTPException(401)
    return await get_all_followings(session=session, query=query, user=user)


add_pagination(users_app)

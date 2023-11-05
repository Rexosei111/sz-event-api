from typing import List, Optional

from database import get_async_session
from fastapi import Depends, FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.links import Page
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Admins
from .schemas import (
    AdminsCreate,
    AdminsRead,
    AdminsUpdate,
    OrganiserRead,
    OrganiserUpdate,
)
from .services import (
    add_admin_to_organisation,
    delete_admin_user_from_organisation,
    get_organisation_admins,
    get_organiser_by_id,
    update_organiser_data,
)
from .utils import auth_backend, fastapi_users

admins_app = FastAPI(title="Admins API", version="0.1.0")

auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(AdminsRead, AdminsCreate)
verify_router = fastapi_users.get_verify_router(AdminsRead)
# reset_password_router = fastapi_users.get_reset_password_router()
users_router = fastapi_users.get_users_router(AdminsRead, AdminsUpdate)

# users_router.routes = [route for route in users_router.routes if route.path != "/{id}"]

admins_app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
admins_app.include_router(register_router, prefix="/auth", tags=["Authentication"])
admins_app.include_router(verify_router, prefix="", tags=["Authentication"])
admins_app.include_router(users_router, prefix="", tags=["Admin"])
get_current_active_user = fastapi_users.current_user(active=True, verified=True)


@admins_app.post("/new-admin", tags=["Organisation"], response_model=AdminsRead)
async def add_new_admin_to_organisation(
    data: AdminsCreate,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    user = await add_admin_to_organisation(
        session=session, user_data=data, organiser_id=admin.organiser_id
    )
    return user


@admins_app.delete("/admin/delete-admin", tags=["Organisation"])
async def delete_organisation_admin(
    admin_id: str,
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await delete_admin_user_from_organisation(
        session=session, organiser_id=admin.organiser_id, admin_id=admin_id
    )


@admins_app.get("/admin/admins", tags=["Organisation"], response_model=Page[AdminsRead])
async def get_all_organisation_admins(
    query: Optional[str] = "",
    admin: Admins = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await get_organisation_admins(
        session=session, organiser_id=admin.organiser_id, admin_id=admin.id, query=query
    )


@admins_app.patch(
    "/admin/organiser", response_model=OrganiserRead, tags=["Organisation"]
)
async def update_organiser_information(
    data: OrganiserUpdate,
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),
):
    organiser = await update_organiser_data(
        session=session, data=data, organiser_id=admin.organiser_id
    )
    return organiser


@admins_app.get("/admin/organiser", response_model=OrganiserRead, tags=["Organisation"])
async def get_organiser_profile(
    session: AsyncSession = Depends(get_async_session),
    admin: Admins = Depends(get_current_active_user),
):
    print(admin.organiser_id)
    organiser = await get_organiser_by_id(
        session=session, organiser_id=admin.organiser_id
    )
    return organiser


add_pagination(admins_app)

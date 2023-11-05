from contextlib import asynccontextmanager

import uvicorn
from admins.main import admins_app
from attendance.main import attendance_app
from database import create_db_tables, delete_db_tables
from events.main import event_app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from mangum import Mangum
from users.main import users_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield
    # await delete_db_tables()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/users/", users_app)
app.mount("/admins/", admins_app)
app.mount("/events/", event_app)
app.mount("/attendance/", attendance_app)


add_pagination(app)

handler = Mangum(app=app)
if __name__ == "__main__":
    uvicorn.run(
        app="main:app", log_level="debug", reload=True, host="127.0.0.1", port=8000
    )

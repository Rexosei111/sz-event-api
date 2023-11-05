from typing import AsyncGenerator

from config import get_logger, get_settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

settings = get_settings()
logger = get_logger()
engine = create_async_engine(settings.db_url, future=True, echo=False)

async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=True
)


class Base(DeclarativeBase):
    pass


async def create_db_tables(**kwargs):
    async with engine.begin() as conn:
        logger.info("Creating database tables")
        await conn.run_sync(Base.metadata.create_all, **kwargs)


async def delete_db_tables(**kwargs):
    async with engine.begin() as conn:
        logger.warning("Deleting database tables")
        await conn.run_sync(Base.metadata.drop_all, **kwargs)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

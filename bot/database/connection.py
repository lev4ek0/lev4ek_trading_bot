from typing import AsyncGenerator

from settings import SQLALCHEMY_ORM_CONFIG
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(**SQLALCHEMY_ORM_CONFIG)
async_session_maker = async_sessionmaker(bind=engine)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    pass

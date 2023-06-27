from settings import SQLALCHEMY_ORM_CONFIG
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(**SQLALCHEMY_ORM_CONFIG)

Session = async_sessionmaker(bind=engine)


async def get_db_session():
    db = Session()
    try:
        yield db
    finally:
        await db.close()


class Base(AsyncAttrs, DeclarativeBase):
    pass

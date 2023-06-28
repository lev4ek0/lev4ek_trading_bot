from settings import SQLALCHEMY_ORM_CONFIG
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine, AsyncConnection,
)
from sqlalchemy.orm import DeclarativeBase


class PostgresConnection:
    def __init__(self):
        self.connection: AsyncConnection
        self.engine = None

    async def connect(self):
        self.engine = create_async_engine(**SQLALCHEMY_ORM_CONFIG)
        async_session_maker = async_sessionmaker(bind=self.engine)
        self.connection = async_session_maker()

    async def select(self, stmt):
        return await self.connection.execute(stmt)

    async def execute(self, *stmts):
        try:
            for stmt in stmts:
                await self.connection.execute(stmt)
            await self.connection.commit()
        except Exception as e:
            await self.connection.rollback()
            raise e

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


postgres_connection = PostgresConnection()


class Base(AsyncAttrs, DeclarativeBase):
    pass

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession


class SessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = await anext(get_db_session())
        data["session"] = session
        return await handler(event, data)

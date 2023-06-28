from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware, types
from aiogram.types import Message
from database import Chat, History, User
from sqlalchemy import insert, select


class UserMiddleware(BaseMiddleware):
    async def setup_chat(self, user: types.User, chat: Optional[types.Chat] = None):
        user_id = user.id
        full_name = user.full_name
        chat_id = chat.id if chat else user.id
        chat_type = chat.type if chat else "private"
        ans = await self.session.select(
            select(User).where(User.telegram_id == user_id)
        )
        if not ans.scalars().first():
            insert_user = insert(User).values(telegram_id=user_id, full_name=full_name)
            await self.session.execute(insert_user)
        ans = await self.session.select(select(Chat).where(Chat.id == chat_id))
        if not ans.scalars().first():
            insert_chat = insert(Chat).values(id=chat_id, type=chat_type)
            await self.session.execute(insert_chat)

        return user_id, chat_id

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        self.session = data["session"]
        chat = event.chat if event else None
        user_id, chat_id = await self.setup_chat(event.from_user, chat)
        insert_history = insert(History).values(
            chat_id=chat_id, user_id=user_id, command=event.text
        )
        await self.session.execute(insert_history)
        return await handler(event, data)

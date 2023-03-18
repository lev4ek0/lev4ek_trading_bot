from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from models.base import Chat, User


class ACLMiddleware(BaseMiddleware):
    async def setup_chat(
        self, data: dict, user: types.User, chat: Optional[types.Chat] = None
    ):
        user_id = user.id
        full_name = user.full_name
        chat_id = chat.id if chat else user.id
        chat_type = chat.type if chat else "private"

        user = await User.get_or_none(id=user_id)
        if user is None:
            user = await User.create(id=user_id, full_name=full_name)
        chat = await Chat.get_or_none(id=chat_id)
        if chat is None:
            chat = await Chat.create(id=chat_id, type=chat_type)

        data["user"] = user
        data["chat"] = chat

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(
        self, query: types.CallbackQuery, data: dict
    ):
        chat = query.message.chat if query.message else None
        await self.setup_chat(data, query.from_user, chat)

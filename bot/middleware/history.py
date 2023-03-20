from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from models.base import History


class HistoryMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.is_command():
            await History.create(
                command=message.text, user_id=message.from_user, chat_id=message.chat
            )

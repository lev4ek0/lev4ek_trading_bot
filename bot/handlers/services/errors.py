from typing import Union

from aiogram import types
from aiogram.types import Message


def handle_errors(func):
    async def wrapper(message_or_call: Union[Message, types.CallbackQuery], *args):
        try:
            await func(message_or_call, *args)
        except Exception as e:
            if hasattr(message_or_call, 'answer'):
                await message_or_call.answer(str(e) or "Что-то пошло не так")
            else:
                await message_or_call.message.answer(str(e) or "Что-то пошло не так")
    return wrapper

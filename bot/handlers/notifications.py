from aiogram import types, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from models.models import User


async def enable_notifications(message: types.Message, apscheduler: AsyncIOScheduler):
    user = await User.get(id=message.from_user.id)
    user.is_notifications = True
    await user.save()

    await message.answer(text="Уведомления успешно включены")


async def disable_notifications(message: types.Message):
    user = await User.get(id=message.from_user.id)
    user.is_notifications = False
    await user.save()

    await message.answer(text="Уведомления успешно выключены")


def register_notifications_handlers(dp: Dispatcher):
    dp.register_message_handler(
        enable_notifications, commands=["enable_notifications"], state="*"
    )
    dp.register_message_handler(
        disable_notifications, commands=["disable_notifications"], state="*"
    )

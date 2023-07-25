from aiogram import types
from aiogram.filters import Command
from handlers import create_router

router = create_router()


@router.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    text = (
        "Это бот для трейдинга, но еще у меня есть подписка "
        "на уведомления о поступлении. Чтобы воспользоваться, "
        "нужно написать /add_speciality\n\n"
        "Доступные команды:\n\n"
        "/help\n"
        "/add_broker\n"
        "/remove_broker\n"
        "/manage_notifications\n"
        "/shares\n"
        "/add_speciality\n"
        "/remove_speciality\n"
    )
    await message.answer(text=text)

from aiogram import types
from aiogram.filters import Command
from handlers.common import create_router

router = create_router()


@router.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    text = (
        "Доступные команды:\n\n"
        "/help\n"
        "/add_broker\n"
        # "/accounts\n"
        # "/enable_notifications\n"
        # "/disable_notifications\n"
        # "/instruments\n"
        # "/add_instrument\n"
        # "/remove_instrument\n"
        # "/recalculate_proportion\n"
        "/shares\n"
        # "/error\n"
    )
    await message.answer(text=text)

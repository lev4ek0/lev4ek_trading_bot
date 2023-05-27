from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from prettytable import PrettyTable

from handlers.services.instruments import get_shares_table, build_shares_table
from models.models import User
from robot.trading_robot import Robot


async def start(message: types.Message):
    text = (
        "Доступные команды:\n\n"
        "/help\n"
        "/add_broker\n"
        "/accounts\n"
        "/enable_notifications\n"
        "/disable_notifications\n"
        "/instruments\n"
        "/add_instrument\n"
        "/remove_instrument\n"
        "/recalculate_proportion\n"
        "/shares\n"
        "/error\n"
    )
    await message.answer(text=text)


async def my_shares(message: types.Message):
    total, shares_output = await get_shares_table(message.from_user.id)
    text = build_shares_table(total, shares_output)

    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
    )


async def my_error(message: types.Message):
    user = await User.get(id=message.from_user.id)
    robot = await Robot.create(
        token=user.tinkoff_api_key,
        account_id=user.tinkoff_account_id,
        user_id=message.from_user.id,
    )
    errors = robot.get_current_error()
    robot.client.close()

    table = PrettyTable(["Name", "Deviation"])
    table.align["Name"] = "l"
    for name, error in errors.items():
        table.add_row([name, f"{error * 100:.2f}"])

    await message.answer(
        text=f"<pre>{table}</pre>",
        parse_mode=ParseMode.HTML,
    )


def register_main_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start", "help"], state="*")
    dp.register_message_handler(my_shares, commands=["shares"], state="*")
    dp.register_message_handler(my_error, commands=["error"], state="*")

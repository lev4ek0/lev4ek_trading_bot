from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from prettytable import PrettyTable

from robot.trading_robot import Robot


async def start(message: types.Message):
    text = (
        "Доступные команды:\n"
        "/help\n"
        "/instruments\n"
        "/shares\n"
        "/error\n"
        "/add_instrument\n"
        "/remove_instrument\n"
    )
    await message.answer(text=text)


async def handle_shares(message: types.Message):
    robot = await Robot.create()
    shares = robot.get_shares()
    total = robot.get_total()
    text = f"Всего: {total}\n\n"
    table = PrettyTable(["Name", "Money", "%"])
    table.align["Name"] = "l"
    for share in sorted(shares.items(), key=lambda x: x[1], reverse=True):
        table.add_row([share[0][:10], share[1], f"{share[1] / total * 100:.2f}"])

    await message.answer(
        text=text + f"<pre>{table}</pre>",
        parse_mode=ParseMode.HTML,
    )


async def handle_error(message: types.Message):
    robot = await Robot.create()
    errors = robot.get_current_error()

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
    dp.register_message_handler(handle_shares, commands=["shares"], state="*")
    dp.register_message_handler(handle_error, commands=["error"], state="*")

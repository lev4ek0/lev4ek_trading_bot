from aiogram import types, Dispatcher

from robot.trading_robot import Robot


async def start(message: types.Message):
    text = "Доступные команды:\n" "/shares\n" "/error\n" "/add_instrument\n"
    await message.answer(text=text)


async def handle_shares(message: types.Message):
    robot = Robot()
    shares = robot.get_shares()
    total = robot.get_total()
    text = f"Всего: {total}\n\n"
    text += "\n".join(
        map(
            lambda x: f"{x[0]}: {x[1]}, {round(x[1] / total * 100)}%",
            sorted(shares.items(), key=lambda x: x[1], reverse=True),
        )
    )
    await message.answer(text=text)


async def handle_error(message: types.Message):
    robot = Robot()
    error = robot.get_current_error()

    await message.answer(text=f"Среднее отклонение акций от плана - {round(error * 100)}%")


def register_main_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(handle_shares, commands=["shares"], state="*")
    dp.register_message_handler(handle_error, commands=["error"], state="*")

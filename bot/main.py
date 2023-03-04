import logging

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook

from models.db import db
from settings import tortoise_orm_settings
from robot.trading_robot import Robot
from settings import bot_settings

TOKEN = bot_settings.TOKEN.get_secret_value()

# webhook settings
WEBHOOK_URL = bot_settings.WEBHOOK_URL

# webserver settings
WEBAPP_HOST = "bot"  # or ip
WEBAPP_PORT = 3001

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    text = "Доступные команды:\n" "/shares\n" "/error\n"
    await bot.send_message(message.chat.id, text=text)


@dp.message_handler(commands=["shares"])
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
    await bot.send_message(message.chat.id, text=text)


@dp.message_handler(commands=["error"])
async def handle_error(message: types.Message):
    robot = Robot()
    error = robot.get_current_error()

    await bot.send_message(
        message.chat.id, text=f"Среднее отклонение акций от плана - {round(error * 100)}%"
    )


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    await db.init(config=tortoise_orm_settings)


async def on_shutdown(dp):
    await db.close_connections()
    logging.warning("Shutting down..")

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning("Bye!")


if __name__ == "__main__":
    if bot_settings.IS_POLLING:
        executor.start_polling(dp)
    else:
        start_webhook(
            dispatcher=dp,
            webhook_path=bot_settings.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )

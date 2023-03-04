import logging

from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook
from tortoise import run_async

from handlers import register_handlers
from models.db import db
from settings import TORTOISE_ORM_CONFIG
from settings import bot_settings
from settings import redis_settings

TOKEN = bot_settings.TOKEN.get_secret_value()


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = RedisStorage2(
    host=redis_settings.REDIS_HOST,
    port=redis_settings.REDIS_PORT,
)

dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


async def init_db():
    await db.init(config=TORTOISE_ORM_CONFIG)


async def on_startup(dp):
    await bot.set_webhook(bot_settings.WEBHOOK_URL)
    await init_db()


async def on_shutdown(dp):
    logging.warning("Shutting down..")

    await bot.delete_webhook()
    await db.close_connections()
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning("Bye!")


if __name__ == "__main__":
    register_handlers(dp)
    if bot_settings.IS_POLLING:
        run_async(init_db())
        executor.start_polling(dp)
    else:
        start_webhook(
            dispatcher=dp,
            webhook_path=bot_settings.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=bot_settings.WEBAPP_HOST,
            port=bot_settings.WEBAPP_PORT,
        )

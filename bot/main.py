import logging

from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tortoise import run_async

from handlers import register_handlers
from handlers.services.instruments import get_shares_table
from middleware import setup_middleware
from models.db import db
from models.models import User
from settings import TORTOISE_ORM_CONFIG
from settings import bot_settings
from settings import redis_settings
from tasks.share_changes import share_changes_task

TOKEN = bot_settings.TOKEN.get_secret_value()


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = RedisStorage2(
    host=redis_settings.REDIS_HOST,
    port=redis_settings.REDIS_PORT,
)

dp = Dispatcher(bot, storage=storage)

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
scheduler.start()

setup_middleware(dp, scheduler)


async def init_db():
    await db.init(config=TORTOISE_ORM_CONFIG)


async def on_startup(dp, is_polling=False):
    await init_db()

    users = await User.filter(is_notifications=True)
    for user in users:
        if user.can_trade:
            print(2)
            total, shares_output = await get_shares_table(user.id)
            scheduler.add_job(
                share_changes_task,
                trigger="interval",
                seconds=60,
                kwargs={
                    "bot": bot,
                    "total": [total],
                    "shares_output": [shares_output],
                    "user_id": user.id,
                },
            )

    if not is_polling:
        await bot.set_webhook(bot_settings.WEBHOOK_URL)


async def on_shutdown(dp):
    logging.warning("Shutting down..")

    await bot.delete_webhook()
    await db.close_connections()
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning("Bye!")


if __name__ == "__main__":
    register_handlers(dp)
    if is_polling := bot_settings.IS_POLLING:
        run_async(on_startup(dp, is_polling))
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

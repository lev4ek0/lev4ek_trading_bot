import asyncio
import logging
from collections import defaultdict

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import postgres_connection
from handlers import broker_router, shares_router, start_router, notifications_router
from settings import bot_settings
from tasks.periodic import share_changes_task

TOKEN = bot_settings.TOKEN.get_secret_value()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def on_startup():
    await postgres_connection.connect()
    await postgres_connection.create_all()

    scheduler.add_job(
        share_changes_task,
        trigger="interval",
        seconds=60,
        kwargs={
            "bot": bot,
            "map_accounts_money": defaultdict(int),
        },
    )

    scheduler.start()


async def main():
    if is_polling := bot_settings.IS_POLLING:
        await on_startup()
        await dp.start_polling(bot)
    # todo: webhooks


if __name__ == "__main__":
    dp.include_routers(start_router, broker_router, shares_router, notifications_router)
    asyncio.run(main())

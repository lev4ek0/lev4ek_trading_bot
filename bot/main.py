import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from database import postgres_connection, redis_connection
from handlers import broker_router, notifications_router, shares_router, start_router
from settings import bot_settings, redis_settings
from tasks import share_changes_task, store_data


async def on_startup(scheduler):
    await postgres_connection.connect()
    await postgres_connection.create_all()

    redis_connection.connect()

    scheduler.add_job(
        share_changes_task,
        trigger="cron",
        minute="*",
        replace_existing=True,
        id="share_changes_task",
    )

    scheduler.add_job(
        store_data,
        trigger="cron",
        minute=54,
        hour=23,
        replace_existing=True,
        id="store_data",
    )

    scheduler.start()


async def main():
    TOKEN = bot_settings.TOKEN.get_secret_value()

    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    storage = RedisStorage.from_url(
        f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/0"
    )
    dp = Dispatcher(storage=storage)
    dp.include_routers(start_router, broker_router, shares_router, notifications_router)
    jobstores = {
        "default": RedisJobStore(
            jobs_key="dispatched_trips_jobs",
            run_times_key="dispatched_trips_running",
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            db=1,
        )
    }
    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(timezone="Europe/Moscow", jobstores=jobstores)
    )
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    if is_polling := bot_settings.IS_POLLING:
        await on_startup(scheduler)
        await dp.start_polling(bot)
    # todo: webhooks


if __name__ == "__main__":
    asyncio.run(main())

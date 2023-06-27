import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import Account, Base, engine
from handlers import broker_router, shares_router, start_router
from settings import bot_settings
from sqlalchemy import select
from tasks.periodic import share_changes_task
from utils.broker_client import get_broker_client

TOKEN = bot_settings.TOKEN.get_secret_value()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(start_router, broker_router, shares_router)

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        select_accounts = select(Account).filter()
        accounts = await conn.execute(select_accounts)
        for account in accounts.all():
            broker_client = get_broker_client(account)
            broker_account = await broker_client.show_account()
            scheduler.add_job(
                share_changes_task,
                trigger="interval",
                seconds=10,
                kwargs={
                    "bot": bot,
                    "total": [broker_account.balance],
                    "account": account,
                },
            )

    scheduler.start()


async def main():
    if is_polling := bot_settings.IS_POLLING:
        await on_startup()
        await dp.start_polling(bot)
    # todo: webhooks


if __name__ == "__main__":
    asyncio.run(main())

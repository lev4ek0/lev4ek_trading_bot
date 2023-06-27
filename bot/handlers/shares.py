from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from brokers import BrokerClient
from brokers.common import BaseClient
from database import Account
from handlers import create_router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_broker_class
from utils.broker_client import get_broker_client

router = create_router()


@router.message(Command("shares"))
async def shares(message: types.Message, session: AsyncSession):
    select_accounts = select(Account).where(Account.user_id == message.from_user.id)
    accounts = list((await session.execute(select_accounts)).scalars())
    if not accounts:
        await message.answer(
            text="Воспользуйтесь командой /add_broker, чтобы привязать брокера к аккаунту",
        )
    for account in accounts:
        broker_client = get_broker_client(account)
        broker_account = await broker_client.show_account()
        await message.answer(
            text=str(broker_account),
            parse_mode=ParseMode.HTML,
        )

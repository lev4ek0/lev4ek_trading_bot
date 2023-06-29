from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from database import Account, BrokerType
from database.connection import PostgresConnection
from handlers.common import create_router
from handlers.states import BrokerAddState, BrokerRemoveState
from sqlalchemy import delete, insert, select
from utils import get_broker_client

router = create_router()


@router.message(Command("remove_broker"))
async def remove_broker(
    message: types.Message, state: FSMContext, session: PostgresConnection
):
    select_accounts = select(Account).where(Account.user_id == message.from_user.id)
    accounts = await session.select(select_accounts)
    accounts_list, accounts_mapper = [], {}
    accounts = list(accounts.scalars())
    for account in accounts:
        broker_client = get_broker_client(
            account.broker_type.value.capitalize(), account.api_key
        )
        broker_account = await broker_client.show_account(account.broker_account_id)
        button = InlineKeyboardButton(
            text=f"{broker_account.name} ({broker_account.balance})"
        )
        accounts_mapper[
            f"{broker_account.name} ({broker_account.balance})"
        ] = account.broker_account_id
        accounts_list.append([button])
    if not accounts:
        return await message.answer(
            text="У вас нет аккаунтов брокеров. Чтобы его добавить, введите /add_broker",
        )
    await state.update_data(accounts_mapper=accounts_mapper)
    accounts_kb = ReplyKeyboardMarkup(
        keyboard=accounts_list, resize_keyboard=True, one_time_keyboard=True
    )
    await state.set_state(BrokerRemoveState.broker)

    await message.answer(
        text="Выберите брокера",
        reply_markup=accounts_kb,
    )


@router.message(BrokerRemoveState.broker)
async def remove_broker_finish(
    message: types.Message, state: FSMContext, session: PostgresConnection
):
    data = await state.get_data()
    accounts_mapper = data.get("accounts_mapper")
    account_id = accounts_mapper[message.text]
    delete_account = delete(Account).where(Account.broker_account_id == account_id)
    await session.execute(delete_account)
    await state.clear()
    await message.answer(
        text="Аккаунт успешно удален", reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("add_broker"))
async def add_broker(message: types.Message, state: FSMContext):
    brokers_list = []
    for broker in ["Tinkoff"]:
        button = InlineKeyboardButton(text=broker)
        brokers_list.append([button])
    brokers_kb = ReplyKeyboardMarkup(
        keyboard=brokers_list, resize_keyboard=True, one_time_keyboard=True
    )

    await state.set_state(BrokerAddState.broker)
    await message.answer(
        text="Выберите брокера",
        reply_markup=brokers_kb,
    )


@router.message(BrokerAddState.broker)
async def choose_broker(message: types.Message, state: FSMContext):
    await state.update_data(broker=message.text)
    await state.set_state(BrokerAddState.token)
    await message.answer(
        text="Введите токен вашего брокера. Чтобы его получить, перейдите по ссылке https://www.tinkoff.ru/invest/settings/api/ , затем выпустите токен с полным доступом",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(BrokerAddState.token)
async def add_broker_token(message: types.Message, state: FSMContext):
    await state.update_data(token=message.text)
    await state.set_state(BrokerAddState.account)
    data = await state.get_data()
    broker_name = data.get("broker")
    broker_client = get_broker_client(broker_name, message.text)
    accounts = await broker_client.accounts_list()
    accounts_list, accounts_mapper = [], {}
    #  todo: show only accounts that aren't connected yet
    for account in accounts:
        accounts_mapper[account.name] = account.account_id
        button = InlineKeyboardButton(text=account.name)
        accounts_list.append([button])
    await state.update_data(accounts_mapper=accounts_mapper)
    accounts_kb = ReplyKeyboardMarkup(
        keyboard=accounts_list, resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer(
        text="Выберите аккаунт вашего брокера",
        reply_markup=accounts_kb,
    )


@router.message(BrokerAddState.account)
async def add_broker_finish(
    message: types.Message, state: FSMContext, session: PostgresConnection
):
    data = await state.get_data()
    broker = data.get("broker")
    token = data.get("token")
    accounts_mapper = data.get("accounts_mapper")
    user_id = message.from_user.id
    insert_account = insert(Account).values(
        user_id=user_id,
        broker_type=BrokerType(broker.lower()).name,
        api_key=token,
        broker_account_id=accounts_mapper.get(message.text) or "0",
    )
    await state.clear()
    await session.execute(insert_account)
    await message.answer(
        text=f"Аккаунт '{message.text}' был успешно добавлен",
        reply_markup=ReplyKeyboardRemove(),
    )

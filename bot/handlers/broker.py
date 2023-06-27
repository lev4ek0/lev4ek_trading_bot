from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup
from database import Account, BrokerType
from handlers.common import create_router
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

router = create_router()


class BrokerState(StatesGroup):
    broker = State()
    token = State()
    account = State()


@router.message(Command("add_broker"))
async def add_broker(message: types.Message, state: FSMContext):
    brokers_list = []
    for broker in ["Tinkoff"]:
        button = InlineKeyboardButton(text=broker)
        brokers_list.append([button])
    brokers_list = ReplyKeyboardMarkup(
        keyboard=brokers_list, resize_keyboard=True, one_time_keyboard=True
    )

    await state.set_state(BrokerState.broker)
    await message.answer(
        text="Выберите брокера",
        reply_markup=brokers_list,
    )


@router.message(BrokerState.broker)
async def choose_broker(message: types.Message, state: FSMContext):
    await state.update_data(broker=message.text)
    await state.set_state(BrokerState.token)
    await message.answer(
        text="Введите токен вашего брокера",
    )


@router.message(BrokerState.token)
async def add_broker_token(message: types.Message, state: FSMContext):
    await state.update_data(token=message.text)
    await state.set_state(BrokerState.account)
    await message.answer(
        text="Введите id аккаунта вашего брокера",
    )


@router.message(BrokerState.account)
async def add_broker_finish(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    broker = data.get("broker")
    token = data.get("token")
    user_id = message.from_user.id
    insert_account = insert(Account).values(
        user_id=user_id,
        broker_type=BrokerType(broker.lower()).name,
        api_key=token,
        broker_account_id=message.text,
    )
    await session.execute(insert_account)
    await session.commit()
    await state.clear()
    await message.answer(text=f"Аккаунт '{message.text}' был успешно добавлен")

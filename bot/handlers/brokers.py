from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from models.models import User
from states import BrokerState


async def add_broker(message: types.Message):
    brokers_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for broker in ["Tinkoff"]:
        button = InlineKeyboardButton(broker)
        brokers_list.add(button)
    await BrokerState.broker.set()
    await message.answer(
        text="Выберите брокера",
        reply_markup=brokers_list,
    )


async def all_accounts(message: types.Message):
    user = await User.get(id=message.from_user.id)
    text = f"Уведомления {'включены' if user.is_notifications else 'выключены'}\n\n"
    text += "\n".join(
        f"{broker}: {accounts}" for broker, accounts in user.accounts.items()
    )
    await message.answer(
        text=text or "Чтобы добавить аккаунт используйте команду /add_broker",
    )


async def choose_broker(message: types.Message, state: FSMContext):
    await state.update_data(broker=message.text)
    await BrokerState.token.set()
    await message.answer(
        text="Введите токен вашего брокера",
    )


async def add_broker_token(message: types.Message, state: FSMContext):
    await state.update_data(token=message.text)
    await BrokerState.account.set()
    await message.answer(
        text="Введите id аккаунта вашего брокера",
    )


async def add_broker_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    broker = data.get("broker")
    token = data.get("token")
    user = await User.get(id=message.from_user.id)
    setattr(user, f"{broker.lower()}_account_id", message.text)
    setattr(user, f"{broker.lower()}_api_key", token)
    await user.save()
    await state.finish()
    await message.answer(text=f"Аккаунт '{message.text}' был успешно добавлен")


def register_brokers_handlers(dp: Dispatcher):
    dp.register_message_handler(add_broker, commands=["add_broker"], state="*")
    dp.register_message_handler(all_accounts, commands=["accounts"], state="*")
    dp.register_message_handler(choose_broker, state=BrokerState.broker)
    dp.register_message_handler(add_broker_token, state=BrokerState.token)
    dp.register_message_handler(add_broker_finish, state=BrokerState.account)

from aiogram import types
from aiogram.filters import Command, Text

from database import Account
from database.connection import PostgresConnection
from handlers import create_router
from sqlalchemy import select, update
from utils.broker_client import get_broker_client

router = create_router()


async def build_kb(user_id, session):
    select_accounts = (
        select(Account).where(Account.user_id == user_id).order_by(Account.id)
    )
    accounts = list((await session.select(select_accounts)).scalars())
    buttons = []
    for account in accounts:
        broker_client = get_broker_client(
            account.broker_type.value.capitalize(), account.api_key
        )
        broker_account = await broker_client.show_account(account.broker_account_id)
        button = types.InlineKeyboardButton(
            text=("on" if account.is_notifications else "off")
            + f" {broker_account.name} ({broker_account.balance})",
            callback_data=("turn-off" if account.is_notifications else "turn-on")
            + f"_{account.id}",
        )
        buttons.append([button])
    buttons.append(
        [
            types.InlineKeyboardButton(
                text="Подтвердить",
                callback_data="exit",
            )
        ]
    )
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return keyboard


@router.message(Command("manage_notifications"))
async def shares(message: types.Message, session: PostgresConnection):
    keyboard = await build_kb(message.from_user.id, session)
    if len(keyboard.inline_keyboard) < 2:
        return await message.answer(
            text="Воспользуйтесь командой /add_broker, чтобы привязать брокера к аккаунту",
        )
    await message.answer("Нажмите на нужную кнопку", reply_markup=keyboard)


@router.callback_query(Text(startswith="turn"))
async def turn_off_notifications(
    callback: types.CallbackQuery, session: PostgresConnection
):
    account_id = callback.data.split("_")[1]
    update_account = (
        update(Account)
        .where(Account.id == int(account_id))
        .values(is_notifications=callback.data.startswith("turn-on"))
    )
    await session.execute(update_account)
    await callback.message.edit_reply_markup(
        reply_markup=await build_kb(callback.from_user.id, session)
    )
    await callback.answer()


@router.callback_query(Text("exit"))
async def exit_notifications(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

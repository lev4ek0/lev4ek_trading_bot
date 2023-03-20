from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ParseMode,
)
from aiogram.utils.callback_data import CallbackData
from prettytable import PrettyTable
from pydantic import ValidationError
from tortoise.functions import Sum

from handlers.services.errors import handle_errors
from models.models import Share, User
from robot.trading_robot import Robot
from states import InstrumentState

instrument_data = CallbackData("instrument", "name", "figi")


@handle_errors
async def add_instrument(message: types.Message):
    await InstrumentState.name.set()
    await message.answer(text="Введите название инструмента")


@handle_errors
async def remove_instrument(message: types.Message):
    instrument_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    instruments = await Share.filter(user_id=message.from_user.id).order_by(
        "-proportion"
    )
    for instrument in instruments:
        button = InlineKeyboardButton(instrument.name)
        instrument_list.add(button)
    await InstrumentState.remove.set()
    await message.answer(
        text="Выберите подходящий инструмент", reply_markup=instrument_list
    )


@handle_errors
async def all_instruments(message: types.Message):
    instruments = await Share.filter(user_id=message.from_user.id).order_by(
        "-proportion"
    )
    table = PrettyTable(["Name", "%"])
    table.align["Name"] = "l"
    total_percent = 0
    for instrument in instruments:
        table.add_row([instrument.name, f"{instrument.proportion * 100:.2f}"])
        total_percent += instrument.proportion
    await message.answer(
        text=f"Список всех инструментов, общий процент - {round(total_percent * 100, 2):.2f}:\n\n"
        + f"<pre>{table}</pre>",
        parse_mode=ParseMode.HTML,
    )


@handle_errors
async def add_instrument_name(message: types.Message, state: FSMContext):
    user = await User.get(id=message.from_user.id)
    robot = await Robot.create(
        token=user.tinkoff_api_key,
        account_id=user.tinkoff_account_id,
        user_id=message.from_user.id,
    )
    instruments = robot.find_instrument(message.text)
    robot.client.close()
    instrument_list = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for instrument in instruments:
        button = InlineKeyboardButton(
            instrument.name,
            callback_data=instrument_data.new(
                name=instrument.name[:20], figi=instrument.figi
            ),
        )
        instrument_list.add(button)
    await InstrumentState.choose.set()
    await message.answer(
        text="Выберите подходящий инструмент", reply_markup=instrument_list
    )


@handle_errors
async def choose_instrument(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    await state.update_data(figi=callback_data.get("figi"))
    await state.update_data(name=callback_data.get("name"))
    await InstrumentState.proportion.set()
    await call.message.answer(text="Введите долю инструмента")


@handle_errors
async def add_instrument_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    figi = data.get("figi")
    try:
        proportion = float(message.text)
    except ValueError:
        raise ValidationError("Значение должно быть числом")
    if proportion < 0 or proportion > 1:
        raise ValidationError(f"Значение должно быть в диапазоне от 0 до 1")
    await Share.create(
        name=name, proportion=proportion, figi=figi, user_id=message.from_user.id
    )
    await state.finish()
    await message.answer(text=f"Инструмент '{name}' успешно добавлен")


@handle_errors
async def remove_instrument_finish(message: types.Message, state: FSMContext):
    await Share.filter(name=message.text, user_id=message.from_user.id).delete()
    await state.finish()
    await message.answer(text=f"Инструмент '{message.text}' успешно убран")


@handle_errors
async def recalculate_proportion(message: types.Message):
    shares = (
        await Share.filter(user_id=message.from_user.id)
        .annotate(total_percent=Sum("proportion"))
        .values("total_percent")
    )
    if not shares:
        await message.answer(
            "Чтобы пересчитать проценты, нужно добавить хотя бы один инструмент"
        )
        return
    total_percent = shares[0]["total_percent"]
    shares = await Share.filter(user_id=message.from_user.id)
    for share in shares:
        share.proportion = round(share.proportion / total_percent, 2)
        await share.save()
    await message.answer("Новые проценты успешно сформированы")
    await all_instruments(message)


def register_instruments_handlers(dp: Dispatcher):
    dp.register_message_handler(add_instrument, commands=["add_instrument"], state="*")
    dp.register_message_handler(
        remove_instrument, commands=["remove_instrument"], state="*"
    )
    dp.register_message_handler(all_instruments, commands=["instruments"], state="*")
    dp.register_message_handler(
        recalculate_proportion, commands=["recalculate_proportion"], state="*"
    )
    dp.register_message_handler(add_instrument_name, state=InstrumentState.name)
    dp.register_callback_query_handler(
        choose_instrument, instrument_data.filter(), state=InstrumentState.choose
    )
    dp.register_message_handler(add_instrument_finish, state=InstrumentState.proportion)
    dp.register_message_handler(remove_instrument_finish, state=InstrumentState.remove)

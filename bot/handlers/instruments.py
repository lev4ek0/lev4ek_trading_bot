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

from models.models import Share
from robot.trading_robot import Robot
from states import InstrumentState

instrument_data = CallbackData("instrument", "name", "figi")


async def add_instrument(message: types.Message):
    await InstrumentState.name.set()
    await message.answer(text="Введите название инструмента")


async def remove_instrument(message: types.Message):
    instrument_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    instruments = await Share.all()
    for instrument in instruments:
        button = InlineKeyboardButton(instrument.name)
        instrument_list.add(button)
    await InstrumentState.remove.set()
    await message.answer(
        text="Выберите подходящий инструмент", reply_markup=instrument_list
    )


async def all_instruments(message: types.Message):
    instruments = await Share.all().order_by("-proportion")
    table = PrettyTable(["Name", "%"])
    table.align["Name"] = "l"
    for instrument in instruments:
        table.add_row([instrument.name, f"{instrument.proportion * 100:.2f}"])
    await message.answer(
        text="Список всех инструментов:\n\n" + f"<pre>{table}</pre>",
        parse_mode=ParseMode.HTML,
    )


async def add_instrument_name(message: types.Message, state: FSMContext):
    robot = await Robot.create()
    instruments = robot.find_instrument(message.text)
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


async def choose_instrument(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    await state.update_data(figi=callback_data.get("figi"))
    await state.update_data(name=callback_data.get("name"))
    await InstrumentState.proportion.set()
    await call.message.answer(text="Введите долю инструмента")


async def add_instrument_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    figi = data.get("figi")
    await Share.create(name=name, proportion=message.text, figi=figi)
    await state.finish()
    await message.answer(text=f"Инструмент '{name}' успешно добавлен")


async def remove_instrument_finish(message: types.Message, state: FSMContext):
    await Share.filter(name=message.text).delete()
    await state.finish()
    await message.answer(text=f"Инструмент '{message.text}' успешно убран")


def register_instruments_handlers(dp: Dispatcher):
    dp.register_message_handler(add_instrument, commands=["add_instrument"], state="*")
    dp.register_message_handler(
        remove_instrument, commands=["remove_instrument"], state="*"
    )
    dp.register_message_handler(all_instruments, commands=["instruments"], state="*")
    dp.register_message_handler(add_instrument_name, state=InstrumentState.name)
    dp.register_callback_query_handler(
        choose_instrument, instrument_data.filter(), state=InstrumentState.choose
    )
    dp.register_message_handler(add_instrument_finish, state=InstrumentState.proportion)
    dp.register_message_handler(remove_instrument_finish, state=InstrumentState.remove)

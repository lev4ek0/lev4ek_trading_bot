from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from models.models import Share
from robot.trading_robot import Robot
from states import AddInstrumentState

instrument_data = CallbackData("instrument", "name", "figi")


async def add_instrument(message: types.Message):
    await AddInstrumentState.name.set()
    await message.answer(text="Введите название инструмента")


async def add_instrument_name(message: types.Message, state: FSMContext):
    instruments = Robot().find_instrument(message.text)
    instrument_list = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for instrument in instruments:
        button = InlineKeyboardButton(
            instrument.name, callback_data=instrument_data.new(name=instrument.name, figi=instrument.figi)
        )
        instrument_list.add(button)
    await AddInstrumentState.choose.set()
    await message.answer(text="Выберите подходящий инструмент", reply_markup=instrument_list)


async def choose_instrument(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(figi=callback_data.get("figi"))
    await state.update_data(name=callback_data.get("name"))
    await AddInstrumentState.proportion.set()
    await call.message.answer(text="Введите долю инструмента")


async def add_instrument_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    figi = data.get("figi")
    await Share.create(name=name, proportion=message.text, figi=figi)
    await state.finish()
    await message.answer(text=f"Инструмент '{name}' успешно добавлен")


def register_instruments_handlers(dp: Dispatcher):
    dp.register_message_handler(add_instrument, commands=["add_instrument"], state="*")
    dp.register_message_handler(add_instrument_name, state=AddInstrumentState.name)
    dp.register_callback_query_handler(
        choose_instrument, instrument_data.filter(), state=AddInstrumentState.choose
    )
    dp.register_message_handler(add_instrument_finish, state=AddInstrumentState.proportion)

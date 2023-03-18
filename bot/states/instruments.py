from aiogram.dispatcher.filters.state import StatesGroup, State


class InstrumentState(StatesGroup):
    name = State()
    remove = State()
    choose = State()
    proportion = State()

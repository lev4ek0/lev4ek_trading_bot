from aiogram.dispatcher.filters.state import StatesGroup, State


class AddInstrumentState(StatesGroup):
    name = State()
    choose = State()
    proportion = State()

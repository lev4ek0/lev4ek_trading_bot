from aiogram.dispatcher.filters.state import StatesGroup, State


class InstrumentState(StatesGroup):
    name = State()
    remove = State()
    choose = State()
    proportion = State()


class BrokerState(StatesGroup):
    broker = State()
    token = State()
    account = State()

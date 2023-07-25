from aiogram.fsm.state import State, StatesGroup


class BrokerAddState(StatesGroup):
    broker = State()
    token = State()
    account = State()


class BrokerRemoveState(StatesGroup):
    broker = State()


class SpecialityAddState(StatesGroup):
    link = State()
    snils = State()


class SpecialityRemoveState(StatesGroup):
    link = State()

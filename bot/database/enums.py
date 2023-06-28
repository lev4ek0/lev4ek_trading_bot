import enum


class BrokerType(enum.Enum):
    TINKOFF = "tinkoff"


class CurrencyType(enum.Enum):
    RUB = "rub"
    EUR = "eur"
    USD = "usd"

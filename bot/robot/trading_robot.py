import functools
import math
import operator
from itertools import product
from typing import Callable

from robot.brokers import tinkoff_connection
from settings import tinkoff_settings

# for i in client.instruments.shares().instruments:
#     if 'никель' in i.name.lower():
#         figi = i.figi
#         print(figi)
#         print(i.name)


class Instrument:
    def __init__(self, name, figi, percent):
        self.name = name
        self.figi = figi
        self.percent = percent
        self.connection = tinkoff_connection

    @property
    @functools.lru_cache()
    def amount(self):
        client = self.connection
        positions = client.operations.get_positions(account_id=tinkoff_settings.ACCOUNT_ID)
        for instrument in positions.securities:
            if instrument.figi == self.figi:
                return instrument.balance

    @property
    @functools.lru_cache()
    def price(self):
        client = self.connection
        return (
            client.market_data.get_last_prices(figi=[self.figi]).last_prices[0].price.units
            + client.market_data.get_last_prices(figi=[self.figi]).last_prices[0].price.nano / 1_000_000_000
        )


class Robot:
    def __init__(self):
        self.connection = tinkoff_connection
        self.instruments = [
            Instrument('Газпром', 'BBG004730RP0', 0.5),
            Instrument('ММК', 'BBG004S68507', 0.25),
            Instrument('Северсталь', 'BBG00475K6C3', 0.15),
            Instrument('Норникель', 'BBG004731489', 0.1),
        ]

    @functools.lru_cache()
    def get_total(self):
        client = self.connection
        positions = client.operations.get_positions(account_id=tinkoff_settings.ACCOUNT_ID).securities
        g = [
            client.market_data.get_last_prices(figi=[position.figi]).last_prices[0].price.units
            * position.balance
            + client.market_data.get_last_prices(figi=[position.figi]).last_prices[0].price.nano
            * position.balance
            / 1_000_000_000
            for position in positions
        ]
        total = functools.reduce(operator.add, g)
        return total

    def get_right_instrument_amount(self, instrument, lh):
        amount = self.get_total() * instrument.percent / instrument.price
        int_amount = math.floor(amount) if lh == 'l' else math.ceil(amount)
        return int_amount

    @staticmethod
    def get_actual_instrument_amount(instrument, *args):
        return instrument.amount

    def get_current_error(
        self, get_int_amount_func: Callable = get_actual_instrument_amount, combination=None
    ):
        error = 0
        for counter, instrument in enumerate(self.instruments):
            lh = None if combination is None else combination[counter]
            int_amount = get_int_amount_func(instrument, lh)
            error += abs(int_amount * instrument.price / self.get_total() - instrument.percent)
        error /= len(self.instruments)
        return error

    def get_best_choice(self):
        best_choice = (math.inf, '')
        for combination in product('lh', repeat=4):
            error = self.get_current_error(self.get_right_instrument_amount, combination=combination)
            if error < best_choice[0]:
                best_choice = (error, combination)
        return best_choice

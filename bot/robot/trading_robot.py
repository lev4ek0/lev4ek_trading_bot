import functools
import math
import operator
from itertools import product
from typing import Callable

from models.models import Share
from robot.brokers import tinkoff_connection
from settings import tinkoff_settings


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
        positions = client.operations.get_positions(
            account_id=tinkoff_settings.ACCOUNT_ID
        )
        for instrument in positions.securities:
            if instrument.figi == self.figi:
                return instrument.balance

    @property
    @functools.lru_cache()
    def price(self):
        client = self.connection
        return (
            client.market_data.get_last_prices(figi=[self.figi])
            .last_prices[0]
            .price.units
            + client.market_data.get_last_prices(figi=[self.figi])
            .last_prices[0]
            .price.nano
            / 1_000_000_000
        )


class Robot:
    def __init__(self):
        self.connection = tinkoff_connection
        self.instruments: dict[str, Instrument] = {}

    @classmethod
    async def create(cls):
        self = Robot()
        shares = await Share.all()
        self.instruments = {
            i.figi: Instrument(i.name, i.figi, i.proportion) for i in shares
        }
        print(self.instruments)
        return self

    def find_instrument(self, name):
        client = self.connection
        instrument = client.instruments.find_instrument(query=name)
        return filter(
            lambda x: x.instrument_type == "share" and x.class_code == "TQBR",
            instrument.instruments,
        )

    @functools.lru_cache()
    def get_shares(self):
        client = self.connection
        positions = client.operations.get_positions(
            account_id=tinkoff_settings.ACCOUNT_ID
        ).securities
        print(positions)
        shares = {
            self.instruments[position.figi]
            .name: client.market_data.get_last_prices(figi=[position.figi])
            .last_prices[0]
            .price.units
            * position.balance
            + client.market_data.get_last_prices(figi=[position.figi])
            .last_prices[0]
            .price.nano
            * position.balance
            / 1_000_000_000
            for position in positions
        }
        return shares

    @functools.lru_cache()
    def get_total(self):
        shares = list(self.get_shares().values())
        total = functools.reduce(operator.add, shares)
        return total

    def get_right_instrument_amount(self, instrument, lh):
        amount = self.get_total() * instrument.percent / instrument.price
        int_amount = math.floor(amount) if lh == "l" else math.ceil(amount)
        return int_amount

    @staticmethod
    def get_actual_instrument_amount(instrument, *args):
        return instrument.amount

    def get_current_error(
        self,
        get_int_amount_func: Callable = get_actual_instrument_amount,
        combination=None,
    ):
        error_mae = error_mse = max_error = 0
        for counter, instrument in enumerate(self.instruments.values()):
            lh = None if combination is None else combination[counter]
            int_amount = get_int_amount_func(instrument, lh)
            error = abs(
                int_amount * instrument.price / self.get_total() - instrument.percent
            )
            error_mae += error
            error_mse += (error * 100) ** 2
            max_error = max_error if max_error > error else error
        error_mae /= len(self.instruments.values())
        error_mse /= len(self.instruments.values()) * 100
        return {
            "MAE": error_mae,
            "MSE": error_mse,
            "MAX_E": max_error,
        }

    def get_best_choice(self):
        best_choice = (math.inf, "")
        for combination in product("lh", repeat=4):
            error_mae = self.get_current_error(
                self.get_right_instrument_amount, combination=combination
            )["MAE"]
            if error_mae < best_choice[0]:
                best_choice = (error_mae, combination)
        return best_choice

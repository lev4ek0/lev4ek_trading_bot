from dataclasses import dataclass
from typing import List

from prettytable import PrettyTable


@dataclass
class Instrument:
    instrument_id: str
    money: float
    amount: int
    name: str


@dataclass
class Account:
    account_id: str
    name: str
    instruments: List[Instrument]

    @property
    def balance(self):
        return sum(instrument.money for instrument in self.instruments)

    def __str__(self):
        text = f"Аккаунт: {self.name}, всего: {self.balance:.2f}\n\n"
        table = PrettyTable(["Name", "Money", "%"])
        table.align["Name"] = "l"

        for share in sorted(self.instruments, key=lambda x: x.money, reverse=True):
            table.add_row(
                [
                    share.name[:9],
                    share.money,
                    f"{share.money / self.balance * 100:.2f}",
                ]
            )

        return text + (f"<pre>{table}</pre>" if self.instruments else "")

from dataclasses import dataclass
from typing import List, Optional

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
    instruments: Optional[List[Instrument]] = None

    @property
    def balance(self):
        return sum(
            instrument.money for instrument in self.instruments if self.instruments
        )

    def __str__(self):
        text = f"Аккаунт: {self.name}, всего: {self.balance:.2f}\n\n"
        table = PrettyTable(["Name", "Money", "%"])
        table.align["Name"] = "l"

        for share in sorted(
            self.instruments or [], key=lambda x: x.money, reverse=True
        ):
            table.add_row(
                [
                    share.name[:9],
                    f"{share.money:.0f}",
                    f"{share.money / self.balance * 100:.1f}",
                ]
            )

        return text + (f"<pre>{table}</pre>" if self.instruments else "")

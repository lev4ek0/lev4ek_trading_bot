from abc import ABCMeta, abstractmethod

from brokers.dataclasses import Account


class BaseClient(metaclass=ABCMeta):
    def __init__(self, token: str):
        self.token = token

    @abstractmethod
    async def accounts_list(self) -> list[Account]:
        ...

    @abstractmethod
    async def get_account(self, account_id: int) -> Account:
        ...

from abc import ABCMeta, abstractmethod

from brokers.dataclasses import Account


class BaseClient(metaclass=ABCMeta):
    def __init__(self, account_id: int, token: str):
        self.account_id = account_id
        self.token = token

    @abstractmethod
    async def get_account(self) -> Account:
        ...

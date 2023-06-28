from brokers.common import BaseClient
from brokers.dataclasses import Account


class BrokerClient:
    def __init__(self, client: BaseClient):
        self.client = client

    async def accounts_list(self) -> list[Account]:
        return await self.client.accounts_list()

    async def show_account(self, account_id: int) -> Account:
        return await self.client.get_account(account_id)

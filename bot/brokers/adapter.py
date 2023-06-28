from brokers.common import BaseClient
from brokers.dataclasses import Account


class BrokerClient:
    def __init__(self, client: BaseClient):
        self.client = client

    async def show_account(self) -> Account:
        return await self.client.get_account()

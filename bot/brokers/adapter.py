from typing import List

from brokers.common import Account, BaseClient


class BrokerClient:
    def __init__(self, client: BaseClient):
        self.client = client

    async def show_account(self) -> Account:
        return await self.client.get_account()

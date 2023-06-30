from brokers.common import BaseClient
from brokers.dataclasses import Account, Instrument
from tinkoff.invest import AsyncClient, GetAccountsResponse, InstrumentIdType

from database.connection import redis_connection


class TinkoffClient(BaseClient):
    async def accounts_list(self) -> list[Account]:
        async with AsyncClient(self.token) as client:
            response: GetAccountsResponse = await client.users.get_accounts()

        return [Account(account_id=acc.id, name=acc.name) for acc in response.accounts]

    async def get_last_price(self, figi, client):
        price_prefix = "pp"
        cur_price = redis_connection[price_prefix + figi]
        if cur_price:
            return float(cur_price)
        last_prices_response = await client.market_data.get_last_prices(
            figi=[figi]
        )
        quotation = last_prices_response.last_prices[0].price
        price = (
            quotation.units + quotation.nano / 1_000_000_000
        )
        redis_connection.set_expire(price_prefix + figi, price)
        return price

    async def get_instrument_name(self, figi, client):
        name_prefix = "np"
        instrument_name = redis_connection[name_prefix + figi]
        if instrument_name:
            return instrument_name
        instrument = (
            await client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi
            )
        ).instrument
        redis_connection[name_prefix + figi] = instrument.name
        return instrument.name

    async def get_account(self, account_id):
        account, shares = None, []

        async with AsyncClient(self.token) as client:
            response: GetAccountsResponse = await client.users.get_accounts()
            positions = await client.operations.get_positions(account_id=account_id)
            for share in positions.securities:
                figi, amount = share.figi, share.balance
                price = await self.get_last_price(figi, client)
                name = await self.get_instrument_name(figi, client)
                money = price * amount
                shares.append(
                    Instrument(
                        instrument_id=share.figi,
                        money=money,
                        amount=amount,
                        name=name,
                    )
                )
            money = positions.money
            if money:
                shares.append(
                    Instrument(
                        instrument_id="Money",
                        money=money[0].units + money[0].nano / 1_000_000_000,
                        amount=1,
                        name="Деньги",
                    )
                )
        res_account = filter(lambda acc: acc.id == account_id, response.accounts)
        if acc := next(res_account, None):
            account = Account(acc.id, acc.name, shares)
        return account

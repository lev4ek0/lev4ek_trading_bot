from brokers.common import BaseClient
from brokers.dataclasses import Account, Instrument
from tinkoff.invest import AsyncClient, GetAccountsResponse, InstrumentIdType


class TinkoffClient(BaseClient):
    async def accounts_list(self) -> list[Account]:
        async with AsyncClient(self.token) as client:
            response: GetAccountsResponse = await client.users.get_accounts()

        return [Account(account_id=acc.id, name=acc.name) for acc in response.accounts]

    async def get_account(self, account_id):
        account, shares = None, []

        async with AsyncClient(self.token) as client:
            response: GetAccountsResponse = await client.users.get_accounts()
            positions = await client.operations.get_positions(account_id=account_id)
            for share in positions.securities:
                figi, amount = share.figi, share.balance
                last_prices_response = await client.market_data.get_last_prices(
                    figi=[figi]
                )
                instrument = (
                    await client.instruments.get_instrument_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi
                    )
                ).instrument
                quotation = last_prices_response.last_prices[0].price
                money = (
                    quotation.units * amount + quotation.nano * amount / 1_000_000_000
                )
                shares.append(
                    Instrument(
                        instrument_id=share.figi,
                        money=money,
                        amount=amount,
                        name=instrument.name,
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

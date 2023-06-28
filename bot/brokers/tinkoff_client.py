from brokers.common import BaseClient
from brokers.dataclasses import Account, Instrument
from tinkoff.invest import AsyncClient, GetAccountsResponse, InstrumentIdType


class TinkoffClient(BaseClient):
    async def get_account(self):
        account, shares = None, []

        async with AsyncClient(self.token) as client:
            response: GetAccountsResponse = await client.users.get_accounts()
            securities = (
                await client.operations.get_positions(account_id=self.account_id)
            ).securities
            for share in securities:
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
        res_account = filter(lambda acc: acc.id == self.account_id, response.accounts)
        if acc := next(res_account, None):
            account = Account(acc.id, acc.name, shares)
        return account

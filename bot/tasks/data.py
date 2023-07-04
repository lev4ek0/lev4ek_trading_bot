import asyncio
import os

from aiogram import Bot
from dateutil.relativedelta import relativedelta
from settings import bot_settings
from tinkoff.invest import (
    AsyncClient,
    CandleInterval,
    GetAccountsResponse,
)
from tinkoff.invest.utils import now
from utils import get_money


async def store_data(bot: Bot):
    TOKEN = bot_settings.TINKOFF_API_TOKEN.get_secret_value()
    async with AsyncClient(TOKEN) as client:
        try:
            os.makedirs("sources")
        except FileExistsError:
            pass
        response: GetAccountsResponse = await client.users.get_accounts()
        account_ids = map(lambda acc: acc.id, response.accounts)
        figis = set()
        for account_id in account_ids:
            positions = await client.operations.get_positions(account_id=account_id)
            for share in positions.securities:
                figis.add(share.figi)
        for figi in list(figis):
            try:
                os.makedirs(f"sources/{figi}")
            except FileExistsError:
                pass
            for month in range(1, 60):
                moment = now()
                start = (moment - relativedelta(months=month + 1)).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                finish = (moment - relativedelta(months=month)).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                counter = 1
                path = f"sources/{figi}/{start.year % 100:02d}.{start.month :02d}.txt"
                if os.path.isfile(path):
                    continue
                with open(path, "w") as f:
                    async for candle in client.get_all_candles(
                        figi=figi,
                        from_=start,
                        interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
                        to=finish,
                    ):
                        if counter % 500 == 0:
                            await asyncio.sleep(1)
                        if candle.time.weekday() < 5:
                            f.write(
                                f"{get_money(candle.open)};"
                                f"{get_money(candle.close)};"
                                f"{get_money(candle.high)};"
                                f"{get_money(candle.low)};"
                                f"{candle.volume};"
                                f"{candle.time}\n"
                            )
                        counter += 1

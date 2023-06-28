import emoji
from aiogram import Bot
from aiogram.enums import ParseMode
from sqlalchemy import select

from database import Account, get_db_session
from utils.broker_client import get_broker_client

emoji = {
    "good": emoji.emojize(":green_circle:"),
    "bad": emoji.emojize(":red_circle:"),
    "neutral": emoji.emojize(":white_circle:"),
}


async def send_message(text, new, old, bot, chat_id):
    circle = emoji["good" if new > old else "bad" if new < old else "neutral"]
    await bot.send_message(
        chat_id,
        text=f"{circle} {text} с {old:.2f} до {new:.2f} {circle}",
    )


def get_diff_in_percents(new, old):
    if new and old:
        return abs(new - old) / old
    else:
        return bool(new or old)


async def share_changes_task(bot: Bot, map_accounts_money: dict[str, int]):
    session = await anext(get_db_session())
    select_accounts = select(Account).filter()
    accounts = await session.execute(select_accounts)
    for account in accounts.all():
        total_value = map_accounts_money[account.id]
        broker_client = get_broker_client(account)
        broker_account = await broker_client.show_account()
        total_new = broker_account.balance
        is_sent_message = False
        if (diff := get_diff_in_percents(total_new, total_value)) > 0.0001:
            map_accounts_money[account.id] = total_new
            await send_message(
                f"Общая сумма на счете изменилась на {diff * 100:.2f}%",
                new=total_new,
                old=total_value,
                bot=bot,
                chat_id=account.user_id,
            )
            is_sent_message = True

        if is_sent_message:
            await bot.send_message(
                account.user_id,
                text=str(broker_account),
                parse_mode=ParseMode.HTML,
            )

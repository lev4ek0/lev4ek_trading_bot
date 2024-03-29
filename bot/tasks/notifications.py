import emoji
from aiogram import Bot
from aiogram.enums import ParseMode
from database import Account, postgres_connection
from database.connection import redis_connection
from sqlalchemy import select
from utils import get_broker_client

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


async def share_changes_task(bot: Bot):
    session = postgres_connection
    select_accounts = select(Account).where(Account.is_notifications == True)
    accounts = await session.select(select_accounts)
    for account in accounts.scalars():
        total_value = redis_connection[account.id]
        broker_client = get_broker_client(
            account.broker_type.value.capitalize(), account.api_key
        )
        broker_account = await broker_client.show_account(account.broker_account_id)
        total_new = broker_account.balance
        if not total_value:
            redis_connection[account.id] = total_new
            continue
        is_sent_message, total_value = False, float(total_value)
        if (diff := get_diff_in_percents(total_new, total_value)) > 0.01:
            redis_connection[account.id] = total_new
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

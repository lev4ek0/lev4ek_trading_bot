import emoji
from aiogram import Bot
from aiogram.types import ParseMode

from handlers.services.instruments import get_shares_table, build_shares_table

emoji = {
    "good": emoji.emojize(":green_circle:"),
    "bad": emoji.emojize(":red_circle:"),
    "neutral": emoji.emojize(":white_circle:"),
}


async def send_message(text, new, old, bot, chat_id):
    circle = emoji["good" if new > old else "bad" if new < old else "neutral"]
    await bot.send_message(
        chat_id,
        text=f"{circle} {text} с {old} до {new} {circle}",
    )


async def share_changes_task(
    bot: Bot, total: list[float], shares_output: list[dict], user_id: int
):
    total_value = total[0]
    shares_output_value = shares_output[0]
    total_new, shares_output_new = await get_shares_table(user_id)
    is_sent_message = False
    if abs(total_new - total_value) / total_value < 0.01:
        total[0] = total_new
        await send_message(
            "Общая сумма на счете изменилась на 1%",
            new=total_new,
            old=total_value,
            bot=bot,
            chat_id=user_id,
        )
        is_sent_message = True
    for name, money in shares_output_new.items():
        share_new_money = shares_output_new.get(name)
        share_money = shares_output_value.get(name)
        if share_money and share_new_money:
            shares_output[0] = shares_output_new
            if abs(share_new_money - share_money) / share_money > 0.03:
                await send_message(
                    f'Сумма акций "{name}" изменилась на 3%',
                    new=share_new_money,
                    old=share_money,
                    bot=bot,
                    chat_id=user_id,
                )
                is_sent_message = True

    if is_sent_message:
        table = build_shares_table(total_new, shares_output_new)
        await bot.send_message(
            user_id,
            text=table,
            parse_mode=ParseMode.HTML,
        )

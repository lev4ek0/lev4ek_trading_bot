import asyncio
from itertools import groupby
from operator import attrgetter

import aiohttp
from aiogram import Bot

from database import Speciality, postgres_connection
from database.connection import redis_connection
from sqlalchemy import select


def get_color(el):
    import re
    pattern = "RatingPage_table__item_(.+?)__"
    newlist = [out.group(1) for x in el["class"] if (out := re.search(pattern, x))]
    return newlist[0] if newlist else None


async def speciality_task(bot: Bot):
    session = postgres_connection
    select_specialities = select(Speciality).order_by(Speciality.link)
    specialities = await session.select(select_specialities)
    links = {k: list(g) for k, g in groupby(specialities.scalars(), attrgetter('link'))}

    async with aiohttp.ClientSession() as session:
        tasks = []
        for link in links:
            tasks.append(asyncio.create_task(session.get(link)))
        responses = await asyncio.gather(*tasks)
        texts = [await r.text() for r in responses]
        from bs4 import BeautifulSoup

        for text, link in zip(texts, links):
            soup = BeautifulSoup(text, "html.parser")
            r = soup.select('div[class*="RatingPage_rating__placesBlock"]')
            places = redis_connection[f"{speciality.link}_place"] or int(list(list(r[0])[0])[2])
            redis_connection[f"{speciality.link}_place"] = places
            r = soup.select('div[class*="RatingPage_rating__text"]')
            program = str(list(list(r[0])[0])[0])
            r = soup.select('div[class*="RatingPage_table__item"]')
            for speciality in links[link]:
                my_place, my_score = -1, -1
                counter1, counter2, counter3, place = 0, 0, 0, 1
                for el in r:
                    color = get_color(el)
                    snils = str(list(el)[0].text.split("№")[1])
                    priority = int(list(list(list(list(list(el)[1])[0])[0])[0])[1].text)
                    originals = bool(list(list(list(list(list(el)[1])[1])[1])[0])[1].text == 'да')
                    if priority == 1 and originals and color != 'gray':
                        counter1 += 1
                    if originals and color != 'gray':
                        counter2 += 1
                    if priority == 1 and color != 'gray':
                        counter3 += 1
                    if snils == speciality.snils:
                        my_place = place
                        my_score = str(list(list(list(list(list(el)[1])[1])[0])[2])[1].text)
                        break
                    if color != 'gray':
                        place += 1
                prev_place = redis_connection[f"{speciality.user_id}_{speciality.link}_place"]
                if not prev_place:
                    prev_place = my_place
                    redis_connection[f"{speciality.user_id}_{speciality.link}_place"] = my_place
                if int(prev_place) != my_place:
                    redis_connection[f"{speciality.user_id}_{speciality.link}_place"] = my_place
                    if my_place != -1:
                        await bot.send_message(
                            speciality.user_id,
                            text=f"Всего мест: {places}\n"
                                 f"Ваше место по дисциплине {program} изменилось с {prev_place} на {my_place}\n"
                                 f"До вас подали с приоритетом 1 и оригиналами документов: {counter1}\n"
                                 f"До вас подали с оригиналами документов: {counter2}\n"
                                 f"До вас подали с приоритетом 1: {counter3}",
                        )
                prev_score = redis_connection[f"{speciality.user_id}_{speciality.link}_score"]
                if not prev_score:
                    prev_score = my_score
                    redis_connection[f"{speciality.user_id}_{speciality.link}_score"] = my_score
                if prev_score != my_score:
                    redis_connection[f"{speciality.user_id}_{speciality.link}_score"] = my_score
                    if my_place != -1:
                        await bot.send_message(
                            speciality.user_id,
                            text=f"Ваш результат по дисциплине {program} изменился с {prev_score} на {my_score}",
                        )

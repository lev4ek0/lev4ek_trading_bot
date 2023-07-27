import aiohttp
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from database import Speciality
from database.connection import PostgresConnection, redis_connection
from handlers import create_router
from sqlalchemy import select, insert, delete

from handlers.states import SpecialityAddState, SpecialityRemoveState

router = create_router()


@router.message(Command("add_speciality"))
async def add_speciality(message: types.Message, state: FSMContext):
    await state.set_state(SpecialityAddState.link)
    await message.answer(
        text="Введите ссылку на вашу специальность",
    )


@router.message(SpecialityAddState.link)
async def add_link(message: types.Message, state: FSMContext):
    if not message.text.startswith("https://"):
        await message.answer(
            text="Ссылка должна быть вида 'https://abit.itmo.ru/ranking/master/{budget/contract}/id'.\n\n"
                 "Ее можно найти здесь: https://abit.itmo.ru/rankings/master",
        )
        return
    async with aiohttp.ClientSession() as sess:
        ans = await sess.get(message.text)
        if ans.status != 200:
            await message.answer(
                text=f"Ссылка недействительна: status: {ans.status}",
            )
            await state.clear()
            await message.answer(
                text=f"Специальность не была добавлена. Попробуйте команду /add_speciality еще раз.",
            )
            return
    if not message.text.startswith("https://abit.itmo.ru/ranking/master/"):
        await message.answer(
            text="Ссылка должна быть вида 'https://abit.itmo.ru/ranking/master/{budget/contract}/id'.\n\n"
                 "Ее можно найти здесь: https://abit.itmo.ru/rankings/master",
        )
        return
    await state.update_data(link=message.text)
    await state.set_state(SpecialityAddState.snils)
    await message.answer(
        text="Введите снилс",
    )


@router.message(SpecialityAddState.snils)
async def add_broker_finish(
    message: types.Message, state: FSMContext, session: PostgresConnection
):
    data = await state.get_data()
    link = data.get("link")
    user_id = message.from_user.id
    insert_speciality = insert(Speciality).values(
        user_id=user_id,
        link=link,
        snils="".join(c for c in message.text if c.isnumeric()),
    )
    await state.clear()
    await session.execute(insert_speciality)
    await message.answer(
        text=f"Специальность '{link}' была успешно добавлена",
        disable_web_page_preview=True,
    )


@router.message(Command("my_specialities"))
async def my_specialities(message: types.Message, session: PostgresConnection):
    select_specialities = select(Speciality).where(Speciality.user_id == message.from_user.id)
    specialities = await session.select(select_specialities)
    specialities = list(specialities.scalars())
    specialities_list = []
    for speciality in specialities:
        place = redis_connection[f"{speciality.user_id}_{speciality.link}_place"]
        text = f"Ссылка: {speciality.link}, СНИЛС: {speciality.snils}"
        if place:
            total_places = redis_connection[f"{speciality.link}_place"]
            text += f", Место: {place}/{total_places}"
        specialities_list.append(text)
    if not specialities:
        return await message.answer(
            text="У вас нет специализаций. Чтобы ее добавить, введите /add_speciality",
        )
    specs = '\n'.join(specialities_list)
    await message.answer(
        text=f"Ваши специализации: \n{specs}",
        disable_web_page_preview=True,
    )


@router.message(Command("remove_speciality"))
async def remove_speciality(
    message: types.Message, state: FSMContext, session: PostgresConnection
):
    select_specialities = select(Speciality).where(Speciality.user_id == message.from_user.id)
    specialities = await session.select(select_specialities)
    specialities = list(specialities.scalars())
    specialities_list = []
    for speciality in specialities:
        button = InlineKeyboardButton(
            text=speciality.link
        )
        specialities_list.append([button])
    if not specialities:
        return await message.answer(
            text="У вас нет специализаций. Чтобы ее добавить, введите /add_speciality",
        )
    specialities_kb = ReplyKeyboardMarkup(
        keyboard=specialities_list, resize_keyboard=True, one_time_keyboard=True
    )
    await state.set_state(SpecialityRemoveState.link)

    await message.answer(
        text="Выберите специализацию",
        reply_markup=specialities_kb,
    )


@router.message(SpecialityRemoveState.link)
async def remove_broker_finish(
    message: types.Message, state: FSMContext, session: PostgresConnection
):
    delete_speciality = delete(Speciality).where(Speciality.link == message.text, Speciality.user_id == message.from_user.id)
    await session.execute(delete_speciality)
    await state.clear()
    await message.answer(
        text="Специализация успешно удалена", reply_markup=ReplyKeyboardRemove()
    )

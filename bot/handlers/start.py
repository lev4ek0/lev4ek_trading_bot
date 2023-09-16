from aiogram import types
from aiogram.filters import Command

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from handlers import create_router

router = create_router()

@router.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    text = (
        "Это бот для трейдинга, но еще у меня есть подписка "
        "на уведомления о поступлении. Чтобы воспользоваться, "
        "нужно написать /add_speciality\n\n"
        "Доступные команды:\n\n"
        "/help\n"
        "/add_broker\n"
        "/remove_broker\n"
        "/manage_notifications\n"
        "/shares\n"
        "/add_speciality\n"
        "/my_specialities\n"
        "/remove_speciality\n"
    )
    await message.answer(text=text)
    registry = CollectorRegistry()
    g = Gauge('job_last_success_unixtime', 'Last time a batch job successfully finished', registry=registry)
    g.set_to_current_time()
    push_to_gateway('lev4ek.ru:9090', job='batchA', registry=registry)

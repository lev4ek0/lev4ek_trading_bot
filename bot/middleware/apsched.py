from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler
        super().__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        data["apscheduler"] = self.scheduler

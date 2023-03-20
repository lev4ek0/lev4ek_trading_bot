from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from middleware.acl import ACLMiddleware
from middleware.history import HistoryMiddleware
from middleware.apsched import SchedulerMiddleware


def setup_middleware(dispatcher: Dispatcher, scheduler):
    dispatcher.middleware.setup(LoggingMiddleware("bot"))
    dispatcher.middleware.setup(ACLMiddleware())
    dispatcher.middleware.setup(HistoryMiddleware())
    dispatcher.middleware.setup(SchedulerMiddleware(scheduler=scheduler))

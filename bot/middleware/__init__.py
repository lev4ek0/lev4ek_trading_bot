from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from middleware.acl import ACLMiddleware


def setup_middleware(dispatcher: Dispatcher):
    dispatcher.middleware.setup(LoggingMiddleware("bot"))
    dispatcher.middleware.setup(ACLMiddleware())

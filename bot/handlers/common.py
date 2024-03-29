from aiogram import Router
from middleware import ErrorsMiddleware, SessionMiddleware, UserMiddleware, MetricsMiddleware


def create_router():
    router = Router()
    router.message.middleware(SessionMiddleware())
    router.callback_query.middleware(SessionMiddleware())
    router.message.middleware(UserMiddleware())
    router.message.middleware(ErrorsMiddleware())
    router.message.middleware(MetricsMiddleware())
    return router

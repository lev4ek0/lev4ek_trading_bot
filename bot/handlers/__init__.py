from .main import register_main_handlers
from .instruments import register_instruments_handlers


def register_handlers(dp):
    register_main_handlers(dp)
    register_instruments_handlers(dp)

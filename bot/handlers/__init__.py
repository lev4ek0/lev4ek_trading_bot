from .main import register_main_handlers
from .instruments import register_instruments_handlers
from .brokers import register_brokers_handlers
from .notifications import register_notifications_handlers


def register_handlers(dp):
    register_main_handlers(dp)
    register_notifications_handlers(dp)
    register_instruments_handlers(dp)
    register_brokers_handlers(dp)

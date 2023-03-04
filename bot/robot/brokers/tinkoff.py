from tinkoff.invest import Client

from settings.settings import tinkoff_settings


class ConnectionTinkoff:
    def __init__(self, token):
        self.token = token.get_secret_value()
        self.connection = None

    def connect(self):
        self.connection = Client(self.token)
        return self.connection.__enter__()

    def close(self):
        return self.connection.__exit__()


tinkoff_connection = ConnectionTinkoff(tinkoff_settings.TOKEN).connect()

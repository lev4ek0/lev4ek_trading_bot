from tinkoff.invest import Client


class ClientTinkoff:
    def __init__(self, token):
        self.token = token
        self.connection = None

    def connect(self):
        self.connection = Client(self.token)
        return self.connection.__enter__()

    def close(self):
        return self.connection.__exit__("a", "b", "c")


tinkoff_client = ClientTinkoff

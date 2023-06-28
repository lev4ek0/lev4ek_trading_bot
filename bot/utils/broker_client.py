from brokers import BrokerClient
from brokers.common import BaseClient
from utils import get_broker_class


def get_broker_client(broker_name: str, token: str):
    client = get_broker_class(class_name=f"{broker_name}Client")
    init_client: BaseClient = client(
        token=token,
    )
    return BrokerClient(init_client)

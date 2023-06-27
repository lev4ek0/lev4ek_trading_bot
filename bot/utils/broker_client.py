from brokers import BrokerClient
from brokers.common import BaseClient
from database import Account
from utils import get_broker_class


def get_broker_client(account: Account):
    broker_name = account.broker_type.value.capitalize()
    client = get_broker_class(class_name=f"{broker_name}Client")
    init_client: BaseClient = client(
        account_id=account.broker_account_id,
        token=account.api_key,
    )
    return BrokerClient(init_client)

import importlib
from abc import ABCMeta


def get_broker_class(class_name: str, module_name: str = "brokers") -> ABCMeta:
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_

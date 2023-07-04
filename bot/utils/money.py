from tinkoff.invest import Quotation


def get_money(quotation: Quotation):
    return quotation.units + quotation.nano / 1_000_000_000

from prettytable import PrettyTable

from models.models import User
from robot.trading_robot import Robot


async def get_shares_table(user_id: int) -> tuple[float, dict]:
    user = await User.get(id=user_id)
    robot = await Robot.create(
        token=user.tinkoff_api_key,
        account_id=user.tinkoff_account_id,
        user_id=user.id,
    )
    shares = robot.get_shares()
    instruments = robot.instruments
    shares_output = {}
    for figi, share in shares.items():
        instrument_name = (
            instruments.get(figi) or robot.find_instrument_by_figi(figi)
        ).name
        shares_output[instrument_name] = share
    total = robot.get_total()
    robot.client.close()
    return total, shares_output


def build_shares_table(total, shares_output):
    text = f"Всего: {total}\n\n"
    table = PrettyTable(["Name", "Money", "%"])
    table.align["Name"] = "l"

    for share in sorted(shares_output.items(), key=lambda x: x[1], reverse=True):
        table.add_row([share[0][:10], share[1], f"{share[1] / total * 100:.2f}"])

    return text + f"<pre>{table}</pre>"

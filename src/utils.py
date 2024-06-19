import base64
import json
import os.path
import sys

import urllib3
from art import tprint
from loguru import logger

from models import Account


def setup():
    urllib3.disable_warnings()
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<light-cyan>{time:HH:mm:ss}</light-cyan> | <level> {level: <8}</level> | - <white>{"
        "message}</white>",
    )
    logger.add("./logs/logs.log", rotation="1 day", retention="7 days")


def show_dev_info():
    os.system("cls")
    tprint("JamBit")
    print("\033[36m" + "VERSION: " + "\033[34m" + "1.0" + "\033[34m")
    print("\033[36m" + "Channel: " + "\033[34m" + "https://t.me/JamBitPY" + "\033[34m")
    print(
        "\033[36m"
        + "GitHub: "
        + "\033[34m"
        + "https://github.com/Jaammerr"
        + "\033[34m"
    )
    print(
        "\033[36m"
        + "DONATION EVM ADDRESS: "
        + "\033[34m"
        + "0xe23380ae575D990BebB3b81DB2F90Ce7eDbB6dDa"
        + "\033[0m"
    )
    print()



def export_results(data: list[tuple[bool, Account]]):
    if not os.path.exists("results"):
        os.makedirs("results")

    with open("results/success.txt", "w") as file:
        file.write(
            "\n".join(
                [
                    (
                        f"{wallet.auth_token}:{wallet.mnemonic}"
                        if wallet.mnemonic
                        else wallet.auth_token
                    )
                    for status, wallet in data
                    if status
                ]
            )
        )

    with open("results/failed.txt", "w") as file:
        file.write(
            "\n".join([wallet.auth_token for status, wallet in data if not status])
        )

    logger.info("Results exported to results/success.txt and results/failed.txt")


def base64url_decode(data: str):
    padding = "=" * (4 - len(data) % 4)
    data += padding
    return base64.urlsafe_b64decode(data)


def decode_id_token(token: str) -> dict[str, str]:
    parts = token.split(".")
    payload = parts[1]

    decoded_payload = base64url_decode(payload).decode("utf-8")
    user_info = json.loads(decoded_payload)
    return user_info

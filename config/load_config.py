import os
from itertools import cycle
from typing import List

import yaml
import random

from loguru import logger
from models import Config, Account
from better_proxy import Proxy


def get_accounts() -> "Account":
    accounts_path = os.path.join(os.path.dirname(__file__), "data", "accounts.txt")
    if not os.path.exists(accounts_path):
        logger.error(f"File <<{accounts_path}>> does not exist")
        exit(1)

    with open(accounts_path, "r") as f:
        accounts = [account.strip() for account in f.readlines()]

        if not accounts:
            logger.error(f"File <<{accounts_path}>> is empty")
            exit(1)

        proxy_cycle = cycle(get_proxies())
        for account in accounts:
            parts = account.split(":")

            if len(parts) == 2:
                yield Account(
                    auth_token=parts[0].strip(),
                    proxy=next(proxy_cycle),
                    mnemonic=parts[1].strip(),
                )

            elif len(parts) == 3:
                yield Account(
                    auth_token=parts[0].strip(),
                    proxy=next(proxy_cycle),
                    mnemonic=parts[1].strip(),
                    discord_token=parts[2].strip(),
                )

            else:
                yield Account(auth_token=parts[0].strip(), proxy=next(proxy_cycle))


def get_proxies() -> list[Proxy]:
    proxies_path = os.path.join(os.path.dirname(__file__), "data", "proxies.txt")
    if not os.path.exists(proxies_path):
        logger.error(f"File <<{proxies_path}>> does not exist")
        exit(1)

    valid_proxies = []
    with open(proxies_path, "r") as f:
        proxies = [proxy.strip() for proxy in f.readlines()]

        if not proxies:
            logger.error(f"File <<{proxies_path}>> is empty")
            exit(1)

        try:
            for proxy in proxies:
                if proxy != "":
                    proxy = Proxy.from_str(proxy.strip())
                    valid_proxies.append(proxy)

        except Exception as error:
            logger.error(f"Error while parsing proxy <<{proxy}>>: {error}")
            exit(1)

        return valid_proxies


def load_config() -> Config:
    settings_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    if not os.path.exists(settings_path):
        logger.error(f"File <<{settings_path}>> does not exist")
        exit(1)

    with open(settings_path, "r") as f:
        settings = yaml.safe_load(f)

    REQUIRED_KEYS = (
        "threads",
        "delay_between_quests",
        "delay_between_quests_verification",
        "delay_between_chests",
        "eth_rpc"
    )

    for key in REQUIRED_KEYS:
        if key not in settings:
            logger.error(f"Key <<{key}>> is missing in settings.yaml")
            exit(1)

    accounts = list(get_accounts())
    return Config(accounts=accounts, **settings)

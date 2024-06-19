import asyncio

from loguru import logger

from models import Account
from loader import config, semaphore

from src.bot import Bot
from src.utils import export_results, setup, show_dev_info



async def run_safe(account: Account) -> tuple[bool, Account]:
    async with semaphore:
        bot = Bot(account)
        status = await bot.start()
        return status, bot.account


async def run():
    logger.info(f"Bot Started:\n- Accounts: {len(config.accounts)}\n- Threads: {config.threads}\n\n")
    tasks = [asyncio.create_task(run_safe(account)) for account in config.accounts]

    results = await asyncio.gather(*tasks)
    export_results(results)


if __name__ == "__main__":
    setup()
    show_dev_info()
    asyncio.run(run())

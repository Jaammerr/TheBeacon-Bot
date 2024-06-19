import asyncio

from config.load_config import load_config

config = load_config()
semaphore = asyncio.Semaphore(config.threads)

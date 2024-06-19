import asyncio
import random_string

from datetime import datetime
from typing import Any

from models import Account
from loguru import logger
from loader import config

from .api import TheBeaconAPI
from .exceptions.base import APIError
from .wallet import Wallet
from .twitter_connect import TwitterConnectModded


class Bot(TheBeaconAPI):
    def __init__(self, account_data: Account):
        super().__init__(account_data)

        self.wallet = Wallet(account_data.mnemonic)
        if not account_data.mnemonic:
            account_data.mnemonic = self.wallet.mnemonic

    async def process_complete_quest(
        self, quest_id: str, description: str, reward_xp: int = 0
    ):
        for _ in range(2):
            logger.info(
                f"Account: {self.account.auth_token} | Verifying quest: {description}"
            )

            try:
                response = await self.verify_quest(quest_id)
                if response.data.status != "Verified":
                    logger.warning(
                        f"Account: {self.account.auth_token} | Quest not verified: {description} | Retrying.."
                    )
                    await asyncio.sleep(3)
                    return await self.process_complete_quest(
                        quest_id, description, reward_xp
                    )

                await asyncio.sleep(config.delay_between_quests_verification)
                logger.info(
                    f"Account: {self.account.auth_token} | Claiming reward for quest: {description}"
                )
                response = await self.claim_quest_reward(quest_id)

                if response.get("message", "") == "Created":
                    logger.success(
                        f"Account: {self.account.auth_token} | Quest completed: {description} | Reward: {reward_xp} XP"
                    )
                    return
                else:
                    logger.error(
                        f"Account: {self.account.auth_token} | Failed to complete quest: {description} | Response: {response} | Retrying.."
                    )
                    await asyncio.sleep(3)

            except Exception as error:
                logger.error(
                    f"Account: {self.account.auth_token} | Failed to complete quest: {description} | Error: {error} | Retrying.."
                )
                await asyncio.sleep(3)

    async def process_create_account(self) -> bool:
        logger.info(
            f"Account: {self.account.auth_token} | Creating account with wallet: {self.wallet.address}"
        )

        for _ in range(2):
            try:
                try:
                    await self.first_login(self.wallet.sign_login_message())
                except APIError as error:
                    if "User not found" in str(error):
                        logger.success(
                            f"Account: {self.account.auth_token} | Wallet approved"
                        )
                    else:
                        logger.error(
                            f"Account: {self.account.auth_token} | Failed to approve wallet: {error} | Retrying.."
                        )

                await asyncio.sleep(3)
                username = random_string.generate(min_length=12)
                response = await self.approve_username(
                    self.wallet.sign_login_message(), username
                )

                if response.jwt:
                    # self.update_token_info(response.jwt)
                    await self.save_beacon_info()

                    logger.success(
                        f"Account: {self.account.auth_token} | Username approved: {username}"
                    )
                    return True
                else:
                    logger.error(
                        f"Account: {self.account.auth_token} | Failed to approve username: {username} | Retrying.."
                    )
                    await asyncio.sleep(3)

            except Exception as error:
                logger.error(
                    f"Account: {self.account.auth_token} | Failed to create account | Error: {error} | Retrying.."
                )
                await asyncio.sleep(3)

        logger.error(
            f"Account: {self.account.auth_token} | Failed to create account | Max retries exceeded"
        )
        return False

    def get_available_quests(self, quests: Any) -> list:
        available_quests = []

        for quest in quests.data.quests:
            if quest.UserQuest:
                if quest.UserQuest[0].status != "Completed":

                    if quest.shortDescription == "Connect your Discord":
                        logger.info(
                            f"Account: {self.account.auth_token} | Skipping quest: {quest.shortDescription}"
                        )
                        continue

                    if quest.availableAt:
                        formatted_time = datetime.strptime(
                            quest.availableAt, "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                        if formatted_time < datetime.now():
                            available_quests.append(quest)
                    else:
                        available_quests.append(quest)

        return available_quests

    async def process_open_chests(self):
        while True:
            try:
                response = await self.open_chest(self.wallet.sign_login_message())
                if response.lootDrops[0]:
                    item = response.lootDrops[0].item.kind
                    logger.success(
                        f"Account: {self.account.auth_token} | Opened chest | Received item: {item}"
                    )
                else:
                    logger.error(
                        f"Account: {self.account.auth_token} | Failed to open chest: {response}"
                    )

            except APIError as error:
                if "User cannot open chest" in str(error):
                    logger.info(
                        f"Account: {self.account.auth_token} | All chests are opened"
                    )
                    return

                elif "User not found" in str(error):
                    logger.warning(
                        f"Account: {self.account.auth_token} | Cannot open chest because loaded invalid wallet or wallet not approved"
                    )
                    return

                else:
                    logger.error(
                        f"Account: {self.account.auth_token} | Failed to open chest: {error}"
                    )
                    return

            finally:
                await asyncio.sleep(config.delay_between_chests)

    async def process_quests(self):
        while True:
            quests = await self.get_quests()

            available_quests = self.get_available_quests(quests)
            logger.info(
                f"Account: {self.account.auth_token} | Available quests: {len(available_quests)}"
            )

            if available_quests:
                for quest in available_quests:
                    if quest.shortDescription == "Create Your Account":
                        status = await self.process_create_account()
                        if not status:
                            return status

                    await self.process_complete_quest(
                        quest.id, quest.shortDescription, quest.xp
                    )
                    await asyncio.sleep(config.delay_between_quests)

            else:
                logger.info(
                    f"Account: {self.account.auth_token} | All available quests are completed"
                )
                return True

    async def start(self) -> bool:
        try:
            twitter_connect = TwitterConnectModded(session=self.session, account_data=self.account)
            account = await twitter_connect.start()

            if not account:
                return False

            self.__init__(account)
            status = await self.process_quests()
            if status:
                await self.process_open_chests()
                return True

            return False

        except Exception as error:
            logger.error(
                f"Account: {self.account.auth_token} | Unhandled error: {error}"
            )
            return False

        finally:
            if self.account:
                logger.success(f"Account: {self.account.auth_token} | Finished")

import asyncio
import time

from loguru import logger
from undetected_playwright.async_api import (
    async_playwright,
    Playwright,
    BrowserContext,
    Page,
    Request,
)
from undetected_playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

from models import Account
from loader import config


class TwitterConnect:
    def __init__(self, account_data: Account):
        self.account = account_data
        self.playwright: Playwright = None  # type: ignore
        self.browser: Browser = None  # type: ignore
        self.context: BrowserContext = None  # type: ignore
        self.page: Page = None  # type: ignore

    async def setup_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
            headless=config.invisible_browser,
            proxy={
                "server": self.account.proxy.server,
                "username": self.account.proxy.login,
                "password": self.account.proxy.password,
            },
        )

        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.context.on("request", self.__handle_response)

    async def __handle_response(self, response: Request) -> None:
        if response.url.startswith("https://nfq-api.thebeacon.gg"):
            if response.headers.get("authorization"):
                self.account.access_token = response.headers.get(
                    "authorization", ""
                ).replace("Bearer ", "")

        # if response.url == "https://nfq-production.us.auth0.com/oauth/token":
        #     try:
        #         # body = (await response.body()).decode("utf-8")
        #         # json_body = json.loads(body)
        #         #
        #         # self.account.access_token = json_body.get("access_token", "")
        #         # self.account.id_token = json_body.get("id_token", "")
        #
        #     except Exception as error:
        #         logger.debug(f"Failed to parse response body: {error} | Reloading page..")
        #         # await self.page.reload()

    async def setup_twitter(self) -> None:
        await self.context.add_cookies(
            [
                {
                    "name": "auth_token",
                    "value": self.account.auth_token,
                    "domain": "twitter.com",
                    "path": "/",
                }
            ]
        )
        await self.page.goto("https://twitter.com/home")

    def __verify_url(self) -> bool:
        if self.page.url.startswith("https://nfq.thebeacon.gg/"):
            if self.page.url.startswith(
                "https://nfq.thebeacon.gg/login?error=access_denied"
            ):
                return False
            return True

        return False

    async def __login(self) -> None:
        await self.page.goto("https://nfq.thebeacon.gg/")
        await self.page.click("text=Login with Twitter")

        try:
            await self.page.click("#allow", timeout=3000)
        except PlaywrightTimeoutError:
            pass

    async def close_browser(self) -> None:
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def collect_beacon_cookie(self) -> None:
        cookies = await self.context.cookies()
        for cookie in cookies:
            if cookie["name"].startswith("ph_phc_tk"):
                self.account.cookies = {cookie["name"]: cookie["value"]}
                return

    async def wait_for_auth(self) -> Account or bool:
        end_time = time.time() + config.max_timeout_for_login_account
        while time.time() < end_time:
            if self.account.access_token:
                await self.collect_beacon_cookie()
                logger.success(
                    f"Twitter: {self.account.auth_token} | Successfully logged in"
                )
                return self.account

            await asyncio.sleep(1)

        logger.error(
            f"Twitter: {self.account.auth_token} | Failed to login, twitter is not eligible or invalid token"
        )
        return False

    async def start_connect(self) -> Account or bool:
        for _ in range(2):
            try:
                logger.info(f"Twitter: {self.account.auth_token} | Logging in..")
                await self.setup_browser()
                await self.setup_twitter()

                await self.__login()
                return await self.wait_for_auth()

            except PlaywrightTimeoutError:
                logger.error(
                    f"Twitter: {self.account.auth_token} | Failed to login, timeout error | Most likely too slow proxy | Retrying.."
                )
                await self.close_browser()
                continue

            except Exception as error:
                logger.error(
                    f"Twitter: {self.account.auth_token} | Failed to login | Error: {error}"
                )
                return False

            finally:
                await self.close_browser()

import pyuseragents

from typing import Literal
from noble_tls import Session, Client

from models import *
from models import LootDropData
from models.api.user_info_v1 import UserInfoV1Data
from src.exceptions.base import APIError
from src.utils import decode_id_token


class TheBeaconAPI:
    API_URL = "https://nfq-api.thebeacon.gg/api"

    def __init__(self, account_data: Account):
        self.account = account_data
        self.session = self.setup_session()

        if self.account.access_token:
            self.token_info = decode_id_token(self.account.access_token)
            # self.session.cookies.update(self.account.cookies)

    @property
    def username(self) -> str:
        return self.token_info["https://thebeacon.gg/username"]

    @property
    def user_id(self) -> str:
        return self.token_info["https://thebeacon.gg/user_id"]

    @property
    def jwt_token(self) -> str:
        return self.session.headers["authorization"].replace("Bearer ", "")

    @property
    async def beacon_user_id(self) -> str:
        return (await self.get_user_info()).data.beaconUserId

    def update_token_info(self, token: str) -> None:
        self.account.id_token = token
        self.token_info = decode_id_token(token)

    def setup_session(self) -> Session:
        session = Session(client=Client.CHROME_120)
        session.random_tls_extension_order = True

        session.timeout_seconds = 15
        session.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
            "authorization": f"Bearer {self.account.access_token}",
            "origin": "https://nfq.thebeacon.gg",
            "referer": "https://nfq.thebeacon.gg/",
            "user-agent": pyuseragents.random(),
        }
        session.proxies = {
            "http": self.account.proxy.as_url,
            "https": self.account.proxy.as_url,
        }
        return session

    async def send_request(
            self,
            request_type: Literal["POST", "GET", "OPTIONS"] = "POST",
            method: str = None,
            json_data: dict = None,
            params: dict = None,
            url: str = None,
            headers: dict = None,
            cookies: dict = None,
            verify: bool = True,
    ):
        def _verify_response(_response: dict) -> dict:
            if all(key in _response for key in ("code", "message")) or "statusCode" in _response:
                if _response["statusCode"] in (404, 500, 503, 403):
                    raise APIError(
                        f"{_response.get('message')} | Method: {method} | Url: {url}"
                    )

            return _response

        if request_type == "POST":
            if not url:
                response = await self.session.post(
                    f"{self.API_URL}{method}",
                    json=json_data,
                    params=params,
                    headers=headers if headers else self.session.headers,
                    cookies=cookies,
                )

            else:
                response = await self.session.post(
                    url,
                    json=json_data,
                    params=params,
                    headers=headers if headers else self.session.headers,
                    cookies=cookies,
                )

        elif request_type == "OPTIONS":
            response = await self.session.options(
                url,
                headers=headers if headers else self.session.headers,
                cookies=cookies,
            )

        else:
            if not url:
                response = await self.session.get(
                    f"{self.API_URL}{method}",
                    params=params,
                    headers=headers if headers else self.session.headers,
                    cookies=cookies,
                )

            else:
                response = await self.session.get(
                    url,
                    params=params,
                    headers=headers if headers else self.session.headers,
                    cookies=cookies,
                )

        if response.cookies.get(name="refreshToken"):
            self.session.cookies.update(response.cookies)

        if verify:
            return _verify_response(response.json())
        return response.text

    async def get_user_info(self) -> UserInfoData:
        response = await self.send_request(
            request_type="GET",
            method=f"/users/{self.user_id}",
        )
        return UserInfoData(**response)

    async def get_quests(self) -> QuestsData:
        _user_info = await self.get_user_info()
        response = await self.send_request(
            request_type="GET",
            method=f"/users/{self.user_id}/events/{_user_info.data.currentEventId}",
        )
        return QuestsData(**response)

    async def verify_quest(self, quest_id: str) -> VerifyQuestData:
        response = await self.send_request(
            request_type="POST",
            method=f"/users/{self.user_id}/quests/{quest_id}/verify",
        )
        return VerifyQuestData(**response)

    async def claim_quest_reward(self, quest_id: str) -> dict:
        return await self.send_request(
            request_type="POST",
            method=f"/users/{self.user_id}/quests/{quest_id}/claim",
        )

    async def approve_username(
            self, data: LoginData, username: str
    ) -> ApproveUsernameData:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "lt",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://app.thebeacon.gg",
            "Referer": "https://app.thebeacon.gg/",
            "User-Agent": self.session.headers["user-agent"],
        }

        response = await self.send_request(
            request_type="POST",
            url="https://api.thebeacon.gg/api/v1/users",
            json_data={
                "signature": data.signed_message,
                "message": data.message,
                "username": username,
            },
            headers=headers,
            cookies={},
        )
        return ApproveUsernameData(**response)

    async def first_login(self, data: LoginData) -> UserInfoV1Data:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "lt",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://app.thebeacon.gg",
            "Referer": "https://app.thebeacon.gg/",
            "User-Agent": self.session.headers["user-agent"],
        }

        response = await self.send_request(
            request_type="POST",
            url="https://api.thebeacon.gg/api/v1/auth/login",
            json_data={
                "signature": data.signed_message,
                "message": data.message,
            },
            headers=headers,
        )
        return UserInfoV1Data(**response)

    async def save_beacon_info(self) -> None:
        return await self.send_request(
            request_type="POST",
            method=f"/users/{self.user_id}/save-beacon-info",
        )

    async def open_chest(self, data: LoginData) -> LootDropData:
        _user_info_v1 = await self.login_v1(data)
        headers = self.session.headers.copy()
        headers.update({"authorization": f"Bearer {_user_info_v1.jwt}"})

        response = await self.send_request(
            request_type="POST",
            url="https://api.thebeacon.gg/api/v1/new-frontiers/open-chest",
            headers=headers,
            cookies={},
        )
        return LootDropData(**response)

    async def refresh_session(self) -> UserInfoV1Data:
        response = await self.send_request(
            request_type="GET",
            url="https://api.thebeacon.gg/api/v1/auth/refresh-session",
        )
        return UserInfoV1Data(**response)

    async def login_v1(self, data: LoginData) -> UserInfoV1Data:
        response = await self.send_request(
            request_type="POST",
            url="https://api.thebeacon.gg/api/v1/auth/login",
            json_data={
                "signature": data.signed_message,
                "message": data.message,
            },
        )
        return UserInfoV1Data(**response)

    async def bind_discord(self, discord_data: LinkedDiscordData) -> dict:
        json_data = {
            'sub': f'CustomDiscord|{self.account.discord_app_id}',
            'provider': 'Discord',
            'username': discord_data.name,
            'nickname': discord_data.nickname,
            'picture': discord_data.picture,
            'data': {
                'email': discord_data.email,
                'email_verified': discord_data.email_verified,
                'nickname': discord_data.nickname,
                'name': discord_data.name,
                'picture': discord_data.picture,
                'premium_type': discord_data.premium_type,
                'locale': discord_data.locale,
            },
        }

        return await self.send_request(
            request_type="POST",
            method=f"/users/{self.user_id}/link",
            json_data=json_data,
        )



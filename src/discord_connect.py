import base64
import hashlib
import re
import secrets

from loguru import logger
from noble_tls import Session
from models import Account, LinkedDiscordData


class DiscordConnect:
    def __init__(self, session: Session, account_data: Account, twitter_sub: str):
        self.account_data = account_data
        self.twitter_sub = twitter_sub
        self.auth_state, self.auth_nonce, self.auth_code_verifier, self.auth_code_challenge = self.generate_auth_data()
        self.auth_session = session

        self.auth_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
            'priority': 'u=0, i',
            'referer': 'https://nfq.thebeacon.gg/',
            'user-agent': session.headers["user-agent"],
        }
        self.discord_auth_headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'lt',
            'authorization': self.account_data.discord_token,
            'referer': 'https://discord.com/',
            'user-agent': session.headers["user-agent"],
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'Europe/Vilnius',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6Imx0IiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL2Rpc2NvcmQuY29tLz9kaXNjb3JkdG9rZW49TVRJek9UY3dNREF5TURFd01qWTVNamc1TmcuR2lVd2g1Llo0UnBIc1h2bnNDRm1wNVFNWEFMbEIzLTBkd1hpUHRwVUt1TEVNIiwicmVmZXJyaW5nX2RvbWFpbiI6ImRpc2NvcmQuY29tIiwicmVmZXJyZXJfY3VycmVudCI6Imh0dHBzOi8vbmZxLnRoZWJlYWNvbi5nZy8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJuZnEudGhlYmVhY29uLmdnIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MzA0MTg3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9',
        }

    @staticmethod
    def __encode_base64(input_string: str) -> str:
        input_bytes = input_string.encode("utf-8")
        base64_bytes = base64.b64encode(input_bytes)
        base64_string = base64_bytes.decode("utf-8")
        return base64_string

    @staticmethod
    def __sha256_to_base64(input_string: str) -> str:
        input_bytes = input_string.encode("utf-8")
        sha256_hash = hashlib.sha256(input_bytes).digest()
        base64_hash = base64.b64encode(sha256_hash).decode("utf-8")
        return base64_hash

    @staticmethod
    def __generate_random_string(length: int = 43) -> str:
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_~."
        random_string = "".join(secrets.choice(characters) for _ in range(length))
        return random_string

    def generate_auth_data(self) -> tuple[str, str, str, str]:
        state = self.__encode_base64(self.__generate_random_string())
        nonce = self.__encode_base64(self.__generate_random_string())
        code_verifier = self.__generate_random_string()
        code_challenge = (
            self.__sha256_to_base64(code_verifier)
            .replace("+", "-")
            .replace("/", "_")
            .replace("=", "")
        )
        return state, nonce, code_verifier, code_challenge

    async def get_state_token(self) -> str:
        params = {
            'client_id': 'KP3Ju3kFcXfYNsguvM6wwetzkzByjSBF',
            'scope': 'openid email profile read:current_user',
            'audience': 'https://nfq-production.us.auth0.com/api/v2/',
            'redirect_uri': 'https://nfq.thebeacon.gg',
            'connection': 'CustomDiscord',
            'response_type': 'code',
            'response_mode': 'web_message',
            'state': self.auth_state,
            'nonce': self.auth_nonce,
            'code_challenge': self.auth_code_challenge,
            'code_challenge_method': 'S256',
            'auth0Client': 'eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMi4yLjQifQ==',
        }

        response = await self.auth_session.get('https://nfq-production.us.auth0.com/authorize', params=params, headers=self.auth_headers)
        response = await self.auth_session.get(response.url, headers=self.auth_headers)

        state = response.url.split("state=")[1].split("&")[0]
        return state

    async def approve_state(self, state: str):
        params = {
            'client_id': '1249318659822846014',
            'response_type': 'code',
            'redirect_uri': 'https://nfq-production.us.auth0.com/login/callback',
            'scope': 'guilds identify email guilds.members.read',
            'state': state,
            'integration_type': '0',
        }

        # application info
        response = await self.auth_session.get('https://discord.com/api/v9/oauth2/authorize', params=params, headers=self.discord_auth_headers)
        if "application" in response.text:
            self.account_data.discord_app_id = response.json()['user']['id']
        else:
            raise Exception("Failed to approve state")


    async def get_auth_code(self, state: str) -> str:
        params = {
            'client_id': '1249318659822846014',
            'response_type': 'code',
            'redirect_uri': 'https://nfq-production.us.auth0.com/login/callback',
            'scope': 'guilds identify email guilds.members.read',
            'state': state,
        }

        json_data = {
            'permissions': '0',
            'authorize': True,
            'integration_type': 0,
        }

        response = await self.auth_session.post(
            'https://discord.com/api/v9/oauth2/authorize',
            params=params,
            headers=self.discord_auth_headers,
            json=json_data,
        )

        response = await self.auth_session.get(response.json()['location'], headers=self.auth_headers, allow_redirects=True)
        code_pattern = r'"code":"([^"]+)"'

        code_match = re.search(code_pattern, response.text)

        if code_match:
            return code_match.group(1)
        else:
            raise Exception("Failed to get authorization code")

    async def approve_auth_code(self, code: str):
        params = {
            'client_id': 'KP3Ju3kFcXfYNsguvM6wwetzkzByjSBF',
            'code_verifier': self.auth_code_verifier,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'https://nfq.thebeacon.gg',
        }

        response = await self.auth_session.post('https://nfq-production.us.auth0.com/oauth/token', headers=self.auth_headers, json=params)
        if "access_token" in response.text:
            return response.json()['access_token'], response.json()['id_token']
        else:
            raise Exception(f"Failed to approve auth code")


    async def pre_bind_discord(self, bearer: str, id_token: str) -> LinkedDiscordData | bool:
        headers = {
            'authority': 'nfq-production.us.auth0.com',
            'accept': '*/*',
            'accept-language': 'uk',
            'authorization': f'Bearer {bearer}',
            'content-type': 'application/json',
            'origin': 'https://nfq.thebeacon.gg',
            'referer': 'https://nfq.thebeacon.gg/',
            'user-agent': self.auth_headers["user-agent"],
        }

        json_data = {
            'link_with': id_token,
        }

        oauth_id = f"oauth2|CustomDiscord|{self.account_data.discord_app_id}"
        response = await self.auth_session.get(f"https://nfq-production.us.auth0.com/api/v2/users/{oauth_id}", headers=headers)

        if "created_at" in response.text:
            await self.auth_session.post(
                f'https://nfq-production.us.auth0.com/api/v2/users/{self.twitter_sub}/identities',
                json=json_data,
            )

            return LinkedDiscordData(**response.json())

        logger.error(f"Twitter: {self.account_data.auth_token} | Failed to pre-bind discord: {response.text}")
        return False


    async def start(self) -> LinkedDiscordData | bool:
        try:
            logger.info(f"{self.account_data.auth_token} | Authorizing discord..")

            state = await self.get_state_token()
            await self.approve_state(state)

            code = await self.get_auth_code(state)
            bearer_token, id_token = await self.approve_auth_code(code)
            return await self.pre_bind_discord(bearer_token, id_token)

        except Exception as error:
            logger.error(f"Twitter: {self.account_data.auth_token} | Failed to pre-bind discord: {error}")
            return False

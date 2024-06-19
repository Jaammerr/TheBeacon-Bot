import asyncio
import base64
import hashlib
import re
import secrets

from Jam_Twitter_API.account import TwitterAccount
from Jam_Twitter_API.errors import *
from loguru import logger
from noble_tls import Session
from models import Account


class TwitterConnectModded:
    def __init__(self, session: Session, account_data: Account):
        self.auth_session = session
        self.auth_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
            'priority': 'u=0, i',
            'referer': 'https://nfq.thebeacon.gg/',
            'user-agent': session.headers["user-agent"],
        }

        self.account_data = account_data
        self.auth_state, self.auth_nonce, self.auth_code_verifier, self.auth_code_challenge = self.generate_auth_data()


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

    @staticmethod
    def bind_account_v1(account: TwitterAccount, oauth_token: str) -> str:

        def get_authenticity_token(
            _oauth_token: str,
        ):
            _params = {
                "oauth_token": _oauth_token,
            }
            _response = account.session.get(
                "https://api.twitter.com/oauth/authenticate", params=_params
            )

            token = re.search(
                r'<input name="authenticity_token" type="hidden" value="([^"]+)"',
                _response.text,
            )
            if token:
                return token.group(1)

            bond_url = re.search(
                r'<a class="maintain-context" href="([^"]+)', _response.text
            )
            if bond_url:
                bond_url = bond_url.group(1).replace("&amp;", "&")
                _oauth_token, _oauth_verifier = bond_url.split("oauth_token=")[1].split(
                    "&oauth_verifier="
                )

                return {
                    "url": bond_url,
                    "oauth_token": _oauth_token,
                    "oauth_verifier": _oauth_verifier,
                }

            raise Exception(
                {
                    "error_message": "Failed to get authenticity token. "
                    "Make sure you are using correct cookies or url."
                }
            )

        def get_confirm_url(_oauth_token: str, _authenticity_token: str) -> str:
            _data = {
                "authenticity_token": _authenticity_token,
                "redirect_after_login": f"https://api.twitter.com/oauth/authorize?oauth_token={_oauth_token}",
                "oauth_token": _oauth_token,
            }

            response = account.session.post(
                "https://api.twitter.com/oauth/authorize",
                data=_data,
                allow_redirects=True,
            )

            _confirm_url = re.search(
                r'<a class="maintain-context" href="([^"]+)', response.text
            )
            if _confirm_url:
                return _confirm_url.group(1).replace("&amp;", "&")

            raise Exception(
                {
                    "error_message": "Failed to get confirm url. "
                    "Make sure you are using correct cookies or url."
                }
            )

        # oauth_token = get_oauth_token()
        authenticity_token = get_authenticity_token(oauth_token)

        if isinstance(authenticity_token, dict):
            return authenticity_token["url"]

        confirm_url = get_confirm_url(oauth_token, authenticity_token)
        return confirm_url

    async def get_oauth_token(self) -> str:
        params = {
            'client_id': 'KP3Ju3kFcXfYNsguvM6wwetzkzByjSBF',
            'scope': 'openid email profile read:current_user update:current_user_identities',
            'audience': 'https://nfq-production.us.auth0.com/api/v2/',
            'redirect_uri': 'https://nfq.thebeacon.gg/login',
            'connection': 'twitter',
            'response_type': 'code',
            'response_mode': 'query',
            'state': self.auth_state,
            'nonce': self.auth_nonce,
            'code_challenge': self.auth_code_challenge,
            'code_challenge_method': 'S256',
            'auth0Client': 'eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMi4yLjQifQ==',
        }

        response = await self.auth_session.get('https://nfq-production.us.auth0.com/authorize', params=params, headers=self.auth_headers)
        response.raise_for_status()

        oauth_token = response.url.split("oauth_token=")[1].split("&")[0]
        return oauth_token

    async def get_auth_code(self, url: str) -> str:
        response = await self.auth_session.get(url)
        response.raise_for_status()

        try:
            code, state = response.url.split("code=")[1].split("&state=")
            return code
        except IndexError:
            raise Exception(f"twitter is not eligible")

    async def get_access_token(self, code: str) -> None:
        json_data = {
            "client_id": "KP3Ju3kFcXfYNsguvM6wwetzkzByjSBF",
            "code_verifier": self.auth_code_verifier,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://nfq.thebeacon.gg/login"
        }

        response = await self.auth_session.post('https://nfq-production.us.auth0.com/oauth/token', headers=self.auth_headers, json=json_data)
        response.raise_for_status()

        data = response.json()
        if data.get("access_token"):
            self.account_data.access_token = data["access_token"]
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    async def start(self) -> Account | bool:
        try:
            logger.info(f"Twitter: {self.account_data.auth_token} | Authorizing..")
            twitter_account = TwitterAccount.run(auth_token=self.account_data.auth_token, proxy=self.account_data.proxy.as_url)

            oauth_token = await self.get_oauth_token()
            authorize_url = self.bind_account_v1(twitter_account, oauth_token)

            auth_code = await self.get_auth_code(authorize_url)
            await self.get_access_token(auth_code)

            logger.success(f"Twitter: {self.account_data.auth_token} | Authorized")
            return self.account_data

        except TwitterAccountSuspended:
            logger.error(f"Twitter: {self.account_data.auth_token} | Account Suspended")

        except TwitterError as error:
            logger.error(f"Twitter: {self.account_data.auth_token} | Failed to authorize: {error.error_message} | {error.error_code}")

        except Exception as error:
            logger.error(f"Twitter: {self.account_data.auth_token} | Error while authorizing: {error}")

        return False

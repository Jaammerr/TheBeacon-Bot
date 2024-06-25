from better_proxy import Proxy
from pydantic import BaseModel, PositiveInt, HttpUrl


class Account(BaseModel):
    auth_token: str
    discord_token: str | None = None
    discord_app_id: str | None = None
    access_token: str | None = None
    id_token: str | None = None
    cookies: dict[str, str] | None = None
    proxy: Proxy
    mnemonic: str | None = None


class Config(BaseModel):
    accounts: list[Account]
    eth_rpc: HttpUrl
    threads: PositiveInt
    delay_between_quests: PositiveInt
    delay_between_quests_verification: PositiveInt
    delay_between_chests: PositiveInt

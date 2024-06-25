from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Identity(BaseModel):
    provider: str
    user_id: str
    connection: str
    isSocial: bool


class LinkedDiscordData(BaseModel):
    created_at: str
    email: str
    email_verified: bool
    identities: List[Identity]
    locale: str
    name: str
    nickname: str
    picture: str
    premium_type: int
    updated_at: str
    user_id: str
    last_ip: str
    last_login: str
    logins_count: int

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class User(BaseModel):
    id: str
    address: str
    referralCode: str
    username: str
    displayUsername: str
    isAdmin: bool
    currentCharacterId: Any
    mintingAddress: Any
    isWhitelisted: bool
    luxShards: int
    scalesOfEmerion: int
    zeeverseTickets: int
    trilightTickets: int


class UserInfoV1Data(BaseModel):
    user: User
    jwt: str

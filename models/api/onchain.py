from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel


class LoginData(BaseModel):
    message: str
    signed_message: str


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


class ApproveUsernameData(BaseModel):
    user: User
    jwt: str

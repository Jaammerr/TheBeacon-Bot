from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Identity(BaseModel):
    provider: str


class UserEventItem(BaseModel):
    xp: int
    referralXp: int
    openedChests: int
    progressShareId: str


class Role(BaseModel):
    commissionRate: float
    refereeIncentive: int


class Data(BaseModel):
    id: str
    externalAuthId: str
    beaconUserId: str | None = None
    address: str | None = None
    currentEventId: str
    referralCode: str
    createdAt: str
    updatedAt: str
    roleType: str
    identities: List[Identity]
    UserEvent: List[UserEventItem]
    role: Role


class UserInfoData(BaseModel):
    data: Data

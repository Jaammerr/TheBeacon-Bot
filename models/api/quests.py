from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class PathSegment(BaseModel):
    id: str
    col: int
    row: int
    type: str
    isFinal: bool
    clip: str


class Child(BaseModel):
    parentId: str
    childId: str
    pathSegments: List[PathSegment]


class UserQuestItem(BaseModel):
    status: str


class Quest(BaseModel):
    type: str
    id: str
    col: int
    row: int
    tilesetRow: int
    shortDescription: str
    xp: int
    availableAt: Optional[str]
    endsAt: Any
    children: List[Child]
    UserQuest: List[UserQuestItem]


class Data(BaseModel):
    id: str
    title: str
    description: Any
    isDefault: bool
    startingQuestId: str
    availableQuests: int
    endsAt: Any
    createdAt: str
    updatedAt: str
    quests: List[Quest]
    lastCompletedNodeId: str | None = None


class QuestsData(BaseModel):
    data: Data

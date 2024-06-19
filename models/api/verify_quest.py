from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class Data(BaseModel):
    questId: str
    userId: str
    status: str
    verifyJobId: str | None = None
    verifyStartedAt: str | None = None
    verifyFinishedAt: str | None = None
    verifyErrorResponse: Any | None = None
    completedAt: Any
    createdAt: str
    updatedAt: str


class VerifyQuestData(BaseModel):
    data: Data

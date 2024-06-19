from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    itemType: str
    kind: str
    ownerId: str


class ShowcaseItem(BaseModel):
    id: str
    count: int


class LootDrop(BaseModel):
    item: Item
    showcaseItems: List[ShowcaseItem]


class LootDropData(BaseModel):
    lootDrops: List[LootDrop]

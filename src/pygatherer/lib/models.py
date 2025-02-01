from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathurl import URL


@dataclass(frozen=True)
class Cost:
    type: str
    value: int | None = None
    colors: list[str] | None = None


@dataclass(frozen=True)
class Card:
    name: str
    cost: list[Cost]
    color_indicator: list[str]
    subtypes: list[str]
    types: list[str]
    supertypes: list[str]
    expansion: str
    image_url: URL
    power: str
    loyalty: str
    toughness: str
    rules: list[str]
    multiverse_id: int

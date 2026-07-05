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
    cost: list[Cost] | None
    color_indicator: list[str] | None
    subtypes: list[str]
    types: list[str]
    supertypes: list[str]
    expansion: str
    image_url: URL
    power: str | None
    loyalty: str | None
    toughness: str | None
    rules: list[str] | None
    multiverse_id: int

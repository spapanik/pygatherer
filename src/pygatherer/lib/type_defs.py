from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from pygatherer.lib.models import Cost


class RightColumnInfo(TypedDict):
    name: str
    expansion: str
    supertypes: list[str]
    types: list[str]
    subtypes: list[str]
    cost: list[Cost] | None
    color_indicator: list[str] | None
    loyalty: str | None
    rules: list[str] | None
    power: str | None
    toughness: str | None

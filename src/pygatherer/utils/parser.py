from __future__ import annotations

import re
from dataclasses import dataclass
from http import HTTPStatus
from typing import TYPE_CHECKING, TypedDict

import requests
from bs4 import BeautifulSoup
from pathurl import URL, Query

from pygatherer.lib.exceptions import MissingTagError, MultipleAttributeError
from pygatherer.utils.constants import CARD_DETAILS_URL, CARD_URL, SUPERTYPES

if TYPE_CHECKING:
    from bs4.element import Tag


FALSE_TAG = re.compile(r"^<\?xml.*?\?>")


class LeftColumnInfo(TypedDict):
    image_url: str
    multiverse_id: int
    variation: int | None


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
    variation: str
    rules: list[str]
    multiverse_id: int


def parse_cost_image(cost_img: Tag) -> Cost:
    alt = cost_img["alt"]
    if not isinstance(alt, str):
        raise MultipleAttributeError(cost_img, "alt")

    try:
        cost = int(alt)
    except ValueError:
        pass
    else:
        return Cost(type="Colorless", value=cost)

    if alt.startswith("Phyrexian"):
        _, color = alt.split()
        return Cost(type="Phyrexian", colors=[color])

    if " or " in alt:
        first, second = alt.split(" or ")
        if first == "Two":
            return Cost(type="Monocolored Hybrid", colors=[second])
        return Cost(type="Hybrid", colors=[first, second])

    return Cost(type="Colored", colors=[alt])


def parse_types(type_info: str) -> tuple[list[str], list[str], list[str]]:
    main_types, *subtypes = type_info.split("—")
    supertypes = []
    types = []
    for main_type in main_types.split():
        main_type.strip()
        if main_type in SUPERTYPES:
            supertypes.append(main_type)
        else:
            types.append(main_type)

    if subtypes:
        subtype_info = subtypes[0]
        if "Plane" in types:
            subtypes = [subtype_info.strip()]
        else:
            subtypes = [subtype.strip() for subtype in subtype_info.split()]

    return supertypes, types, subtypes


def parse_cost(cost: Tag) -> list[Cost]:
    return [parse_cost_image(cost_img) for cost_img in cost.select("img")]


def parse_rules(rules: Tag) -> list[str]:
    return [rule.text for rule in rules.select("div.cardtextbox")]


def parse_pt(pt: str) -> tuple[str, str]:
    power, toughness = pt.split("/")
    return power.strip(), toughness.strip()


def get_id_from_image_url(image_url: URL) -> str:
    if (id_list := image_url.query.get("multiverseid")) is None:
        msg = f"Image url {image_url} does not contain multiverseid"
        raise ValueError(msg)
    return id_list[0]


def parse_left_col(left_col: Tag) -> LeftColumnInfo:
    img = left_col.img
    if img is None:
        raise MissingTagError(left_col, "img")

    img_src = img["src"]
    if not isinstance(img_src, str):
        raise MultipleAttributeError(img, "src")

    image_url = CARD_URL.join(img_src)
    multiverse_id = get_id_from_image_url(image_url)
    variation = None
    variations_div = left_col.select_one("div.variations")
    if variations_div is None:
        raise MissingTagError(left_col, "div.variations")
    variations = [
        variation
        for variation in variations_div.select("a")
        if variation["id"] == multiverse_id
    ]

    if variations:
        variation = int(variations[0].text)

    return {
        "image_url": image_url.string,
        "multiverse_id": int(multiverse_id),
        "variation": variation,
    }


def parse_right_col(right_col: Tag) -> RightColumnInfo:
    rows = {
        label.text.strip(): value
        for row in right_col.select("div.row")
        if (label := row.select_one(".label")) and (value := row.select_one(".value"))
    }
    supertypes, types, subtypes = parse_types(rows["Types:"].text.strip())
    cost = color_indicator = loyalty = rules = power = toughness = None

    if "Mana Cost:" in rows:
        cost = parse_cost(rows["Mana Cost:"])

    if "Color Indicator:" in rows:
        color_indicator = [
            indication.strip()
            for indication in rows["Color Indicator:"].text.split(",")
        ]

    if "Loyalty:" in rows:
        loyalty = rows["Loyalty:"].text.strip()

    if "Card Text:" in rows:
        rules = parse_rules(rows["Card Text:"])

    if "P/T:" in rows:
        power, toughness = parse_pt(rows["P/T:"].text.strip())

    return {
        "name": rows["Card Name:"].text.strip(),
        "expansion": rows["Expansion:"].select("a")[1].text.strip(),
        "supertypes": supertypes,
        "types": types,
        "subtypes": subtypes,
        "cost": cost,
        "color_indicator": color_indicator,
        "loyalty": loyalty,
        "rules": rules,
        "power": power,
        "toughness": toughness,
    }


def parse_gatherer_content(content: str, gatherer_url: URL) -> Card:
    soup = BeautifulSoup(content, "lxml")
    multiverse_id = int(get_id_from_image_url(gatherer_url))
    faces_table = soup.select_one("table.cardComponentTable")
    if not faces_table:
        raise MissingTagError(soup, "table.cardComponentTable")
    faces = faces_table.select("table.cardDetails")
    for face in faces:
        right_col = face.select_one("td.rightCol")
        if right_col is None:
            raise MissingTagError(face, "td.rightCol")

        left_col = face.select_one("td.leftCol")
        if left_col is None:
            left_col = face.select_one("td.plane")
        if left_col is None:
            raise MissingTagError(face, "td.leftCol/td.plane")

        card_info = {**parse_left_col(left_col), **parse_right_col(right_col)}
        if card_info["multiverse_id"] == multiverse_id:
            return Card(**card_info)  # type: ignore[arg-type]

    msg = "No race is having the multiverse id."
    raise RuntimeError(msg)


def get_card_by_id(multiverse_id: int) -> Card:
    gatherer_url = CARD_DETAILS_URL.replace(
        query=Query(f"multiverseid={multiverse_id}")
    )

    response = requests.get(
        gatherer_url.string, allow_redirects=False, timeout=(60, 120)
    )
    if response.status_code >= HTTPStatus.MULTIPLE_CHOICES:
        msg = f"No card with multiverse_id {multiverse_id} exists"
        raise ValueError(msg)
    content = response.content.decode("utf-8")
    new_content = re.sub(FALSE_TAG, "", content, count=1)
    return parse_gatherer_content(new_content, gatherer_url)

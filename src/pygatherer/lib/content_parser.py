from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pathurl import Query

from pygatherer.lib.constants import CARD_IMAGE_URL, CARD_URL, Supertype
from pygatherer.lib.exceptions import MissingAttributeError, MissingTagError
from pygatherer.lib.models import Card, Cost

if TYPE_CHECKING:
    from bs4.element import Tag
    from pathurl import URL

    from pygatherer.lib.type_defs import RightColumnInfo

FALSE_TAG = re.compile(r"^<\?xml.*?\?>")


def parse_cost_image(cost_img: Tag) -> Cost:
    alt = cost_img.get("alt")
    if not isinstance(alt, str):
        raise MissingAttributeError(cost_img, "alt")

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
        if main_type in Supertype.values():
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


def get_id_from_image_url(image_url: URL) -> int:
    if (id_list := image_url.query.get("multiverseid")) is None:
        msg = f"Image url {image_url} does not contain multiverseid"
        raise ValueError(msg)
    return int(id_list[0])


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


def choose_face(faces: list[Tag], multiverse_id: int) -> Tag:
    for face in faces:
        img = face.img
        if img is None:
            continue
        img_src = img.get("src")
        if not isinstance(img_src, str):
            continue
        image_url = CARD_URL.join(img_src)
        if multiverse_id != get_id_from_image_url(image_url):
            continue
        return face

    msg = "No face is having this multiverse id."
    raise RuntimeError(msg)


def parse_gatherer_content(soup: Tag, multiverse_id: int) -> Card:
    faces_table = soup.select_one("table.cardComponentTable")
    if not faces_table:
        raise MissingTagError(soup, "table.cardComponentTable")

    faces = faces_table.select("table.cardDetails")
    face = choose_face(faces, multiverse_id)
    right_col = face.select_one("td.rightCol")
    if right_col is None:
        raise MissingTagError(face, "td.rightCol")
    right_col_info = parse_right_col(right_col)

    image_url = CARD_IMAGE_URL.replace(
        query=Query.from_dict(type="card", multiverseid=str(multiverse_id))
    )
    return Card(multiverse_id=multiverse_id, image_url=image_url, **right_col_info)  # type: ignore[arg-type]

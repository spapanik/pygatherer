from __future__ import annotations

import pytest
from pathurl import Query

from pygatherer.lib import content_parser
from pygatherer.lib.constants import BASE_URL, CARD_DETAILS_URL
from pygatherer.lib.exceptions import MissingAttributeError

from tests.helpers.tags import create_tag


@pytest.mark.parametrize(
    ("alt", "colors", "type_", "value"),
    [
        ("1", None, "Colorless", 1),
        ("Black", ["Black"], "Colored", None),
        ("Phyrexian Black", ["Black"], "Phyrexian", None),
        ("Two or Black", ["Black"], "Monocolored Hybrid", None),
        ("Black or Green", ["Black", "Green"], "Hybrid", None),
    ],
)
def test_parse_cost_image(
    alt: str, colors: list[str], type_: str, value: int | None
) -> None:
    tag = create_tag("img", alt=alt)
    cost = content_parser.parse_cost_image(tag)
    assert cost.colors == colors
    assert cost.type == type_
    assert cost.value == value


def test_parse_image_without_alt() -> None:
    tag = create_tag("img", inner_text="Black or Green")
    with pytest.raises(MissingAttributeError):
        content_parser.parse_cost_image(tag)


def test_parse_cost() -> None:
    div = create_tag("div")
    div.append(create_tag("img", alt="3"))
    cost = content_parser.parse_cost(div)
    assert len(cost) == 1


def test_parse_rules() -> None:
    div = create_tag("div")
    div.append(create_tag("div", class_="cardtextbox", inner_text="Flying"))
    div.append(
        create_tag(
            "div",
            class_="cardtextbox",
            inner_text="When Angel of Despair enters, destroy target permanent.",
        )
    )
    rules = content_parser.parse_rules(div)
    assert len(rules) == 2


@pytest.mark.parametrize(
    ("type_info", "supertypes", "types", "subtypes"),
    [
        ("Enchantment  — Aura", [], ["Enchantment"], ["Aura"]),
        ("Legendary Planeswalker — Jace", ["Legendary"], ["Planeswalker"], ["Jace"]),
        ("Plane — Kephalai", [], ["Plane"], ["Kephalai"]),
        ("Artifact Land", [], ["Artifact", "Land"], []),
    ],
)
def test_parse_types(
    type_info: str, supertypes: list[str], types: list[str], subtypes: list[str]
) -> None:
    parsed_supertypes, parsed_types, parsed_subtypes = content_parser.parse_types(
        type_info
    )
    assert parsed_supertypes == supertypes
    assert parsed_types == types
    assert parsed_subtypes == subtypes


@pytest.mark.parametrize(
    ("text", "power", "toughness"), [("3 / 3", "3", "3"), ("* / *", "*", "*")]
)
def test_parse_pt(text: str, power: str, toughness: str) -> None:
    parsed_power, parsed_toughness = content_parser.parse_pt(text)
    assert parsed_power == power
    assert parsed_toughness == toughness


def test_get_id_from_image_url() -> None:
    gatherer_url = CARD_DETAILS_URL.replace(query=Query("multiverseid=382866"))
    card_id = content_parser.get_id_from_image_url(gatherer_url)
    assert card_id == 382866


def test_get_id_from_wrong_url() -> None:
    with pytest.raises(ValueError, match="does not contain multiverseid"):
        content_parser.get_id_from_image_url(BASE_URL)

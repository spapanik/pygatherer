from __future__ import annotations

from unittest import mock

import pytest
from pathurl import Query

from pygatherer.lib import content_parser
from pygatherer.lib.constants import BASE_URL, CARD_DETAILS_URL, CARD_IMAGE_URL
from pygatherer.lib.exceptions import MissingAttributeError, MissingTagError
from pygatherer.lib.models import Cost

from tests.helpers.tags import create_right_col, create_tag


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
    with pytest.raises(MissingAttributeError, match="`alt`"):
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


def test_parse_gatherer_content_missing_table() -> None:
    tag = create_tag("div")
    with pytest.raises(MissingTagError, match="`table.cardComponentTable`"):
        content_parser.parse_gatherer_content(tag, 382866)


def test_parse_gatherer_content_missing_info_in_table() -> None:
    tag = create_tag("div")
    table = create_tag("table", class_="cardComponentTable")
    tag.append(table)
    with pytest.raises(RuntimeError):
        content_parser.parse_gatherer_content(tag, 382866)


@mock.patch(
    "pygatherer.lib.content_parser.choose_face", return_value=create_tag("table")
)
def test_parse_gatherer_content_missing_card_details(
    mock_choose_face: mock.MagicMock,
) -> None:
    tag = create_tag("div")
    table = create_tag("table", class_="cardComponentTable")
    nested = create_tag("table", class_="cardDetails")
    table.append(nested)
    tag.append(table)
    with pytest.raises(MissingTagError, match="`td.rightCol`"):
        content_parser.parse_gatherer_content(tag, 382866)
    assert mock_choose_face.call_count == 1
    calls = [mock.call([nested], 382866)]
    assert mock_choose_face.call_args_list == calls


@mock.patch("pygatherer.lib.content_parser.parse_right_col")
@mock.patch("pygatherer.lib.content_parser.choose_face")
def test_parse_gatherer_content(
    mock_choose_face: mock.MagicMock, mock_parse_right_col: mock.MagicMock
) -> None:
    tag = create_tag("div")
    table = create_tag("table", class_="cardComponentTable")
    nested = create_tag("table", class_="cardDetails")
    right_col = create_tag("td", class_="rightCol")
    nested.append(right_col)
    table.append(nested)
    tag.append(table)
    mock_parse_right_col.return_value = {
        "name": "Angel of Despair",
        "expansion": "Commander 2013",
        "supertypes": [],
        "types": ["Creature"],
        "subtypes": ["Angel"],
        "cost": [],
        "color_indicator": [],
        "loyalty": None,
        "rules": [],
        "power": "5",
        "toughness": "5",
    }
    content_parser.parse_gatherer_content(tag, 382866)
    assert mock_choose_face.call_count == 1
    calls = [mock.call([nested], 382866)]
    assert mock_choose_face.call_args_list == calls
    assert mock_parse_right_col.call_count == 1


def test_choose_face_wrong_multiverse_id() -> None:
    face_1 = create_tag("table")
    face_2 = create_tag("table")
    img_2 = create_tag("img")
    face_2.append(img_2)
    face_3 = create_tag("table")
    url = CARD_IMAGE_URL.replace(query=Query.from_dict(multiverseid="1"))
    img_3 = create_tag("img", src=url.string)
    face_3.append(img_3)
    faces = [face_1, face_2, face_3]
    with pytest.raises(RuntimeError, match="No face is having this multiverse id."):
        content_parser.choose_face(faces, 382866)


def test_choose_face() -> None:
    face = create_tag("table")
    url = CARD_IMAGE_URL.replace(query=Query.from_dict(multiverseid="382866"))
    img = create_tag("img", src=url.string)
    face.append(img)
    faces = [face]
    chosen_face = content_parser.choose_face(faces, 382866)
    assert chosen_face == face


def test_right_col_artifact() -> None:
    tag = create_right_col(
        name="Black Lotus",
        expansion="Vintage Masters",
        types="Artifact",
        mana_cost="0",
        rules=["Tap, Sacrifice Black Lotus: Add three mana of any one color."],
    )
    card_info = content_parser.parse_right_col(tag)
    assert card_info["name"] == "Black Lotus"
    assert card_info["expansion"] == "Vintage Masters"
    assert card_info["supertypes"] == []
    assert card_info["types"] == ["Artifact"]
    assert card_info["subtypes"] == []
    assert card_info["cost"] == [Cost(type="Colorless", value=0)]
    assert card_info["rules"] == [
        "Tap, Sacrifice Black Lotus: Add three mana of any one color."
    ]
    assert card_info["color_indicator"] is None
    assert card_info["loyalty"] is None
    assert card_info["power"] is None
    assert card_info["toughness"] is None


def test_right_col_planeswalker() -> None:
    tag = create_right_col(
        name="Jace Beleren",
        expansion="Lorwyn",
        types="Legendary Planeswalker — Jace",
        mana_cost="1UU",
        rules=[
            "+2: Each player draws a card.",
            "-1: Target player draws a card.",
            "-10: Target player puts the top twenty cards of their library into their graveyard.",
        ],
        loyalty="3",
    )
    card_info = content_parser.parse_right_col(tag)
    assert card_info["name"] == "Jace Beleren"
    assert card_info["expansion"] == "Lorwyn"
    assert card_info["supertypes"] == ["Legendary"]
    assert card_info["types"] == ["Planeswalker"]
    assert card_info["subtypes"] == ["Jace"]
    assert card_info["cost"] == [
        Cost(type="Colorless", value=1),
        Cost(type="Colored", colors=["Blue"]),
        Cost(type="Colored", colors=["Blue"]),
    ]
    assert card_info["rules"] == [
        "+2: Each player draws a card.",
        "-1: Target player draws a card.",
        "-10: Target player puts the top twenty cards of their library into their graveyard.",
    ]
    assert card_info["color_indicator"] is None
    assert card_info["loyalty"] == "3"
    assert card_info["power"] is None
    assert card_info["toughness"] is None


def test_right_col_land() -> None:
    tag = create_right_col(
        name="Island",
        expansion="Limited Edition Alpha",
        types="Basic Land — Island",
    )
    card_info = content_parser.parse_right_col(tag)
    assert card_info["name"] == "Island"
    assert card_info["expansion"] == "Limited Edition Alpha"
    assert card_info["supertypes"] == ["Basic"]
    assert card_info["types"] == ["Land"]
    assert card_info["subtypes"] == ["Island"]
    assert card_info["cost"] is None
    assert card_info["rules"] is None
    assert card_info["color_indicator"] is None
    assert card_info["loyalty"] is None
    assert card_info["power"] is None
    assert card_info["toughness"] is None


def test_right_col_with_heft() -> None:
    tag = create_right_col(
        name="Amoeboid Changeling",
        expansion="Jumpstart 2022",
        types="Creature — Shapeshifter",
        mana_cost="1U",
        rules=[
            "Changeling.",
            "Tap: Target creature gains all creature types until end of turn.",
            "Tap: Target creature loses all creature types until end of turn.",
        ],
        power="1",
        toughness="1",
    )
    card_info = content_parser.parse_right_col(tag)
    assert card_info["name"] == "Amoeboid Changeling"
    assert card_info["expansion"] == "Jumpstart 2022"
    assert card_info["supertypes"] == []
    assert card_info["types"] == ["Creature"]
    assert card_info["subtypes"] == ["Shapeshifter"]
    assert card_info["cost"] == [
        Cost(type="Colorless", value=1),
        Cost(type="Colored", colors=["Blue"]),
    ]
    assert card_info["rules"] == [
        "Changeling.",
        "Tap: Target creature gains all creature types until end of turn.",
        "Tap: Target creature loses all creature types until end of turn.",
    ]
    assert card_info["color_indicator"] is None
    assert card_info["loyalty"] is None
    assert card_info["power"] == "1"
    assert card_info["toughness"] == "1"


def test_right_col_with_indicator() -> None:
    tag = create_right_col(
        name="Mishra, Lost to Phyrexia",
        expansion="The Brothers' War",
        types="Legendary Artifact Creature — Phyrexian Artificer",
        rules=[
            "Whenever Mishra, Lost to Phyrexia enters or attacks, choose three —",
            "• Target opponent discards two cards.",
            "• Mishra deals 3 damage to any target.",
            "• Destroy target artifact or planeswalker.",
            "• Creatures you control gain menace and trample until end of turn.",
            "• Creatures you don't control get -1/-1 until end of turn.",
            "• Create two tapped Powerstone tokens.",
        ],
        color_indicator=["Black", "Red"],
        power="9",
        toughness="9",
    )
    card_info = content_parser.parse_right_col(tag)
    assert card_info["name"] == "Mishra, Lost to Phyrexia"
    assert card_info["expansion"] == "The Brothers' War"
    assert card_info["supertypes"] == ["Legendary"]
    assert card_info["types"] == ["Artifact", "Creature"]
    assert card_info["subtypes"] == ["Phyrexian", "Artificer"]
    assert card_info["cost"] is None
    assert card_info["rules"] == [
        "Whenever Mishra, Lost to Phyrexia enters or attacks, choose three —",
        "• Target opponent discards two cards.",
        "• Mishra deals 3 damage to any target.",
        "• Destroy target artifact or planeswalker.",
        "• Creatures you control gain menace and trample until end of turn.",
        "• Creatures you don't control get -1/-1 until end of turn.",
        "• Create two tapped Powerstone tokens.",
    ]
    assert card_info["color_indicator"] == ["Black", "Red"]
    assert card_info["loyalty"] is None
    assert card_info["power"] == "9"
    assert card_info["toughness"] == "9"

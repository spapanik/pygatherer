from pygatherer.utils import card_parser


def test_parse_types() -> None:
    supertypes, types, subtypes = card_parser.parse_types("Enchantment  — Aura")
    assert supertypes == []
    assert types == ["Enchantment"]
    assert subtypes == ["Aura"]

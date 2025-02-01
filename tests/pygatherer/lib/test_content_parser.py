from pygatherer.lib import content_parser


def test_parse_types() -> None:
    supertypes, types, subtypes = content_parser.parse_types("Enchantment  — Aura")
    assert supertypes == []
    assert types == ["Enchantment"]
    assert subtypes == ["Aura"]

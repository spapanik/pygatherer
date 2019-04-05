from pygatherer.utils import parser


def test_parse_types():
    supertypes, types, subtypes = parser.parse_types("Enchantment  — Aura")
    assert supertypes == []
    assert types == ["Enchantment"]
    assert subtypes == ["Aura"]

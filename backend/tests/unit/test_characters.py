"""Unit tests for the fixed v1 character cast (FR-002, FR-007, SC-002)."""

import re

import pytest

from app.schemas.comic import Character
from app.services.characters import ADA, BOB, CARA, CHARACTER_IDS, CHARACTERS, get_character

HEX_COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")


def test_cast_has_exactly_three_characters() -> None:
    assert len(CHARACTERS) == 3


def test_cast_ids_are_distinct_and_fixed() -> None:
    ids = {character.id for character in CHARACTERS}
    assert ids == {"ada", "bob", "cara"}
    assert len(ids) == len(CHARACTERS)


def test_character_names_are_distinct() -> None:
    names = {character.name for character in CHARACTERS}
    assert len(names) == len(CHARACTERS)


def test_each_character_is_typed_schema() -> None:
    for character in CHARACTERS:
        assert isinstance(character, Character)


def test_silhouettes_are_the_distinct_v1_set() -> None:
    silhouettes = {character.silhouette for character in CHARACTERS}
    assert silhouettes == {"circle", "square", "triangle"}


def test_palettes_are_valid_lowercase_hex() -> None:
    for character in CHARACTERS:
        palette = character.palette
        assert HEX_COLOR_RE.fullmatch(palette.primary)
        assert HEX_COLOR_RE.fullmatch(palette.secondary)
        assert HEX_COLOR_RE.fullmatch(palette.accent)


def test_palettes_are_pairwise_distinct() -> None:
    palettes = [
        (character.palette.primary, character.palette.secondary, character.palette.accent)
        for character in CHARACTERS
    ]
    assert len(set(palettes)) == len(palettes)


def test_primary_colors_are_pairwise_distinct() -> None:
    primaries = {character.palette.primary for character in CHARACTERS}
    assert len(primaries) == len(CHARACTERS)


def test_character_ids_match_aggregate() -> None:
    assert CHARACTER_IDS == frozenset(character.id for character in CHARACTERS)


def test_get_character_returns_known_cast_member() -> None:
    assert get_character("ada") is ADA
    assert get_character("bob") is BOB
    assert get_character("cara") is CARA


def test_get_character_raises_on_unknown_id() -> None:
    with pytest.raises(ValueError, match="unknown character id"):
        get_character("nope")
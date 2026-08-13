"""Unit tests for the analyzer's shouting detection and balloon shape (T007, FR-004).

Pins the research.md §2 rule: a message is ``shout`` when at least 50% of its
alphabetic characters (``str.isalpha()``) are uppercase AND it contains at least 3
alphabetic characters; otherwise ``speech``. A message with zero alphabetic
characters is never a ``shout``.
"""

import pytest

from app.schemas.comic import BalloonShape
from app.services.analyzer import balloon_shape, is_shouting


@pytest.mark.parametrize(
    "text",
    [
        "AWESOME!!",
        "AWESOME!! 😃",
        "¡HOLA!",
        "I DID NOT EXPECT THAT.",
        "ÉÉÉ",
        "MiXeD",
        "WHY?!",
    ],
)
def test_is_shouting_all_uppercase(text: str) -> None:
    assert is_shouting(text)


@pytest.mark.parametrize(
    "text",
    [
        "Hello 👋",
        "hello",
        "mIxEd",
        "No",
        "Why?!",
        "not this time",
        "NO",
        "!!!",
        "12345",
        "",
        "漢漢漢",
        "Ωμν",
    ],
)
def test_is_shouting_not_shouting(text: str) -> None:
    assert not is_shouting(text)


def test_exactly_50_percent_uppercase_is_shouting() -> None:
    assert is_shouting("AbCdEf")


def test_below_50_percent_uppercase_is_speech() -> None:
    assert not is_shouting("aBcDeFg")


def test_exactly_three_alphabetic_is_shouting() -> None:
    assert is_shouting("abc".upper())


def test_fewer_than_three_alphabetic_is_not_shouting() -> None:
    assert not is_shouting("AB")
    assert not is_shouting("A!")
    assert not is_shouting("🇺🇸")


def test_non_ascii_letters_count_as_alphabetic() -> None:
    assert is_shouting("ÉÉÉ")


def test_zero_alphabetic_never_shouting() -> None:
    assert not is_shouting("!!! 123 ???")


def test_balloon_shape_shout_for_shouting_text() -> None:
    assert balloon_shape("AWESOME!!") is BalloonShape.shout


def test_balloon_shape_speech_for_normal_text() -> None:
    assert balloon_shape("Hello there") is BalloonShape.speech


def test_balloon_shape_speech_for_zero_alphabetic() -> None:
    assert balloon_shape("!!!") is BalloonShape.speech
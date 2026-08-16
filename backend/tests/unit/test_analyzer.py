"""Unit tests for the analyzer's shouting detection, balloon shape, and emotions.

Shouting/balloon (T007, FR-004): a message is ``shout`` when at least 50% of its
alphabetic characters (``str.isalpha()``) are uppercase AND it contains at least 3
alphabetic characters; otherwise ``speech``. A message with zero alphabetic
characters is never a ``shout``.

Emotion resolution (T019, FR-003/FR-010): ``resolve_expression`` pins the exact
word sets in research.md §1, matched by whole-word boundary on lowercased text
(``yay`` fires inside ``yesterday``); no signal falls back to ``neutral``;
conflicting signals resolve by precedence anger > surprise > joy > sadness.

Thought detection (T023, FR-004): ``is_thought`` recognizes a leading ``[thought]``
marker on the trimmed text, case-insensitively. In ``balloon_shape``, thought
precedes shouting so a ``[thought]`` ALL-CAPS message stays ``thought`` (US3,
research.md §3).
"""

import pytest

from app.schemas.comic import BalloonShape, Expression
from app.services.analyzer import (
    balloon_shape,
    is_shouting,
    is_thought,
    resolve_expression,
)


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


@pytest.mark.parametrize(
    "text",
    [
        "[thought] I wonder if anyone noticed",
        "  [thought] stay quiet... keep it calm  ",
        "[THOUGHT] what if this backfires",
        "[Thought] maybe she already left",
        "[tHoUgHt] hmm",
    ],
)
def test_is_thought_recognizes_leading_marker(text: str) -> None:
    assert is_thought(text)


@pytest.mark.parametrize(
    "text",
    [
        "I thought this would be fine",
        "thought for the day",
        "stay quiet... keep it calm",
        "[thoughts] bubbling up",
        "",
    ],
)
def test_is_thought_rejects_non_marker_text(text: str) -> None:
    assert not is_thought(text)


def test_balloon_shape_thought_for_marked_message() -> None:
    assert balloon_shape("[thought] I wonder if anyone noticed") is BalloonShape.thought


def test_balloon_shape_thought_marker_is_case_insensitive() -> None:
    assert balloon_shape("[THOUGHT] what if this backfires") is BalloonShape.thought


def test_balloon_shape_thought_marker_after_trim() -> None:
    assert (
        balloon_shape("  [thought] stay quiet... keep it calm  ")
        is BalloonShape.thought
    )


def test_balloon_shape_thought_overrides_shout() -> None:
    assert balloon_shape("[thought] EVERYTHING IS FINE") is BalloonShape.thought


def test_balloon_shape_speech_for_normal_message() -> None:
    assert balloon_shape("stay quiet... keep it calm") is BalloonShape.speech


@pytest.mark.parametrize(
    ("text", "expression"),
    [
        *[
            (word, Expression.joy)
            for word in ["yay", "happy", "love", "great", "awesome"]
        ],
        *[(word, Expression.anger) for word in ["hate", "angry", "mad", "no"]],
        *[(word, Expression.surprise) for word in ["wow", "what", "oh", "whoa"]],
        *[(word, Expression.sadness) for word in ["sad", "sorry", "miss"]],
    ],
)
def test_resolve_expression_pins_research_word_sets(
    text: str, expression: Expression
) -> None:
    assert resolve_expression(text) is expression


@pytest.mark.parametrize(
    "text",
    [
        "yesterday",
        "hateful",
        "hater",
        "happily",
        "madder",
        "whatever",
        "whoathere",
        "saddest",
        "missing",
        "not",
        "noise",
    ],
)
def test_resolve_expression_matches_whole_words_only(text: str) -> None:
    assert resolve_expression(text) is Expression.neutral


def test_resolve_expression_is_case_insensitive() -> None:
    assert resolve_expression("YAY!") is Expression.joy
    assert resolve_expression("I HATE THIS") is Expression.anger
    assert resolve_expression("WOW!!") is Expression.surprise


def test_resolve_expression_ignores_punctuation_boundaries() -> None:
    assert resolve_expression("yay!") is Expression.joy
    assert resolve_expression("no.") is Expression.anger
    assert resolve_expression("wow,") is Expression.surprise
    assert resolve_expression("(miss)") is Expression.sadness


def test_resolve_expression_is_independent_of_shouting() -> None:
    assert resolve_expression("I HATE THIS") is Expression.anger


@pytest.mark.parametrize(
    "text",
    ["hello there", "just chatting", "the cat sat down", "", "!!! ??? 123"],
)
def test_resolve_expression_neutral_fallback(text: str) -> None:
    assert resolve_expression(text) is Expression.neutral


@pytest.mark.parametrize(
    ("text", "expression"),
    [
        ("hate yay", Expression.anger),
        ("no wow", Expression.anger),
        ("hate sad", Expression.anger),
        ("wow yay", Expression.surprise),
        ("wow sad", Expression.surprise),
        ("happy sad", Expression.joy),
        ("hate angry wow yay sad", Expression.anger),
    ],
)
def test_resolve_expression_fr010_precedence(text: str, expression: Expression) -> None:
    assert resolve_expression(text) is expression

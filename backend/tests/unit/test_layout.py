"""Unit tests for panel layout (T008, FR-005/FR-006/FR-007).

Pins the research.md §5/§6 rules: a panel holds at most 4 messages and is
split at the latest right-to-left speaker-change boundary within capacity
(else capped at 4); each speaker is assigned a globally stable ``left``/
``right`` side by order of first appearance (research.md §6).
"""

import pytest

from app.schemas.comic import ComicMessage, Side
from app.services.layout import assign_sides, split_into_panels


def message(speaker_id: str) -> ComicMessage:
    return ComicMessage(speaker_id=speaker_id, text="hello")


def conversation(*speakers: str) -> list[ComicMessage]:
    return [message(speaker) for speaker in speakers]


def speaker_ids(messages: list[ComicMessage]) -> list[str]:
    return [m.speaker_id for m in messages]


@pytest.mark.parametrize(
    "speakers",
    [
        ("ada",),
        ("ada", "bob"),
        ("ada", "bob", "ada"),
        ("ada", "bob", "ada", "bob"),
        ("ada", "ada", "ada", "ada"),
    ],
)
def test_one_to_four_messages_single_panel(speakers: tuple[str, ...]) -> None:
    messages = conversation(*speakers)
    panels = split_into_panels(messages)
    assert len(panels) == 1
    assert speaker_ids(panels[0]) == list(speakers)


def test_exactly_four_messages_stay_one_panel() -> None:
    messages = conversation("ada", "bob", "ada", "bob")
    assert len(split_into_panels(messages)) == 1


def test_five_messages_split_at_latest_turn_change() -> None:
    messages = conversation("ada", "bob", "ada", "bob", "ada")
    panels = split_into_panels(messages)
    assert [speaker_ids(panel) for panel in panels] == [
        ["ada", "bob", "ada", "bob"],
        ["ada"],
    ]


def test_split_falls_back_to_earlier_turn_change() -> None:
    messages = conversation("ada", "bob", "bob", "bob", "bob")
    panels = split_into_panels(messages)
    assert [speaker_ids(panel) for panel in panels] == [
        ["ada"],
        ["bob", "bob", "bob", "bob"],
    ]


def test_no_turn_change_caps_at_four() -> None:
    messages = conversation("ada", "ada", "ada", "ada", "ada")
    panels = split_into_panels(messages)
    assert [speaker_ids(panel) for panel in panels] == [
        ["ada", "ada", "ada", "ada"],
        ["ada"],
    ]


def test_long_conversation_multiple_panels_preserving_order() -> None:
    messages = conversation(
        "ada", "bob", "ada", "bob", "ada", "bob", "ada", "bob", "ada", "bob"
    )
    panels = split_into_panels(messages)
    assert [speaker_ids(panel) for panel in panels] == [
        ["ada", "bob", "ada", "bob"],
        ["ada", "bob", "ada", "bob"],
        ["ada", "bob"],
    ]
    assert [m for panel in panels for m in panel] == messages


def test_empty_conversation_no_panels() -> None:
    assert split_into_panels([]) == []


def test_assign_sides_first_speaker_left_second_right() -> None:
    assert assign_sides(conversation("ada", "bob", "ada")) == {
        "ada": Side.left,
        "bob": Side.right,
    }


def test_assign_sides_reversed_first_appearance() -> None:
    assert assign_sides(conversation("bob", "ada", "bob")) == {
        "bob": Side.left,
        "ada": Side.right,
    }


def test_assign_sides_single_speaker_is_left() -> None:
    assert assign_sides(conversation("ada", "ada", "ada")) == {"ada": Side.left}


def test_assign_sides_deterministic() -> None:
    messages = conversation("ada", "bob", "ada", "bob", "ada", "bob")
    assert assign_sides(messages) == assign_sides(messages)


def test_sides_stable_across_panels() -> None:
    messages = conversation("ada", "bob", "bob", "bob", "bob", "bob")
    global_sides = assign_sides(messages)
    panels = split_into_panels(messages)
    assert len(panels) > 1
    for panel in panels:
        for msg in panel:
            assert (
                global_sides[msg.speaker_id] == assign_sides(messages)[msg.speaker_id]
            )
    assert global_sides["ada"] is Side.left
    assert global_sides["bob"] is Side.right

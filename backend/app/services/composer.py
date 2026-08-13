"""Pure orchestration of the Comic Render Engine (T013, constitution principle II).

``compose`` is the typed entry point that turns a conversation of
``ComicMessage`` into a ``ComicInstruction``. Every derived decision is a pure
function: the ``analyzer`` derives balloon shape, the ``layout`` splits panels
and assigns stable left/right placement, and the ``characters`` module provides
the fixed v1 cast. Message ``id`` values are deterministic UUID5 hashes of the
message content so the same input always yields a byte-identical response
(SC-002). Unknown ``speaker_id`` values raise ``ValueError`` (the API layer maps
this to HTTP 422).

No DB or HTTP imports: the expert engine stays pure and trivially unit-testable
(constitution principle II).
"""

import uuid

from app.schemas.comic import (
    CharacterPlacement,
    ComicInstruction,
    ComicMessage,
    Expression,
    Panel,
    RenderedMessage,
)
from app.services import analyzer, characters, layout

ID_NAMESPACE = uuid.UUID("4e4a2b9c-8f8d-4b3a-9f2c-3a5d7e9b1c00")


def _message_id(message: ComicMessage, index: int) -> str:
    """Return the deterministic UUID5 id for ``message`` at ``index`` (SC-002)."""
    return str(uuid.uuid5(ID_NAMESPACE, f"{message.speaker_id}:{message.text}:{index}"))


def _validate_speakers(messages: list[ComicMessage]) -> None:
    """Raise ``ValueError`` when any ``speaker_id`` is not part of the v1 cast."""
    for message in messages:
        if message.speaker_id not in characters.CHARACTER_IDS:
            raise ValueError(f"unknown speaker_id: {message.speaker_id!r}")


def compose(messages: list[ComicMessage]) -> ComicInstruction:
    """Assemble a typed comic instruction for ``messages`` (pure, deterministic).

    Args:
        messages: The ordered conversation to render.

    Returns:
        The typed comic instruction.

    Raises:
        ValueError: if any ``message.speaker_id`` is not part of the v1 cast.
    """
    _validate_speakers(messages)
    sides = layout.assign_sides(messages)
    panels: list[Panel] = []
    message_index = 0
    for panel_messages in layout.split_into_panels(messages):
        placements: list[CharacterPlacement] = []
        rendered_messages: list[RenderedMessage] = []
        for message in panel_messages:
            if not any(
                placement.character_id == message.speaker_id for placement in placements
            ):
                placements.append(
                    CharacterPlacement(
                        character_id=message.speaker_id,
                        side=sides[message.speaker_id],
                    )
                )
            rendered_messages.append(
                RenderedMessage(
                    id=_message_id(message, message_index),
                    speaker_id=message.speaker_id,
                    text=message.text,
                    expression=Expression.neutral,
                    balloon=analyzer.balloon_shape(message.text),
                )
            )
            message_index += 1
        panels.append(Panel(characters=placements, messages=rendered_messages))
    return ComicInstruction(characters=list(characters.CHARACTERS), panels=panels)

"""Pure panel layout for the Comic Render Engine (T008/T011, FR-005/FR-006/FR-007).

A panel holds at most 4 messages. When a conversation exceeds capacity it is
split at the latest right-to-left speaker-change boundary within capacity,
else it caps at 4 (research.md §5). Placement is derived from turn parity
plus speaker identity: the first distinct speaker is ``left``, the second is
``right``, and a speaker keeps the same side across every panel
(research.md §6, data-model.md §Panel).

No DB or HTTP imports: the expert engine stays pure (constitution principle II).
"""

from app.schemas.comic import ComicMessage, Side

PANEL_CAPACITY = 4


def split_into_panels(messages: list[ComicMessage]) -> list[list[ComicMessage]]:
    """Split ``messages`` into ordered panels of at most ``PANEL_CAPACITY`` (FR-006).

    When more messages remain than capacity, scan right-to-left from the
    boundary after message ``PANEL_CAPACITY`` for the latest position where the
    next speaker differs from the current (``speaker[p] != speaker[p+1]``) and
    split there; if no turn-change boundary exists within capacity, cap at
    ``PANEL_CAPACITY`` (research.md §5).
    """
    if not messages:
        return []
    panels: list[list[ComicMessage]] = []
    remaining = messages
    while len(remaining) > PANEL_CAPACITY:
        split = _latest_turn_change_boundary(remaining)
        panels.append(remaining[:split])
        remaining = remaining[split:]
    panels.append(remaining)
    return panels


def _latest_turn_change_boundary(messages: list[ComicMessage]) -> int:
    """Return the split boundary (1-indexed position) for ``messages`` (FR-006).

    Scans right-to-left from ``PANEL_CAPACITY`` for the latest position ``p``
    where ``messages[p - 1].speaker_id != messages[p].speaker_id``; splits
    before that position. Returns ``PANEL_CAPACITY`` when no turn change exists
    within capacity.
    """
    for position in range(PANEL_CAPACITY, 0, -1):
        if messages[position - 1].speaker_id != messages[position].speaker_id:
            return position
    return PANEL_CAPACITY


def assign_sides(messages: list[ComicMessage]) -> dict[str, Side]:
    """Assign each speaker a globally stable side by first appearance (FR-005/FR-007).

    The first distinct speaker maps to ``left``, the second to ``right``
    (research.md §6). The mapping is global: a speaker keeps the same side in
    every panel, regardless of which panel they speak in first.
    """
    sides: dict[str, Side] = {}
    for message in messages:
        if message.speaker_id not in sides:
            sides[message.speaker_id] = Side.left if not sides else Side.right
    return sides

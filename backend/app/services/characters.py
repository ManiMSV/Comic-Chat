"""Fixed v1 character cast for the Comic Render Engine (FR-002, FR-007).

Three procedurally defined `Character` constants covering the v1 cast pinned in
``specs/001-comic-render-engine/`` (data-model.md, research.md §7). Identity is
invariant: a character renders identically in every panel, so these values are
never mutated at render time.

Provenance of values:

- ``ADA``: contract-pinned palette and silhouette from the response example in
  ``specs/001-comic-render-engine/contracts/api.md``.
- ``BOB`` / ``CARA``: newly pinned here (no other source defines them). Their
  palettes keep the same shape as Ada's: a light ``secondary`` (panel/balloon
  fill), a dark ``accent`` (text), and a distinct ``primary`` identity color.
"""

from app.schemas.comic import Character, Palette

ADA = Character(
    id="ada",
    name="Ada",
    palette=Palette(primary="#e63946", secondary="#f1faee", accent="#1d3557"),
    silhouette="circle",
)

BOB = Character(
    id="bob",
    name="Bob",
    palette=Palette(primary="#2a9d8f", secondary="#f0fdfa", accent="#123c3a"),
    silhouette="square",
)

CARA = Character(
    id="cara",
    name="Cara",
    palette=Palette(primary="#f4a261", secondary="#fff7ed", accent="#5b3a1e"),
    silhouette="triangle",
)

CHARACTERS: tuple[Character, ...] = (ADA, BOB, CARA)

CHARACTER_IDS: frozenset[str] = frozenset(character.id for character in CHARACTERS)


def get_character(character_id: str) -> Character:
    """Return the fixed character with ``character_id``.

    Raises:
        ValueError: if ``character_id`` is not part of the v1 cast.
    """
    for character in CHARACTERS:
        if character.id == character_id:
            return character
    raise ValueError(f"unknown character id: {character_id!r}")

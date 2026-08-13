"""Pure message analysis for the Comic Render Engine (T007, FR-004).

Balloon-shape selection is a pure, deterministic function of the message text:
a message is ``shout`` when at least 50% of its alphabetic characters are
uppercase AND it contains at least 3 alphabetic characters; otherwise it is
``speech`` (research.md §2). Emotion and thought refinement land in US2/US3.

No DB or HTTP imports: the expert engine stays pure (constitution principle II).
"""

from app.schemas.comic import BalloonShape


def is_shouting(text: str) -> bool:
    """Return whether ``text`` meets the shouting rule (research.md §2).

    Alphabetic characters are those for which ``str.isalpha()`` is true (any
    Unicode letter). Digits, whitespace, punctuation, and symbols are ignored.
    A message with fewer than 3 alphabetic characters is never a shout.
    """
    alphabetic = [character for character in text if character.isalpha()]
    if len(alphabetic) < 3:
        return False
    uppercase = sum(character.isupper() for character in alphabetic)
    return uppercase / len(alphabetic) >= 0.5


def balloon_shape(text: str) -> BalloonShape:
    """Derive the balloon shape for ``text`` (FR-004).

    Returns ``shout`` when the shouting rule fires, else ``speech``.
    """
    return BalloonShape.shout if is_shouting(text) else BalloonShape.speech

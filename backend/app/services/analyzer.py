"""Pure message analysis for the Comic Render Engine (T007/T019/T023, FR-003/FR-004).

Balloon-shape selection is a pure, deterministic function of the message text:
a message is ``thought`` when its trimmed text starts with the ``[thought]``
marker (case-insensitive); else ``shout`` when at least 50% of its alphabetic
characters are uppercase AND it contains at least 3 alphabetic characters;
otherwise ``speech`` (research.md §2/§3). Thought precedes shouting so a
``[thought]`` ALL-CAPS message stays a thought balloon. Emotion resolution uses
whole-word boundary matching against the authoritative word sets in research.md
§1 with FR-010 precedence.

No DB or HTTP imports: the expert engine stays pure (constitution principle II).
"""

import re

from app.schemas.comic import BalloonShape, Expression

_JOY_WORDS = frozenset({"yay", "happy", "love", "great", "awesome"})
_ANGER_WORDS = frozenset({"hate", "angry", "mad", "no"})
_SURPRISE_WORDS = frozenset({"wow", "what", "oh", "whoa"})
_SADNESS_WORDS = frozenset({"sad", "sorry", "miss"})

_EMOTION_SETS = (
    (Expression.anger, _ANGER_WORDS),
    (Expression.surprise, _SURPRISE_WORDS),
    (Expression.joy, _JOY_WORDS),
    (Expression.sadness, _SADNESS_WORDS),
)

_WORD_RE = re.compile(r"[a-z]+")


def resolve_expression(text: str) -> Expression:
    """Resolve ``text``'s emotion by whole-word boundary match (FR-003, FR-010).

    Words are lowercased alphabetic tokens; a set word fires only as a complete
    token, never as a substring. Conflicting signals resolve by the fixed
    precedence anger > surprise > joy > sadness; no signal yields ``neutral``.
    """
    tokens = _WORD_RE.findall(text.lower())
    for expression, words in _EMOTION_SETS:
        if words.intersection(tokens):
            return expression
    return Expression.neutral


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


def is_thought(text: str) -> bool:
    """Return whether ``text`` starts with the ``[thought]`` marker (US3).

    Detection is on the trimmed text and case-insensitive (research.md §3).
    """
    return text.strip().lower().startswith("[thought]")


def balloon_shape(text: str) -> BalloonShape:
    """Derive the balloon shape for ``text`` (FR-004, US3).

    Precedence: ``thought`` when ``[thought]``-marked, else ``shout`` when the
    shouting rule fires, else ``speech``. Thought precedes shouting so an
    ALL-CAPS ``[thought]`` message stays a thought balloon (research.md §3).
    """
    if is_thought(text):
        return BalloonShape.thought
    if is_shouting(text):
        return BalloonShape.shout
    return BalloonShape.speech

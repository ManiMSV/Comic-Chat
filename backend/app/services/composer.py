"""Pure orchestration of the Comic Render Engine (constitution principle II).

``compose`` is the typed entry point that turns a conversation of
``ComicMessage`` into a ``ComicInstruction``. It references the pure
``analyzer`` (expression/balloon derivation), ``layout`` (panel split and
placement), and ``characters`` (fixed v1 cast) modules and assembles the
typed result. The analyzer/layout modules are empty until T010/T011, so
this skeleton raises until their orchestration lands in T013.

No DB or HTTP imports: the expert engine stays pure and trivially
unit-testable (constitution principle II).
"""

from app.schemas.comic import ComicInstruction, ComicMessage
from app.services import (  # noqa: F401 - referenced by T013 orchestration
    analyzer,
    characters,
    layout,
)


def compose(messages: list[ComicMessage]) -> ComicInstruction:
    """Assemble a typed comic instruction for ``messages`` (pure, deterministic).

    The full orchestration of ``analyzer`` (expression/balloon), ``layout``
    (panels/placement), and ``characters`` (v1 cast) is completed in T013.

    Args:
        messages: The ordered conversation to render.

    Returns:
        The typed comic instruction.

    Raises:
        NotImplementedError: always, until analyzer/layout orchestration is
            implemented (T013).
    """
    raise NotImplementedError(
        "compose() orchestration of analyzer/layout/characters lands in T013"
    )

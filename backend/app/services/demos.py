"""Ready-made demo dialogues for the Comic Render Engine (T012, FR-011).

Three fixed dialogues in fixed order, pinned exactly in
``specs/001-comic-render-engine/data-model.md`` §Demo Dialogues. The
``quiet-tension`` demo uses a plain speech line until US3 (T024) adds the
``[thought]``-marked message, so no demo references un-implemented thought
behavior.

No DB or HTTP imports: the expert engine stays pure (constitution principle II).
"""

from app.schemas.comic import ComicMessage, DemoDialogue

SURPRISE = DemoDialogue(
    id="surprise",
    name="A Surprising Find",
    messages=[
        ComicMessage(speaker_id="ada", text="wow, whoa, look at that!"),
        ComicMessage(speaker_id="bob", text="oh my, what a find!"),
    ],
)

DISAGREEMENT = DemoDialogue(
    id="disagreement",
    name="The Great Argument",
    messages=[
        ComicMessage(speaker_id="ada", text="I HATE THIS SO MUCH"),
        ComicMessage(speaker_id="bob", text="NO. JUST NO."),
    ],
)

QUIET_TENSION = DemoDialogue(
    id="quiet-tension",
    name="A Quiet Tension",
    messages=[
        ComicMessage(speaker_id="ada", text="sorry, i miss this place"),
        ComicMessage(speaker_id="bob", text="stay quiet... keep it calm"),
    ],
)

DEMOS: tuple[DemoDialogue, ...] = (SURPRISE, DISAGREEMENT, QUIET_TENSION)

# API Contract: Comic Render Engine

**Phase 1 output** | **Date**: 2026-08-11 | **Branch**: `001-comic-render-engine`

Base path: `/comic`. All endpoints require authentication (Bearer token, following the existing
scaffold). Request and response bodies are typed Pydantic models that flow into the OpenAPI schema
and are consumed by the regenerated frontend client.

---

## `GET /comic/demos`

Returns the three ready-made demo dialogues (FR-011). Used to populate the composer page with
one click.

**Response** `200`:

```json
{
  "demos": [
    {
      "id": "surprise",
      "name": "A Surprising Find",
      "messages": [
        { "speaker_id": "ada", "text": "..." }
      ]
    }
  ]
}
```

| Field | Type | Notes |
|-------|------|-------|
| `demos` | `list[DemoDialogue]` | Ordered list of available demo dialogues. |
| `DemoDialogue.id` | `str` | Stable identifier. |
| `DemoDialogue.name` | `str` | Human-readable title. |
| `DemoDialogue.messages` | `list[ComicMessage]` | Message bodies (`speaker_id`, `text`). |

---

## `POST /comic/render`

Renders a conversation into a typed comic instruction (pure, deterministic — SC-002). Stateless:
inputs are transient; nothing is stored (principle VI).

**Request** `ComicRequest`:

```json
{
  "messages": [
    { "speaker_id": "ada", "text": "yay, we found it!" },
    { "speaker_id": "bob", "text": "I DID NOT expect that." }
  ]
}
```

| Field | Type | Constraint |
|-------|------|------------|
| `messages` | `list[ComicMessage]`, min 1 | Non-empty request (else 422). |
| `ComicMessage.speaker_id` | `str` | Must reference a known character. |
| `ComicMessage.text` | `str` | Max 500 chars; non-empty after trim. |

**Response `200`** `ComicResponse` — `{ "comic": ComicInstruction }`:

```json
{
  "comic": {
    "characters": [
      { "id": "ada", "name": "Ada", "palette": { "primary": "#e63946", "secondary": "#f1faee", "accent": "#1d3557" }, "silhouette": "circle" }
    ],
    "panels": [
      {
        "characters": [
          { "character_id": "ada", "side": "left" },
          { "character_id": "bob", "side": "right" }
        ],
        "messages": [
          { "id": "uuid", "speaker_id": "ada", "text": "yay, we found it!", "expression": "joy", "balloon": "speech" },
          { "id": "uuid", "speaker_id": "bob", "text": "I DID NOT expect that.", "expression": "surprise", "balloon": "shout" }
        ]
      }
    ]
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| `ComicInstruction.characters` | `list[Character]` | v1 cast referenced by panels. |
| `ComicInstruction.panels` | `list[Panel]` | Ordered, reading order, ≥1. |
| `Panel.characters` | `list[CharacterPlacement]` | Speakers + `side` (`left`/`right`). |
| `Panel.messages` | `list[RenderedMessage]` | Adds `expression` and `balloon` derived server-side (FR-003, FR-004). |

**Errors**:

| Status | Condition |
|--------|-----------|
| `422` | Empty or absent `messages`; empty/whitespace `text`; unknown `speaker_id`; overlong text. |
| `401` | Missing/invalid auth token. |

---

## Types

```
Expression     = "neutral" | "joy" | "anger" | "surprise" | "sadness"
BalloonShape   = "speech"  | "shout" | "thought"
Side           = "left"    | "right"

CharacterPlacement { character_id: str, side: Side }
RenderedMessage    { id: deterministic_hash, speaker_id: str, text: str, expression: Expression, balloon: BalloonShape }
Panel              { characters: list[CharacterPlacement], messages: list[RenderedMessage] }
Character          { id: str, name: str, palette: Palette, silhouette: str }
Palette            { primary: str, secondary: str, accent: str }
ComicInstruction   { characters: list[Character], panels: list[Panel] }

ComicMessage       { speaker_id: str, text: str }
ComicRequest       { messages: list[ComicMessage] }
ComicResponse      { comic: ComicInstruction }
DemoDialogue       { id: str, name: str, messages: list[ComicMessage] }
DemosResponse      { demos: list[DemoDialogue] }
```

Derivation rules (pure, documented in the data model):
- Deterministic id: `RenderedMessage.id` = hash of speaker_id + text + index; same input → same id (SC-002).
- Shouting: ≥50% alphabetic uppercase AND ≥3 alphabetic chars → `shout`.
- Thought: leading `[thought]` (case-insensitive) → `thought`.
- Emotion: whole-word boundary match against word sets in research.md §1; precedence `anger > surprise > joy > sadness > neutral`.
- Placement: turn parity + speaker identity; side stable across panels.
- Panels: max 4 messages; split at latest right-to-left speaker-change position ≤4, else cap at 4.
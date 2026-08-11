# Data Model: Comic Render Engine

**Phase 1 output** | **Date**: 2026-08-11 | **Branch**: `001-comic-render-engine`

The system is **stateless** (constitution principle VI): no tables are created. The entities below
are **abstract/pure concepts** encoded as typed Pydantic schemas that flow through the render
request and response. All derived fields are pure functions of their inputs (principle II) and
are never stored.

---

## Entities

### Character

A participant in the conversation with a stable visual identity used in every panel.

| Field | Type | Constraint / Notes |
|-------|------|--------------------|
| `id` | `str` | Unique within the fixed v1 cast. |
| `name` | `str` | Display name. |
| `palette` | `{ primary, secondary, accent }` | Hex colors; distinct per character. |
| `silhouette` | `str` | Simple geometric shape description rendered by the frontend (e.g. "circle", "square", "triangle"). |

**Relationships**: A `Comic` references characters by `id`. A `CharacterPlacement` pairs a
`character_id` with a `side`.

**Validation / rules**:
- The v1 cast is fixed at **three** characters defined as pure constants (FR-002).
- Identity is invariant: a character renders the same in every panel (FR-007, US1 #3).

**State transitions**: None (immutable constants).

---

### Message

A single line spoken by one character. The unit of input to the render.

| Field | Type | Constraint / Notes |
|-------|------|--------------------|
| `speaker_id` | `str` | Must reference a known char in the v1 cast. |
| `text` | `str` | Max 500 chars; trimmed. Empty (after trim) is invalid. |

**Derived fields** (pure functions of the request, not part of it):
- `id: uuid` — **deterministic** hash of the message (`speaker_id` + `text` + index in the
  conversation). Same input always yields the same id, so SC-002 ("identical output on re-render")
  is trivially byte-verifiable. `Panel.message_refs` reuse these same deterministic ids (FR-003,
  principle II).
- `expression: Expression` — `neutral` \| `joy` \| `anger` \| `surprise` \| `sadness`, resolved
  by **whole-word boundary** matching against the fixed word sets enumerated in research.md §1,
  with precedence `anger > surprise > joy > sadness > neutral` (FR-003, FR-010).
- `balloon: BalloonShape` — `speech` \| `shout` \| `thought` (FR-004):
  - `shout` if ≥50% of alphabetic chars are uppercase and length ≥3.
  - else `thought` if trimmed text starts with `[thought]` case-insensitively.
  - else `speech`.

**Relationships**: A `Message` belongs to exactly one speaker; several messages form a `Panel`.

**Validation / rules**:
- Empty conversation or any empty message → HTTP 422 with a clear message (FR-009, edge case).
- Speaker must exist; unknown `speaker_id` → HTTP 422 (typed content boundaries, principle IV).

**State transitions**: None (stateless single-shot analysis).

---

### Panel

A single comic frame holding a sub-sequence of messages and the positioned characters who speak
them.

| Field | Type | Constraint / Notes |
|-------|------|--------------------|
| `message_refs` | `list[uuid]` | Ordered sub-sequence of the input messages in this panel. |
| `characters` | `list[CharacterPlacement]` | Speakers in this panel with their side. |

**Characters placed**: `CharacterPlacement { character_id: str, side: "left" | "right" }`.

**Derived rules**:
- Panel capacity: at most **4** messages (FR-006).
- Split boundary aligns to a character-turn change where possible (edge case, clean breaks).
- Placement: `left`/`right` assigned by turn parity + speaker identity; each speaker keeps the same
  side across every panel (FR-005, edge case "speaks last panel N, first in panel N+1").

**State transitions**: None.

---

### Comic

The full rendered strip consisting of one or more ordered panels.

| Field | Type | Constraint / Notes |
|-------|------|--------------------|
| `panels` | `list[Panel]` | Ordered in reading order; ≥1. |
| `characters` | `list[Character]` | The v1 cast referenced by the panels. |

**Rules**: Derived entirely from the request by the pure `composer`; deterministic (SC-002).
At least one panel always present for a valid non-empty conversation.

**State transitions**: None (stateless render).

---

## Boundaries / Contracts

- **API request**: `ComicRequest { messages: list[ComicMessage] }` — `ComicMessage {
  speaker_id: str, text: str }`.
- **API response**: `ComicResponse { comic: ComicInstruction }` — `ComicInstruction {
  panels: list[Panel], characters: list[Character] }`, where each `Panel` embeds the resolved
  `expression` and `balloon` per message reference alongside placement.

All schemas are Pydantic (principle IV) and become the OpenAPI contract consumed by the
regenerated frontend client (principle V). See [contracts/api.md](contracts/api.md).

---

## Validation Matrix

| Input | Expected |
|-------|----------|
| Conversation with 1–4 messages | Single panel. |
| 5–8 messages | Two panels split at a turn boundary. |
| Empty messages list | 422 with clear message. |
| Message with empty/whitespace text | 422. |
| Unknown speaker_id | 422. |
| ALL-CAPS message (≥50%, len≥3) | `shout` balloon. |
| `[thought]` message | `thought` balloon. |
| "yay" | `joy` expression. |
| "hate" | `anger` expression. |
| No emotional signal | `neutral` expression. |
| Same input re-rendered | Identical comic (SC-002). |
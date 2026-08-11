# Research: Comic Render Engine

**Phase 0 output** | **Date**: 2026-08-11 | **Branch**: `001-comic-render-engine`

Resolves all NEEDS CLARIFICATION items and technology choices from the feature spec's Technical
Context. Each entry records the Decision, its Rationale, and the Alternatives considered.

## Unknowns Resolved

### 1. Emotion model and expression mapping (FR-003, FR-010, US2)

**Decision**: A fixed set of **five emotions** — `joy`, `anger`, `surprise`, `sadness`, `neutral`.
Each supported emotion maps to a curated keyword/stemset. A message's emotion is the resolved
result of scanning the stemsets. Conflicting emotion signals resolve by a **fixed, documented
precedence**: `anger > surprise > joy > sadness > neutral` (FR-010). Output is fully deterministic.

**Rationale**:
- Satisfies constitution principle II (pure function, no LLM, no randomness).
- Small, explicit vocab means each emotion is independently unit-testable (SC-004, US2 scenarios).
- Curated stemsets give predictable behavior on demo dialogues.

**Alternatives considered**:
- Machine-learning / LLM sentiment analysis — rejected: nondeterministic, breaks principle II.
- Third-party sentiment library — rejected: external nondeterminism, unnecessary dependency.
- Weighted keyword scoring across emotions — rejected: overkill for a 5-emotion v1; precedence
  order is simpler and already reproducible.

### 2. Shouting detection (FR-004, US1 #2, edge case "all-caps + long")

**Decision**: A message is `shout` when **at least 50% of its alphabetic characters are uppercase
AND the message contains at least 3 alphabetic characters**. Balloon must still wrap text within
the panel regardless of length.

**Rationale**: Distinguishes genuine emphasis (ALL CAPS) from normal case without ambiguity, so
the rule is deterministic and testable. Threshold chosen so mixed-case messages stay speech.

**Alternatives considered**:
- "Any one uppercase character" — rejected: false positives on abbreviated/camel text.
- Heuristic on line count plus caps — rejected: over-engineered for v1.

### 3. Thought balloon detection (P3, US3)

**Decision**: A message whose trimmed text starts with the explicit marker `[thought]` is drawn in
a **thought balloon** (cloud shape with a connector tail); otherwise a normal message uses a
**speech balloon**. Detection precedes and overrides speech but is independent of shouting: a
`[thought]` ALL-CAPS message stays a thought balloon (shout only applies to speech).

**Rationale**: The spec requires a thought state to be expressed by the user; an explicit,
user-facing marker is deterministic, cheap, and testable (US3 scenario 1).

**Alternatives considered**:
- NLP introspection of "inner voice" — rejected: unreliable and nondeterministic.
- Implicit punctuation rules (`...`, `*emphasis*`) — rejected: ambiguous, not user-controllable.

### 4. Balloon shape selection (FR-004)

**Decision**: Balloon shape is a pure function of the message content evaluated once by the
analyzer: `shout` if shouting, else `thought` if `[thought]`-marked, else `speech`.

**Rationale**: Single clear precedence that is documented and testable; matches US1/US3 acceptance
scenarios exactly.

**Alternatives considered**: Signal-based union scoring — rejected: unnecessary.

### 5. Panel capacity and conversation splitting (FR-006, edge "more messages than one panel")

**Decision**: A panel holds at most **4 messages**. When a conversation exceeds capacity it is
split in reading order at a **panel boundary that also aligns to a character turn change** (page
break occurs when the next speaker differs from the current) — so a character never has a single
turn split awkwardly. If no turn-change boundary exists within capacity, the panel caps at 4.

**Rationale**: Bounded, deterministic split (principle II) that composes clean multi-panel strips
(US1 #1, FR-006) and avoids a character appearing as "last of panel N and first of panel N+1"
without a clean break (edge case).

**Alternatives considered**:
- Chronology/time-based sliding window — rejected: no timestamps in v1.
- Fully adaptive layout — rejected: nondeterministic, deferred (spec defers zoom/background).

### 6. Character placement within a panel (FR-005, edge "speaks last in one panel, first in next")

**Decision**: Placement is derived from **turn parity plus speaker identity**. For a two-speaker
panel, the speakers are assigned `left`/`right` by the order of their first appearance in the
conversation, then alternate per message turn. A speaker keeps the same side across all panels
(their identity maps to a side globally), ensuring the reader never loses track (edge case) and
satisfying consistency (FR-007). v1 panels are two-character by construction.

**Rationale**: Deterministic and stable across panel boundaries — matches "placement must stay
consistent" edge case and FR-005/FR-007.

**Alternatives considered**:
- Mirror the last speaker of a panel to lead the next — rejected: complex, breaks stability.
- Keyboard-style directionality — rejected: nondeterministic feel.

### 7. Character identity model (FR-002, FR-007, assumption "3 stylized characters")

**Decision**: Three **fixed procedurally defined characters** are coded as pure constants. Each
has `id`, `name`, a small `palette` (primary/secondary/accent colors), and a `silhouette`
description (simple geometric shape) that the frontend renders. Because identity is a constant,
a character renders identically in every panel (SC-002, FR-007, US1 #3).

**Rationale**: Clean geometric silhouettes and palettes match the "clean and geometric" visual
style assumption; fixed constants keep determinism trivial.

**Alternatives considered**:
- User-uploaded avatars — rejected: out of scope for v1.
- Randomized generation at render time — rejected: breaks determinism (principle II).

### 8. API contract shape (FR-008)

**Decision**: Two stateless endpoints behind the existing auth:
- `POST /comic/render` — accepts a `ComicRequest { messages: [ { speaker_id, text } ] }` and
  returns a typed `ComicResponse { comic: ComicInstruction }`.
- `GET /comic/demos` — returns the three ready-made demo dialogues (FR-011).

**Rationale**: A single stateless POST keeps the math pure and is trivially frontend- and
test-drivable (FR-008, US1's independent test). A separate GET exposes FR-011 without coupling
demo data to the render request.

**Alternatives considered**: GraphQL (overkill); WebSocket streaming (out of scope for v1).

### 9. SVG rendering strategy (assumption "vector graphics (SVG)")

**Decision**: The backend emits a **typed abstract `ComicInstruction`** (panels, character
placements, messages with derived expression/balloon). The **frontend translates it to SVG** in
`components/Comic/*`.

**Rationale**: Backend remains the single source of truth (principle III) and stays trivially
testable (principle II), while all visual drawing lives on the client (matches the existing
React + Tailwind stack). SVG scales cleanly at any zoom per the assumption.

**Alternatives considered**: Backend emits an SVG string directly — rejected: frontend would then
"render" a blob with no ability to re-derive structure, blurring responsibility and complicating
backend tests (violates III). A canvas renderer — rejected: vector/scalability requirement favors
SVG.

## Technology Choices

| Topic | Choice | Rationale | Alternatives considered |
|-------|--------|-----------|-------------------------|
| Backend engine | Pure Python module (`services/`) | Determinism + trivial unit tests | LLM, ML libs (rejected) |
| API layer | FastAPI + Pydantic (existing) | Already the scaffold stack, typed contracts (IV) | GraphQL, WS (rejected) |
| Rendering | React + SVG (client) | Matches stack; scalable vector output | Backend SVG string, canvas |
| Frontend client | Regenerated OpenAPI TS client | Existing scaffold discipline (V) | Hand-written API (rejected) |
| Storage | None (stateless) | VI; no persistence until needed | New DB tables (rejected) |
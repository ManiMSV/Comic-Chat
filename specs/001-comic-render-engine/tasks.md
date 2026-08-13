---

description: "Task list for Comic Render Engine feature implementation"
---

# Tasks: Comic Render Engine

**Input**: Design documents from `/specs/001-comic-render-engine/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api.md

**Tests**: Tests are required for this feature. SC-004 and constitution principle II mandate automated unit tests pinning every derived decision (expression, balloon shape, placement, panel layout), plus API tests. Frontend uses Playwright E2E.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend** (uv workspace): `backend/app/schemas/comic.py`, `backend/app/services/*.py`, `backend/app/api/routes/comic.py`, `backend/tests/**`
- **Frontend** (bun): `frontend/src/routes/_layout/comic.tsx`, `frontend/src/components/Comic/*`, `frontend/tests/comic.spec.ts`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the repository and remove the scaffold demo that the new feature replaces.

- [X] T001 Delete the Items CRUD demo: remove `Item`/`ItemBase`/`ItemCreate`/`ItemUpdate`/`ItemPublic`/`ItemsPublic` from `backend/app/models.py`, delete `backend/app/api/routes/items.py`, remove items router registration from `backend/app/api/main.py`, delete `frontend/src/components/Items/*`, `frontend/src/routes/_layout/items.tsx`, and `frontend/tests/items.spec.ts`; also remove the Items nav entry (`{ icon: Briefcase, title: "Items", path: "/items" }` plus the now-unused `Briefcase` import) from `frontend/src/components/Sidebar/AppSidebar.tsx` (CHK015)
- [X] T002 Create the expert-engine package structure: add `backend/app/services/__init__.py` and the empty module files `backend/app/services/analyzer.py`, `layout.py`, `characters.py`, `demos.py`, `composer.py`
- [ ] T003 [P] Confirm the working dev environment: run `uv sync` from `backend/` and `bun install` from repo root; verify `uv run fastapi dev` boots and `bun run dev` compiles the scaffold

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Typed contracts and pure building blocks that EVERY user story depends on. Must complete before any user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Create all typed Pydantic schemas in `backend/app/schemas/comic.py`: `Character`, `Palette` (primary/secondary/accent), `CharacterPlacement` (character_id, side), `ComicMessage` (speaker_id, text), `RenderedMessage` (id with deterministic hash, speaker_id, text, expression, balloon), `Panel` (characters, messages), `ComicInstruction` (characters, panels), `ComicRequest` (messages), `ComicResponse` (comic), `DemoDialogue` (id, name, messages), `DemosResponse` (demos); enums `Expression` (neutral/joy/anger/surprise/sadness), `BalloonShape` (speech/shout/thought), `Side` (left/right)
- [ ] T005 Create `backend/app/services/characters.py`: three fixed, procedurally defined `Character` constants (id, name, distinct palette hex, silhouette description: circle/square/triangle) covering the v1 cast from data-model.md and research.md §7
- [ ] T006 Create `backend/app/services/composer.py` skeleton: a pure `compose(messages: list[ComicMessage]) -> ComicInstruction` that references `analyzer`/`layout`/`characters` and assembles the typed result (empty bodies for the referenced modules may raise initially); keep it free of DB/HTTP imports per constitution principle II

**Checkpoint**: Typed contract boundary established (principle IV). User story implementation can now begin.

---

## Phase 3: User Story 1 - Render a conversation as a comic strip (Priority: P1) 🎯 MVP

**Goal**: Accept an ordered, character-assigned conversation and produce a typed comic instruction rendered as an SVG comic strip, including speech and shout balloons, deterministic panel layout, and consistent character appearance across panels.

**Independent Test**: Submit a short scripted dialogue via `POST /comic/render` and/or the Comic page; confirm ≥1 panel shows both speakers with speech balloons; re-render the same input and confirm identical output (SC-002).

### Tests for User Story 1 ⚠️ (write first, verify they FAIL before implementation)

- [ ] T007 [P] [US1] Unit test shouting + speech balloon + placement in `backend/tests/unit/test_analyzer.py` (pure functions): ≥50% uppercase & ≥3 alphabetic → `shout`, else `speech`
- [ ] T008 [P] [US1] Unit test panel layout in `backend/tests/unit/test_layout.py`: max 4 messages per panel; split by scanning right-to-left from message 4 for the latest speaker-change position ≤4 (split there if found, else cap at 4); left/right placement by turn parity + speaker identity with stable side across panels
- [ ] T009 [P] [US1] API test for the render and demos endpoints in `backend/tests/api/routes/test_comic.py`: `POST /comic/render` happy path returns typed instruction, `GET /comic/demos` returns three demo dialogues, plus `422` cases (empty messages, empty/whitespace text, unknown speaker_id, overlong text); include a determinism assertion — render the same request twice and assert the two `ComicResponse` bodies are byte-identical (validates SC-002 and the deterministic message `id`)

### Implementation for User Story 1

- [ ] T010 [P] [US1] Implement `backend/app/services/analyzer.py`: pure function for balloon shape (`speech` vs `shout` by shouting rule) — emotion/thought refinement deferred to US2/US3
- [ ] T011 [P] [US1] Implement `backend/app/services/layout.py`: pure function splitting messages into panels (capacity 4, split at the latest right-to-left speaker-change position ≤4 else cap at 4) and assigning stable left/right placement via turn parity + speaker identity (FR-005/FR-006/FR-007)
- [ ] T012 [P] [US1] Create `backend/app/services/demos.py`: three ready-made demo dialogues in fixed order — `surprise` ("A Surprising Find"), `disagreement` ("The Great Argument"), `quiet-tension` ("A Quiet Tension") — each with stable id/name and message bodies exactly as pinned in data-model.md §Demo Dialogues (FR-011, CHK010/CHK016). Covers shout and speech balloons only. The thought-marked message for the quiet/tension demo is added in T024 (US3) so no demo references un-implemented thought behavior
- [ ] T013 [US1] Complete `backend/app/services/composer.py`: orchestrate analyzer + layout + characters into the typed `ComicInstruction`, keeping every decision a pure function (depends on T010, T011, T012, T004, T005)
- [ ] T014 [US1] Implement `backend/app/api/routes/comic.py`: `POST /comic/render` (stateless, returns `ComicResponse`) and `GET /comic/demos` (returns `DemosResponse`), both behind the existing auth; register the router in `backend/app/api/main.py`
- [ ] T015 [US1] Regenerate the frontend OpenAPI client after the backend schema change via `bash ./scripts/generate-client.sh`; commit the regenerated `frontend/src/client/` (never hand-edit)
- [ ] T016 [P] [US1] Create frontend SVG render components in `frontend/src/components/Comic/`: `Character.tsx` (draws a character's silhouette + palette), `Balloon.tsx` (speech bubble shape + tail), `Panel.tsx`, and `ComicStrip.tsx` that renders a `ComicInstruction` to `<svg>` exactly as received (client must NOT re-derive decisions, principle III); render balloon text as real `<text>` elements and give each panel `<g>` an accessible name via `aria-label`/`<title>` (CHK030)
- [ ] T017 [US1] Create the `frontend/src/routes/_layout/comic.tsx` route: a demo picker (fetches `GET /comic/demos`) plus a message editor that submits `POST /comic/render` and displays the resulting SVG comic (FR-008); implement the loading, empty (no render yet), and error/retry states from plan.md §Frontend UX & Accessibility (CHK022)

### Checkpoint (MVP Validation)

- [ ] T018 [US1] E2E test in `frontend/tests/comic.spec.ts`: user opens the Comic page, picks a demo dialogue, and sees an SVG comic with ≥1 panel (requires Docker Compose stack per `quickstart.md`)

At this point, User Story 1 is fully functional and testable independently (MVP).

---

## Phase 4: User Story 2 - Automatic expressions and gestures (Priority: P2)

**Goal**: Messages conveying emotion (joy, anger, surprise, sadness) cause the speaking character's derived `expression` to reflect that emotion, with conflicting signals resolved by a fixed documented precedence.

**Independent Test**: Submit messages containing "yay" (→ joy) and "hate" (→ anger) and a neutral message (→ neutral); confirm the response `expression` matches per US2 acceptance scenarios, while other render aspects are unchanged.

### Tests for User Story 2 ⚠️ (write first, verify they FAIL before implementation)

- [ ] T019 [P] [US2] Extend `backend/tests/unit/test_analyzer.py` with emotion tests pinned to the exact word sets in research.md §1, matched by whole-word boundary (e.g. `yay` → `joy`, `yesterday` → `neutral`, `hate` → `anger`), `neutral` fallback when no signal, and FR-010 precedence resolution (anger > surprise > joy > sadness > neutral) for conflicting signals
- [ ] T020 [P] [US2] Extend `backend/tests/api/routes/test_comic.py` to assert rendered `expression` values flow through `POST /comic/render` for the emotion-triggering messages

### Implementation for User Story 2

- [ ] T021 [US2] Extend `backend/app/services/analyzer.py`: add deterministic emotion detection using whole-word boundary matching against the exact word sets in research.md §1, and FR-010 precedence resolution so a message resolves to exactly one `Expression` (FR-003/FR-010; depends on T019)
- [ ] T022 [US2] Wire `expression` through `backend/app/services/composer.py` and the `RenderedMessage` payload in `backend/app/api/routes/comic.py` so the response carries each message's resolved expression (depends on T021)

**Checkpoint**: User Stories 1 AND 2 both work and remain independently testable.

---

## Phase 5: User Story 3 - Thought balloons (Priority: P3)

**Goal**: A message explicitly marked as an inner thought or quiet aside is rendered in a thought (cloud) balloon with a connector tail, distinct from speech and shout.

**Independent Test**: Submit a message prefixed `[thought]` and confirm it derives a `thought` balloon (cloud shape + tail); confirm a normal message still derives `speech` (US3 scenarios).

### Tests for User Story 3 ⚠️ (write first, verify they FAIL before implementation)

- [ ] T023 [P] [US3] Extend `backend/tests/unit/test_analyzer.py` with thought detection: leading `[thought]` marker (after trim, case-insensitive) → `thought`; a `[thought]` ALL-CAPS message stays `thought` (thought overrides shout); normal message → `speech`

### Implementation for User Story 3

- [ ] T024 [US3] Extend `backend/app/services/analyzer.py` balloon rule to the full documented precedence: `shout` if shouting, else `thought` if `[thought]`-marked (case-insensitive), else `speech`; add the `[thought]` message to the quiet/tension demo in `backend/app/services/demos.py` (FR-004; depends on T023)
- [ ] T025 [P] [US3] Extend `frontend/src/components/Comic/Balloon.tsx` to render a cloud-shaped `thought` balloon with a connector tail pointing at the speaker, distinct from the speech shape

**Checkpoint**: All user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and cleanup that affect multiple user stories or the whole feature.

- [ ] T026 [P] Update the dashboard route `frontend/src/routes/_layout/index.tsx` title/welcome copy to remove Items references (per plan §Structure)
- [ ] T027 Run quality gates and validation: `uv run prek run --all-files` (ruff, ruff-format, mypy, type checks, typos) from `backend/`, `bun run build` from repo root, `bunx playwright test`, and validate the full matrix in `quickstart.md` (all acceptance scenarios + SC-001/SC-002/SC-004)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational completion; US2/US3 also depend on US1 modules (shared `analyzer.py`/`composer.py`) but are independently testable increments
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational — establishes analyzer/layout/composer/endpoints/UI
- **User Story 2 (P2)**: Depends on US1 `analyzer.py` and `composer.py` — extends them with emotion detection
- **User Story 3 (P3)**: Depends on US1 `analyzer.py` and `Balloon.tsx` — extends balloon precedence and rendering

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per SC-004)
- Schemas/models before services; services before endpoints; backend before frontend wiring
- Story complete before moving to the next priority

### Parallel Opportunities

- Phase 1 Setup: T002 and T003 marked [P] can run in parallel
- Phase 2 Foundational: T004/T005 can be parallel; T006 depends on both
- US1 unit/API tests T007/T008/T009 run in parallel
- US1 implementation T010/T011/T012 are [P]; T013 depends on them
- Frontend components T016 [P] can be built in parallel with backend work after T015 regenerate

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together:
"Unit test analyzer in backend/tests/unit/test_analyzer.py"
"Unit test layout in backend/tests/unit/test_layout.py"
"API test in backend/tests/api/routes/test_comic.py"

# Launch analyzer/layout/demos implementations together:
"Implement analyzer.py"
"Implement layout.py"
"Create demos.py"

# Then composer (depends on all three), then endpoint, then frontend.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (remove Items demo)
2. Complete Phase 2: Foundational (typed schemas + characters + composer skeleton)
3. Complete Phase 3: User Story 1 (speech/shout + layout + endpoints + SVG render)
4. **STOP and VALIDATE**: run pytest + E2E; confirm ≥1 panel comic and deterministic re-render
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → typed contract boundary established
2. Add US1 → test → MVP demo
3. Add US2 (emotions) → test → richer comics
4. Add US3 (thought balloons) → test → full balloon vocabulary
5. Each story adds value without breaking prior stories

### Parallel Team Strategy

With multiple developers after Foundational:
- Developer A: US1 backend (analyzer/layout/composer/endpoints + tests)
- Developer B: US1 frontend (Comic components + route + E2E) after T015 regenerate
- Developer C: US1 unit/API tests (T007/T008/T009)
- Then reassign for US2/US3 increments

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Write tests first and verify they FAIL before implementing (SC-004)
- Keep the expert engine pure — no DB/HTTP imports in `backend/app/services/*` (principle II)
- Commit after each task or logical group; never commit red
- Regenerated `frontend/src/client/` must be committed, never hand-edited (principle V)
- Stop at any checkpoint to validate the story independently
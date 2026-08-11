# Implementation Plan: Comic Render Engine

**Branch**: `001-comic-render-engine` | **Date**: 2026-08-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-comic-render-engine/spec.md`

## Summary

Render transient message conversations into viewable comic strips. The backend analyzes each
message deterministically (expression, balloon shape, character placement, panel layout) and
emits a **typed abstract comic instruction**; the frontend renders that instruction to SVG. This
replaces the scaffold's Items CRUD demo while keeping authentication. First release is stateless
— no new database tables.

## Technical Context

**Language/Version**: Python 3.14 (backend, `requires-python = ">=3.14,<4.0"`), TypeScript 5.9 +
React 19 (frontend).

**Primary Dependencies**: `fastapi[standard]`, `pydantic`, `sqlmodel` retained for the existing
User/auth models. Frontend: `@tanstack/react-query`, `react-hook-form`, `lucide-react`, `react`,
`zod`. **No new runtime dependencies required** — SVG is produced client-side from the typed
instruction, so the expert engine stays pure.

**Storage**: N/A (stateless v1, constitution principle VI). Reuses existing Postgres-backed
`User`/auth models; no new tables, no migration.

**Testing**: Backend `pytest` — unit tests for the pure expert-engine functions plus an API test
via `TestClient`. Frontend `bun run build` (tsc typecheck) + `bunx playwright test` E2E. Quality
gates via `uv run prek run --all-files`.

**Target Platform**: Browser. Frontend served by FastAPI static; API at `:8000`.

**Project Type**: Web application (FastAPI backend + React SPA).

**Performance Goals**: Render under 10 seconds (SC-001) — trivially met since SVG is derived from
a pure O(n) instruction.

**Constraints**: **Deterministic** output, 100% reproducible (SC-002) — no randomness, no LLM, no
wall-clock dependence (principle II). Backend is the single source of comic truth; the client never
re-derives decisions (principle III).

**Scale/Scope**: v1 = 3 characters, 3 demo dialogues, single render endpoint + demo listing.
Stateless.

## Constitution Check

*GATE: Passes. No violations — complexity is minimized.*

- **I. Tracer-Bullet First** — Satisfied. The P1 slice (analyze → instruction → SVG → browser) is
  the primary deliverable and remains the working backbone.
- **II. Deterministic, Testable Core** — Satisfied. Every decision (emotion, balloon, placement,
  panel layout) is a pure function with unit tests.
- **III. Backend Produces, Frontend Renders** — Satisfied. Backend emits the typed instruction;
  the client is a dumb SVG renderer that never re-derives decisions.
- **IV. Typed Contracts at Every Boundary** — Satisfied. Pydantic request/instruction/response
  models + regenerated typed TS client.
- **V. Generated-Client Discipline** — Satisfied. `frontend/src/client/` is regenerated from
  OpenAPI after the backend change.
- **VI. Stateless v1, Database Later** — Satisfied. No new tables; the Items DB demo is removed.
- **Complexity Tracking**: **None.** Single backend module tree + one frontend page; no third
  project or repository pattern required.

## Project Structure

### Documentation (this feature)

```text
specs/001-comic-render-engine/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models.py                 # KEEP User/auth; REMOVE Item/ItemBase/ItemCreate/ItemUpdate/ItemPublic/ItemsPublic
│   ├── schemas/
│   │   └── comic.py              # NEW: ComicMessage, ComicRequest, Expression, BalloonShape, CharacterPlacement, PanelInstruction, ComicInstruction, ComicResponse
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analyzer.py           # NEW: pure functions -> expression, is_shouting, is_thought, balloon shape
│   │   ├── layout.py             # NEW: pure functions -> panel split + left/right placement by turn
│   │   ├── characters.py         # NEW: 3 fixed character definitions (identity/color/palette/silhouette)
│   │   ├── demos.py              # NEW: 3 ready-made demo dialogues
│   │   └── composer.py           # NEW: orchestrates analyzer+layout+characters -> ComicInstruction (pure)
│   ├── api/routes/
│   │   ├── comic.py              # NEW: POST /comic/render (stateless), GET /comic/demos
│   │   ├── items.py              # DELETE (removed per spec assumption)
│   │   └── __init__.py
│   └── api/main.py               # register comic; drop items router
└── tests/
    ├── unit/
    │   ├── test_analyzer.py
    │   ├── test_layout.py
    │   └── test_composer.py
    └── api/routes/
        └── test_comic.py         # replaces test_items.py (deleted)

frontend/
├── src/
│   ├── routes/_layout/
│   │   ├── index.tsx             # dashboard -> update title/welcome copy (Items removed)
│   │   └── comic.tsx             # NEW: demo picker + message editor -> SVG preview
│   ├── components/Comic/
│   │   ├── ComicStrip.tsx        # NEW: renders ComicInstruction to <svg>
│   │   ├── Panel.tsx
│   │   ├── Balloon.tsx
│   │   └── Character.tsx
│   ├── components/Items/*        # DELETE (replaced)
│   └── client/                   # regenerated from OpenAPI, never hand-edited
├── src/routes/_layout/items.tsx  # DELETE (replaced)
└── tests/
    ├── comic.spec.ts             # NEW E2E
    └── items.spec.ts             # DELETE
```

**Structure Decision**: Follows the existing single-backend + SPA frontend layout. The expert
engine is kept **pure** (`services/` with no DB/HTTP imports) so it is trivially unit-testable —
this directly satisfies constitution principle II. Removal of the Items demo keeps the repository
aligned with the spec assumption "demo Items CRUD example is removed."

## Complexity Tracking

> None required. The design adds no redundant abstraction (no repository layer, no third project).
> The `services/` split exists solely to keep the core pure and testable (principle II), which is
> the simplest structure that satisfies the constitution.
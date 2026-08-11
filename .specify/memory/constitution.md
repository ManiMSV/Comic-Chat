<!-- Sync Impact Report
- Version change: 0.0.0 → 1.0.0
- Initial constitution written for Comic-Chat (template placeholders replaced)
- Added principles I–VI, Governance, and Development Workflow sections
- No prior principled content existed (template only)
-->

# Comic-Chat Constitution

## Core Principles

### I. Tracer-Bullet First
Build one thin end-to-end slice (backend engine → API → SVG → browser render) before any
hardening. Validate the architecture on the riskiest path first, then iterate. Every feature
keeps a working, vertically-integrated demo as its backbone.

### II. Deterministic, Testable Core
The expert engine is pure and reproducible: no randomness, no LLM, no wall-clock dependence.
Every decision (emotion, expression, balloon shape, character placement, panel layout) MUST be
a pure function whose output is fully determined by its inputs. Each decision MUST have unit
tests that pin its behavior. Determinism is what makes the comic output predictable and the
test suite reliable.

### III. Backend Produces, Frontend Renders
The backend is the single source of comic truth. It classifies messages and emits a structured
comic instruction; the frontend only draws what it receives. The client MUST NOT re-derive
layout, emotion, or balloon decisions. SVG is the rendering target because it is vector,
scalable, and directly driven by the structured instruction.

### IV. Typed Contracts at Every Boundary
All data crossing the API boundary uses explicit typed models (Pydantic/SQLModel). No raw
dicts, no untyped payloads. request → instruction → SVG must all be typed so schema changes
fail loudly at build time, not silently at runtime.

### V. Generated-Client Discipline
The frontend API client under `frontend/src/client/` is generated from the OpenAPI schema and
MUST NOT be hand-edited. After any backend schema change, regenerate it and commit the result.
The backend MUST expose accurate OpenAPI for every endpoint.

### VI. Stateless v1, Database Later
The first slice is stateless: conversations are transient inputs, no new database tables. Keep
the door open for persistence and real-time transport in later features. Do not add persistence
until a feature actually needs it.

## Technology Constraints

Backend is FastAPI + SQLAlchemy/SQLModel + Pydantic, run as a `uv` workspace from `backend/`.
Frontend is React + TanStack Router/Query + Tailwind CSS + an OpenAPI-generated client, run
with `bun`. Postgres is the database engine; migration, seed, and version-control rules follow
the operations contract in `AGENTS.md`.

## Development Workflow

- Use the spec-kit SDD cycle only: specify → plan → tasks → implement, with hard review gates
  after `specify` and `plan`.
- One feature per branch named `NNN-feature-name`; feature artifacts live under
  `specs/NNN-feature-name/`.
- Keep every task small and independently testable; track status in `tasks.md` and the todo
  list in real time.
- Never commit red: complete a task, run its tests, fix failures, only then commit.
- Affirmative quality gates before commit: ruff, ruff-format, mypy, type checks, and typos via
  prek; frontend must build clean.
- Commits use gitmoji-style conventional subjects as documented in `AGENTS.md`.

## Governance

- The constitution supersedes all other practices where they conflict.
- Amendments require a documented change, an explicit version bump, and a migration plan.
- All PRs and reviews MUST verify constitution compliance. Justify any complexity that is not
  required by the principles above.

**Version**: 1.0.0 | **Ratified**: 2026-08-11 | **Last Amended**: 2026-08-11
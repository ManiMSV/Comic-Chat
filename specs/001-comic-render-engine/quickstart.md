# Quickstart / Validation Guide: Comic Render Engine

**Phase 1 output** | **Date**: 2026-08-11 | **Branch**: `001-comic-render-engine`

This guide validates the feature end-to-end: analyze messages → typed comic instruction → SVG in
the browser. It is a run/validation guide; implementation detail lives in `tasks.md`.

## Prerequisites

- Docker Compose stack up for PostgreSQL + MailCatcher: `docker compose up -d db mailcatcher`
- Python + `uv` (from `backend/`), `bun` (frontend).

## Setup

```bash
# Backend (from backend/)
uv sync
uv run bash scripts/prestart.sh        # wait for DB, run migrations

# Frontend (from repo root)
bun install
bash scripts/generate-client.sh        # regenerate TS client after backend API change
```

## Run

```bash
# Backend — API on :8000, Swagger at /docs
uv run fastapi dev                     # (workdir: backend)

# Frontend — dev server on :5173
bun run dev                            # (workdir: frontend)
```

For a served build: `bun run build` (writes to `backend/app/frontend`, served by FastAPI).

## Validation Scenarios

Reference: [contracts/api.md](contracts/api.md) for the request/response shape,
[data-model.md](data-model.md) for derivation rules.

### Backend (pytest)

```bash
uv run bash scripts/test.sh            # coverage to backend/htmlcov/
```

- `tests/unit/test_analyzer.py` — expression mapping + precedence, shouting, thought ballooons.
- `tests/unit/test_layout.py` — panel split (capacity + turn boundary), left/right placement and
  cross-panel side stability.
- `tests/unit/test_composer.py` — end-to-end pure instruction assembly.
- `tests/api/routes/test_comic.py` — `POST /comic/render` and `GET /comic/demos` happy paths and
  the `422` cases (empty conversation, unknown speaker).

### Frontend (Playwright E2E — requires the stack up)

```bash
bunx playwright test
```

- `tests/comic.spec.ts` — user opens the Comic page, picks a demo dialogue, and sees an SVG comic.

## Expected Outcomes by Acceptance Scenario

| Scenario | How to trigger | Expected result |
|----------|----------------|-----------------|
| US1 #1 two-char multi-panel | Render a demo / own alternating dialogue | ≥1 panel showing both characters + speech balloons |
| US1 #2 shout balloon | Message that is ALL-CAPS (≥50%, len≥3) | `shout` balloon, distinct from `speech` |
| US1 #3 consistent appearance | Character in multiple panels | Same silhouette + palette each panel |
| US2 #1 joy | Message containing e.g. "yay" | Speaker drawn `joy` |
| US2 #2 anger | Message containing e.g. "hate" | Speaker drawn `anger` |
| US2 #3 neutral | No emotional signal | Speaker drawn `neutral` |
| US3 #1 thought | Message prefixed `[thought]` | Cloud-shaped `thought` balloon + tail to speaker |
| US3 #2 speech default | Normal message | `speech` balloon, not thought |
| Edge: empty conversation | Submit empty message list | Clear `422`, no malformed comic |
| SC-001 | Render any demo | Comic appears in <10s |
| SC-002 | Re-render same input | Identical output |
| SC-004 | run full `pytest` | All emotion/balloon/edge tests pass |
| FR-011 / Items removed | Check sidebar/nav | Demo dialogues available; no Items CRUD anywhere |

## Notes

- No database, migrations, or new persistence involved — the render is stateless (principle VI).
  The existing Postgres schema and auth are untouched. Removal of the scaffold Items demo (model,
  route, frontend page) is tracked in `tasks.md`.
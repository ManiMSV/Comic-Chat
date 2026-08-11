# AGENTS.md — Operating Contract

This file is the operating contract for agents in this repository. Follow the rules without exception unless the constitution at `.specify/memory/constitution.md` overrides them.

## Build and Process Rules

- **Build a tracer bullet first.** Before any hardening, stand up one thin end-to-end slice (database -> API -> frontend) that proves the riskiest path, then iterate from there. This is the cheapest way to validate the architecture before committing to detail.
- **Build features with the speckit SDD cycle only.** Run `/speckit.specify` -> `/speckit.plan` -> `/speckit.tasks` -> `/speckit.implement`. Command definitions live in `.opencode/commands/speckit.*.md`; workflow orchestration in `.specify/workflows/speckit/workflow.yml`.
- **Hard stop after `specify` and `plan`.** Present the generated artifacts and wait for user approval before proceeding. Never auto-advance past a review gate. Review gates are the safety net; bypassing them produces unreviewed work.
- **One feature per branch.** Name branches `NNN-feature-name` using sequential numbering. Feature artifacts live under `specs/NNN-feature-name/` (`spec.md`, `plan.md`, `research.md`, `tasks.md`). Never mix multiple features in one branch or PR. This isolates review and makes rollback trivial.
- **Break every feature into small, simple tasks** in `tasks.md`. Keep each task a single, testable increment.
- **Always track progress.** Keep the opencode todo list and `tasks.md` statuses current in real time. Anyone should be able to see exactly where the work stands.
- **Follow the loop per task: commit, test, fix, repeat.** Complete a task -> run the relevant tests -> fix any bug immediately -> only then commit -> move to the next task. **Never commit red.** This keeps history green and stops bugs from piling up.

## Commit and PR Rules

- **Use gitmoji-style conventional commit subjects**, matching this repository's history: `✨` feature, `🐛` fix, `📝` docs, `🔧` config, `♻️` refactor, `👷` CI, `✅` tests, `🔖` release.
- **One commit per task.** A commit is self-contained and must pass the tests for its scope. This keeps git history mapping one-to-one to the plan.
- **One feature per PR.** A PR must pass CI (tests + lint) and be reviewed before merge. Never merge a failing or unreviewed PR. This keeps main branch shippable.

## Commands

### Backend (use `uv`, run from `backend/`)

Backend is its own uv workspace; run all Python commands from `backend/`.

```bash
uv sync
uv run bash scripts/prestart.sh   # prepare DB, run migrations
uv run fastapi dev                # API on :8000, Swagger at /docs
uv run bash scripts/test.sh       # Pytest; coverage to backend/htmlcov/
```

Migrations: after every change to `backend/app/models.py`, create a revision, upgrade, and commit the generated revision file.

```bash
uv run alembic revision --autogenerate -m "Describe the change"
uv run alembic upgrade head
```

### Frontend (use `bun`)

Run from project root or `frontend/`.

```bash
bun install
bun run dev         # Vite dev server on :5173
bun run build       # writes to backend/app/frontend; rebuild after every frontend change
bunx playwright test  # E2E; requires the Docker Compose stack to be up
```

Always rebuild the frontend after frontend changes, otherwise FastAPI serves stale assets.

### Infrastructure

```bash
docker compose up -d db mailcatcher   # local PostgreSQL + mail
docker compose watch                  # full stack in Docker Compose
```

### Linting and Formatting

This repo uses **prek** (a modern pre-commit replacement), not classic pre-commit. Enable it once from `backend/`, then run on demand:

```bash
uv run prek install -f
uv run prek run --all-files
```

prek enforces ruff, ruff-format, mypy, `ty check`, biome, and typos, and regenerates generated artifacts. It runs automatically at commit time.

## Generated Code and Security

- **Never hand-edit `frontend/src/client/`.** It is generated from the OpenAPI schema. After any backend API change, regenerate it with `bash ./scripts/generate-client.sh` and commit the result; hand edits are overwritten on the next generate.
- **Never hand-edit `backend/app/email-templates/`.** It is generated from React Email components in `packages/react-email/` via `bun run email:export`. Edit the `.tsx` components; new backend values must also be added as Jinja placeholders in `generate_*_email()` in `backend/app/utils.py`.
- **Never commit real secrets.** `.env` is committed with development placeholders (`SECRET_KEY=changethis`). Change these for any real or deployed environment and keep real keys out of the repository.
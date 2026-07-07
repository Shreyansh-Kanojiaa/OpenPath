# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

OpenPath is an AI-driven personalized learning path platform. Users specify a skill, level, and time budget; Gemini 2.5 Flash generates a structured module syllabus, and a custom YouTube ranking engine attaches a best-fit video to each module. Also includes quiz-to-skip, a transcript-grounded live tutor chat, offline notes, flashcards, a career/job-readiness calculator, a skill graph, and a public course marketplace.

## Commands

### Backend (FastAPI, from `backend/`)
```bash
source ../venv/bin/activate        # existing venv at repo root
uvicorn main:app --reload          # dev server on :8000, docs at /docs
pytest -v                          # run all tests (in-memory SQLite, no network calls)
pytest tests/test_auth.py -v       # run a single test file
pytest tests/test_auth.py::test_login_success_returns_jwt -v   # run a single test
```
Installing deps: `pip install -r requirements.txt -r requirements-dev.txt` (dev file adds pytest/httpx/pytest-mock; prod image never installs these).

### Frontend (React 19 + Vite, from `react-frontend/`)
```bash
npm run dev      # dev server on :5173
npm run build    # production build (must succeed before shipping — CI checks this)
```
No lint or test script is configured for the frontend.

### Docker Compose (full stack: Postgres + backend + nginx-served frontend)
```bash
docker compose up --build -d
```
`.env` must set `JWT_SECRET_KEY` and `POSTGRES_PASSWORD` explicitly — compose fails fast (`${VAR:?...}`) if either is missing, there is no insecure default. Avoid special characters like `@` in `POSTGRES_PASSWORD` — it's interpolated unescaped into `DATABASE_URL` and will break the connection string. Backend/frontend host ports are overridable via `BACKEND_PORT`/`FRONTEND_PORT` env vars (both default to their container's standard port) in case those are already taken locally.

### Database migrations
Two migration mechanisms coexist and must both be updated together when adding a column:
- `backend/alembic/` — standard Alembic revisions (`alembic upgrade head` from `backend/`).
- `backend/migrate_db.py` — a hand-rolled idempotent column-adder keyed by `MIGRATIONS = {table: [(col, sql_def), ...]}`, run automatically on every backend startup (see `main.py`). This is what actually keeps existing SQLite/Postgres databases in sync in practice; the Alembic revision is the canonical schema history.

When adding a nullable column to an existing table, add it in three places: the SQLAlchemy model (`models.py`), a new Alembic revision chained off the latest `down_revision`, and an entry in `migrate_db.py`'s `MIGRATIONS` dict.

## Architecture

### Backend layout
- `main.py` — thin composition root: creates the app, configures CORS (`CORS_ORIGINS` env var, comma-separated — never re-add a wildcard-origin + credentials combo), wires the rate limiter, and calls `app.include_router(...)` for each router.
- `routers/{auth,courses,modules,quiz,career,analytics}.py` — one FastAPI `APIRouter` per resource area. Because `backend/auth.py` (JWT/hash helpers) and `routers/auth.py` (route handlers) would collide on the name, the router module is imported aliased: `from routers import auth as auth_router`. Inside router files themselves, `import auth` still refers to the JWT/hash helper module.
- `models.py` — SQLAlchemy ORM models (`User`, `Course`, `Module`, `QuizAttempt`). Note `Module.has_transcript`'s boolean default uses SQLAlchemy's `false()` construct (not `text('0')`) specifically because `text('0')` is valid SQLite but breaks table creation on Postgres (integer literal default on a boolean column) — keep using dialect-aware constructs for any new boolean server defaults.
- `schemas.py` — Pydantic schemas, several of which double as Gemini structured-output schemas (passed directly as `response_schema` in `services.py` — e.g. `CourseCreate`, `Quiz`, `FlashcardSet`, `JobReadyResponse`, `SkillGraphResponse`).
- `services.py` — all Gemini/YouTube integration logic lives here as module-level functions (`generate_syllabus`, `find_best_video`/`rank_video`, `generate_quiz_from_transcript`, `generate_flashcards`, `chat_with_module`, `generate_offline_notes`, `calculate_job_readiness`, `generate_skill_graph`). Every one of these has an explicit hardcoded mock fallback if `GEMINI_API_KEY` is unset or the API call throws — this is intentional graceful degradation, not a stub. Because these are plain module-level functions, the natural test seam is `monkeypatch.setattr(services, "fn_name", fake)` in the *router's* imported `services` module reference — no dependency injection layer exists.
- `auth.py` — JWT (python-jose) + bcrypt (used directly, bypassing passlib, per an intentional Python-version-compatibility workaround noted in the file). `JWT_SECRET_KEY` fails fast (`RuntimeError`) if unset when `ENVIRONMENT=production`; in any other environment it falls back to a generated ephemeral key with a loud console warning rather than a shared hardcoded default — never reintroduce a literal default secret.
- `limiter.py` — shared `slowapi` `Limiter` instance, kept in its own module (not inline in `main.py`) specifically to avoid a circular import, since router modules need to import the limiter but `main.py` imports the routers.
- `database.py` — SQLAlchemy engine/session; `DATABASE_URL` env var selects Postgres, otherwise defaults to local SQLite (`sql_app.db`).

### Frontend layout
- `react-frontend/` is the actively developed UI (React 19 + Vite + Tailwind v4, Tokyo Night theme). `legacy/streamlit/` is an archived prototype UI kept only for quick manual API smoke-testing — do not build new features there.
- The API base URL is `import.meta.env.VITE_API_URL`, falling back to `http://<hostname>:8000` for plain `npm run dev` against a locally-running backend. This constant is duplicated in four files (`App.jsx`, `features/LiveTutor.jsx`, `features/CareerHub.jsx`, `features/OfflineNotes.jsx`) — keep them in sync if it ever changes. The Docker build (`Dockerfile.frontend`) bakes in `VITE_API_URL=/api` at build time so the deployed bundle always goes through nginx's `/api/` reverse proxy (`docker/nginx.conf`) rather than assuming any particular host-exposed backend port.
- `App.jsx` is the main dashboard/page router (auth screen, course dashboard, marketplace/Discover, generate flow, watch-gated video player). `LandingPage.jsx` is the marketing page. `features/` holds larger standalone views (CareerHub's skill graph + job-readiness, LiveTutor's chat panel, OfflineNotes' markdown export). `components/ui/` holds small shared atoms.

### Testing
- `backend/tests/` — pytest suite using an in-memory SQLite engine (`StaticPool`, `check_same_thread=False`) with `database.get_db` overridden via FastAPI's `dependency_overrides`; auth flows are tested through the real JWT register→login path rather than bypassing `get_current_user`, since auth correctness is itself part of what's under test. Gemini/YouTube calls are always mocked (see `conftest.py`'s `create_course_with_module` fixture) — tests must never hit the real network.
- `.github/workflows/ci.yml` runs backend pytest and a frontend `npm run build` on every push/PR to `main`.

### Watch-time / completion gating
`POST /modules/{id}/complete` requires the client-reported `watch_time` to be ≥80% of `Module.video_duration`, enforced server-side (not just client-side) in `routers/modules.py`. `Module.completed_at` is set once, on first completion only (guarded by `if not module.is_completed`), from both this endpoint and the passed-quiz branch of `/submit-quiz` — don't let it get overwritten on repeat calls, since `GET /users/me/progress` relies on it for `last_completed_at`.

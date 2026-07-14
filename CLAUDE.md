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
pytest tests/test_auth.py::test_google_auth_new_user_creates_and_returns_jwt -v   # run a single test
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
`.env` must set `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`, and `GOOGLE_CLIENT_ID` explicitly — compose fails fast (`${VAR:?...}`) if any is missing, there is no insecure default. Avoid special characters like `@` in `POSTGRES_PASSWORD` — it's interpolated unescaped into `DATABASE_URL` and will break the connection string. Backend/frontend host ports are overridable via `BACKEND_PORT`/`FRONTEND_PORT` env vars (both default to their container's standard port) in case those are already taken locally.

`GOOGLE_CLIENT_ID` is consumed in **two** places from that single `.env` value: the backend reads it at runtime (to verify Google ID tokens), and the frontend bakes it into the JS bundle at **build time** via the `VITE_GOOGLE_CLIENT_ID` build arg (`Dockerfile.frontend`). So changing it — or setting it for the first time — requires rebuilding the frontend image (`docker compose ... up -d --build`), not just a restart; a bare restart ships the old bundle with no/stale client id and the Google button won't render. The value is public (safe in the bundle); there is no client secret in this flow.

Production runs the prod overlay explicitly: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build` (this skips `docker-compose.override.yml`, which is dev-only: it publishes ports, forces `ENVIRONMENT=development`, and bind-mounts `./backend`). Deployment gotchas learned the hard way:
- **SELinux hosts (Fedora/RHEL):** the dev override's `./backend:/app` bind mount carries a `:z` relabel suffix. Without it, SELinux denies the container read access → uvicorn can't import `main` → nginx returns a 502 HTML page → the frontend's `JSON.parse` throws `Unexpected token '<'`. Any new bind mount on these hosts needs `:z`/`:Z`.
- **Postgres password changes don't take on an existing volume:** `POSTGRES_PASSWORD` is only applied when the `postgres_data` volume is first initialized. Editing it later in `.env` leaves the DB user on the old password, and the backend crash-loops with `password authentication failed for user "openpath"`. Fix by re-initializing the volume (`docker volume rm <project>_postgres_data`, destroys data) or `ALTER USER … PASSWORD` inside the db container (keeps data).
- **Backend `print()` diagnostics need `PYTHONUNBUFFERED=1`:** the Dockerfile sets this so stdout isn't block-buffered under gunicorn (Python fully buffers stdout whenever it isn't a TTY, which is always true for a backgrounded container process). Without it, `print()`-based diagnostics (Gemini fallback warnings, YouTube search failures in `services.py`) can sit unflushed indefinitely and never show up in `docker compose logs`, even though the code ran — don't trust an empty `docker compose logs | grep ...` as proof something didn't happen unless this env var is confirmed set.

### Database migrations
Two migration mechanisms coexist and must both be updated together when adding a column:
- `backend/alembic/` — standard Alembic revisions (`alembic upgrade head` from `backend/`).
- `backend/migrate_db.py` — a hand-rolled idempotent column-adder keyed by `MIGRATIONS = {table: [(col, sql_def), ...]}`, run automatically on every backend startup (see `main.py`). This is what actually keeps existing SQLite/Postgres databases in sync in practice; the Alembic revision is the canonical schema history.

When adding a nullable column to an existing table, add it in three places: the SQLAlchemy model (`models.py`), a new Alembic revision chained off the latest `down_revision`, and an entry in `migrate_db.py`'s `MIGRATIONS` dict.

### One-off maintenance scripts (`backend/`)
- `backfill_videos.py` — re-runs `services.find_best_video` for every existing `Module` with `video_id IS NULL` across all courses (e.g. after improving the search/fallback logic in `services.py`, to fix modules that were already stuck before the fix shipped). Run with `--dry-run` first to preview; safe to re-run, only touches rows still missing a video. In production: `docker compose exec backend python backfill_videos.py`.
- `debug_video_search.py <module_id>` — read-only diagnostic that reproduces `find_best_video`'s exact search strategies for one module and prints every raw YouTube result plus why `rank_video` accepted/rejected it (too short/long, non-Latin, clickbait, or low keyword relevance with the actual numbers). Use this before touching ranking logic, to see whether a module's search is failing because YouTube has genuinely nothing relevant, or because the scoring is rejecting viable candidates.

## Architecture

### Backend layout
- `main.py` — thin composition root: creates the app, configures CORS (`CORS_ORIGINS` env var, comma-separated — never re-add a wildcard-origin + credentials combo), wires the rate limiter, and calls `app.include_router(...)` for each router.
- `routers/{auth,courses,modules,quiz,career,analytics}.py` — one FastAPI `APIRouter` per resource area. Because `backend/auth.py` (JWT/hash helpers) and `routers/auth.py` (route handlers) would collide on the name, the router module is imported aliased: `from routers import auth as auth_router`. Inside router files themselves, `import auth` still refers to the JWT/hash helper module.
  - `routers/modules.py`'s `POST /modules/{module_id}/retry-video` re-runs `services.find_best_video` for a module whose `video_id` is still `null` (course-creation-time search came back empty), checked against course ownership. The frontend (`WatchGatedVideo` in `App.jsx`) calls this automatically once whenever a module loads with no `video_id`, and exposes a manual "Try again" button if that retry also fails — a module with no video is recoverable now, not permanently stuck.
- `models.py` — SQLAlchemy ORM models (`User`, `Course`, `Module`, `QuizAttempt`). `User.google_sub` (Google's stable subject id, unique + nullable) is the primary sign-in lookup key, with `email` as the secondary link key; `User.hashed_password` remains on the model but is legacy/unused (no password login). Note `Module.has_transcript`'s boolean default uses SQLAlchemy's `false()` construct (not `text('0')`) specifically because `text('0')` is valid SQLite but breaks table creation on Postgres (integer literal default on a boolean column) — keep using dialect-aware constructs for any new boolean server defaults.
- `schemas.py` — Pydantic schemas, several of which double as Gemini structured-output schemas (passed directly as `response_schema` in `services.py` — e.g. `CourseCreate`, `Quiz`, `FlashcardSet`, `JobReadyResponse`, `SkillGraphResponse`).
- `services.py` — all Gemini/YouTube integration logic lives here as module-level functions (`generate_syllabus`, `find_best_video`/`rank_video`, `generate_quiz_from_transcript`, `generate_flashcards`, `chat_with_module`, `generate_offline_notes`, `calculate_job_readiness`, `generate_skill_graph`). Every one of these has an explicit hardcoded mock fallback if `GEMINI_API_KEY` is unset or the API call throws — this is intentional graceful degradation, not a stub. Because these are plain module-level functions, the natural test seam is `monkeypatch.setattr(services, "fn_name", fake)` in the *router's* imported `services` module reference — no dependency injection layer exists.
  - `_cached_syllabus` (the Gemini call behind `generate_syllabus`) retries once with a 2s backoff before giving up and falling into the mock template — a single transient Gemini error (rate limit, network blip) used to permanently commit a course to the generic mock syllabus, whose module titles/search queries are written with a software/programming course in mind (e.g. "debugging and architecture", "ecosystem and third-party integrations") and produce nonsensical YouTube searches for non-technical skills.
  - `find_best_video` builds a `Module.video_id` from `rank_video`-scored search results; if every strategy's candidates get hard-rejected by the strict keyword-relevance gate, it now falls back to a *relaxed* pass (`rank_video(..., strict_relevance=False)`) over everything already fetched, keeping only the duration/language/clickbait gates — a generic-but-on-skill video beats a permanently empty module. Only if that relaxed pool is also empty does it return `None`, which becomes a `null` `Module.video_id`.
- `auth.py` — issues/decodes the app's own JWT (python-jose) **and** verifies Google ID tokens. Sign-in is **Google-only** (Google Identity Services ID-token flow): the frontend obtains a signed Google credential and POSTs it to `/auth/google`; `verify_google_credential()` validates it against Google's public keys via the `google-auth` library, then `routers/auth.py` upserts the user and mints the app JWT with `create_access_token` — so everything downstream of login (`op_token`, `/auth/me`, `Authorization: Bearer`) is unchanged. `verify_google_credential` is a module-level function specifically so tests can monkeypatch it (the same seam pattern as `services.py`). There is **no** `/auth/register` or `/auth/login` and no password path; the bcrypt helpers (used directly, bypassing passlib, per a Python-version-compatibility workaround in the file) and `User.hashed_password` remain but are dead code — do not reintroduce password registration. `JWT_SECRET_KEY` fails fast (`RuntimeError`) if unset when `ENVIRONMENT=production` (otherwise a generated ephemeral key with a loud warning); `GOOGLE_CLIENT_ID` fails fast the same way in production. Never reintroduce a literal default secret.
- `limiter.py` — shared `slowapi` `Limiter` instance, kept in its own module (not inline in `main.py`) specifically to avoid a circular import, since router modules need to import the limiter but `main.py` imports the routers.
- `database.py` — SQLAlchemy engine/session; `DATABASE_URL` env var selects Postgres, otherwise defaults to local SQLite (`sql_app.db`).

### Frontend layout
- `react-frontend/` is the actively developed UI (React 19 + Vite + Tailwind v4, Tokyo Night theme). `legacy/streamlit/` is an archived prototype UI kept only for quick manual API smoke-testing — do not build new features there.
- The API base URL is `import.meta.env.VITE_API_URL`, falling back to `http://<hostname>:8000` for plain `npm run dev` against a locally-running backend. This constant is duplicated in four files (`App.jsx`, `features/LiveTutor.jsx`, `features/CareerHub.jsx`, `features/OfflineNotes.jsx`) — keep them in sync if it ever changes. The Docker build (`Dockerfile.frontend`) bakes in `VITE_API_URL=/api` at build time so the deployed bundle always goes through nginx's `/api/` reverse proxy (`docker/nginx.conf`) rather than assuming any particular host-exposed backend port.
- The auth screen (`AuthScreen` in `App.jsx`) renders a Google Identity Services "Sign in with Google" button — the GIS library is loaded via a `<script src="https://accounts.google.com/gsi/client">` tag in `index.html`, and the button's client id comes from `import.meta.env.VITE_GOOGLE_CLIENT_ID` (baked at build time; see the Docker Compose note above). On success it POSTs the credential to `/auth/google` and stores the returned app JWT as `op_token` — there is no password/register form.
- `App.jsx` is the main dashboard/page router (auth screen, course dashboard, marketplace/Discover, generate flow, watch-gated video player). `LandingPage.jsx` is the marketing page. `features/` holds larger standalone views (CareerHub's skill graph + job-readiness, LiveTutor's chat panel, OfflineNotes' markdown export). `components/ui/` holds small shared atoms.

### Testing
- `backend/tests/` — pytest suite using an in-memory SQLite engine (`StaticPool`, `check_same_thread=False`) with `database.get_db` overridden via FastAPI's `dependency_overrides`. Auth flows run through the real `/auth/google` → JWT → `get_current_user` path (not bypassed), with only the Google token check mocked: `monkeypatch.setattr(auth_lib, "verify_google_credential", …)` returns fixed claims, so no test ever hits Google's network (see `conftest.py`'s `registered_user` fixture). Gemini/YouTube calls are likewise always mocked (see `create_course_with_module`) — tests must never hit the real network.
- `.github/workflows/ci.yml` runs backend pytest and a frontend `npm run build` on every push/PR to `main`.

### Watch-time / completion gating
`POST /modules/{id}/complete` requires the client-reported `watch_time` to be ≥80% of `Module.video_duration`, enforced server-side (not just client-side) in `routers/modules.py`. `Module.completed_at` is set once, on first completion only (guarded by `if not module.is_completed`), from both this endpoint and the passed-quiz branch of `/submit-quiz` — don't let it get overwritten on repeat calls, since `GET /users/me/progress` relies on it for `last_completed_at`.

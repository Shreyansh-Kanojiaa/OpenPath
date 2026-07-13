import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

import models, database
from limiter import limiter
from routers import auth as auth_router, courses, modules, quiz, career, analytics, account

models.Base.metadata.create_all(bind=database.engine)

# Auto-migrate: add any new columns that models.py defines but the DB doesn't have yet.
# This is idempotent — safe to run on every startup.
try:
    import migrate_db
    migrate_db.migrate()
except Exception as e:
    print(f"[startup] Auto-migration note: {e}")

app = FastAPI(title="OpenPath — Skill Aggregator API", version="2.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_default_origins = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:80,http://localhost"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the OpenPath API v2"}


app.include_router(auth_router.router)
app.include_router(courses.router)
app.include_router(modules.router)
app.include_router(quiz.router)
app.include_router(career.router)
app.include_router(analytics.router)
app.include_router(account.router)

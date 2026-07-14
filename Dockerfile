# OpenPath Backend - FastAPI
# Multi-stage: build wheels in a throwaway stage, ship only the runtime.

# ── Build stage: install dependencies into an isolated prefix ─────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install into /install so the final stage can copy a clean tree with no pip cache.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage: slim image, non-root user ─────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Unbuffer stdout/stderr so print() output (Gemini/YouTube fallback diagnostics, etc.)
# reaches `docker compose logs` immediately instead of sitting in Python's block
# buffer, which applies whenever stdout isn't a TTY (i.e. always, under gunicorn).
ENV PYTHONUNBUFFERED=1

# Bring in the installed packages only (default prefix is /usr/local).
COPY --from=builder /install /usr/local

# Copy backend source. A .dockerignore keeps sql_app.db, __pycache__, and tests out.
COPY backend/ .

# Run as an unprivileged user rather than root.
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Container-level liveness: the / route returns a small JSON payload.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Production default: gunicorn managing uvicorn workers. The dev compose override
# swaps this for `uvicorn --reload`. Timeout is generous because Gemini calls can be slow.
# --preload imports the app once in the master before forking, so the startup
# create_all + migrate_db run a single time instead of racing across workers.
CMD ["gunicorn", "main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--preload", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]

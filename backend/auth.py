import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

import models
import database

# ── Config ────────────────────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
_env_secret = os.getenv("JWT_SECRET_KEY")

if not _env_secret:
    if ENVIRONMENT == "production":
        raise RuntimeError(
            "JWT_SECRET_KEY must be set in production. "
            'Generate one: python -c "import secrets; print(secrets.token_hex(32))"'
        )
    _env_secret = secrets.token_hex(32)
    print(
        "[auth] WARNING: JWT_SECRET_KEY not set — using an ephemeral dev-only key "
        "(existing tokens will be invalidated on restart). Set JWT_SECRET_KEY in .env "
        "for a persistent dev session."
    )

SECRET_KEY = _env_secret
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h

# Google Sign-In: the OAuth Client ID the ID token must be issued for (its `aud`).
# Fail fast in production if missing — without it we cannot verify Google tokens.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID and ENVIRONMENT == "production":
    raise RuntimeError("GOOGLE_CLIENT_ID must be set in production (Google Sign-In cannot be verified without it).")

# ── Crypto ────────────────────────────────────────────────────────────────────
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt directly (bypasses passlib/Python 3.14 incompatibility)."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── Token ─────────────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def verify_google_credential(credential: str) -> dict:
    """Verify a Google ID token and return its claims.

    Raises on any invalid/expired/wrong-audience token. Imported lazily so the
    google-auth dependency is only needed when Google Sign-In is actually used,
    and so tests can monkeypatch this function without importing google-auth.
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    return id_token.verify_oauth2_token(credential, google_requests.Request(), GOOGLE_CLIENT_ID)


# ── FastAPI Dependency ────────────────────────────────────────────────────────
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(database.get_db),
) -> models.User:
    """Validates Bearer JWT and returns the authenticated User ORM object."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload invalid.")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user

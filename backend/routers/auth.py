import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import models, database, schemas, auth as auth_lib
from limiter import limiter, LOGIN_RATE

router = APIRouter(tags=["auth"])


def _unique_username(db: Session, preferred: str) -> str:
    """Return a username based on `preferred`, appending a numeric suffix on collision."""
    base = re.sub(r"[^a-z0-9_]", "", preferred.strip().lower().replace(" ", "_")) or "user"
    base = base[:40]
    candidate = base
    n = 1
    while db.query(models.User).filter(models.User.username == candidate).first():
        n += 1
        candidate = f"{base}{n}"
    return candidate


@router.post("/auth/google", response_model=schemas.Token)
@limiter.limit(LOGIN_RATE)
def google_auth(request: Request, body: schemas.GoogleAuthRequest, db: Session = Depends(database.get_db)):
    """Sign in with Google. Verifies the ID token, upserts the user, returns our app JWT."""
    try:
        claims = auth_lib.verify_google_credential(body.credential)
    except Exception as exc:
        logging.getLogger("uvicorn.error").warning("Google sign-in verify failed: %r", exc)
        raise HTTPException(status_code=401, detail="Invalid Google sign-in.")

    google_sub = claims.get("sub")
    email = (claims.get("email") or "").strip().lower()
    if not google_sub or not email:
        raise HTTPException(status_code=401, detail="Google account missing an email.")

    # 1. known Google account  2. else link to an existing account by email  3. else create.
    user = db.query(models.User).filter(models.User.google_sub == google_sub).first()
    if not user:
        user = db.query(models.User).filter(models.User.email == email).first()

    if user:
        user.google_sub = google_sub
        if not user.email:
            user.email = email
    else:
        preferred = claims.get("name") or email.split("@", 1)[0]
        user = models.User(
            google_sub=google_sub,
            email=email,
            username=_unique_username(db, preferred),
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    token = auth_lib.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token, user_id=user.id, username=user.username)


@router.get("/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth_lib.get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user

import json
import re
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, database, schemas, services, auth

router = APIRouter(tags=["account"])

USERNAME_CHANGE_COOLDOWN_DAYS = 30
USERNAME_PATTERN = re.compile(r"^[a-z0-9_]{3,40}$")


def _next_username_change_allowed_at(user: models.User) -> datetime | None:
    if not user.last_username_change_at:
        return None
    return user.last_username_change_at + timedelta(days=USERNAME_CHANGE_COOLDOWN_DAYS)


@router.get("/account/settings", response_model=schemas.AccountSettingsResponse)
def get_account_settings(
    current_user: models.User = Depends(auth.get_current_user),
):
    next_allowed = _next_username_change_allowed_at(current_user)
    can_change = next_allowed is None or datetime.utcnow() >= next_allowed

    return schemas.AccountSettingsResponse(
        username=current_user.username,
        email=current_user.email,
        known_skills=json.loads(current_user.known_skills or "[]"),
        can_change_username=can_change,
        next_username_change_allowed_at=next_allowed,
    )


@router.patch("/account/username", response_model=schemas.UsernameUpdateResponse)
def update_username(
    request: schemas.UsernameUpdateRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    candidate = request.username.strip().lower()

    if candidate == current_user.username:
        return schemas.UsernameUpdateResponse(
            username=current_user.username,
            next_username_change_allowed_at=_next_username_change_allowed_at(current_user) or datetime.utcnow(),
        )

    next_allowed = _next_username_change_allowed_at(current_user)
    if next_allowed is not None and datetime.utcnow() < next_allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "message": f"You can only change your username once every {USERNAME_CHANGE_COOLDOWN_DAYS} days.",
                "next_username_change_allowed_at": next_allowed.isoformat(),
            },
        )

    if not USERNAME_PATTERN.match(candidate):
        raise HTTPException(
            status_code=400,
            detail="Username must be 3-40 characters, using only lowercase letters, numbers, and underscores.",
        )

    taken = (
        db.query(models.User)
        .filter(models.User.username == candidate, models.User.id != current_user.id)
        .first()
    )
    if taken:
        raise HTTPException(status_code=409, detail="Username already taken.")

    current_user.username = candidate
    current_user.last_username_change_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return schemas.UsernameUpdateResponse(
        username=current_user.username,
        next_username_change_allowed_at=_next_username_change_allowed_at(current_user),
    )


@router.put("/account/skills", response_model=schemas.SkillsUpdateResponse)
def update_known_skills(
    request: schemas.SkillsUpdateRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    deduped = services.dedupe_skills_case_insensitive(request.skills)
    current_user.known_skills = json.dumps(deduped)
    db.commit()

    return schemas.SkillsUpdateResponse(known_skills=deduped)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models, database, schemas, auth
from badges_catalog import BADGE_CATALOG

router = APIRouter(tags=["badges"])


@router.get("/users/me/badges", response_model=schemas.BadgesResponse)
def get_my_badges(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Full badge catalog with this user's earned/locked state. Read-only — does not award badges."""
    earned = {
        ub.badge_key: ub.earned_at
        for ub in db.query(models.UserBadge).filter(models.UserBadge.user_id == current_user.id).all()
    }
    badges = [
        schemas.BadgeInfo(
            key=key,
            name=meta["name"],
            description=meta["description"],
            icon=meta["icon"],
            category=meta["category"],
            earned=key in earned,
            earned_at=earned.get(key),
        )
        for key, meta in BADGE_CATALOG.items()
    ]
    return schemas.BadgesResponse(badges=badges)

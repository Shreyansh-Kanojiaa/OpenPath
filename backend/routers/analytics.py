from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models, database, schemas, auth

router = APIRouter(tags=["analytics"])


@router.get("/users/me/progress", response_model=schemas.ProgressResponse)
def get_my_progress(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Cumulative progress across all of the current user's courses/modules."""
    courses = db.query(models.Course).filter(models.Course.user_id == current_user.id).all()
    all_modules = [m for c in courses for m in c.modules]
    completed = [m for m in all_modules if m.is_completed]

    completion_rate = (len(completed) / len(all_modules)) if all_modules else 0.0
    last_completed_at = max((m.completed_at for m in completed if m.completed_at), default=None)

    return schemas.ProgressResponse(
        courses_count=len(courses),
        total_modules=len(all_modules),
        modules_completed=len(completed),
        completion_rate=round(completion_rate, 4),
        last_completed_at=last_completed_at,
    )


@router.get("/users/me/activity", response_model=schemas.ActivityResponse)
def get_my_activity(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Sparse day->count activity for the contribution graph (module completions + passed quizzes)."""
    cutoff = datetime.utcnow() - timedelta(days=365)

    courses = db.query(models.Course).filter(models.Course.user_id == current_user.id).all()
    completed_dates = [
        m.completed_at.date() for c in courses for m in c.modules
        if m.completed_at and m.completed_at >= cutoff
    ]

    passed_quiz_dates = [
        a.attempted_at.date()
        for a in db.query(models.QuizAttempt).filter(
            models.QuizAttempt.user_id == current_user.id,
            models.QuizAttempt.passed == True,  # noqa: E712 — SQLAlchemy needs `== True`, not `is True`
            models.QuizAttempt.attempted_at >= cutoff,
        ).all()
    ]

    counts = Counter(completed_dates + passed_quiz_dates)
    days = [schemas.ActivityDay(date=d.isoformat(), count=n) for d, n in sorted(counts.items())]
    return schemas.ActivityResponse(days=days)

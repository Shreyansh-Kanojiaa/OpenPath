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

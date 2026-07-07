from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, database, schemas, services, auth

router = APIRouter(tags=["quiz"])


@router.post("/generate-quiz", response_model=schemas.Quiz)
def generate_quiz(
    module_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found.")
    return services.generate_quiz_from_transcript(
        module.video_id or "", module.id, f"{module.title}: {module.description}"
    )


@router.post("/submit-quiz")
def submit_quiz(
    module_id: int,
    score: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    passed = score >= 4  # ≥80% to pass

    attempt = models.QuizAttempt(
        module_id=module_id,
        user_id=current_user.id,
        score=score,
        passed=passed,
    )
    db.add(attempt)

    if passed:
        module = db.query(models.Module).filter(models.Module.id == module_id).first()
        if module:
            if not module.is_completed:
                module.completed_at = datetime.utcnow()
            module.is_skipped = True
            module.is_completed = True

    db.commit()
    return {"passed": passed, "score": score}

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, database, schemas, services, auth

router = APIRouter(tags=["career"])


@router.post("/modules/{module_id}/chat")
def chat_with_module(
    module_id: int,
    request: schemas.ChatRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found.")

    response_text = services.chat_with_module(
        module.video_id,
        f"{module.title}: {module.description}",
        request.messages
    )
    return {"response": response_text}


@router.get("/modules/{module_id}/offline-notes")
def get_offline_notes(
    module_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found.")

    notes = services.generate_offline_notes(
        module.video_id,
        f"{module.title}: {module.description}"
    )
    return {"notes": notes}


@router.post("/career/job-ready")
def check_job_readiness(
    request: schemas.JobReadyRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    courses = db.query(models.Course).filter(models.Course.user_id == current_user.id).all()
    completed_skills = [c.skill_name for c in courses if any(m.is_completed for m in c.modules)]

    known_skills = json.loads(current_user.known_skills or "[]")
    merged_skills = services.dedupe_skills_case_insensitive(completed_skills + known_skills)

    return services.calculate_job_readiness(request.job_title, request.company, merged_skills)


@router.get("/career/skill-graph")
def get_skill_graph(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    courses = db.query(models.Course).filter(models.Course.user_id == current_user.id).all()
    completed_skills = [c.skill_name for c in courses if any(m.is_completed for m in c.modules)]

    return services.generate_skill_graph(completed_skills)

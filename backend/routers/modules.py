from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, database, schemas, services, auth, badge_service

router = APIRouter(tags=["modules"])


@router.post("/modules/{module_id}/complete")
def complete_module(
    module_id: int,
    body: schemas.ModuleCompleteRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Mark a module as completed — requires that the user actively watched ≥80% of the video."""
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found.")

    required_secs = int((module.video_duration or 600) * 0.80)
    if body.watch_time < required_secs:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient watch time. You watched {body.watch_time}s but {required_secs}s is required.",
        )

    if not module.is_completed:
        module.completed_at = datetime.utcnow()
    module.is_completed = True
    db.commit()
    new_badges = badge_service.evaluate_and_award(db, current_user)
    return {"status": "success", "module_id": module_id, "new_badges": new_badges}


@router.post("/modules/{module_id}/retry-video")
def retry_video(
    module_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Re-run the YouTube search for a module whose initial video assignment came back empty."""
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found.")

    course = db.query(models.Course).filter(models.Course.id == module.course_id).first()
    if not course or course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    if module.video_id:
        return {"video_id": module.video_id, "video_duration": module.video_duration}

    used_videos = {m.video_id for m in course.modules if m.video_id}
    best_video_data = services.find_best_video(
        module.search_query,
        exclude_ids=used_videos,
        module_title=module.title,
        module_description=module.description,
        skill_name=course.skill_name,
    )
    if not best_video_data:
        raise HTTPException(status_code=404, detail="No suitable video found. Please try again shortly.")

    module.video_id = best_video_data["id"]
    module.video_duration = best_video_data["duration"]
    db.commit()
    return {"video_id": module.video_id, "video_duration": module.video_duration}


@router.patch("/modules/{module_id}/notes")
def save_notes(
    module_id: int,
    note_in: schemas.NoteUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Save or update user notes for a specific module."""
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found.")
    module.notes = note_in.notes
    db.commit()
    return {"status": "saved", "module_id": module_id}


@router.get("/modules/{module_id}/flashcards", response_model=schemas.FlashcardSet)
def get_flashcards(
    module_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Generate AI flashcards for a completed module using its transcript or topic."""
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found.")
    if not module.is_completed:
        raise HTTPException(status_code=400, detail="Complete this module first to unlock flashcards.")
    return services.generate_flashcards(module_id, module.video_id, f"{module.title}: {module.description}")


@router.get("/modules/{module_id}/has-transcript")
def check_transcript(module_id: int, db: Session = Depends(database.get_db)):
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module or not module.video_id:
        return {"has_transcript": False}
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        YouTubeTranscriptApi.list_transcripts(module.video_id)
        return {"has_transcript": True}
    except Exception:
        return {"has_transcript": False}

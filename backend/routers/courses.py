from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

import models, database, schemas, services, auth, badge_service

router = APIRouter(tags=["courses"])


@router.post("/generate-course", response_model=schemas.CourseResponse)
def generate_course(
    skill: str,
    level: int,
    time: str,
    depth: str = "Standard (5 modules)",
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Generate an AI syllabus with best-fit YouTube videos, saved to the user's account."""
    if not skill.strip():
        raise HTTPException(status_code=400, detail="Please enter a skill to learn.")

    validation = services.validate_skill(skill)
    if not validation.is_valid_skill:
        raise HTTPException(status_code=400, detail="That doesn't look like a valid skill to learn. Try something like \"Python\" or \"watercolor painting\".")

    course_data = services.generate_syllabus(skill, level, time, depth)

    new_course = models.Course(
        user_id=current_user.id,
        skill_name=course_data.skill_name,
        current_level=course_data.start_level,
        time_commitment=course_data.time_commitment,
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    used_videos: set = set()
    for mod in course_data.modules:
        best_video_data = services.find_best_video(
            mod.search_query,
            exclude_ids=used_videos,
            depth=depth,
            module_title=mod.title,
            module_description=mod.description,
            skill_name=course_data.skill_name,
        )
        best_video_id = best_video_data["id"] if best_video_data else None
        video_duration = best_video_data["duration"] if best_video_data else 600  # 10-min wall

        if best_video_id:
            used_videos.add(best_video_id)

        new_module = models.Module(
            course_id=new_course.id,
            title=mod.title,
            description=mod.description,
            order_index=mod.order_index,
            search_query=mod.search_query,
            video_id=best_video_id,
            video_duration=video_duration,
        )
        db.add(new_module)

    db.commit()
    new_course.new_badges = badge_service.evaluate_and_award(db, current_user)
    return new_course


@router.get("/courses", response_model=List[schemas.CourseResponse])
def get_user_courses(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Return all courses belonging to the authenticated user."""
    return db.query(models.Course).filter(models.Course.user_id == current_user.id).all()


@router.get("/courses/public", response_model=schemas.PaginatedCoursesResponse)
def get_public_courses(
    skill: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(database.get_db),
):
    """Public marketplace endpoint — no auth required. Supports search by skill and pagination."""
    q = db.query(models.Course).filter(models.Course.is_public == True)
    if skill:
        q = q.filter(models.Course.skill_name.ilike(f"%{skill}%"))

    total = q.count()
    courses = q.order_by(models.Course.created_at.desc()).offset(offset).limit(limit).all()

    items = [
        schemas.CoursePublicResponse(
            id=c.id,
            skill_name=c.skill_name,
            current_level=c.current_level,
            time_commitment=c.time_commitment,
            owner_username=c.owner.username if c.owner else "Anonymous",
            module_count=len(c.modules),
        )
        for c in courses
    ]
    return schemas.PaginatedCoursesResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/courses/{course_id}")
def get_course(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Fetch a single course with its modules. Must belong to the user OR be public."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    if course.user_id != current_user.id and not course.is_public:
        raise HTTPException(status_code=403, detail="Access denied.")

    modules = (
        db.query(models.Module)
        .filter(models.Module.course_id == course_id)
        .order_by(models.Module.order_index)
        .all()
    )
    return {"course": course, "modules": modules}


@router.patch("/courses/{course_id}/visibility")
def toggle_visibility(
    course_id: int,
    make_public: bool,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Toggle a course between public and private."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    if course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course owner can change visibility.")
    course.is_public = make_public
    db.commit()
    return {"course_id": course_id, "is_public": make_public}


@router.post("/courses/{course_id}/enroll", response_model=schemas.CourseResponse)
def enroll_public_course(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Copy a public community course to the authenticated user's dashboard."""
    source = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Course not found.")
    if not source.is_public:
        raise HTTPException(status_code=403, detail="Course is not public.")
    if source.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You already own this course.")

    new_course = models.Course(
        user_id=current_user.id,
        skill_name=source.skill_name,
        current_level=source.current_level,
        time_commitment=source.time_commitment,
        is_public=False,
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    for mod in sorted(source.modules, key=lambda m: m.order_index):
        db.add(
            models.Module(
                course_id=new_course.id,
                title=mod.title,
                description=mod.description,
                order_index=mod.order_index,
                search_query=mod.search_query,
                video_id=mod.video_id,
                video_duration=mod.video_duration,
            )
        )
    db.commit()
    new_course.new_badges = badge_service.evaluate_and_award(db, current_user)
    return new_course

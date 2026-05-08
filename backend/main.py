from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv

import models, database, schemas, services, auth

load_dotenv(find_dotenv())

models.Base.metadata.create_all(bind=database.engine)

# Auto-migrate: add any new columns that models.py defines but the DB doesn't have yet.
# This is idempotent — safe to run on every startup.
try:
    import migrate_db
    migrate_db.migrate()
except Exception as e:
    print(f"[startup] Auto-migration note: {e}")

app = FastAPI(title="OpenPath — Skill Aggregator API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the OpenPath API v2"}


# ─────────────────────────────────────────────────────────────────────────────
# AUTH ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Register a new user. Returns a success message — client must redirect to login."""
    email_norm = user_in.email.strip().lower()
    username_norm = user_in.username.strip()

    if db.query(models.User).filter(models.User.email == email_norm).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    if db.query(models.User).filter(models.User.username == username_norm).first():
        raise HTTPException(status_code=400, detail="Username already taken.")

    new_user = models.User(
        username=username_norm,
        email=email_norm,
        hashed_password=auth.hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Account created successfully. Please log in.", "username": new_user.username}


@app.post("/auth/login", response_model=schemas.Token)
def login(creds: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """Login with email + password and return a JWT."""
    email_norm = creds.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email_norm).first()
    if not user or not user.hashed_password or not auth.verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = auth.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token, user_id=user.id, username=user.username)


@app.get("/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


# ─────────────────────────────────────────────────────────────────────────────
# COURSE ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/generate-course", response_model=schemas.CourseResponse)
def generate_course(
    skill: str,
    level: int,
    time: str,
    depth: str = "Standard (5 modules)",
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Generate an AI syllabus with best-fit YouTube videos, saved to the user's account."""
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
    return new_course


@app.get("/courses", response_model=List[schemas.CourseResponse])
def get_user_courses(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Return all courses belonging to the authenticated user."""
    return db.query(models.Course).filter(models.Course.user_id == current_user.id).all()


@app.get("/courses/public", response_model=List[schemas.CoursePublicResponse])
def get_public_courses(db: Session = Depends(database.get_db)):
    """Public marketplace endpoint — no auth required."""
    courses = db.query(models.Course).filter(models.Course.is_public == True).all()
    result = []
    for c in courses:
        owner_username = c.owner.username if c.owner else "Anonymous"
        module_count = len(c.modules)
        result.append(
            schemas.CoursePublicResponse(
                id=c.id,
                skill_name=c.skill_name,
                current_level=c.current_level,
                time_commitment=c.time_commitment,
                owner_username=owner_username,
                module_count=module_count,
            )
        )
    return result


@app.get("/courses/{course_id}")
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


@app.patch("/courses/{course_id}/visibility")
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


@app.post("/courses/{course_id}/enroll", response_model=schemas.CourseResponse)
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
    return new_course


# ─────────────────────────────────────────────────────────────────────────────
# MODULE ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/modules/{module_id}/complete")
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

    module.is_completed = True
    db.commit()
    return {"status": "success", "module_id": module_id}


@app.patch("/modules/{module_id}/notes")
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


@app.get("/modules/{module_id}/flashcards", response_model=schemas.FlashcardSet)
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


@app.get("/modules/{module_id}/has-transcript")
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


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/generate-quiz", response_model=schemas.Quiz)
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


@app.post("/submit-quiz")
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
            module.is_skipped = True
            module.is_completed = True

    db.commit()
    return {"passed": passed, "score": score}

"""Badge (achievement) evaluation. DB-query-only — no Gemini/YouTube calls, hence
kept separate from services.py, which is entirely content-generation logic.

`evaluate_and_award` is the only public entry point: call it after any event
that could unlock a badge (module completion, quiz submission, course
creation/enrollment). It's idempotent and safe to call as often as needed.
"""
import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas
from badges_catalog import BADGE_CATALOG


def _fully_completed_courses(db: Session, user: models.User) -> list[models.Course]:
    courses = db.query(models.Course).filter(models.Course.user_id == user.id).all()
    return [c for c in courses if c.modules and all(m.is_completed for m in c.modules)]


def _active_dates(db: Session, user: models.User) -> set[datetime.date]:
    courses = db.query(models.Course).filter(models.Course.user_id == user.id).all()
    dates = {m.completed_at.date() for c in courses for m in c.modules if m.completed_at}
    passed_attempts = (
        db.query(models.QuizAttempt)
        .filter(models.QuizAttempt.user_id == user.id, models.QuizAttempt.passed == True)  # noqa: E712
        .all()
    )
    dates |= {a.attempted_at.date() for a in passed_attempts if a.attempted_at}
    return dates


def _current_streak(db: Session, user: models.User) -> int:
    dates = _active_dates(db, user)
    if not dates:
        return 0
    streak = 0
    day = datetime.datetime.utcnow().date()
    while day in dates:
        streak += 1
        day -= datetime.timedelta(days=1)
    return streak


def _passed_quiz_count(db: Session, user: models.User) -> int:
    return (
        db.query(models.QuizAttempt)
        .filter(models.QuizAttempt.user_id == user.id, models.QuizAttempt.passed == True)  # noqa: E712
        .count()
    )


def _check_first_course_created(db, user):
    return db.query(models.Course).filter(models.Course.user_id == user.id).count() >= 1


def _check_first_course_completed(db, user):
    return len(_fully_completed_courses(db, user)) >= 1


def _check_five_courses_completed(db, user):
    return len(_fully_completed_courses(db, user)) >= 5


def _check_ten_courses_created(db, user):
    return db.query(models.Course).filter(models.Course.user_id == user.id).count() >= 10


def _check_three_skills_mastered(db, user):
    completed = _fully_completed_courses(db, user)
    return len({c.skill_name for c in completed}) >= 3


def _check_deep_dive(db, user):
    return any(len(c.modules) >= 8 for c in _fully_completed_courses(db, user))


def _check_perfectionist_module(db, user):
    return any(
        not any(m.is_skipped for m in c.modules)
        for c in _fully_completed_courses(db, user)
    )


def _check_streak_3(db, user):
    return _current_streak(db, user) >= 3


def _check_streak_7(db, user):
    return _current_streak(db, user) >= 7


def _check_streak_30(db, user):
    return _current_streak(db, user) >= 30


def _check_first_quiz_passed(db, user):
    return _passed_quiz_count(db, user) >= 1


def _check_perfect_quiz(db, user):
    return (
        db.query(models.QuizAttempt)
        .filter(
            models.QuizAttempt.user_id == user.id,
            models.QuizAttempt.passed == True,  # noqa: E712
            models.QuizAttempt.score == 5,
        )
        .count()
        >= 1
    )


def _check_quiz_master(db, user):
    return _passed_quiz_count(db, user) >= 10


_CHECKERS = {
    "first_course_created": _check_first_course_created,
    "first_course_completed": _check_first_course_completed,
    "five_courses_completed": _check_five_courses_completed,
    "ten_courses_created": _check_ten_courses_created,
    "three_skills_mastered": _check_three_skills_mastered,
    "deep_dive": _check_deep_dive,
    "perfectionist_module": _check_perfectionist_module,
    "streak_3": _check_streak_3,
    "streak_7": _check_streak_7,
    "streak_30": _check_streak_30,
    "first_quiz_passed": _check_first_quiz_passed,
    "perfect_quiz": _check_perfect_quiz,
    "quiz_master": _check_quiz_master,
}


def evaluate_and_award(db: Session, user: models.User) -> list["schemas.NewlyEarnedBadge"]:
    """Re-evaluate all badge conditions for `user`, award any newly-satisfied
    ones, and return the list of badges newly unlocked by this call (empty if
    none). Already-earned badges are never re-evaluated or revoked."""
    already_earned = {
        ub.badge_key for ub in db.query(models.UserBadge).filter(models.UserBadge.user_id == user.id).all()
    }

    newly_earned: list[schemas.NewlyEarnedBadge] = []
    for key, checker in _CHECKERS.items():
        if key in already_earned or not checker(db, user):
            continue

        db.add(models.UserBadge(user_id=user.id, badge_key=key))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue

        meta = BADGE_CATALOG[key]
        newly_earned.append(
            schemas.NewlyEarnedBadge(key=key, name=meta["name"], description=meta["description"], icon=meta["icon"])
        )

    return newly_earned

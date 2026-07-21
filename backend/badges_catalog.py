"""Static badge/achievement metadata. Pure data — no DB or session imports.

Each entry maps a stable `badge_key` (never rename once shipped — it's the
persisted identity in `UserBadge.badge_key`) to display metadata. Evaluation
logic (whether a user has earned a given key) lives in `badge_service.py`.
"""

BADGE_CATALOG: dict[str, dict] = {
    # ── Course milestones ───────────────────────────────────────────────────
    "first_course_created": {
        "name": "First Steps",
        "description": "Create your first learning path.",
        "icon": "BookOpen",
        "category": "course_milestone",
    },
    "first_course_completed": {
        "name": "Course Complete",
        "description": "Finish every module in a course.",
        "icon": "Trophy",
        "category": "course_milestone",
    },
    "five_courses_completed": {
        "name": "Path Finder",
        "description": "Fully complete 5 courses.",
        "icon": "Award",
        "category": "course_milestone",
    },
    "ten_courses_created": {
        "name": "Curriculum Builder",
        "description": "Create 10 learning paths.",
        "icon": "GraduationCap",
        "category": "course_milestone",
    },
    # ── Skill mastery ────────────────────────────────────────────────────────
    "three_skills_mastered": {
        "name": "Multi-Disciplinary",
        "description": "Fully complete courses in 3 different skills.",
        "icon": "Star",
        "category": "skill_mastery",
    },
    "deep_dive": {
        "name": "Deep Dive",
        "description": "Complete every module of a course with 8 or more modules.",
        "icon": "Target",
        "category": "skill_mastery",
    },
    "perfectionist_module": {
        "name": "Zero Skips",
        "description": "Fully complete a course by watching every module, no quiz-skips.",
        "icon": "CheckCircle2",
        "category": "skill_mastery",
    },
    # ── Streaks ──────────────────────────────────────────────────────────────
    "streak_3": {
        "name": "On a Roll",
        "description": "Stay active for 3 days in a row.",
        "icon": "Flame",
        "category": "streak",
    },
    "streak_7": {
        "name": "Week Warrior",
        "description": "Stay active for 7 days in a row.",
        "icon": "Flame",
        "category": "streak",
    },
    "streak_30": {
        "name": "Unstoppable",
        "description": "Stay active for 30 days in a row.",
        "icon": "Zap",
        "category": "streak",
    },
    # ── Quiz performance ─────────────────────────────────────────────────────
    "first_quiz_passed": {
        "name": "Quiz Rookie",
        "description": "Pass your first quiz.",
        "icon": "Briefcase",
        "category": "quiz_performance",
    },
    "perfect_quiz": {
        "name": "Perfect Score",
        "description": "Ace a quiz with a perfect score.",
        "icon": "Star",
        "category": "quiz_performance",
    },
    "quiz_master": {
        "name": "Quiz Master",
        "description": "Pass 10 quizzes.",
        "icon": "Trophy",
        "category": "quiz_performance",
    },
}

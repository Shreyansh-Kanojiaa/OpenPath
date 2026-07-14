"""
One-off maintenance script: re-runs YouTube video search for every existing module
that has no video_id (find_best_video came back empty at course-creation time —
see routers/modules.py's retry-video endpoint for the same logic exposed per-module
over the API). Safe to re-run — only touches modules where video_id IS NULL.

Usage (from backend/, with the venv active and DATABASE_URL set for the target DB):
    python backfill_videos.py [--dry-run]
"""

import sys

from database import SessionLocal
import models
import services


def backfill(dry_run: bool = False):
    db = SessionLocal()
    try:
        courses = db.query(models.Course).all()
        total_missing = 0
        total_fixed = 0

        for course in courses:
            used_videos = {m.video_id for m in course.modules if m.video_id}
            missing = [m for m in course.modules if not m.video_id]
            if not missing:
                continue

            for module in missing:
                total_missing += 1
                print(f"[course {course.id} '{course.skill_name}'] module {module.id} '{module.title}' -> searching...")

                best_video_data = services.find_best_video(
                    module.search_query,
                    exclude_ids=used_videos,
                    module_title=module.title,
                    module_description=module.description,
                    skill_name=course.skill_name,
                )
                if not best_video_data:
                    print(f"  still no video found for module {module.id}")
                    continue

                used_videos.add(best_video_data["id"])
                total_fixed += 1
                print(f"  -> found video_id={best_video_data['id']} duration={best_video_data['duration']}")

                if not dry_run:
                    module.video_id = best_video_data["id"]
                    module.video_duration = best_video_data["duration"]

            if not dry_run:
                db.commit()

        print(f"\nDone. {total_fixed}/{total_missing} previously-empty modules now have a video.")
        if dry_run:
            print("(dry run — no changes were saved)")
    finally:
        db.close()


if __name__ == "__main__":
    backfill(dry_run="--dry-run" in sys.argv)

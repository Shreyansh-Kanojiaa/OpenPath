"""
Read-only diagnostic for a module whose video search comes back empty
("ALL strategies exhausted"). Reproduces find_best_video()'s exact search
strategies and rank_video() scoring, but prints every raw result and why it
was rejected — instead of silently returning None. Makes no DB writes.

Usage (inside the backend container, from backend/):
    python debug_video_search.py <module_id>
"""

import sys

from database import SessionLocal
import models
import services
from youtube_search import YoutubeSearch


def explain_rejection(video: dict, query: str, depth: str, module_title: str,
                       module_description: str, skill_name: str) -> str:
    duration_str = str(video.get("duration", "0:00"))
    parts = duration_str.split(":")
    minutes = 0
    try:
        if len(parts) == 3:
            minutes = int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 2:
            minutes = int(parts[0])
    except ValueError:
        pass
    if minutes < 5:
        return f"too short ({duration_str})"
    max_duration = 120 if "In-Depth" in depth or "Comprehensive" in depth else 60
    if minutes > max_duration:
        return f"too long ({duration_str}, cap={max_duration}m)"

    title = str(video.get("title", ""))
    if services._has_non_latin(title):
        return "non-Latin title"
    if services._NEGATIVE_TITLE_PATTERNS.search(title.lower()):
        return "clickbait pattern"

    query_keywords = services._extract_topic_keywords(query)
    title_keywords = services._extract_topic_keywords(module_title) if module_title else set()
    desc_keywords = services._extract_topic_keywords(module_description) if module_description else set()
    skill_keywords = services._extract_topic_keywords(skill_name) if skill_name else set()
    all_context_keywords = query_keywords | title_keywords | desc_keywords | skill_keywords
    video_title_keywords = services._extract_topic_keywords(title)

    if all_context_keywords:
        forward_matches = all_context_keywords.intersection(video_title_keywords)
        phrase_bonus = 0.0
        if skill_name and skill_name.lower() in title.lower():
            phrase_bonus += 0.2
        if module_title and services._clean_module_title(module_title).lower() in title.lower():
            phrase_bonus += 0.3
        forward_ratio = len(forward_matches) / len(all_context_keywords)
        if forward_ratio < 0.15 and phrase_bonus < 0.3:
            return (f"low relevance (forward_ratio={forward_ratio:.2f}, phrase_bonus={phrase_bonus:.2f}, "
                    f"context_kw={sorted(all_context_keywords)}, video_kw={sorted(video_title_keywords)})")

    return "PASSED (score computed normally)"


def debug(module_id: int):
    db = SessionLocal()
    try:
        module = db.query(models.Module).filter(models.Module.id == module_id).first()
        if not module:
            print(f"No module with id {module_id}")
            return
        course = db.query(models.Course).filter(models.Course.id == module.course_id).first()

        query = module.search_query
        module_title = module.title
        module_description = module.description
        skill_name = course.skill_name

        print(f"module {module_id}: '{module_title}'  (course: '{skill_name}')")
        print(f"  search_query = {query!r}")
        print(f"  description  = {module_description!r}")
        print()

        clean_title = services._clean_module_title(module_title) if module_title else ""
        strategies = [query]
        if clean_title and skill_name:
            strategies.append(f"{skill_name} {clean_title} tutorial")
        if clean_title:
            strategies.append(f"{clean_title} explained {skill_name}")
        if module_description:
            desc_keywords = list(services._extract_topic_keywords(module_description))[:3]
            if desc_keywords:
                strategies.append(f"{skill_name} {clean_title} {' '.join(desc_keywords)}")
        strategies.append(f"{skill_name} tutorial")

        for i, strat_query in enumerate(strategies):
            print(f"--- strategy {i}: {strat_query!r} ---")
            try:
                results = YoutubeSearch(strat_query, max_results=15).to_dict()
            except Exception as e:
                print(f"  SEARCH RAISED: {e}")
                continue
            print(f"  raw results: {len(results)}")
            if not results:
                print("  (empty result set from youtube_search — scraper returned nothing for this query)")
            for v in results:
                reason = explain_rejection(v, query, "", module_title, module_description, skill_name)
                score = services.rank_video(v, query, "", module_title, module_description, skill_name)
                print(f"    [{v.get('id')}] score={score:+.2f}  {reason}  -- {v.get('title', '')[:70]!r}")
            print()

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_video_search.py <module_id>")
        sys.exit(1)
    debug(int(sys.argv[1]))

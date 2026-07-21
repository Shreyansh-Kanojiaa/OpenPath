import datetime

from sqlalchemy.orm import sessionmaker

import models


def test_badges_endpoint_returns_full_catalog_all_locked_for_new_user(client, registered_user):
    resp = client.get("/users/me/badges", headers=registered_user["headers"])
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["badges"]) == 13
    assert all(b["earned"] is False and b["earned_at"] is None for b in body["badges"])


def test_first_course_created_badge_awarded_on_generate_course(client, registered_user, create_course_with_module):
    create_course_with_module(registered_user["headers"])

    resp = client.get("/users/me/badges", headers=registered_user["headers"])
    badges = {b["key"]: b for b in resp.json()["badges"]}
    assert badges["first_course_created"]["earned"] is True
    assert badges["first_course_created"]["earned_at"] is not None


def test_first_course_completed_badge_awarded_on_last_module_complete(client, registered_user, create_course_with_module):
    course, module = create_course_with_module(registered_user["headers"])

    resp = client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": module["video_duration"] or 600},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    new_badge_keys = {b["key"] for b in resp.json()["new_badges"]}
    assert "first_course_completed" in new_badge_keys
    assert "perfectionist_module" in new_badge_keys

    # Calling complete again must not re-award or duplicate the UserBadge row.
    resp2 = client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": module["video_duration"] or 600},
        headers=registered_user["headers"],
    )
    assert resp2.json()["new_badges"] == []

    badges_resp = client.get("/users/me/badges", headers=registered_user["headers"])
    assert badges_resp.json()["badges"]  # sanity: still a valid response


def test_quiz_badges_first_pass_and_perfect_score(client, registered_user, create_course_with_module):
    course, module = create_course_with_module(registered_user["headers"])

    resp = client.post(
        f"/submit-quiz?module_id={module['id']}&score=5",
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    new_badge_keys = {b["key"] for b in resp.json()["new_badges"]}
    assert "first_quiz_passed" in new_badge_keys
    assert "perfect_quiz" in new_badge_keys


def test_streak_badge_via_backdated_completions(client, registered_user, create_course_with_module, db_engine):
    course, module = create_course_with_module(registered_user["headers"])

    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestSession()
    today = datetime.datetime.utcnow()
    for days_ago in (2, 1):
        db.add(models.QuizAttempt(
            module_id=module["id"],
            user_id=registered_user["user_id"],
            score=5,
            passed=True,
            attempted_at=today - datetime.timedelta(days=days_ago),
        ))
    db.commit()
    db.close()

    resp = client.post(
        f"/submit-quiz?module_id={module['id']}&score=5",
        headers=registered_user["headers"],
    )
    new_badge_keys = {b["key"] for b in resp.json()["new_badges"]}
    assert "streak_3" in new_badge_keys


def test_badges_response_reflects_earned_after_award(client, registered_user, create_course_with_module):
    course, module = create_course_with_module(registered_user["headers"])
    client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": module["video_duration"] or 600},
        headers=registered_user["headers"],
    )

    resp = client.get("/users/me/badges", headers=registered_user["headers"])
    badges = {b["key"]: b for b in resp.json()["badges"]}
    assert badges["first_course_completed"]["earned"] is True
    assert badges["first_course_completed"]["earned_at"] is not None
    assert badges["ten_courses_created"]["earned"] is False

import schemas
import services


def test_generate_quiz_mocked(client, registered_user, create_course_with_module, monkeypatch):
    _, module = create_course_with_module(registered_user["headers"])
    monkeypatch.setattr(
        services,
        "generate_quiz_from_transcript",
        lambda *a, **kw: schemas.Quiz(
            module_id=module["id"],
            questions=[
                schemas.QuizQuestion(
                    question="Q1?",
                    options=["a", "b", "c", "d"],
                    correct_answer_index=0,
                    explanation="because",
                )
            ],
        ),
    )
    resp = client.post(
        "/generate-quiz", params={"module_id": module["id"]}, headers=registered_user["headers"]
    )
    assert resp.status_code == 200
    assert len(resp.json()["questions"]) == 1


def test_submit_quiz_failed_below_threshold(client, registered_user, create_course_with_module):
    _, module = create_course_with_module(registered_user["headers"])
    resp = client.post(
        "/submit-quiz",
        params={"module_id": module["id"], "score": 2},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["passed"] is False


def test_submit_quiz_passed_marks_completed_and_skipped(client, registered_user, create_course_with_module):
    course, module = create_course_with_module(registered_user["headers"])
    resp = client.post(
        "/submit-quiz",
        params={"module_id": module["id"], "score": 4},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["passed"] is True

    updated = client.get(f"/courses/{course['id']}", headers=registered_user["headers"]).json()
    updated_module = next(m for m in updated["modules"] if m["id"] == module["id"])
    assert updated_module["is_completed"] is True
    assert updated_module["is_skipped"] is True

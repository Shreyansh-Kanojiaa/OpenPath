def test_complete_module_rejects_insufficient_watch_time(client, registered_user, create_course_with_module):
    _, module = create_course_with_module(registered_user["headers"], video_duration=600)
    resp = client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": 100},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 400


def test_complete_module_accepts_sufficient_watch_time(client, registered_user, create_course_with_module):
    _, module = create_course_with_module(registered_user["headers"], video_duration=600)
    resp = client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": 480},  # 80% of 600
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_notes_roundtrip(client, registered_user, create_course_with_module):
    course, module = create_course_with_module(registered_user["headers"])
    resp = client.patch(
        f"/modules/{module['id']}/notes",
        json={"notes": "these are my notes"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "saved"

    updated = client.get(f"/courses/{course['id']}", headers=registered_user["headers"]).json()
    saved_module = next(m for m in updated["modules"] if m["id"] == module["id"])
    assert saved_module["notes"] == "these are my notes"


def test_has_transcript_false_without_video(client, registered_user, create_course_with_module):
    _, module = create_course_with_module(registered_user["headers"], video_id=None)
    resp = client.get(f"/modules/{module['id']}/has-transcript")
    assert resp.status_code == 200
    assert resp.json()["has_transcript"] is False

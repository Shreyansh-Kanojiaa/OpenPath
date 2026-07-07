def test_progress_empty_for_new_user(client, registered_user):
    resp = client.get("/users/me/progress", headers=registered_user["headers"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["courses_count"] == 0
    assert body["total_modules"] == 0
    assert body["modules_completed"] == 0
    assert body["completion_rate"] == 0.0
    assert body["last_completed_at"] is None


def test_progress_reflects_completed_module(client, registered_user, create_course_with_module):
    _, module = create_course_with_module(registered_user["headers"], video_duration=600)

    resp = client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": 600},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200

    resp = client.get("/users/me/progress", headers=registered_user["headers"])
    body = resp.json()
    assert body["courses_count"] == 1
    assert body["total_modules"] == 1
    assert body["modules_completed"] == 1
    assert body["completion_rate"] == 1.0
    assert body["last_completed_at"] is not None


def test_progress_completed_at_not_overwritten_on_recomplete(client, registered_user, create_course_with_module):
    _, module = create_course_with_module(registered_user["headers"], video_duration=600)
    client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": 600},
        headers=registered_user["headers"],
    )
    first = client.get("/users/me/progress", headers=registered_user["headers"]).json()

    client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": 600},
        headers=registered_user["headers"],
    )
    second = client.get("/users/me/progress", headers=registered_user["headers"]).json()

    assert first["last_completed_at"] == second["last_completed_at"]

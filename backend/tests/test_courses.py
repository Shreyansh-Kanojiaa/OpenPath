import schemas
import services


def _register_and_login(client, monkeypatch, username, email):
    """Create a distinct user via the Google flow (verification mocked) and return auth headers."""
    import auth as auth_lib

    monkeypatch.setattr(
        auth_lib,
        "verify_google_credential",
        lambda credential: {"sub": f"google-{username}", "email": email, "name": username},
    )
    resp = client.post("/auth/google", json={"credential": "x"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_generate_course_creates_two_modules(client, registered_user, monkeypatch):
    monkeypatch.setattr(
        services,
        "validate_skill",
        lambda skill: schemas.SkillValidation(is_valid_skill=True, reason="ok"),
    )
    monkeypatch.setattr(
        services,
        "generate_syllabus",
        lambda *a, **kw: schemas.CourseCreate(
            skill_name="python",
            start_level=3,
            time_commitment="3-4 hrs/week",
            modules=[
                schemas.ModuleBase(title="M1", description="d1", order_index=1, search_query="q1"),
                schemas.ModuleBase(title="M2", description="d2", order_index=2, search_query="q2"),
            ],
        ),
    )
    monkeypatch.setattr(services, "find_best_video", lambda *a, **kw: {"id": "abc123", "duration": 600})

    resp = client.post(
        "/generate-course",
        params={"skill": "python", "level": 3, "time": "3-4 hrs/week"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    course = resp.json()
    assert course["skill_name"] == "python"

    detail = client.get(f"/courses/{course['id']}", headers=registered_user["headers"])
    assert len(detail.json()["modules"]) == 2


def test_generate_course_rejects_invalid_skill(client, registered_user, monkeypatch):
    monkeypatch.setattr(
        services,
        "validate_skill",
        lambda skill: schemas.SkillValidation(is_valid_skill=False, reason="gibberish"),
    )

    resp = client.post(
        "/generate-course",
        params={"skill": "asdkjfh", "level": 3, "time": "3-4 hrs/week"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 400
    assert "valid skill" in resp.json()["detail"].lower()


def test_my_courses_only_returns_own(client, registered_user, create_course_with_module, monkeypatch):
    create_course_with_module(registered_user["headers"])
    other_headers = _register_and_login(client, monkeypatch, "other", "other@test.com")

    resp = client.get("/courses", headers=other_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_public_courses_only_shows_public(client, registered_user, create_course_with_module):
    course, _ = create_course_with_module(registered_user["headers"])

    resp = client.get("/courses/public")
    assert resp.json()["items"] == []
    assert resp.json()["total"] == 0

    client.patch(
        f"/courses/{course['id']}/visibility",
        params={"make_public": True},
        headers=registered_user["headers"],
    )
    resp = client.get("/courses/public")
    assert len(resp.json()["items"]) == 1
    assert resp.json()["total"] == 1


def test_public_courses_search_and_pagination(client, registered_user, create_course_with_module):
    course, _ = create_course_with_module(registered_user["headers"])
    client.patch(
        f"/courses/{course['id']}/visibility",
        params={"make_public": True},
        headers=registered_user["headers"],
    )

    resp = client.get("/courses/public", params={"skill": "python"})
    assert resp.json()["total"] == 1

    resp = client.get("/courses/public", params={"skill": "rust"})
    assert resp.json()["total"] == 0
    assert resp.json()["items"] == []

    resp = client.get("/courses/public", params={"limit": 1, "offset": 5})
    assert resp.json()["items"] == []
    assert resp.json()["total"] == 1
    assert resp.json()["limit"] == 1
    assert resp.json()["offset"] == 5


def test_private_course_denied_to_others(client, registered_user, create_course_with_module, monkeypatch):
    course, _ = create_course_with_module(registered_user["headers"])
    other_headers = _register_and_login(client, monkeypatch, "other", "other@test.com")

    resp = client.get(f"/courses/{course['id']}", headers=other_headers)
    assert resp.status_code == 403


def test_visibility_toggle_requires_ownership(client, registered_user, create_course_with_module, monkeypatch):
    course, _ = create_course_with_module(registered_user["headers"])
    other_headers = _register_and_login(client, monkeypatch, "other", "other@test.com")

    resp = client.patch(
        f"/courses/{course['id']}/visibility",
        params={"make_public": True},
        headers=other_headers,
    )
    assert resp.status_code == 403


def test_enroll_copies_modules_and_rejects_own_course(client, registered_user, create_course_with_module, monkeypatch):
    course, _ = create_course_with_module(registered_user["headers"])
    client.patch(
        f"/courses/{course['id']}/visibility",
        params={"make_public": True},
        headers=registered_user["headers"],
    )

    resp = client.post(f"/courses/{course['id']}/enroll", headers=registered_user["headers"])
    assert resp.status_code == 400  # already owns it

    other_headers = _register_and_login(client, monkeypatch, "other", "other@test.com")
    resp = client.post(f"/courses/{course['id']}/enroll", headers=other_headers)
    assert resp.status_code == 200
    enrolled = resp.json()

    detail = client.get(f"/courses/{enrolled['id']}", headers=other_headers)
    assert len(detail.json()["modules"]) == 1


def test_enroll_rejects_non_public_course(client, registered_user, create_course_with_module, monkeypatch):
    course, _ = create_course_with_module(registered_user["headers"])
    other_headers = _register_and_login(client, monkeypatch, "other", "other@test.com")

    resp = client.post(f"/courses/{course['id']}/enroll", headers=other_headers)
    assert resp.status_code == 403

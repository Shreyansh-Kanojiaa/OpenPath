import schemas
import services


def _stub_response():
    return schemas.JobReadyResponse(
        readiness_percentage=50,
        missing_skills=[],
        suggested_modules=[],
        roadmap=[],
        estimated_time="1 month",
    )


def test_job_ready_merges_saved_skills_with_completed(client, registered_user, create_course_with_module, monkeypatch):
    _, module = create_course_with_module(registered_user["headers"], video_duration=600)
    client.post(
        f"/modules/{module['id']}/complete",
        json={"watch_time": 600},
        headers=registered_user["headers"],
    )
    client.put(
        "/account/skills",
        json={"skills": ["Docker", "python"]},
        headers=registered_user["headers"],
    )

    captured = {}

    def fake_calculate_job_readiness(job_title, company, user_completed_skills):
        captured["skills"] = user_completed_skills
        return _stub_response()

    monkeypatch.setattr(services, "calculate_job_readiness", fake_calculate_job_readiness)

    resp = client.post(
        "/career/job-ready",
        json={"job_title": "Backend Engineer", "company": "Acme"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    assert len(captured["skills"]) == 2
    assert {s.lower() for s in captured["skills"]} == {"python", "docker"}


def test_job_ready_works_without_any_saved_skills(client, registered_user, monkeypatch):
    monkeypatch.setattr(services, "calculate_job_readiness", lambda *a, **kw: _stub_response())

    resp = client.post(
        "/career/job-ready",
        json={"job_title": "Backend Engineer", "company": "Acme"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200


def test_job_ready_dedupes_saved_skills_case_insensitively(client, registered_user, monkeypatch):
    client.put(
        "/account/skills",
        json={"skills": ["React", "react", " React "]},
        headers=registered_user["headers"],
    )

    captured = {}

    def fake_calculate_job_readiness(job_title, company, user_completed_skills):
        captured["skills"] = user_completed_skills
        return _stub_response()

    monkeypatch.setattr(services, "calculate_job_readiness", fake_calculate_job_readiness)

    resp = client.post(
        "/career/job-ready",
        json={"job_title": "Frontend Engineer", "company": "Acme"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    assert captured["skills"] == ["React"]

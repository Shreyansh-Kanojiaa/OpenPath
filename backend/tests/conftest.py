import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-not-for-prod")
os.environ.setdefault("GEMINI_API_KEY", "test-dummy-key")
os.environ.setdefault("RATE_LIMIT_LOGIN", "1000/minute")
os.environ.setdefault("RATE_LIMIT_REGISTER", "1000/minute")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import models, database, schemas, services
from main import app

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_engine():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    models.Base.metadata.create_all(bind=engine)
    yield engine
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_engine):
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def create_course_with_module(client, monkeypatch):
    """Returns a factory(headers, video_duration=600, video_id="abc123") -> (course, module)."""

    def _make(headers, video_duration: int = 600, video_id: str | None = "abc123"):
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
                modules=[schemas.ModuleBase(title="M1", description="d1", order_index=1, search_query="q1")],
            ),
        )
        monkeypatch.setattr(
            services,
            "find_best_video",
            lambda *a, **kw: ({"id": video_id, "duration": video_duration} if video_id else None),
        )
        course = client.post(
            "/generate-course",
            params={"skill": "python", "level": 3, "time": "3-4 hrs/week"},
            headers=headers,
        ).json()
        module = client.get(f"/courses/{course['id']}", headers=headers).json()["modules"][0]
        return course, module

    return _make


@pytest.fixture()
def registered_user(client, monkeypatch):
    """Signs in via /auth/google with the Google credential verification mocked."""
    import auth as auth_lib

    monkeypatch.setattr(
        auth_lib,
        "verify_google_credential",
        lambda credential: {"sub": "google-alice", "email": "alice@test.com", "name": "Alice"},
    )
    resp = client.post("/auth/google", json={"credential": "dummy-token"})
    body = resp.json()
    token = body["access_token"]
    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": body["user_id"],
    }

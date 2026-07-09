import auth as auth_lib
import models


def _mock_google(monkeypatch, sub="google-bob", email="bob@test.com", name="Bob"):
    monkeypatch.setattr(
        auth_lib,
        "verify_google_credential",
        lambda credential: {"sub": sub, "email": email, "name": name},
    )


def test_google_auth_new_user_creates_and_returns_jwt(client, monkeypatch):
    _mock_google(monkeypatch)
    resp = client.post("/auth/google", json={"credential": "x"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["username"]  # a username was derived


def test_google_auth_existing_google_sub_reuses_account(client, monkeypatch):
    _mock_google(monkeypatch)
    first = client.post("/auth/google", json={"credential": "x"}).json()
    second = client.post("/auth/google", json={"credential": "x"}).json()
    assert first["user_id"] == second["user_id"]


def test_google_auth_links_existing_email(client, db_engine, monkeypatch):
    # Pre-seed a legacy account (no google_sub) with the same email.
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=db_engine)
    db = Session()
    legacy = models.User(username="legacy", email="bob@test.com")
    db.add(legacy)
    db.commit()
    legacy_id = legacy.id
    db.close()

    _mock_google(monkeypatch, email="bob@test.com")
    resp = client.post("/auth/google", json={"credential": "x"})
    assert resp.status_code == 200
    assert resp.json()["user_id"] == legacy_id

    db = Session()
    linked = db.query(models.User).filter(models.User.id == legacy_id).first()
    assert linked.google_sub == "google-bob"
    db.close()


def test_google_auth_invalid_credential_rejected(client, monkeypatch):
    def _raise(credential):
        raise ValueError("bad token")

    monkeypatch.setattr(auth_lib, "verify_google_credential", _raise)
    resp = client.post("/auth/google", json={"credential": "x"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_token(registered_user, client):
    resp = client.get("/auth/me", headers=registered_user["headers"])
    assert resp.status_code == 200
    assert resp.json()["username"]

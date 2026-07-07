def test_register_success(client):
    resp = client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@test.com", "password": "password123"},
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "bob"


def test_register_duplicate_email_rejected(client):
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@test.com", "password": "password123"},
    )
    resp = client.post(
        "/auth/register",
        json={"username": "bob2", "email": "bob@test.com", "password": "password123"},
    )
    assert resp.status_code == 400


def test_register_duplicate_username_rejected(client):
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@test.com", "password": "password123"},
    )
    resp = client.post(
        "/auth/register",
        json={"username": "bob", "email": "other@test.com", "password": "password123"},
    )
    assert resp.status_code == 400


def test_login_success_returns_jwt(registered_user):
    assert registered_user["token"]


def test_login_wrong_password_rejected(client):
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@test.com", "password": "password123"},
    )
    resp = client.post("/auth/login", json={"email": "bob@test.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_token(registered_user, client):
    resp = client.get("/auth/me", headers=registered_user["headers"])
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"

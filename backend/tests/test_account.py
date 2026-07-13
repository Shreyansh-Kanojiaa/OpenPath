def test_get_account_settings_defaults(client, registered_user):
    resp = client.get("/account/settings", headers=registered_user["headers"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["known_skills"] == []
    assert body["can_change_username"] is True
    assert body["next_username_change_allowed_at"] is None


def test_username_change_success(client, registered_user):
    resp = client.patch(
        "/account/username",
        json={"username": "new_handle"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "new_handle"
    assert body["next_username_change_allowed_at"] is not None

    settings = client.get("/account/settings", headers=registered_user["headers"]).json()
    assert settings["username"] == "new_handle"
    assert settings["can_change_username"] is False


def test_username_change_rejects_invalid_characters(client, registered_user):
    resp = client.patch(
        "/account/username",
        json={"username": "bad name!"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 400


def test_username_change_rejects_taken_username(client, registered_user, monkeypatch):
    import auth as auth_lib

    monkeypatch.setattr(
        auth_lib,
        "verify_google_credential",
        lambda credential: {"sub": "google-bob", "email": "bob@test.com", "name": "Bob"},
    )
    second = client.post("/auth/google", json={"credential": "dummy-token"}).json()
    second_headers = {"Authorization": f"Bearer {second['access_token']}"}
    second_username = second["username"]

    resp = client.patch(
        "/account/username",
        json={"username": second_username},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 409


def test_username_change_blocked_by_cooldown(client, registered_user):
    resp = client.patch(
        "/account/username",
        json={"username": "first_rename"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200

    resp = client.patch(
        "/account/username",
        json={"username": "second_rename"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 403
    assert "next_username_change_allowed_at" in resp.json()["detail"]


def test_username_unchanged_noop_does_not_reset_cooldown(client, registered_user):
    client.patch(
        "/account/username",
        json={"username": "stable_name"},
        headers=registered_user["headers"],
    )
    before = client.get("/account/settings", headers=registered_user["headers"]).json()

    resp = client.patch(
        "/account/username",
        json={"username": "stable_name"},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200

    after = client.get("/account/settings", headers=registered_user["headers"]).json()
    assert before["next_username_change_allowed_at"] == after["next_username_change_allowed_at"]


def test_put_skills_persists_and_dedupes(client, registered_user):
    resp = client.put(
        "/account/skills",
        json={"skills": ["Docker", "docker", " Python "]},
        headers=registered_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["known_skills"] == ["Docker", "Python"]

    settings = client.get("/account/settings", headers=registered_user["headers"]).json()
    assert settings["known_skills"] == ["Docker", "Python"]


def test_put_skills_replaces_not_merges(client, registered_user):
    client.put("/account/skills", json={"skills": ["Docker"]}, headers=registered_user["headers"])
    resp = client.put("/account/skills", json={"skills": ["Python"]}, headers=registered_user["headers"])
    assert resp.json()["known_skills"] == ["Python"]

from tests.conftest import register_and_login, auth_headers


def test_register_success(client):
    resp = client.post("/auth/register", json={
        "full_name": "Mohammed",
        "email": "mo@example.com",
        "password": "secure123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "mo@example.com"
    assert "password" not in data   # never expose the hash


def test_register_duplicate_email(client):
    payload = {"full_name": "A", "email": "dup@example.com", "password": "password1"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_weak_password(client):
    resp = client.post("/auth/register", json={
        "full_name": "A",
        "email": "a@example.com",
        "password": "short",
    })
    assert resp.status_code == 422


def test_register_invalid_email(client):
    resp = client.post("/auth/register", json={
        "full_name": "A",
        "email": "not-an-email",
        "password": "password123",
    })
    assert resp.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={
        "full_name": "User",
        "email": "user@example.com",
        "password": "mypassword",
    })
    resp = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "mypassword",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "full_name": "User",
        "email": "user@example.com",
        "password": "correctpassword",
    })
    resp = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/auth/login", json={
        "email": "ghost@example.com",
        "password": "anything",
    })
    assert resp.status_code == 401

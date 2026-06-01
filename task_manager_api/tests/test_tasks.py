from tests.conftest import register_and_login, auth_headers


def test_create_task(client):
    token = register_and_login(client)
    resp = client.post("/tasks", json={
        "title": "Buy groceries",
        "priority": "high",
    }, headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.json()["title"] == "Buy groceries"


def test_create_task_unauthenticated(client):
    resp = client.post("/tasks", json={"title": "No auth"})
    assert resp.status_code in (401, 403)


def test_get_tasks(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    client.post("/tasks", json={"title": "Task 1"}, headers=hdrs)
    client.post("/tasks", json={"title": "Task 2"}, headers=hdrs)
    resp = client.get("/tasks", headers=hdrs)
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_get_task_by_id(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    created = client.post("/tasks", json={"title": "Find me"}, headers=hdrs).json()
    resp = client.get(f"/tasks/{created['id']}", headers=hdrs)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Find me"


def test_get_task_not_found(client):
    token = register_and_login(client)
    resp = client.get("/tasks/9999", headers=auth_headers(token))
    assert resp.status_code == 404


def test_update_task(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    task = client.post("/tasks", json={"title": "Old title"}, headers=hdrs).json()
    resp = client.put(f"/tasks/{task['id']}", json={"title": "New title", "status": "done"}, headers=hdrs)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"
    assert resp.json()["status"] == "done"


def test_delete_task(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    task = client.post("/tasks", json={"title": "Delete me"}, headers=hdrs).json()
    resp = client.delete(f"/tasks/{task['id']}", headers=hdrs)
    assert resp.status_code == 200
    assert client.get(f"/tasks/{task['id']}", headers=hdrs).status_code == 404


def test_filter_by_status(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    client.post("/tasks", json={"title": "A", "status": "todo"}, headers=hdrs)
    client.post("/tasks", json={"title": "B", "status": "done"}, headers=hdrs)
    resp = client.get("/tasks?status=done", headers=hdrs)
    assert resp.json()["total"] == 1
    assert resp.json()["results"][0]["title"] == "B"


def test_filter_by_priority(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    client.post("/tasks", json={"title": "Lo", "priority": "low"}, headers=hdrs)
    client.post("/tasks", json={"title": "Hi", "priority": "high"}, headers=hdrs)
    resp = client.get("/tasks?priority=high", headers=hdrs)
    assert resp.json()["total"] == 1


def test_search_tasks(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    client.post("/tasks", json={"title": "Buy milk", "description": "from store"}, headers=hdrs)
    client.post("/tasks", json={"title": "Go running"}, headers=hdrs)
    resp = client.get("/tasks?search=milk", headers=hdrs)
    assert resp.json()["total"] == 1


def test_pagination(client):
    token = register_and_login(client)
    hdrs = auth_headers(token)
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"}, headers=hdrs)
    resp = client.get("/tasks?page=1&page_size=2", headers=hdrs)
    data = resp.json()
    assert data["total"] == 5
    assert len(data["results"]) == 2


def test_user_cannot_access_other_users_task(client):
    token_a = register_and_login(client, email="a@x.com")
    token_b = register_and_login(client, email="b@x.com")
    task = client.post("/tasks", json={"title": "Private"}, headers=auth_headers(token_a)).json()
    resp = client.get(f"/tasks/{task['id']}", headers=auth_headers(token_b))
    assert resp.status_code == 404

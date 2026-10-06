def test_create_task(client, auth_headers, db):
    proj = client.post("/projects", headers=auth_headers, json={"name": "Work", "color": "#0000FF"})
    assert proj.status_code == 200
    project_id = proj.json()["id"]
    
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "API bauen",
            "description": "FastAPI lernen",
            "status": "in_progress",
            "priority": "high",
            "project_id": project_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API bauen"
    assert data["status"] == "in_progress"


def test_filter_tasks_by_status(client, auth_headers, db):
    # Setup: Projekt + Tasks erstellen
    proj = client.post("/projects", headers=auth_headers, json={"name": "Test", "color": "#FFFFFF"})
    assert proj.status_code == 200
    pid = proj.json()["id"]
    
    r1 = client.post("/tasks", headers=auth_headers, json={
        "title": "Todo 1", "status": "todo", "project_id": pid
    })
    assert r1.status_code == 200
    
    r2 = client.post("/tasks", headers=auth_headers, json={
        "title": "Done 1", "status": "done", "project_id": pid
    })
    assert r2.status_code == 200
    
    # Filter: nur done
    response = client.get("/tasks?status=done", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Done 1"


def test_delete_task(client, auth_headers, db):
    proj = client.post("/projects", headers=auth_headers, json={"name": "Del", "color": "#FF0000"})
    assert proj.status_code == 200
    pid = proj.json()["id"]
    
    task = client.post("/tasks", headers=auth_headers, json={
        "title": "Lösch mich", "project_id": pid
    })
    assert task.status_code == 200
    task_id = task.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Sicherstellen, dass er wirklich weg ist
    get_resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 404
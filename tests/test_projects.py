def test_create_project(client, auth_headers):
    response = client.post(
        "/projects",
        headers=auth_headers,
        json={
            "name": "Fitness",
            "description": "Sportprojekt",
            "color": "#FF5733"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fitness"
    assert data["owner_id"] == 1


def test_create_project_without_auth(client):
    response = client.post(
        "/projects",
        json={"name": "Hacking", "color": "#000000"}
    )
    assert response.status_code == 401


def test_list_projects_only_own(client, auth_headers, db):
    # Erstelle ein Projekt für testuser
    client.post("/projects", headers=auth_headers, json={"name": "Meins", "color": "#FF0000"})
    
    # Erstelle einen zweiten User mit eigenem Projekt
    from app import crud, schemas
    user2 = crud.create_user(db=db, user=schemas.UserCreate(
        username="other", email="other@test.de", password="geheim123"
    ))
    crud.create_project(db=db, project=schemas.ProjectCreate(
        name="Fremd", color="#00FF00"
    ), owner_id=user2.id)
    
    # Liste sollte nur "Meins" enthalten
    response = client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Meins"
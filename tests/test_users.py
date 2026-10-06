def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "username": "max",
            "email": "max@test.de",
            "password": "geheim123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "max"
    assert data["email"] == "max@test.de"
    assert "password" not in data  # Passwort nie im Response!
    assert "id" in data


def test_create_user_duplicate_username(client, test_user):
    response = client.post(
        "/users",
        json={
            "username": "testuser",  # Bereits existiert via Fixture
            "email": "neu@test.de",
            "password": "geheim123"
        }
    )
    assert response.status_code == 400
    assert "bereits" in response.json()["detail"]


def test_get_user_me(client, auth_headers, test_user):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_get_user_me_without_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401
def test_login_success(client, test_user):
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "geheim123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "falsch"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={"username": "nichtda", "password": "geheim123"}
    )
    assert response.status_code == 401
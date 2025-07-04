from fastapi import status

def test_login_success(client, test_user):
    response = client.post(
        "/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    wrong_credentials = {
        "username": test_user["email"],
        "password": "wrongpassword",
        "grant_type": "password"
    }
    response = client.post(
        "/token",
        data=wrong_credentials,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_without_token(client):
    response = client.get("/protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_with_token(client, auth_headers):
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "is_active" in data
    assert data["username"] == "demo@example.com"
    assert data["is_active"] == True 
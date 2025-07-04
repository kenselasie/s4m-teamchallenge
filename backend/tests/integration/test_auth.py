import pytest
from fastapi import status

@pytest.mark.parametrize(
    "password,expected_status,check_token",
    [
        ("password", status.HTTP_200_OK, True),   # Correct password from test_user fixture
        ("wrongpassword", status.HTTP_401_UNAUTHORIZED, False), # Wrong password
    ],
)
def test_login_scenarios(client, test_user, password, expected_status, check_token):
    # Use the actual password from test_user if password param is "password"
    actual_password = test_user["password"] if password == "password" else password
    
    response = client.post(
        "/token",
        data={
            "username": test_user["email"],
            "password": actual_password,
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == expected_status
    
    if check_token:
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.parametrize(
    "headers,expected_status,check_user_data",
    [
        (None, status.HTTP_401_UNAUTHORIZED, False),
        ("auth_headers", status.HTTP_200_OK, True),
    ],
)
def test_protected_route_scenarios(client, auth_headers, headers, expected_status, check_user_data):
    headers_to_use = auth_headers if headers == "auth_headers" else None
    response = client.get("/protected", headers=headers_to_use)
    assert response.status_code == expected_status
    
    if check_user_data:
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "is_active" in data
        assert data["username"] == "demo@example.com"
        assert data["is_active"] == True 
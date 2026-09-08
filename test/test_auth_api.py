from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.jwt import JWTService
from app.auth.service import UserService
from app.main import app
from app.api.routes.auth import configure_auth_services


user_service = UserService()
jwt_service = JWTService(
    secret_key="test-auth-api-secret-123456",
)

configure_auth_services(
    user_service,
    jwt_service,
)

client = TestClient(app)


def setup_function() -> None:
    global user_service
    global jwt_service

    user_service = UserService()
    jwt_service = JWTService(
        secret_key="test-auth-api-secret-123456",
    )

    configure_auth_services(
        user_service,
        jwt_service,
    )


def test_login_success():
    user = user_service.create_user(
        username="admin",
        password="Secret123",
        role="admin",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Secret123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["expires_in"] == 3600
    assert data["user_id"] == user.user_id
    assert data["username"] == "admin"
    assert data["role"] == "admin"
    assert "password" not in data


def test_login_token_contains_expected_claims():
    user_service.create_user(
        username="admin",
        password="Secret123",
        role="admin",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Secret123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    payload = jwt_service.decode_token(token)

    assert payload["sub"]
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"
    assert payload["exp"] > payload["iat"]


def test_login_wrong_password_returns_401():
    user_service.create_user(
        username="admin",
        password="Secret123",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Username hoặc password không đúng."
    )


def test_login_unknown_user_returns_401():
    response = client.post(
        "/auth/login",
        json={
            "username": "unknown",
            "password": "Secret123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Username hoặc password không đúng."
    )


def test_login_inactive_user_returns_401():
    user = user_service.create_user(
        username="admin",
        password="Secret123",
    )

    user_service.deactivate(user.user_id)

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Secret123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Username hoặc password không đúng."
    )


def test_login_username_is_case_insensitive():
    user_service.create_user(
        username="AdminUser",
        password="Secret123",
        role="admin",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "ADMINUSER",
            "password": "Secret123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "adminuser"


def test_login_invalid_request_returns_422():
    response = client.post(
        "/auth/login",
        json={
            "username": "ab",
            "password": "",
        },
    )

    assert response.status_code == 422


def test_login_missing_fields_returns_422():
    response = client.post(
        "/auth/login",
        json={},
    )

    assert response.status_code == 422


def test_login_does_not_expose_password_hash():
    user_service.create_user(
        username="admin",
        password="Secret123",
        role="admin",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Secret123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "password" not in data
    assert "password_hash" not in data
    assert "secret" not in data


def test_openapi_contains_login_endpoint():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/auth/login" in paths
    assert "post" in paths["/auth/login"]


def test_login_response_contract():
    user_service.create_user(
        username="admin",
        password="Secret123",
        role="admin",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Secret123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "success",
        "access_token",
        "token_type",
        "expires_in",
        "user_id",
        "username",
        "role",
        "message",
    }

    assert expected_fields.issubset(data.keys())
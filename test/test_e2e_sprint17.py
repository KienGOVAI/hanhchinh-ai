from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.routes.auth import (
    configure_auth_services,
    get_jwt_service,
    get_user_service,
)
from app.api.routes.protected import get_rbac_service
from app.auth.jwt import JWTService
from app.auth.rbac_service import RBACService
from app.auth.service import UserService
from app.main import app


JWT_SECRET = "sprint17-e2e-secret-123456"


@pytest.fixture()
def e2e():
    user_service = UserService()

    jwt_service = JWTService(
        secret_key=JWT_SECRET,
    )

    configure_auth_services(
        user_service,
        jwt_service,
    )

    rbac_service: RBACService = get_rbac_service()
    rbac_service.clear()

    rbac_service.create_permission(
        "document.read",
        "Đọc văn bản",
    )

    rbac_service.create_permission(
        "document.write",
        "Ghi văn bản",
    )

    rbac_service.create_role("admin")
    rbac_service.create_role("viewer")

    rbac_service.grant_permission(
        "admin",
        "document.read",
    )

    rbac_service.grant_permission(
        "admin",
        "document.write",
    )

    rbac_service.grant_permission(
        "viewer",
        "document.read",
    )

    admin = user_service.create_user(
        username="sprint17_admin",
        password="Admin123!",
        role="admin",
    )

    viewer = user_service.create_user(
        username="sprint17_viewer",
        password="Viewer123!",
        role="viewer",
    )

    rbac_service.assign_role(
        admin.user_id,
        "admin",
    )

    rbac_service.assign_role(
        viewer.user_id,
        "viewer",
    )

    client = TestClient(app)

    return {
        "client": client,
        "user_service": user_service,
        "jwt_service": jwt_service,
        "rbac_service": rbac_service,
        "admin": admin,
        "viewer": viewer,
    }


def test_sprint17_admin_full_authentication_flow(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "sprint17_admin",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 200

    body = login.json()

    assert body["success"] is True
    assert body["token_type"] == "bearer"
    assert body["user_id"] == e2e["admin"].user_id
    assert body["username"] == "sprint17_admin"
    assert body["role"] == "admin"

    token = body["access_token"]

    me = client.get(
        "/protected/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert me.status_code == 200
    assert me.json()["user_id"] == e2e["admin"].user_id

    read = client.get(
        "/protected/document/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert read.status_code == 200

    write = client.get(
        "/protected/document/write",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert write.status_code == 200


def test_sprint17_viewer_full_authentication_flow(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "sprint17_viewer",
            "password": "Viewer123!",
        },
    )

    assert login.status_code == 200

    body = login.json()

    assert body["success"] is True
    assert body["role"] == "viewer"

    token = body["access_token"]

    me = client.get(
        "/protected/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert me.status_code == 200

    read = client.get(
        "/protected/document/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert read.status_code == 200

    write = client.get(
        "/protected/document/write",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert write.status_code == 403


def test_sprint17_wrong_password_cannot_enter_system(e2e):
    response = e2e["client"].post(
        "/auth/login",
        json={
            "username": "sprint17_admin",
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == 401


def test_sprint17_unknown_user_cannot_enter_system(e2e):
    response = e2e["client"].post(
        "/auth/login",
        json={
            "username": "unknown_sprint17_user",
            "password": "Admin123!",
        },
    )

    assert response.status_code == 401


def test_sprint17_missing_token_cannot_access_protected_api(e2e):
    response = e2e["client"].get(
        "/protected/me",
    )

    assert response.status_code == 401


def test_sprint17_invalid_token_cannot_access_protected_api(e2e):
    response = e2e["client"].get(
        "/protected/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_sprint17_token_contains_expected_identity(e2e):
    login = e2e["client"].post(
        "/auth/login",
        json={
            "username": "sprint17_admin",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    payload = e2e["jwt_service"].decode_token(token)

    assert payload["sub"] == e2e["admin"].user_id
    assert payload["username"] == "sprint17_admin"
    assert payload["role"] == "admin"


def test_sprint17_token_identity_matches_database_user(e2e):
    login = e2e["client"].post(
        "/auth/login",
        json={
            "username": "sprint17_viewer",
            "password": "Viewer123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    payload = e2e["jwt_service"].decode_token(token)

    user = e2e["user_service"].get_user(
        payload["sub"],
    )

    assert user.user_id == e2e["viewer"].user_id
    assert user.username == "sprint17_viewer"
    assert user.role == "viewer"


def test_sprint17_rbac_matches_login_role(e2e):
    login = e2e["client"].post(
        "/auth/login",
        json={
            "username": "sprint17_viewer",
            "password": "Viewer123!",
        },
    )

    assert login.status_code == 200

    body = login.json()

    token = body["access_token"]

    payload = e2e["jwt_service"].decode_token(token)

    assert payload["role"] == body["role"]

    assert e2e["rbac_service"].has_role(
        e2e["viewer"].user_id,
        "viewer",
    )


def test_sprint17_admin_role_has_full_document_access(e2e):
    admin_id = e2e["admin"].user_id

    assert e2e["rbac_service"].has_role(
        admin_id,
        "admin",
    )

    assert e2e["rbac_service"].has_permission(
        admin_id,
        "document.read",
    )

    assert e2e["rbac_service"].has_permission(
        admin_id,
        "document.write",
    )


def test_sprint17_viewer_role_has_limited_document_access(e2e):
    viewer_id = e2e["viewer"].user_id

    assert e2e["rbac_service"].has_role(
        viewer_id,
        "viewer",
    )

    assert e2e["rbac_service"].has_permission(
        viewer_id,
        "document.read",
    )

    assert not e2e["rbac_service"].has_permission(
        viewer_id,
        "document.write",
    )


def test_sprint17_openapi_exposes_authentication_surface(e2e):
    response = e2e["client"].get(
        "/openapi.json",
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/auth/login" in paths
    assert "/protected/me" in paths
    assert "/protected/document/read" in paths
    assert "/protected/document/write" in paths


def test_sprint17_runtime_auth_services_are_available(e2e):
    assert isinstance(
        get_user_service(),
        UserService,
    )

    assert isinstance(
        get_jwt_service(),
        JWTService,
    )

    assert isinstance(
        get_rbac_service(),
        RBACService,
    )


def test_sprint17_final_authentication_contract(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "sprint17_admin",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 200

    login_body = login.json()

    token = login_body["access_token"]

    assert login_body["success"] is True
    assert login_body["user_id"] == e2e["admin"].user_id
    assert login_body["username"] == "sprint17_admin"
    assert login_body["role"] == "admin"

    protected = client.get(
        "/protected/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert protected.status_code == 200

    protected_body = protected.json()

    assert protected_body["success"] is True
    assert protected_body["user_id"] == login_body["user_id"]
    assert protected_body["username"] == login_body["username"]
    assert protected_body["role"] == login_body["role"]

    permission = client.get(
        "/protected/document/write",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert permission.status_code == 200

    permission_body = permission.json()

    assert permission_body["success"] is True
    assert permission_body["user_id"] == login_body["user_id"]
    assert permission_body["permission"] == "document.write"
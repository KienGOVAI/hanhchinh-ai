from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.auth import (
    configure_auth_services,
    router as auth_router,
)
from app.api.routes.protected import (
    get_rbac_service,
    router as protected_router,
)
from app.auth.jwt import JWTService
from app.auth.rbac_service import RBACService
from app.auth.service import UserService


JWT_SECRET = "e2e-auth-test-secret-123456"


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
        username="e2e_admin",
        password="Admin123!",
        role="admin",
    )

    viewer = user_service.create_user(
        username="e2e_viewer",
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

    app = FastAPI()

    app.include_router(auth_router)
    app.include_router(protected_router)

    client = TestClient(app)

    return {
        "app": app,
        "client": client,
        "user_service": user_service,
        "jwt_service": jwt_service,
        "rbac_service": rbac_service,
        "admin": admin,
        "viewer": viewer,
    }


def test_e2e_admin_login_to_current_user(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "e2e_admin",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 200

    login_body = login.json()

    assert login_body["success"] is True
    assert login_body["token_type"] == "bearer"
    assert login_body["user_id"] == e2e["admin"].user_id
    assert login_body["username"] == "e2e_admin"
    assert login_body["role"] == "admin"

    token = login_body["access_token"]

    me = client.get(
        "/protected/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert me.status_code == 200

    me_body = me.json()

    assert me_body["success"] is True
    assert me_body["user_id"] == e2e["admin"].user_id
    assert me_body["username"] == "e2e_admin"
    assert me_body["role"] == "admin"


def test_e2e_admin_login_to_read_permission(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "e2e_admin",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.get(
        "/protected/document/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["user_id"] == e2e["admin"].user_id
    assert body["permission"] == "document.read"


def test_e2e_admin_login_to_write_permission(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "e2e_admin",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.get(
        "/protected/document/write",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["user_id"] == e2e["admin"].user_id
    assert body["permission"] == "document.write"


def test_e2e_viewer_login_to_read_permission(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "e2e_viewer",
            "password": "Viewer123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.get(
        "/protected/document/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["user_id"] == e2e["viewer"].user_id
    assert body["permission"] == "document.read"


def test_e2e_viewer_login_denied_write_permission(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "e2e_viewer",
            "password": "Viewer123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.get(
        "/protected/document/write",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_e2e_wrong_password_stops_at_login(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "e2e_admin",
            "password": "WrongPassword!",
        },
    )

    assert login.status_code == 401


def test_e2e_unknown_user_stops_at_login(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "not_exists",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 401


def test_e2e_token_is_reusable_across_protected_operations(e2e):
    client = e2e["client"]

    login = client.post(
        "/auth/login",
        json={
            "username": "e2e_admin",
            "password": "Admin123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    me = client.get(
        "/protected/me",
        headers=headers,
    )

    read = client.get(
        "/protected/document/read",
        headers=headers,
    )

    write = client.get(
        "/protected/document/write",
        headers=headers,
    )

    assert me.status_code == 200
    assert read.status_code == 200
    assert write.status_code == 200


def test_e2e_bearer_token_without_login_is_rejected(e2e):
    client = e2e["client"]

    response = client.get(
        "/protected/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_e2e_missing_bearer_token_is_rejected(e2e):
    client = e2e["client"]

    response = client.get(
        "/protected/me",
    )

    assert response.status_code == 401


def test_e2e_openapi_contains_authentication_chain(e2e):
    client = e2e["client"]

    response = client.get(
        "/openapi.json",
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/auth/login" in paths
    assert "/protected/me" in paths
    assert "/protected/document/read" in paths
    assert "/protected/document/write" in paths


def test_e2e_final_rbac_state(e2e):
    rbac_service = e2e["rbac_service"]

    assert rbac_service.has_permission(
        e2e["admin"].user_id,
        "document.read",
    )

    assert rbac_service.has_permission(
        e2e["admin"].user_id,
        "document.write",
    )

    assert rbac_service.has_permission(
        e2e["viewer"].user_id,
        "document.read",
    )

    assert not rbac_service.has_permission(
        e2e["viewer"].user_id,
        "document.write",
    )
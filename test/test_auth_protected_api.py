from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.auth import configure_auth_services
from app.api.routes.protected import (
    get_rbac_service,
    router as protected_router,
)
from app.auth.jwt import JWTService
from app.auth.rbac_service import RBACService
from app.auth.service import UserService


JWT_SECRET = "protected-api-test-secret-123456"


@pytest.fixture()
def client():
    user_service = UserService()

    jwt_service = JWTService(
        secret_key=JWT_SECRET,
    )

    configure_auth_services(
        user_service,
        jwt_service,
    )

    rbac_service = get_rbac_service()
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
        username="protected_admin",
        password="Admin123!",
        role="admin",
    )

    viewer = user_service.create_user(
        username="protected_viewer",
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

    app.include_router(
        protected_router,
    )

    test_client = TestClient(app)

    return {
        "client": test_client,
        "user_service": user_service,
        "jwt_service": jwt_service,
        "rbac_service": rbac_service,
        "admin": admin,
        "viewer": viewer,
    }


def create_token(
    jwt_service: JWTService,
    user_id: str,
    username: str,
    role: str,
) -> str:
    return jwt_service.create_token(
        subject=user_id,
        claims={
            "username": username,
            "role": role,
        },
    )


def test_protected_me_requires_bearer_token(client):
    response = client["client"].get(
        "/protected/me",
    )

    assert response.status_code == 401


def test_protected_me_rejects_invalid_token(client):
    response = client["client"].get(
        "/protected/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_protected_me_returns_current_user(client):
    token = create_token(
        client["jwt_service"],
        client["admin"].user_id,
        client["admin"].username,
        client["admin"].role,
    )

    response = client["client"].get(
        "/protected/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["user_id"] == client["admin"].user_id
    assert body["username"] == "protected_admin"
    assert body["role"] == "admin"


def test_admin_can_read_document(client):
    token = create_token(
        client["jwt_service"],
        client["admin"].user_id,
        client["admin"].username,
        client["admin"].role,
    )

    response = client["client"].get(
        "/protected/document/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["user_id"] == client["admin"].user_id
    assert body["permission"] == "document.read"


def test_admin_can_write_document(client):
    token = create_token(
        client["jwt_service"],
        client["admin"].user_id,
        client["admin"].username,
        client["admin"].role,
    )

    response = client["client"].get(
        "/protected/document/write",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["user_id"] == client["admin"].user_id
    assert body["permission"] == "document.write"


def test_viewer_can_read_document(client):
    token = create_token(
        client["jwt_service"],
        client["viewer"].user_id,
        client["viewer"].username,
        client["viewer"].role,
    )

    response = client["client"].get(
        "/protected/document/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["user_id"] == client["viewer"].user_id
    assert body["permission"] == "document.read"


def test_viewer_cannot_write_document(client):
    token = create_token(
        client["jwt_service"],
        client["viewer"].user_id,
        client["viewer"].username,
        client["viewer"].role,
    )

    response = client["client"].get(
        "/protected/document/write",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_protected_api_preserves_user_identity(client):
    token = create_token(
        client["jwt_service"],
        client["viewer"].user_id,
        client["viewer"].username,
        client["viewer"].role,
    )

    response = client["client"].get(
        "/protected/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == client["viewer"].user_id
    assert body["username"] == "protected_viewer"
    assert body["role"] == "viewer"


def test_protected_api_openapi_contains_routes(client):
    schema = client["client"].get(
        "/openapi.json",
    ).json()

    paths = schema["paths"]

    assert "/protected/me" in paths
    assert "/protected/document/read" in paths
    assert "/protected/document/write" in paths


def test_rbac_service_is_shared_by_protected_routes(client):
    assert isinstance(
        client["rbac_service"],
        RBACService,
    )

    assert (
        client["rbac_service"]
        is get_rbac_service()
    )


def test_admin_permission_contract(client):
    assert client["rbac_service"].has_permission(
        client["admin"].user_id,
        "document.read",
    )

    assert client["rbac_service"].has_permission(
        client["admin"].user_id,
        "document.write",
    )


def test_viewer_permission_contract(client):
    assert client["rbac_service"].has_permission(
        client["viewer"].user_id,
        "document.read",
    )

    assert not client["rbac_service"].has_permission(
        client["viewer"].user_id,
        "document.write",
    )
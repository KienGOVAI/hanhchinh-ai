from __future__ import annotations

import pytest

from app.auth.integration import (
    AuthenticatedUser,
    AuthIntegrationService,
)
from app.auth.jwt import JWTService
from app.auth.rbac import PermissionDeniedError
from app.auth.rbac_service import RBACService
from app.auth.service import (
    AuthValidationError,
    InvalidPasswordError,
    UserNotFoundError,
    UserService,
)


TEST_SECRET = "integration-secret-key-123456"


def build_integration():
    user_service = UserService()

    jwt_service = JWTService(
        secret_key=TEST_SECRET,
    )

    rbac_service = RBACService()

    rbac_service.create_permission(
        "document.read",
        "??c v?n b?n",
    )

    rbac_service.create_permission(
        "document.write",
        "So?n v?n b?n",
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
        username="admin",
        password="admin-password",
        role="admin",
    )

    viewer = user_service.create_user(
        username="viewer",
        password="viewer-password",
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

    service = AuthIntegrationService(
        user_service=user_service,
        jwt_service=jwt_service,
        rbac_service=rbac_service,
    )

    return (
        user_service,
        jwt_service,
        rbac_service,
        service,
        admin,
        viewer,
    )


def test_authenticated_user_contract():
    user = AuthenticatedUser(
        user_id="user-001",
        username="admin",
        role="admin",
    )

    assert user.user_id == "user-001"
    assert user.username == "admin"
    assert user.role == "admin"


def test_authenticate_returns_authenticated_user():
    (
        _,
        _,
        _,
        service,
        admin,
        _,
    ) = build_integration()

    authenticated = service.authenticate(
        "admin",
        "admin-password",
    )

    assert isinstance(
        authenticated,
        AuthenticatedUser,
    )

    assert authenticated.user_id == admin.user_id
    assert authenticated.username == "admin"
    assert authenticated.role == "admin"


def test_authenticate_unknown_user_rejected():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    with pytest.raises(UserNotFoundError):
        service.authenticate(
            "unknown",
            "password-123",
        )


def test_authenticate_wrong_password_rejected():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    with pytest.raises(InvalidPasswordError):
        service.authenticate(
            "admin",
            "wrong-password",
        )


def test_authenticate_inactive_user_rejected():
    (
        user_service,
        _,
        _,
        service,
        admin,
        _,
    ) = build_integration()

    user_service.deactivate(admin.user_id)

    with pytest.raises(AuthValidationError):
        service.authenticate(
            "admin",
            "admin-password",
        )


def test_issue_token_contains_authenticated_user_claims():
    (
        _,
        jwt_service,
        _,
        service,
        admin,
        _,
    ) = build_integration()

    authenticated = service.authenticate(
        "admin",
        "admin-password",
    )

    token = service.issue_token(
        authenticated,
    )

    payload = jwt_service.decode_token(
        token,
    )

    assert payload["sub"] == admin.user_id
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_authenticate_and_issue_token():
    (
        _,
        jwt_service,
        _,
        service,
        admin,
        _,
    ) = build_integration()

    authenticated, token = (
        service.authenticate_and_issue_token(
            "admin",
            "admin-password",
        )
    )

    assert authenticated.user_id == admin.user_id
    assert authenticated.username == "admin"
    assert authenticated.role == "admin"

    payload = jwt_service.decode_token(
        token,
    )

    assert payload["sub"] == admin.user_id
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_get_authenticated_user_from_bearer_token():
    (
        _,
        _,
        _,
        service,
        admin,
        _,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "admin",
        "admin-password",
    )

    authenticated = service.get_authenticated_user(
        f"Bearer {token}",
    )

    assert isinstance(
        authenticated,
        AuthenticatedUser,
    )

    assert authenticated.user_id == admin.user_id
    assert authenticated.username == "admin"
    assert authenticated.role == "admin"


def test_invalid_token_rejected():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    with pytest.raises(Exception):
        service.get_authenticated_user(
            "Bearer invalid-token",
        )


def test_missing_authorization_rejected():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    with pytest.raises(Exception):
        service.get_authenticated_user(
            None,
        )


def test_admin_has_read_permission():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "admin",
        "admin-password",
    )

    assert service.has_permission(
        f"Bearer {token}",
        "document.read",
    ) is True


def test_admin_has_write_permission():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "admin",
        "admin-password",
    )

    assert service.has_permission(
        f"Bearer {token}",
        "document.write",
    ) is True


def test_viewer_does_not_have_write_permission():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "viewer",
        "viewer-password",
    )

    assert service.has_permission(
        f"Bearer {token}",
        "document.write",
    ) is False


def test_require_permission_returns_authenticated_user():
    (
        _,
        _,
        _,
        service,
        admin,
        _,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "admin",
        "admin-password",
    )

    authenticated = service.require_permission(
        f"Bearer {token}",
        "document.write",
    )

    assert authenticated.user_id == admin.user_id
    assert authenticated.username == "admin"
    assert authenticated.role == "admin"


def test_require_permission_denies_viewer():
    (
        _,
        _,
        _,
        service,
        _,
        _,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "viewer",
        "viewer-password",
    )

    with pytest.raises(PermissionDeniedError):
        service.require_permission(
            f"Bearer {token}",
            "document.write",
        )


def test_require_role_allows_admin():
    (
        _,
        _,
        _,
        service,
        admin,
        _,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "admin",
        "admin-password",
    )

    authenticated = service.require_role(
        f"Bearer {token}",
        "admin",
    )

    assert authenticated.user_id == admin.user_id
    assert authenticated.username == "admin"
    assert authenticated.role == "admin"


def test_require_role_denies_viewer():
    (
        _,
        _,
        _,
        service,
        _,
        viewer,
    ) = build_integration()

    _, token = service.authenticate_and_issue_token(
        "viewer",
        "viewer-password",
    )

    with pytest.raises(PermissionDeniedError):
        service.require_role(
            f"Bearer {token}",
            "admin",
        )

    assert viewer.role == "viewer"

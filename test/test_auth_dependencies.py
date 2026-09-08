from __future__ import annotations

import pytest

from app.auth.dependencies import AuthDependencyService
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


def build_integration() -> tuple[
    AuthIntegrationService,
    UserService,
    JWTService,
    RBACService,
]:
    user_service = UserService()
    jwt_service = JWTService(
        secret_key="integration-secret-key-123456"
    )
    rbac_service = RBACService()

    integration = AuthIntegrationService(
        user_service=user_service,
        jwt_service=jwt_service,
        rbac_service=rbac_service,
    )

    return (
        integration,
        user_service,
        jwt_service,
        rbac_service,
    )


def create_admin(
    user_service: UserService,
):
    return user_service.create_user(
        username="admin",
        password="admin-password",
        role="admin",
    )


def create_viewer(
    user_service: UserService,
):
    return user_service.create_user(
        username="viewer",
        password="viewer-password",
        role="viewer",
    )


def test_authenticated_user_contract() -> None:
    user = AuthenticatedUser(
        user_id="user-001",
        username="admin",
        role="admin",
    )

    assert user.user_id == "user-001"
    assert user.username == "admin"
    assert user.role == "admin"


def test_authenticate_returns_authenticated_user() -> None:
    integration, user_service, _, _ = build_integration()

    created = create_admin(user_service)

    authenticated = integration.authenticate(
        "admin",
        "admin-password",
    )

    assert isinstance(
        authenticated,
        AuthenticatedUser,
    )
    assert authenticated.user_id == created.user_id
    assert authenticated.username == "admin"
    assert authenticated.role == "admin"


def test_authenticate_rejects_unknown_user() -> None:
    integration, _, _, _ = build_integration()

    with pytest.raises(UserNotFoundError):
        integration.authenticate(
            "unknown",
            "password-123",
        )


def test_authenticate_rejects_invalid_password() -> None:
    integration, user_service, _, _ = build_integration()

    create_admin(user_service)

    with pytest.raises(InvalidPasswordError):
        integration.authenticate(
            "admin",
            "wrong-password",
        )


def test_authenticate_rejects_inactive_user() -> None:
    integration, user_service, _, _ = build_integration()

    user = create_admin(user_service)

    user_service.deactivate(user.user_id)

    with pytest.raises(AuthValidationError):
        integration.authenticate(
            "admin",
            "admin-password",
        )


def test_issue_token_contains_user_identity() -> None:
    integration, user_service, jwt_service, _ = build_integration()

    user = create_admin(user_service)

    authenticated = integration.authenticate(
        "admin",
        "admin-password",
    )

    token = integration.issue_token(authenticated)

    payload = jwt_service.decode_token(token)

    assert payload["sub"] == user.user_id
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_authenticate_and_issue_token() -> None:
    integration, user_service, jwt_service, _ = build_integration()

    user = create_admin(user_service)

    authenticated, token = (
        integration.authenticate_and_issue_token(
            "admin",
            "admin-password",
        )
    )

    assert authenticated.user_id == user.user_id
    assert authenticated.username == "admin"
    assert authenticated.role == "admin"

    payload = jwt_service.decode_token(token)

    assert payload["sub"] == user.user_id
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_get_authenticated_user_from_bearer_token() -> None:
    integration, user_service, _, _ = build_integration()

    user = create_admin(user_service)

    authenticated, token = (
        integration.authenticate_and_issue_token(
            "admin",
            "admin-password",
        )
    )

    result = integration.get_authenticated_user(
        f"Bearer {token}"
    )

    assert result == authenticated
    assert result.user_id == user.user_id
    assert result.username == "admin"
    assert result.role == "admin"


def test_get_authenticated_user_rejects_missing_authorization() -> None:
    integration, _, _, _ = build_integration()

    with pytest.raises(Exception):
        integration.get_authenticated_user(None)


def test_get_authenticated_user_rejects_invalid_token() -> None:
    integration, _, _, _ = build_integration()

    with pytest.raises(Exception):
        integration.get_authenticated_user(
            "Bearer invalid-token"
        )


def test_has_permission_returns_false_without_permission() -> None:
    integration, user_service, _, rbac_service = (
        build_integration()
    )

    user = create_admin(user_service)

    rbac_service.create_permission("document.read")
    rbac_service.create_role("admin")
    rbac_service.assign_role(
        user.user_id,
        "admin",
    )

    authenticated, token = (
        integration.authenticate_and_issue_token(
            "admin",
            "admin-password",
        )
    )

    assert authenticated.user_id == user.user_id

    assert integration.has_permission(
        f"Bearer {token}",
        "document.read",
    ) is False


def test_has_permission_returns_true_when_granted() -> None:
    integration, user_service, _, rbac_service = (
        build_integration()
    )

    user = create_admin(user_service)

    rbac_service.create_permission("document.read")
    rbac_service.create_role("admin")

    rbac_service.grant_permission(
        "admin",
        "document.read",
    )

    rbac_service.assign_role(
        user.user_id,
        "admin",
    )

    _, token = integration.authenticate_and_issue_token(
        "admin",
        "admin-password",
    )

    assert integration.has_permission(
        f"Bearer {token}",
        "document.read",
    ) is True


def test_require_permission_returns_authenticated_user() -> None:
    integration, user_service, _, rbac_service = (
        build_integration()
    )

    user = create_admin(user_service)

    rbac_service.create_permission("document.write")
    rbac_service.create_role("admin")

    rbac_service.grant_permission(
        "admin",
        "document.write",
    )

    rbac_service.assign_role(
        user.user_id,
        "admin",
    )

    authenticated, token = (
        integration.authenticate_and_issue_token(
            "admin",
            "admin-password",
        )
    )

    result = integration.require_permission(
        f"Bearer {token}",
        "document.write",
    )

    assert result == authenticated


def test_require_permission_denies_missing_permission() -> None:
    integration, user_service, _, rbac_service = (
        build_integration()
    )

    user = create_admin(user_service)

    rbac_service.create_permission("document.delete")
    rbac_service.create_role("admin")

    rbac_service.assign_role(
        user.user_id,
        "admin",
    )

    _, token = integration.authenticate_and_issue_token(
        "admin",
        "admin-password",
    )

    with pytest.raises(PermissionDeniedError):
        integration.require_permission(
            f"Bearer {token}",
            "document.delete",
        )


def test_require_role_returns_authenticated_user() -> None:
    integration, user_service, _, rbac_service = (
        build_integration()
    )

    user = create_viewer(user_service)

    rbac_service.create_role("viewer")

    rbac_service.assign_role(
        user.user_id,
        "viewer",
    )

    authenticated, token = (
        integration.authenticate_and_issue_token(
            "viewer",
            "viewer-password",
        )
    )

    result = integration.require_role(
        f"Bearer {token}",
        "viewer",
    )

    assert result == authenticated


def test_require_role_denies_wrong_role() -> None:
    integration, user_service, _, rbac_service = (
        build_integration()
    )

    user = create_viewer(user_service)

    rbac_service.create_role("viewer")
    rbac_service.create_role("admin")

    rbac_service.assign_role(
        user.user_id,
        "viewer",
    )

    _, token = integration.authenticate_and_issue_token(
        "viewer",
        "viewer-password",
    )

    with pytest.raises(PermissionDeniedError):
        integration.require_role(
            f"Bearer {token}",
            "admin",
        )
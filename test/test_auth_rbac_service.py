import pytest

from app.auth.rbac import PermissionDeniedError, RBACValidationError
from app.auth.rbac_service import RBACService


def build_service() -> RBACService:
    service = RBACService()

    service.create_permission(
        "document.read",
        "Đọc văn bản",
    )
    service.create_permission(
        "document.write",
        "Soạn văn bản",
    )
    service.create_permission(
        "document.approve",
        "Duyệt văn bản",
    )

    service.create_role("admin")
    service.create_role("editor")
    service.create_role("viewer")

    service.grant_permission("admin", "document.read")
    service.grant_permission("admin", "document.write")
    service.grant_permission("admin", "document.approve")

    service.grant_permission("editor", "document.read")
    service.grant_permission("editor", "document.write")

    service.grant_permission("viewer", "document.read")

    return service


def test_create_permission():
    service = RBACService()

    permission = service.create_permission(
        "document.read",
        "Đọc văn bản",
    )

    assert permission.name == "document.read"
    assert service.get_permission("DOCUMENT.READ") is permission


def test_list_permissions():
    service = RBACService()

    service.create_permission("document.read")
    service.create_permission("document.write")

    permissions = service.list_permissions()

    assert len(permissions) == 2
    assert {
        permission.name
        for permission in permissions
    } == {
        "document.read",
        "document.write",
    }


def test_create_role():
    service = RBACService()

    service.create_permission("document.read")
    role = service.create_role(
        "viewer",
        {"document.read"},
    )

    assert role.name == "viewer"
    assert role.has_permission("document.read")


def test_create_role_rejects_unknown_permission():
    service = RBACService()

    with pytest.raises(RBACValidationError):
        service.create_role(
            "viewer",
            {"document.read"},
        )


def test_list_roles():
    service = RBACService()

    service.create_role("admin")
    service.create_role("viewer")

    roles = service.list_roles()

    assert len(roles) == 2
    assert {
        role.name
        for role in roles
    } == {
        "admin",
        "viewer",
    }


def test_grant_permission():
    service = RBACService()

    service.create_permission("document.read")
    service.create_role("viewer")

    service.grant_permission(
        "viewer",
        "document.read",
    )

    assert service.get_role("viewer").has_permission(
        "document.read"
    )


def test_revoke_permission():
    service = RBACService()

    service.create_permission("document.read")
    service.create_role(
        "viewer",
        {"document.read"},
    )

    service.revoke_permission(
        "viewer",
        "document.read",
    )

    assert not service.get_role("viewer").has_permission(
        "document.read"
    )


def test_assign_role():
    service = build_service()

    role = service.assign_role(
        "user-001",
        "editor",
    )

    assert role.name == "editor"
    assert service.has_role(
        "user-001",
        "editor",
    )


def test_assign_role_is_case_insensitive():
    service = build_service()

    service.assign_role(
        "user-001",
        "EDITOR",
    )

    assert service.has_role(
        "user-001",
        "editor",
    )


def test_get_user_role():
    service = build_service()

    service.assign_role(
        "user-001",
        "viewer",
    )

    role = service.get_user_role("user-001")

    assert role.name == "viewer"


def test_get_user_role_rejects_unassigned_user():
    service = build_service()

    with pytest.raises(RBACValidationError):
        service.get_user_role("unknown-user")


def test_remove_role():
    service = build_service()

    service.assign_role(
        "user-001",
        "viewer",
    )

    service.remove_role("user-001")

    assert not service.has_role(
        "user-001",
        "viewer",
    )


def test_has_permission_for_authorized_user():
    service = build_service()

    service.assign_role(
        "user-001",
        "editor",
    )

    assert service.has_permission(
        "user-001",
        "document.read",
    )


def test_has_permission_for_unauthorized_user():
    service = build_service()

    service.assign_role(
        "user-001",
        "viewer",
    )

    assert not service.has_permission(
        "user-001",
        "document.write",
    )


def test_has_permission_for_unassigned_user():
    service = build_service()

    assert not service.has_permission(
        "unknown-user",
        "document.read",
    )


def test_require_permission_allows_authorized_user():
    service = build_service()

    service.assign_role(
        "user-001",
        "editor",
    )

    service.require_permission(
        "user-001",
        "document.write",
    )


def test_require_permission_denies_user():
    service = build_service()

    service.assign_role(
        "user-001",
        "viewer",
    )

    with pytest.raises(PermissionDeniedError):
        service.require_permission(
            "user-001",
            "document.write",
        )


def test_require_role_allows_correct_role():
    service = build_service()

    service.assign_role(
        "user-001",
        "admin",
    )

    service.require_role(
        "user-001",
        "admin",
    )


def test_require_role_denies_wrong_role():
    service = build_service()

    service.assign_role(
        "user-001",
        "viewer",
    )

    with pytest.raises(PermissionDeniedError):
        service.require_role(
            "user-001",
            "admin",
        )


def test_get_user_roles_returns_copy():
    service = build_service()

    service.assign_role(
        "user-001",
        "editor",
    )

    roles = service.get_user_roles()
    roles["user-002"] = "admin"

    assert "user-002" not in service.get_user_roles()


def test_clear_removes_all_rbac_state():
    service = build_service()

    service.assign_role(
        "user-001",
        "admin",
    )

    service.clear()

    assert service.list_permissions() == []
    assert service.list_roles() == []
    assert service.get_user_roles() == {}


def test_empty_user_id_rejected():
    service = build_service()

    with pytest.raises(RBACValidationError):
        service.assign_role("", "admin")


def test_unknown_role_rejected():
    service = build_service()

    with pytest.raises(RBACValidationError):
        service.assign_role(
            "user-001",
            "superuser",
        )


def test_permission_check_is_case_insensitive():
    service = build_service()

    service.assign_role(
        "user-001",
        "editor",
    )

    assert service.has_permission(
        "user-001",
        "DOCUMENT.WRITE",
    )


def test_reassigning_user_replaces_previous_role():
    service = build_service()

    service.assign_role(
        "user-001",
        "admin",
    )
    service.assign_role(
        "user-001",
        "viewer",
    )

    assert service.has_role(
        "user-001",
        "viewer",
    )

    assert not service.has_permission(
        "user-001",
        "document.write",
    )
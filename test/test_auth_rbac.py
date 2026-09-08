import pytest

from app.auth.rbac import (
    Permission,
    PermissionDeniedError,
    RBACPolicy,
    RBACValidationError,
    Role,
)


def test_permission_creation():
    permission = Permission(
        name="DOCUMENT.READ",
        description="Đọc văn bản",
    )

    assert permission.name == "DOCUMENT.READ"
    assert permission.description == "Đọc văn bản"
    assert permission.normalized_name() == "document.read"


def test_permission_rejects_empty_name():
    with pytest.raises(RBACValidationError):
        Permission(name="")


def test_role_creation_normalizes_name():
    role = Role(
        name="  ADMIN  ",
        permissions={"DOCUMENT.READ"},
    )

    assert role.name == "admin"
    assert role.has_permission("document.read")
    assert role.has_permission("DOCUMENT.READ")


def test_role_add_permission():
    role = Role(name="admin")

    role.add_permission("DOCUMENT.READ")

    assert role.has_permission("document.read")


def test_role_remove_permission():
    role = Role(
        name="admin",
        permissions={"document.read"},
    )

    role.remove_permission("DOCUMENT.READ")

    assert not role.has_permission("document.read")


def test_role_rejects_empty_name():
    with pytest.raises(RBACValidationError):
        Role(name="")


def test_policy_add_and_get_permission():
    policy = RBACPolicy()
    permission = Permission("document.read")

    policy.add_permission(permission)

    assert policy.get_permission("DOCUMENT.READ") is permission


def test_policy_add_and_get_role():
    policy = RBACPolicy()
    role = Role("admin")

    policy.add_role(role)

    assert policy.get_role("ADMIN") is role


def test_policy_grant_permission():
    policy = RBACPolicy()

    policy.add_permission(Permission("document.read"))
    policy.add_role(Role("admin"))

    policy.grant("admin", "document.read")

    assert policy.allows("admin", "document.read")


def test_policy_revoke_permission():
    policy = RBACPolicy()

    policy.add_permission(Permission("document.read"))
    policy.add_role(Role("admin"))
    policy.grant("admin", "document.read")

    policy.revoke("admin", "document.read")

    assert not policy.allows("admin", "document.read")


def test_policy_require_allows_authorized_role():
    policy = RBACPolicy()

    policy.add_permission(Permission("document.read"))
    policy.add_role(Role("admin"))
    policy.grant("admin", "document.read")

    policy.require("admin", "document.read")


def test_policy_require_denies_unauthorized_role():
    policy = RBACPolicy()

    policy.add_permission(Permission("document.read"))
    policy.add_role(Role("user"))

    with pytest.raises(PermissionDeniedError):
        policy.require("user", "document.read")


def test_policy_missing_permission_rejected():
    policy = RBACPolicy()
    policy.add_role(Role("admin"))

    with pytest.raises(RBACValidationError):
        policy.grant("admin", "document.read")


def test_policy_missing_role_rejected():
    policy = RBACPolicy()
    policy.add_permission(Permission("document.read"))

    with pytest.raises(RBACValidationError):
        policy.grant("admin", "document.read")


def test_permission_check_is_case_insensitive():
    policy = RBACPolicy()

    policy.add_permission(Permission("DOCUMENT.READ"))
    policy.add_role(Role("ADMIN"))
    policy.grant("ADMIN", "DOCUMENT.READ")

    assert policy.allows("admin", "document.read")
    assert policy.allows("ADMIN", "DOCUMENT.READ")


def test_role_permissions_are_isolated():
    admin = Role("admin")
    user = Role("user")

    admin.add_permission("document.read")

    assert admin.has_permission("document.read")
    assert not user.has_permission("document.read")


def test_duplicate_permission_is_idempotent():
    role = Role("admin")

    role.add_permission("document.read")
    role.add_permission("document.read")

    assert role.permissions == {"document.read"}


def test_duplicate_role_replaces_existing_role():
    policy = RBACPolicy()

    first = Role("admin", {"document.read"})
    second = Role("admin", {"document.write"})

    policy.add_role(first)
    policy.add_role(second)

    assert policy.get_role("admin") is second
    assert policy.allows("admin", "document.write")
    assert not policy.allows("admin", "document.read")
"""
Sprint 17.1 - Authentication Domain Tests
"""

from __future__ import annotations

import pytest

from app.auth import (
    AuthenticationValidationError,
    User,
    UserRole,
    UserStatus,
)


# ============================================================
# USER CREATION
# ============================================================


def test_user_creation_defaults():
    user = User(
        username="admin",
        password_hash="hashed-password",
    )

    assert user.user_id
    assert user.username == "admin"
    assert user.password_hash == "hashed-password"
    assert user.role == UserRole.STAFF
    assert user.status == UserStatus.ACTIVE
    assert user.is_active()
    assert not user.is_locked()


def test_user_creation_with_role_and_status():
    user = User(
        username="manager",
        password_hash="hashed-password",
        role=UserRole.MANAGER,
        status=UserStatus.INACTIVE,
        full_name="Manager User",
    )

    assert user.role == UserRole.MANAGER
    assert user.status == UserStatus.INACTIVE
    assert user.full_name == "Manager User"
    assert not user.is_active()


# ============================================================
# VALIDATION
# ============================================================


@pytest.mark.parametrize(
    "username",
    [
        "",
        "  ",
        "ab",
    ],
)
def test_invalid_username_is_rejected(username):
    with pytest.raises(
        AuthenticationValidationError
    ):
        User(
            username=username,
            password_hash="hashed-password",
        )


def test_username_with_space_is_rejected():
    with pytest.raises(
        AuthenticationValidationError
    ):
        User(
            username="admin user",
            password_hash="hashed-password",
        )


def test_empty_password_hash_is_rejected():
    with pytest.raises(
        AuthenticationValidationError
    ):
        User(
            username="admin",
            password_hash="",
        )


# ============================================================
# STATUS
# ============================================================


def test_user_status_lifecycle():
    user = User(
        username="staff",
        password_hash="hashed-password",
    )

    assert user.is_active()

    user.deactivate()

    assert user.status == UserStatus.INACTIVE
    assert not user.is_active()

    user.activate()

    assert user.status == UserStatus.ACTIVE
    assert user.is_active()

    user.lock()

    assert user.status == UserStatus.LOCKED
    assert user.is_locked()


# ============================================================
# ROLE
# ============================================================


def test_user_role_operations():
    user = User(
        username="staff",
        password_hash="hashed-password",
    )

    assert user.has_role(UserRole.STAFF)
    assert not user.has_role(UserRole.ADMIN)

    user.change_role(UserRole.ADMIN)

    assert user.role == UserRole.ADMIN
    assert user.has_role(UserRole.ADMIN)
    assert not user.has_role(UserRole.STAFF)


def test_string_role_is_normalized():
    user = User(
        username="manager",
        password_hash="hashed-password",
        role="manager",
    )

    assert user.role == UserRole.MANAGER


# ============================================================
# SERIALIZATION
# ============================================================


def test_to_dict_does_not_expose_password_hash():
    user = User(
        username="admin",
        password_hash="secret-hash",
        role=UserRole.ADMIN,
        full_name="System Admin",
    )

    data = user.to_dict()

    assert data["user_id"] == user.user_id
    assert data["username"] == "admin"
    assert data["full_name"] == "System Admin"
    assert data["role"] == "admin"
    assert data["status"] == "active"

    assert "password_hash" not in data
import pytest

from app.auth.service import (
    AuthValidationError,
    InvalidPasswordError,
    PasswordHasher,
    UserNotFoundError,
    UserService,
)


def test_password_hash_and_verify():
    password = "Secret123"

    password_hash = PasswordHasher.hash(password)

    assert password_hash != password
    assert password_hash.startswith("pbkdf2_sha256$")
    assert PasswordHasher.verify(password, password_hash)
    assert not PasswordHasher.verify("WrongPassword", password_hash)


def test_password_requires_minimum_length():
    with pytest.raises(AuthValidationError):
        PasswordHasher.hash("1234567")


def test_create_user():
    service = UserService()

    user = service.create_user(
        username="admin",
        password="Secret123",
        role="admin",
    )

    assert user.user_id
    assert user.username == "admin"
    assert user.role == "admin"
    assert user.is_active is True
    assert user.password_hash != "Secret123"
    assert service.count() == 1


def test_duplicate_username_rejected():
    service = UserService()

    service.create_user(
        username="admin",
        password="Secret123",
    )

    with pytest.raises(AuthValidationError):
        service.create_user(
            username="ADMIN",
            password="Another123",
        )


def test_get_user_and_get_by_username():
    service = UserService()

    created = service.create_user(
        username="user01",
        password="Secret123",
    )

    assert service.get_user(created.user_id) == created
    assert service.get_by_username("USER01") == created


def test_missing_user_rejected():
    service = UserService()

    with pytest.raises(UserNotFoundError):
        service.get_user("missing-user")

    with pytest.raises(UserNotFoundError):
        service.get_by_username("missing")


def test_authenticate_success():
    service = UserService()

    created = service.create_user(
        username="admin",
        password="Secret123",
        role="admin",
    )

    authenticated = service.authenticate(
        username="ADMIN",
        password="Secret123",
    )

    assert authenticated == created


def test_authenticate_wrong_password():
    service = UserService()

    service.create_user(
        username="admin",
        password="Secret123",
    )

    with pytest.raises(InvalidPasswordError):
        service.authenticate(
            username="admin",
            password="Wrong123",
        )


def test_inactive_user_cannot_authenticate():
    service = UserService()

    user = service.create_user(
        username="admin",
        password="Secret123",
    )

    service.deactivate(user.user_id)

    with pytest.raises(AuthValidationError):
        service.authenticate(
            username="admin",
            password="Secret123",
        )


def test_update_password():
    service = UserService()

    user = service.create_user(
        username="admin",
        password="Secret123",
    )

    updated = service.update_password(
        user_id=user.user_id,
        new_password="NewSecret123",
    )

    assert updated.user_id == user.user_id
    assert updated.password_hash != user.password_hash

    authenticated = service.authenticate(
        username="admin",
        password="NewSecret123",
    )

    assert authenticated.user_id == user.user_id

    with pytest.raises(InvalidPasswordError):
        service.authenticate(
            username="admin",
            password="Secret123",
        )


def test_activate_and_deactivate():
    service = UserService()

    user = service.create_user(
        username="admin",
        password="Secret123",
    )

    deactivated = service.deactivate(user.user_id)

    assert deactivated.is_active is False

    activated = service.activate(user.user_id)

    assert activated.is_active is True


def test_delete_user():
    service = UserService()

    user = service.create_user(
        username="admin",
        password="Secret123",
    )

    assert service.exists(user.user_id)

    service.delete_user(user.user_id)

    assert not service.exists(user.user_id)

    with pytest.raises(UserNotFoundError):
        service.get_user(user.user_id)

    assert service.count() == 0
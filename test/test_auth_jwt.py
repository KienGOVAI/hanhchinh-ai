import time

import pytest

from app.auth.jwt import (
    JWTExpiredError,
    JWTService,
    JWTValidationError,
)


def test_create_and_decode_token():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    token = service.create_token(
        subject="user-001",
    )

    payload = service.decode_token(token)

    assert isinstance(token, str)
    assert token.count(".") == 2
    assert payload["sub"] == "user-001"
    assert isinstance(payload["iat"], int)
    assert isinstance(payload["exp"], int)
    assert payload["exp"] > payload["iat"]


def test_token_supports_custom_claims():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    token = service.create_token(
        subject="user-001",
        claims={
            "username": "admin",
            "role": "admin",
        },
    )

    payload = service.decode_token(token)

    assert payload["sub"] == "user-001"
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_get_subject():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    token = service.create_token(
        subject="user-123",
    )

    assert service.get_subject(token) == "user-123"


def test_validate_token():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    token = service.create_token(
        subject="user-001",
    )

    assert service.validate_token(token) is True


def test_wrong_secret_rejects_token():
    service_a = JWTService(
        secret_key="test-secret-key-123456",
    )

    service_b = JWTService(
        secret_key="different-secret-123456",
    )

    token = service_a.create_token(
        subject="user-001",
    )

    with pytest.raises(JWTValidationError):
        service_b.decode_token(token)

    assert service_b.validate_token(token) is False


def test_tampered_payload_rejected():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    token = service.create_token(
        subject="user-001",
    )

    parts = token.split(".")

    tampered_payload = parts[1] + "x"

    tampered_token = (
        f"{parts[0]}.{tampered_payload}.{parts[2]}"
    )

    with pytest.raises(JWTValidationError):
        service.decode_token(tampered_token)


def test_malformed_token_rejected():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    with pytest.raises(JWTValidationError):
        service.decode_token("not-a-jwt")

    assert service.validate_token("not-a-jwt") is False


def test_expired_token_rejected():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    token = service.create_token(
        subject="user-001",
        expires_in_seconds=1,
    )

    time.sleep(1.1)

    with pytest.raises(JWTExpiredError):
        service.decode_token(token)

    assert service.validate_token(token) is False


def test_expiration_can_be_disabled_for_decoding():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    token = service.create_token(
        subject="user-001",
        expires_in_seconds=1,
    )

    time.sleep(1.1)

    payload = service.decode_token(
        token,
        verify_exp=False,
    )

    assert payload["sub"] == "user-001"


def test_invalid_secret_rejected():
    with pytest.raises(JWTValidationError):
        JWTService(
            secret_key="short",
        )


def test_invalid_algorithm_rejected():
    with pytest.raises(JWTValidationError):
        JWTService(
            secret_key="test-secret-key-123456",
            algorithm="HS512",
        )


def test_invalid_expiration_rejected():
    with pytest.raises(JWTValidationError):
        JWTService(
            secret_key="test-secret-key-123456",
            expires_in_seconds=0,
        )


def test_subject_is_required():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    with pytest.raises(JWTValidationError):
        service.create_token(subject="")

    with pytest.raises(JWTValidationError):
        service.create_token(subject="   ")


def test_registered_claims_cannot_be_overridden():
    service = JWTService(
        secret_key="test-secret-key-123456",
    )

    before = int(time.time())

    token = service.create_token(
        subject="user-001",
        claims={
            "sub": "attacker",
            "iat": 1,
            "exp": 1,
        },
    )

    payload = service.decode_token(token)

    after = int(time.time())

    assert payload["sub"] == "user-001"
    assert before <= payload["iat"] <= after
    assert payload["exp"] > payload["iat"]
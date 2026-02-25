"""Tests for JWT authentication — token creation, decoding, and service layer."""

from __future__ import annotations

from datetime import timedelta

import pytest

from uncase.exceptions import AuthenticationError
from uncase.services.auth import (
    ACCESS_TOKEN_LIFETIME,
    REFRESH_TOKEN_LIFETIME,
    _create_jwt,
    _decode_jwt,
)

SECRET = "test-secret-key-for-jwt-tests-min-32b"  # noqa: S105


class TestCreateJWT:
    """Test JWT token creation."""

    def test_creates_valid_token(self) -> None:
        token = _create_jwt({"sub": "org123"}, SECRET, timedelta(hours=1))
        assert isinstance(token, str)
        assert len(token) > 20

    def test_token_contains_payload(self) -> None:
        payload = {"sub": "org123", "role": "admin", "scopes": "read write admin"}
        token = _create_jwt(payload, SECRET, timedelta(hours=1))
        decoded = _decode_jwt(token, SECRET)
        assert decoded["sub"] == "org123"
        assert decoded["role"] == "admin"
        assert decoded["scopes"] == "read write admin"

    def test_token_has_standard_claims(self) -> None:
        token = _create_jwt({"sub": "org123"}, SECRET, timedelta(hours=1))
        decoded = _decode_jwt(token, SECRET)
        assert "iat" in decoded
        assert "exp" in decoded
        assert "jti" in decoded

    def test_unique_jti(self) -> None:
        token1 = _create_jwt({"sub": "org"}, SECRET, timedelta(hours=1))
        token2 = _create_jwt({"sub": "org"}, SECRET, timedelta(hours=1))
        d1 = _decode_jwt(token1, SECRET)
        d2 = _decode_jwt(token2, SECRET)
        assert d1["jti"] != d2["jti"]

    def test_different_secrets_produce_different_tokens(self) -> None:
        token1 = _create_jwt({"sub": "x"}, "secret-a", timedelta(hours=1))
        token2 = _create_jwt({"sub": "x"}, "secret-b", timedelta(hours=1))
        assert token1 != token2


class TestDecodeJWT:
    """Test JWT token decoding and verification."""

    def test_valid_token(self) -> None:
        token = _create_jwt({"sub": "org123", "org_id": "org123"}, SECRET, timedelta(hours=1))
        payload = _decode_jwt(token, SECRET)
        assert payload["sub"] == "org123"
        assert payload["org_id"] == "org123"

    def test_expired_token_raises(self) -> None:
        token = _create_jwt({"sub": "org123"}, SECRET, timedelta(seconds=-1))
        with pytest.raises(AuthenticationError):
            _decode_jwt(token, SECRET)

    def test_wrong_secret_raises(self) -> None:
        token = _create_jwt({"sub": "org123"}, SECRET, timedelta(hours=1))
        with pytest.raises(AuthenticationError):
            _decode_jwt(token, "wrong-secret")

    def test_garbage_token_raises(self) -> None:
        with pytest.raises(AuthenticationError):
            _decode_jwt("not.a.valid.token", SECRET)

    def test_empty_token_raises(self) -> None:
        with pytest.raises(AuthenticationError):
            _decode_jwt("", SECRET)


class TestTokenLifetimes:
    """Test token lifetime constants."""

    def test_access_token_lifetime(self) -> None:
        assert timedelta(hours=1) == ACCESS_TOKEN_LIFETIME

    def test_refresh_token_lifetime(self) -> None:
        assert timedelta(days=30) == REFRESH_TOKEN_LIFETIME


class TestAuthServiceVerifyToken:
    """Test AuthService.verify_token method (no DB needed)."""

    def test_verify_access_token(self) -> None:
        from uncase.services.auth import AuthService

        service = AuthService(session=None, secret=SECRET)  # type: ignore[arg-type]
        token = _create_jwt(
            {"sub": "org123", "org_id": "org123", "role": "admin", "scopes": "read write admin"},
            SECRET,
            timedelta(hours=1),
        )
        payload = service.verify_token(token)
        assert payload["org_id"] == "org123"
        assert payload["role"] == "admin"

    def test_reject_refresh_token_as_access(self) -> None:
        from uncase.services.auth import AuthService

        service = AuthService(session=None, secret=SECRET)  # type: ignore[arg-type]
        refresh = _create_jwt(
            {"sub": "org123", "org_id": "org123", "type": "refresh"},
            SECRET,
            timedelta(days=30),
        )
        with pytest.raises(AuthenticationError, match="refresh"):
            service.verify_token(refresh)

    def test_verify_expired_raises(self) -> None:
        from uncase.services.auth import AuthService

        service = AuthService(session=None, secret=SECRET)  # type: ignore[arg-type]
        token = _create_jwt({"sub": "org"}, SECRET, timedelta(seconds=-1))
        with pytest.raises(AuthenticationError):
            service.verify_token(token)

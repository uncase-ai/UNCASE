"""Tests for custom exceptions."""

from __future__ import annotations

from uncase.exceptions import (
    APIKeyRevokedError,
    AuthenticationError,
    AuthorizationError,
    DomainNotFoundError,
    OrganizationNotFoundError,
    PIIDetectedError,
    SeedNotFoundError,
    UNCASEError,
)


class TestExceptionAttributes:
    def test_base_error(self) -> None:
        err = UNCASEError("test")
        assert err.status_code == 500
        assert err.detail == "test"

    def test_default_message(self) -> None:
        err = UNCASEError()
        assert err.detail == "Internal server error"

    def test_auth_error(self) -> None:
        err = AuthenticationError()
        assert err.status_code == 401

    def test_authorization_error(self) -> None:
        err = AuthorizationError()
        assert err.status_code == 403

    def test_not_found_errors(self) -> None:
        assert SeedNotFoundError().status_code == 404
        assert DomainNotFoundError().status_code == 404
        assert OrganizationNotFoundError().status_code == 404

    def test_pii_detected(self) -> None:
        err = PIIDetectedError()
        assert err.status_code == 422

    def test_api_key_revoked(self) -> None:
        err = APIKeyRevokedError()
        assert err.status_code == 401
        assert "revoked" in err.detail.lower()

    def test_inheritance(self) -> None:
        assert isinstance(AuthenticationError(), UNCASEError)
        assert isinstance(APIKeyRevokedError(), AuthenticationError)

"""Tests for OWASP password complexity validation (Fix 17)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from uncase.schemas.user import UserRegisterRequest


class TestPasswordComplexity:
    """Verify that UserRegisterRequest enforces OWASP password rules."""

    def _make_request(self, password: str) -> UserRegisterRequest:
        return UserRegisterRequest(
            email="test@example.com",
            password=password,
            display_name="Test User",
        )

    def test_valid_password(self) -> None:
        req = self._make_request("Str0ng!Pass")
        assert req.password == "Str0ng!Pass"

    def test_missing_uppercase(self) -> None:
        with pytest.raises(ValidationError, match="uppercase"):
            self._make_request("str0ng!pass")

    def test_missing_lowercase(self) -> None:
        with pytest.raises(ValidationError, match="lowercase"):
            self._make_request("STR0NG!PASS")

    def test_missing_digit(self) -> None:
        with pytest.raises(ValidationError, match="digit"):
            self._make_request("Strong!Pass")

    def test_missing_special_char(self) -> None:
        with pytest.raises(ValidationError, match="special"):
            self._make_request("Str0ngPass1")

    def test_too_short(self) -> None:
        with pytest.raises(ValidationError):
            self._make_request("Ab1!")

    def test_too_long(self) -> None:
        with pytest.raises(ValidationError):
            self._make_request("A" * 125 + "b1!x")

    def test_all_special_chars_accepted(self) -> None:
        """Verify various special characters work."""
        for char in "!@#$%^&*()_+-=[]{}|;:',.<>/?`~":
            req = self._make_request(f"Passw0rd{char}")
            assert req.password == f"Passw0rd{char}"

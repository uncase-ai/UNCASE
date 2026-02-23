"""Tests for organization and API key schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from uncase.schemas.organization import APIKeyCreate, OrganizationCreate


class TestOrganizationCreate:
    def test_valid_org(self) -> None:
        org = OrganizationCreate(name="Test Org")
        assert org.name == "Test Org"
        assert org.slug is None

    def test_valid_slug(self) -> None:
        org = OrganizationCreate(name="Test", slug="test-org")
        assert org.slug == "test-org"

    def test_invalid_slug_uppercase(self) -> None:
        with pytest.raises(ValidationError, match="Slug"):
            OrganizationCreate(name="Test", slug="Test-Org")

    def test_invalid_slug_leading_hyphen(self) -> None:
        with pytest.raises(ValidationError, match="Slug"):
            OrganizationCreate(name="Test", slug="-test")

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            OrganizationCreate(name="")


class TestAPIKeyCreate:
    def test_valid_key(self) -> None:
        key = APIKeyCreate(name="My Key", scopes="read,write")
        assert "read" in key.scopes
        assert "write" in key.scopes

    def test_default_scopes(self) -> None:
        key = APIKeyCreate(name="Read Key")
        assert key.scopes == "read"

    def test_admin_scope(self) -> None:
        key = APIKeyCreate(name="Admin", scopes="admin")
        assert key.scopes == "admin"

    def test_invalid_scope(self) -> None:
        with pytest.raises(ValidationError, match="Invalid scopes"):
            APIKeyCreate(name="Bad", scopes="read,delete")

    def test_scopes_sorted(self) -> None:
        key = APIKeyCreate(name="Multi", scopes="write,read")
        assert key.scopes == "read,write"

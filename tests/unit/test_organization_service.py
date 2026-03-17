"""Tests for the organization and API key management service."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from uncase.exceptions import (
    APIKeyNotFoundError,
    APIKeyRevokedError,
    AuthenticationError,
    DuplicateError,
    OrganizationNotFoundError,
)
from uncase.schemas.organization import APIKeyCreate, OrganizationCreate, OrganizationUpdate
from uncase.services.organization import OrganizationService, _slugify
from uncase.utils.security import generate_api_key, hash_api_key

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_org_create(**overrides: object) -> OrganizationCreate:
    """Build a valid OrganizationCreate with fictional defaults."""
    defaults: dict[str, object] = {
        "name": "Acme Synthetic Labs",
        "slug": "acme-synthetic-labs",
        "description": "Fictional organization for testing synthetic data pipelines",
    }
    defaults.update(overrides)
    return OrganizationCreate(**defaults)  # type: ignore[arg-type]


def _make_key_create(**overrides: object) -> APIKeyCreate:
    """Build a valid APIKeyCreate with fictional defaults."""
    defaults: dict[str, object] = {
        "name": "test-key-alpha",
        "scopes": "read,write",
    }
    defaults.update(overrides)
    return APIKeyCreate(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Slugify helper
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_basic(self) -> None:
        assert _slugify("Acme Corp") == "acme-corp"

    def test_special_characters(self) -> None:
        assert _slugify("Hello, World!  ") == "hello-world"

    def test_leading_trailing_hyphens_stripped(self) -> None:
        assert _slugify("---hello---") == "hello"

    def test_empty_string_returns_org(self) -> None:
        assert _slugify("") == "org"

    def test_only_special_chars_returns_org(self) -> None:
        assert _slugify("!!!") == "org"

    def test_numeric(self) -> None:
        assert _slugify("Lab 42") == "lab-42"


# ---------------------------------------------------------------------------
# Organization CRUD
# ---------------------------------------------------------------------------


class TestCreateOrganization:
    async def test_create_basic(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        data = _make_org_create()
        resp = await service.create_organization(data)

        assert resp.id is not None
        assert resp.name == "Acme Synthetic Labs"
        assert resp.slug == "acme-synthetic-labs"
        assert resp.description == "Fictional organization for testing synthetic data pipelines"
        assert resp.is_active is True

    async def test_create_auto_slug(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        data = _make_org_create(slug=None, name="Nova Research Group")
        resp = await service.create_organization(data)

        assert resp.slug == "nova-research-group"

    async def test_create_duplicate_slug_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        data = _make_org_create()
        await service.create_organization(data)

        with pytest.raises(DuplicateError, match="already exists"):
            await service.create_organization(data)

    async def test_create_duplicate_auto_slug_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        await service.create_organization(_make_org_create(slug=None, name="Duplicate Org"))

        with pytest.raises(DuplicateError, match="already exists"):
            await service.create_organization(_make_org_create(slug=None, name="Duplicate Org"))

    async def test_create_without_description(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        data = _make_org_create(description=None, slug="no-desc-org")
        resp = await service.create_organization(data)

        assert resp.description is None

    async def test_create_multiple_distinct_orgs(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        resp1 = await service.create_organization(_make_org_create(slug="org-alpha", name="Alpha"))
        resp2 = await service.create_organization(_make_org_create(slug="org-beta", name="Beta"))

        assert resp1.id != resp2.id
        assert resp1.slug == "org-alpha"
        assert resp2.slug == "org-beta"


class TestGetOrganization:
    async def test_get_existing(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        created = await service.create_organization(_make_org_create())
        found = await service.get_organization(created.id)

        assert found.id == created.id
        assert found.name == created.name

    async def test_get_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        with pytest.raises(OrganizationNotFoundError):
            await service.get_organization("nonexistent-id")


class TestUpdateOrganization:
    async def test_update_name(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        created = await service.create_organization(_make_org_create())
        updated = await service.update_organization(
            created.id,
            OrganizationUpdate(name="Renamed Labs"),
        )

        assert updated.name == "Renamed Labs"
        assert updated.slug == created.slug  # slug unchanged

    async def test_update_description(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        created = await service.create_organization(_make_org_create())
        updated = await service.update_organization(
            created.id,
            OrganizationUpdate(description="Updated description for testing"),
        )

        assert updated.description == "Updated description for testing"

    async def test_update_is_active(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        created = await service.create_organization(_make_org_create())
        updated = await service.update_organization(
            created.id,
            OrganizationUpdate(is_active=False),
        )

        assert updated.is_active is False

    async def test_update_nonexistent_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        with pytest.raises(OrganizationNotFoundError):
            await service.update_organization("nonexistent-id", OrganizationUpdate(name="Nope"))

    async def test_update_no_fields(self, async_session: AsyncSession) -> None:
        """Updating with no fields should still succeed (no-op)."""
        service = OrganizationService(async_session)
        created = await service.create_organization(_make_org_create())
        updated = await service.update_organization(created.id, OrganizationUpdate())

        assert updated.name == created.name

    async def test_update_preserves_other_fields(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        created = await service.create_organization(
            _make_org_create(description="Original description")
        )
        updated = await service.update_organization(
            created.id,
            OrganizationUpdate(name="New Name Only"),
        )

        assert updated.name == "New Name Only"
        assert updated.description == "Original description"


# ---------------------------------------------------------------------------
# API Key CRUD
# ---------------------------------------------------------------------------


class TestCreateAPIKey:
    async def test_create_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        assert key_resp.id is not None
        assert key_resp.key_id is not None
        assert key_resp.plain_key.startswith("uc_test_")
        assert key_resp.name == "test-key-alpha"
        assert key_resp.scopes == "read,write"

    async def test_create_key_live_environment(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create(), environment="live")

        assert key_resp.plain_key.startswith("uc_live_")

    async def test_create_key_read_only_scope(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create(scopes="read"))

        assert key_resp.scopes == "read"

    async def test_create_key_admin_scope(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(
            org.id, _make_key_create(scopes="admin,read,write")
        )

        assert "admin" in key_resp.scopes
        assert "read" in key_resp.scopes
        assert "write" in key_resp.scopes

    async def test_create_key_for_nonexistent_org_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        with pytest.raises(OrganizationNotFoundError):
            await service.create_api_key("nonexistent-org", _make_key_create())

    async def test_create_multiple_keys_for_same_org(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key1 = await service.create_api_key(org.id, _make_key_create(name="key-one"))
        key2 = await service.create_api_key(org.id, _make_key_create(name="key-two"))

        assert key1.key_id != key2.key_id
        assert key1.plain_key != key2.plain_key

    async def test_key_prefix_format(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        # Prefix should be like "uc_test_xxxx..."
        assert key_resp.key_prefix.startswith("uc_test_")
        assert "..." in key_resp.key_prefix


class TestListAPIKeys:
    async def test_list_empty(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        keys = await service.list_api_keys(org.id)

        assert keys == []

    async def test_list_multiple(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        await service.create_api_key(org.id, _make_key_create(name="key-a"))
        await service.create_api_key(org.id, _make_key_create(name="key-b"))

        keys = await service.list_api_keys(org.id)
        assert len(keys) == 2
        # Keys are ordered by created_at desc
        names = [k.name for k in keys]
        assert "key-a" in names
        assert "key-b" in names

    async def test_list_does_not_expose_raw_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        await service.create_api_key(org.id, _make_key_create())

        keys = await service.list_api_keys(org.id)
        assert len(keys) == 1
        # APIKeyResponse should not have plain_key
        assert not hasattr(keys[0], "plain_key") or "plain_key" not in keys[0].model_fields

    async def test_list_for_nonexistent_org_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        with pytest.raises(OrganizationNotFoundError):
            await service.list_api_keys("nonexistent-org")

    async def test_list_keys_scoped_to_org(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org1 = await service.create_organization(_make_org_create(slug="org-one", name="Org One"))
        org2 = await service.create_organization(_make_org_create(slug="org-two", name="Org Two"))
        await service.create_api_key(org1.id, _make_key_create(name="key-org1"))
        await service.create_api_key(org2.id, _make_key_create(name="key-org2"))

        keys1 = await service.list_api_keys(org1.id)
        keys2 = await service.list_api_keys(org2.id)

        assert len(keys1) == 1
        assert keys1[0].name == "key-org1"
        assert len(keys2) == 1
        assert keys2[0].name == "key-org2"


# ---------------------------------------------------------------------------
# API Key Revocation
# ---------------------------------------------------------------------------


class TestRevokeAPIKey:
    async def test_revoke_active_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        await service.revoke_api_key(org.id, key_resp.key_id)

        keys = await service.list_api_keys(org.id)
        assert len(keys) == 1
        assert keys[0].is_active is False

    async def test_revoke_nonexistent_key_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())

        with pytest.raises(APIKeyNotFoundError):
            await service.revoke_api_key(org.id, "nonexistent-key-id")

    async def test_revoke_key_wrong_org_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org1 = await service.create_organization(_make_org_create(slug="org-a", name="Org A"))
        org2 = await service.create_organization(_make_org_create(slug="org-b", name="Org B"))
        key_resp = await service.create_api_key(org1.id, _make_key_create())

        with pytest.raises(APIKeyNotFoundError):
            await service.revoke_api_key(org2.id, key_resp.key_id)

    async def test_revoke_already_revoked_key(self, async_session: AsyncSession) -> None:
        """Revoking an already-revoked key should still succeed (idempotent set to False)."""
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        await service.revoke_api_key(org.id, key_resp.key_id)
        # Second revoke should not raise
        await service.revoke_api_key(org.id, key_resp.key_id)

        keys = await service.list_api_keys(org.id)
        assert keys[0].is_active is False


# ---------------------------------------------------------------------------
# API Key Rotation
# ---------------------------------------------------------------------------


class TestRotateAPIKey:
    async def test_rotate_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        old_key = await service.create_api_key(org.id, _make_key_create())

        new_key = await service.rotate_api_key(org.id, old_key.key_id)

        assert new_key.key_id != old_key.key_id
        assert new_key.plain_key != old_key.plain_key
        assert new_key.name == old_key.name
        assert new_key.scopes == old_key.scopes

    async def test_rotate_revokes_old_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        old_key = await service.create_api_key(org.id, _make_key_create())

        await service.rotate_api_key(org.id, old_key.key_id)

        keys = await service.list_api_keys(org.id)
        assert len(keys) == 2
        old = next(k for k in keys if k.key_id == old_key.key_id)
        assert old.is_active is False

    async def test_rotate_creates_active_new_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        old_key = await service.create_api_key(org.id, _make_key_create())

        new_key = await service.rotate_api_key(org.id, old_key.key_id)

        keys = await service.list_api_keys(org.id)
        new_key_model = next(k for k in keys if k.key_id == new_key.key_id)
        assert new_key_model.is_active is True

    async def test_rotate_nonexistent_key_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())

        with pytest.raises(APIKeyNotFoundError):
            await service.rotate_api_key(org.id, "nonexistent-key-id")

    async def test_rotate_with_live_environment(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        old_key = await service.create_api_key(org.id, _make_key_create())

        new_key = await service.rotate_api_key(org.id, old_key.key_id, environment="live")

        assert new_key.plain_key.startswith("uc_live_")

    async def test_rotate_preserves_scopes(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        old_key = await service.create_api_key(
            org.id, _make_key_create(scopes="admin,read,write")
        )

        new_key = await service.rotate_api_key(org.id, old_key.key_id)

        assert new_key.scopes == old_key.scopes


# ---------------------------------------------------------------------------
# API Key Verification
# ---------------------------------------------------------------------------


class TestVerifyAndGetOrg:
    async def test_verify_valid_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        org_model = await service.verify_and_get_org(key_resp.plain_key)

        assert org_model.id == org.id
        assert org_model.name == org.name

    async def test_verify_stores_last_verified_key(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        await service.verify_and_get_org(key_resp.plain_key)

        assert service.last_verified_key is not None
        assert service.last_verified_key.key_id == key_resp.key_id

    async def test_verify_updates_last_used_at(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        await service.verify_and_get_org(key_resp.plain_key)

        keys = await service.list_api_keys(org.id)
        assert keys[0].last_used_at is not None

    async def test_verify_invalid_format_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)

        with pytest.raises(AuthenticationError, match="Invalid API key format"):
            await service.verify_and_get_org("not-a-valid-key")

    async def test_verify_empty_string_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)

        with pytest.raises(AuthenticationError, match="Invalid API key format"):
            await service.verify_and_get_org("")

    async def test_verify_nonexistent_key_id_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        # Craft a key with valid format but key_id not in DB
        fake_key = "uc_test_aaaaaaaaaaaaaaaa-somesecretvalue1234567890abcdefgh"

        with pytest.raises(AuthenticationError, match="API key not found"):
            await service.verify_and_get_org(fake_key)

    async def test_verify_revoked_key_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        await service.revoke_api_key(org.id, key_resp.key_id)

        with pytest.raises(APIKeyRevokedError):
            await service.verify_and_get_org(key_resp.plain_key)

    async def test_verify_wrong_secret_raises(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        key_resp = await service.create_api_key(org.id, _make_key_create())

        # Tamper with the secret portion of the key
        parts = key_resp.plain_key.rsplit("-", 1)
        tampered_key = parts[0] + "-" + "x" * len(parts[1])

        with pytest.raises(AuthenticationError, match="Invalid API key"):
            await service.verify_and_get_org(tampered_key)

    async def test_verify_rotated_old_key_raises(self, async_session: AsyncSession) -> None:
        """After rotation, the old key should be revoked and fail verification."""
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        old_key_resp = await service.create_api_key(org.id, _make_key_create())
        old_plain_key = old_key_resp.plain_key

        await service.rotate_api_key(org.id, old_key_resp.key_id)

        with pytest.raises(APIKeyRevokedError):
            await service.verify_and_get_org(old_plain_key)

    async def test_verify_rotated_new_key_works(self, async_session: AsyncSession) -> None:
        """After rotation, the new key should work."""
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())
        old_key_resp = await service.create_api_key(org.id, _make_key_create())

        new_key_resp = await service.rotate_api_key(org.id, old_key_resp.key_id)

        org_model = await service.verify_and_get_org(new_key_resp.plain_key)
        assert org_model.id == org.id


# ---------------------------------------------------------------------------
# Schema validation (edge cases)
# ---------------------------------------------------------------------------


class TestAPIKeyCreateSchema:
    def test_valid_scopes_sorted(self) -> None:
        data = APIKeyCreate(name="test", scopes="write,read")
        assert data.scopes == "read,write"

    def test_invalid_scope_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid scopes"):
            APIKeyCreate(name="test", scopes="delete")

    def test_mixed_valid_invalid_scope_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid scopes"):
            APIKeyCreate(name="test", scopes="read,execute")

    def test_default_scope_is_read(self) -> None:
        data = APIKeyCreate(name="test")
        assert data.scopes == "read"

    def test_all_scopes(self) -> None:
        data = APIKeyCreate(name="test", scopes="admin,read,write")
        assert data.scopes == "admin,read,write"


class TestOrganizationCreateSchema:
    def test_slug_validation_rejects_uppercase(self) -> None:
        with pytest.raises(ValueError, match="lowercase"):
            OrganizationCreate(name="Test", slug="BadSlug")

    def test_slug_validation_rejects_leading_hyphen(self) -> None:
        with pytest.raises(ValueError, match="lowercase"):
            OrganizationCreate(name="Test", slug="-bad-slug")

    def test_slug_validation_rejects_trailing_hyphen(self) -> None:
        with pytest.raises(ValueError, match="lowercase"):
            OrganizationCreate(name="Test", slug="bad-slug-")

    def test_slug_validation_accepts_valid(self) -> None:
        data = OrganizationCreate(name="Test", slug="valid-slug-123")
        assert data.slug == "valid-slug-123"

    def test_slug_none_is_accepted(self) -> None:
        data = OrganizationCreate(name="Test", slug=None)
        assert data.slug is None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


class TestGetOrgOrRaise:
    async def test_raises_with_message(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        with pytest.raises(OrganizationNotFoundError, match="fake-id"):
            await service._get_org_or_raise("fake-id")


class TestGetKeyOrRaise:
    async def test_raises_with_message(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org = await service.create_organization(_make_org_create())

        with pytest.raises(APIKeyNotFoundError, match="fake-key-id"):
            await service._get_key_or_raise(org.id, "fake-key-id")

    async def test_raises_for_key_in_wrong_org(self, async_session: AsyncSession) -> None:
        service = OrganizationService(async_session)
        org1 = await service.create_organization(_make_org_create(slug="org-x", name="Org X"))
        org2 = await service.create_organization(_make_org_create(slug="org-y", name="Org Y"))
        key_resp = await service.create_api_key(org1.id, _make_key_create())

        with pytest.raises(APIKeyNotFoundError):
            await service._get_key_or_raise(org2.id, key_resp.key_id)

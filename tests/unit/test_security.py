"""Tests for API key generation and verification."""

from __future__ import annotations

from uncase.utils.security import generate_api_key, parse_api_key, verify_api_key


class TestKeyGeneration:
    def test_generate_test_key(self) -> None:
        full_key, key_id, key_hash = generate_api_key("uc_test")
        assert full_key.startswith("uc_test_")
        assert len(key_id) == 16
        assert key_hash.startswith("$argon2")

    def test_generate_live_key(self) -> None:
        full_key, _key_id, _key_hash = generate_api_key("uc_live")
        assert full_key.startswith("uc_live_")

    def test_keys_are_unique(self) -> None:
        key1, _, _ = generate_api_key()
        key2, _, _ = generate_api_key()
        assert key1 != key2

    def test_key_format_contains_hyphen(self) -> None:
        full_key, _, _ = generate_api_key("uc_test")
        # Format: uc_test_{key_id}-{secret}
        assert "-" in full_key


class TestKeyVerification:
    def test_verify_correct_key(self) -> None:
        full_key, _, key_hash = generate_api_key()
        assert verify_api_key(full_key, key_hash) is True

    def test_verify_wrong_key(self) -> None:
        _, _, key_hash = generate_api_key()
        assert verify_api_key("wrong_key", key_hash) is False

    def test_verify_different_keys(self) -> None:
        _key1, _, hash1 = generate_api_key()
        key2, _, _ = generate_api_key()
        assert verify_api_key(key2, hash1) is False


class TestKeyParsing:
    def test_parse_valid_test_key(self) -> None:
        full_key, key_id, _ = generate_api_key("uc_test")
        result = parse_api_key(full_key)
        assert result is not None
        parsed_id, _ = result
        assert parsed_id == key_id

    def test_parse_valid_live_key(self) -> None:
        full_key, _, _ = generate_api_key("uc_live")
        result = parse_api_key(full_key)
        assert result is not None

    def test_parse_invalid_format(self) -> None:
        assert parse_api_key("no_hyphen_at_all") is None

    def test_parse_wrong_prefix(self) -> None:
        assert parse_api_key("sk_test_abc-secret") is None

    def test_parse_empty_string(self) -> None:
        assert parse_api_key("") is None

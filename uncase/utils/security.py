"""API key generation and verification utilities.

Key format follows industry standards (Stripe/OpenAI pattern):
    uc_test_{key_id}-{secret}   (development)
    uc_live_{key_id}-{secret}   (production)
"""

from __future__ import annotations

import secrets
import uuid

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
)


def generate_api_key(prefix: str = "uc_test") -> tuple[str, str, str]:
    """Generate a new API key with its ID and hash.

    Args:
        prefix: Key prefix, either 'uc_test' or 'uc_live'.

    Returns:
        Tuple of (full_key, key_id, key_hash).
        full_key is returned once and never stored.
        key_hash is stored for verification.
    """
    key_id = uuid.uuid4().hex[:16]
    secret = secrets.token_urlsafe(32)
    full_key = f"{prefix}_{key_id}-{secret}"
    key_hash = hash_api_key(full_key)
    return full_key, key_id, key_hash


def hash_api_key(key: str) -> str:
    """Hash an API key using argon2id.

    Args:
        key: The full API key to hash.

    Returns:
        Argon2id hash string.
    """
    return _hasher.hash(key)


def verify_api_key(key: str, key_hash: str) -> bool:
    """Verify an API key against its stored hash.

    Args:
        key: The full API key to verify.
        key_hash: The stored argon2id hash.

    Returns:
        True if the key matches the hash.
    """
    try:
        return _hasher.verify(key_hash, key)
    except VerifyMismatchError:
        return False


def parse_api_key(key: str) -> tuple[str, str] | None:
    """Parse an API key into its key_id and secret parts.

    Args:
        key: The full API key (e.g. 'uc_test_abc123def456xxxx-secret').

    Returns:
        Tuple of (key_id, secret) or None if format is invalid.
        key_id is the 16-char hex identifier after the prefix.
    """
    # Expected format: uc_{env}_{key_id}-{secret}
    # Split into at most 3 parts on underscore: ['uc', 'test', '{key_id}-{secret}']
    segments = key.split("_", 2)
    if len(segments) != 3 or segments[0] != "uc" or segments[1] not in ("test", "live"):
        return None

    remainder = segments[2]  # '{key_id}-{secret}'
    # key_id is exactly 16 hex chars, followed by '-', then secret
    if len(remainder) < 18 or remainder[16] != "-":
        return None

    key_id = remainder[:16]
    secret = remainder[17:]
    if not secret:
        return None

    return key_id, secret

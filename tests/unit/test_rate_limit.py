"""Tests for the rate limiting middleware."""

from __future__ import annotations

from uncase.api.rate_limit import (
    EXEMPT_PATHS,
    RATE_LIMITS,
    _SlidingWindowCounter,
)


class TestSlidingWindowCounter:
    """Test the in-memory sliding window rate limiter."""

    def test_allows_first_request(self) -> None:
        counter = _SlidingWindowCounter()
        allowed, remaining, _reset = counter.is_allowed("key1", 10, 60)
        assert allowed is True
        assert remaining == 9

    def test_allows_up_to_limit(self) -> None:
        counter = _SlidingWindowCounter()
        for i in range(10):
            allowed, remaining, _ = counter.is_allowed("key1", 10, 60)
            assert allowed is True
            expected = 10 - i - 1  # After adding entry: limit - current_count
            assert remaining == expected

    def test_blocks_after_limit(self) -> None:
        counter = _SlidingWindowCounter()
        for _ in range(10):
            counter.is_allowed("key1", 10, 60)
        allowed, remaining, reset = counter.is_allowed("key1", 10, 60)
        assert allowed is False
        assert remaining == 0
        assert reset > 0

    def test_separate_keys(self) -> None:
        counter = _SlidingWindowCounter()
        for _ in range(5):
            counter.is_allowed("key1", 5, 60)
        # key1 is exhausted
        allowed1, _, _ = counter.is_allowed("key1", 5, 60)
        assert allowed1 is False
        # key2 is fresh
        allowed2, remaining2, _ = counter.is_allowed("key2", 5, 60)
        assert allowed2 is True
        assert remaining2 == 4

    def test_remaining_decreases(self) -> None:
        counter = _SlidingWindowCounter()
        _, r1, _ = counter.is_allowed("k", 5, 60)
        _, r2, _ = counter.is_allowed("k", 5, 60)
        _, r3, _ = counter.is_allowed("k", 5, 60)
        assert r1 == 4
        assert r2 == 3
        assert r3 == 2


class TestRateLimitConfig:
    """Test rate limit configuration."""

    def test_tiers_defined(self) -> None:
        assert "free" in RATE_LIMITS
        assert "developer" in RATE_LIMITS
        assert "enterprise" in RATE_LIMITS
        assert "default" in RATE_LIMITS

    def test_tier_ordering(self) -> None:
        free_limit, _ = RATE_LIMITS["free"]
        dev_limit, _ = RATE_LIMITS["developer"]
        enterprise_limit, _ = RATE_LIMITS["enterprise"]
        assert free_limit < dev_limit < enterprise_limit

    def test_window_is_60_seconds(self) -> None:
        for _tier, (_, window) in RATE_LIMITS.items():
            assert window == 60

    def test_exempt_paths(self) -> None:
        assert "/docs" in EXEMPT_PATHS
        assert "/redoc" in EXEMPT_PATHS
        assert "/openapi.json" in EXEMPT_PATHS
        assert "/api/v1/health" in EXEMPT_PATHS

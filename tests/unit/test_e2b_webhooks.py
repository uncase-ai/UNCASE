"""Tests for inbound E2B webhook receiver endpoints."""

from __future__ import annotations

import hashlib
import hmac

from uncase.api.routers.e2b_webhooks import (
    _event_log,
    _record_event,
    _verify_signature,
)
from uncase.schemas.e2b_webhook import E2BEventType

# ── Signature verification ───────────────────────────────────────


class TestVerifySignature:
    def test_no_secret_configured_always_passes(self) -> None:
        assert _verify_signature(b"anything", "", None) is True
        assert _verify_signature(b"anything", "", "some-header") is True

    def test_secret_but_no_header_fails(self) -> None:
        assert _verify_signature(b"body", "my-secret", None) is False

    def test_valid_signature_passes(self) -> None:
        body = b'{"sandbox_id":"abc123"}'
        hmac_key = "test-secret-e2b"
        digest = hmac.new(hmac_key.encode(), body, hashlib.sha256).hexdigest()

        assert _verify_signature(body, hmac_key, f"sha256={digest}") is True

    def test_valid_signature_raw_hex_passes(self) -> None:
        body = b'{"sandbox_id":"abc123"}'
        hmac_key = "test-secret-e2b"
        digest = hmac.new(hmac_key.encode(), body, hashlib.sha256).hexdigest()

        assert _verify_signature(body, hmac_key, digest) is True

    def test_invalid_signature_fails(self) -> None:
        body = b'{"sandbox_id":"abc123"}'
        assert _verify_signature(body, "real-secret", "sha256=0000deadbeef") is False

    def test_tampered_body_fails(self) -> None:
        hmac_key = "test-secret-e2b"
        original = b'{"sandbox_id":"abc123"}'
        tampered = b'{"sandbox_id":"hacked"}'
        digest = hmac.new(hmac_key.encode(), original, hashlib.sha256).hexdigest()

        assert _verify_signature(tampered, hmac_key, f"sha256={digest}") is False


# ── Event recording (in-memory ring buffer) ──────────────────────


class TestRecordEvent:
    def setup_method(self) -> None:
        _event_log.clear()

    def test_record_event_returns_id(self) -> None:
        event_id = _record_event(
            E2BEventType.SANDBOX_STARTED,
            "sbx-001",
            domain="automotive.sales",
        )
        assert isinstance(event_id, str)
        assert len(event_id) == 32  # uuid hex

    def test_record_event_appends_to_log(self) -> None:
        _record_event(E2BEventType.SANDBOX_STARTED, "sbx-001")
        _record_event(E2BEventType.SANDBOX_COMPLETED, "sbx-002")

        assert len(_event_log) == 2
        assert _event_log[0].event_type == E2BEventType.SANDBOX_STARTED
        assert _event_log[1].event_type == E2BEventType.SANDBOX_COMPLETED

    def test_record_event_stores_metadata(self) -> None:
        _record_event(
            E2BEventType.SANDBOX_STARTED,
            "sbx-001",
            domain="medical.consultation",
            organization_id="org-abc",
            payload={"ttl_minutes": 30},
        )

        record = _event_log[0]
        assert record.sandbox_id == "sbx-001"
        assert record.domain == "medical.consultation"
        assert record.organization_id == "org-abc"
        assert record.payload == {"ttl_minutes": 30}

    def test_ring_buffer_evicts_oldest(self) -> None:
        from uncase.api.routers.e2b_webhooks import _MAX_EVENT_HISTORY

        for i in range(_MAX_EVENT_HISTORY + 10):
            _record_event(E2BEventType.SANDBOX_STARTED, f"sbx-{i:04d}")

        assert len(_event_log) == _MAX_EVENT_HISTORY
        # Oldest should have been evicted — first entry is sbx-0010
        assert _event_log[0].sandbox_id == "sbx-0010"


# ── Schema validation ────────────────────────────────────────────


class TestE2BSchemas:
    def test_start_payload_minimal(self) -> None:
        from uncase.schemas.e2b_webhook import E2BStartPayload

        payload = E2BStartPayload(sandbox_id="sbx-001")
        assert payload.sandbox_id == "sbx-001"
        assert payload.preloaded_seeds == 0
        assert payload.language == "es"
        assert payload.metadata == {}

    def test_start_payload_full(self) -> None:
        from uncase.schemas.e2b_webhook import E2BStartPayload

        payload = E2BStartPayload(
            sandbox_id="sbx-002",
            template_id="demo_automotive",
            domain="automotive.sales",
            organization_id="org-xyz",
            sandbox_url="https://sbx-002.e2b.dev",
            api_url="https://sbx-002.e2b.dev:8000",
            ttl_minutes=30,
            preloaded_seeds=3,
            language="en",
            metadata={"region": "us-west"},
        )
        assert payload.domain == "automotive.sales"
        assert payload.ttl_minutes == 30
        assert payload.preloaded_seeds == 3

    def test_complete_payload(self) -> None:
        from uncase.schemas.e2b_webhook import E2BCompletePayload

        payload = E2BCompletePayload(
            sandbox_id="sbx-003",
            conversations_generated=5,
            duration_seconds=120.5,
        )
        assert payload.conversations_generated == 5
        assert payload.duration_seconds == 120.5

    def test_error_payload(self) -> None:
        from uncase.schemas.e2b_webhook import E2BErrorPayload

        payload = E2BErrorPayload(
            sandbox_id="sbx-004",
            error="Out of memory",
            error_code="OOM",
        )
        assert payload.error == "Out of memory"
        assert payload.error_code == "OOM"

    def test_generic_payload_event_types(self) -> None:
        from uncase.schemas.e2b_webhook import E2BWebhookPayload

        for evt in E2BEventType:
            payload = E2BWebhookPayload(sandbox_id="sbx-test", event_type=evt)
            assert payload.event_type == evt

    def test_webhook_response(self) -> None:
        from uncase.schemas.e2b_webhook import E2BWebhookResponse

        resp = E2BWebhookResponse(
            event_id="abc123",
            event_type="sandbox.started",
        )
        assert resp.received is True
        assert resp.event_id == "abc123"

    def test_event_record(self) -> None:
        from uncase.schemas.e2b_webhook import E2BWebhookEventRecord

        record = E2BWebhookEventRecord(
            event_id="evt-001",
            event_type=E2BEventType.SANDBOX_ERROR,
            sandbox_id="sbx-fail",
            domain="legal.advisory",
        )
        assert record.event_type == E2BEventType.SANDBOX_ERROR
        assert record.received_at is not None


# ── Webhook event types list ─────────────────────────────────────


class TestWebhookEventTypes:
    def test_sandbox_events_in_outbound_list(self) -> None:
        from uncase.schemas.webhook import WEBHOOK_EVENTS

        assert "sandbox_started" in WEBHOOK_EVENTS
        assert "sandbox_completed" in WEBHOOK_EVENTS
        assert "sandbox_error" in WEBHOOK_EVENTS
        assert "sandbox_expired" in WEBHOOK_EVENTS

    def test_e2b_event_type_enum_values(self) -> None:
        assert E2BEventType.SANDBOX_STARTED == "sandbox.started"
        assert E2BEventType.SANDBOX_COMPLETED == "sandbox.completed"
        assert E2BEventType.SANDBOX_ERROR == "sandbox.error"
        assert E2BEventType.SANDBOX_EXPIRED == "sandbox.expired"

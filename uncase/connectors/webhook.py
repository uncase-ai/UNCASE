"""Webhook connector — receive conversation data from external systems."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from uncase.connectors.base import BaseConnector, ConnectorResult
from uncase.core.privacy.scanner import PIIScanner
from uncase.logging import get_logger
from uncase.schemas.conversation import Conversation, ConversationTurn

logger = get_logger(__name__)


class WebhookConnector(BaseConnector):
    """Accept conversation data from external systems via JSON payload.

    Expected JSON format:
    {
        "conversations": [
            {
                "turns": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"}
                ],
                "domain": "automotive.sales",
                "language": "es",
                "metadata": {}
            }
        ]
    }

    All text content is scanned for PII and anonymized before storage.
    """

    def __init__(self, *, pii_confidence: float = 0.85) -> None:
        self._scanner = PIIScanner(confidence_threshold=pii_confidence)

    def connector_name(self) -> str:
        return "Webhook"

    def supported_formats(self) -> list[str]:
        return ["json", "application/json"]

    async def ingest(self, raw_input: str | bytes, **kwargs: object) -> ConnectorResult:
        """Parse webhook JSON payload into anonymized conversations."""
        import json

        text = raw_input if isinstance(raw_input, str) else raw_input.decode("utf-8")

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            return ConnectorResult(errors=[f"Invalid JSON: {exc}"])

        if not isinstance(payload, dict) or "conversations" not in payload:
            return ConnectorResult(errors=["Payload must contain a 'conversations' array"])

        raw_conversations = payload["conversations"]
        if not isinstance(raw_conversations, list):
            return ConnectorResult(errors=["'conversations' must be an array"])

        conversations: list[Conversation] = []
        errors: list[str] = []
        total_pii = 0

        for i, raw_conv in enumerate(raw_conversations):
            if not isinstance(raw_conv, dict) or "turns" not in raw_conv:
                errors.append(f"Conversation {i}: missing 'turns' array")
                continue

            raw_turns = raw_conv["turns"]
            if not isinstance(raw_turns, list) or len(raw_turns) < 1:
                errors.append(f"Conversation {i}: 'turns' must be a non-empty array")
                continue

            turns: list[ConversationTurn] = []
            for j, raw_turn in enumerate(raw_turns):
                role = raw_turn.get("role", f"speaker_{j % 2}")
                content = raw_turn.get("content", "")

                # Anonymize content
                scan = self._scanner.scan_and_anonymize(str(content))
                total_pii += scan.entity_count

                # Convert turn metadata values to strings
                raw_meta = raw_turn.get("metadata", {})
                turn_meta: dict[str, str] = {str(k): str(v) for k, v in raw_meta.items()} if raw_meta else {}

                turns.append(
                    ConversationTurn(
                        turno=j + 1,
                        rol=str(role),
                        contenido=scan.anonymized_text,
                        herramientas_usadas=[],
                        metadata=turn_meta,
                    )
                )

            domain = raw_conv.get("domain", "")
            language = raw_conv.get("language", "es")

            # Build conversation-level metadata with all string values
            conv_meta: dict[str, str] = {
                "source": "webhook",
                "connector": self.connector_name(),
                "pii_entities_anonymized": str(total_pii),
            }
            raw_conv_meta = raw_conv.get("metadata", {})
            if isinstance(raw_conv_meta, dict):
                for k, v in raw_conv_meta.items():
                    conv_meta[str(k)] = str(v)

            conv = Conversation(
                conversation_id=uuid.uuid4().hex,
                seed_id=raw_conv.get("seed_id", ""),
                dominio=str(domain),
                idioma=str(language),
                turnos=turns,
                es_sintetica=False,
                created_at=datetime.now(UTC),
                metadata=conv_meta,
            )
            conversations.append(conv)

        logger.info(
            "webhook_import_complete",
            conversations_created=len(conversations),
            errors=len(errors),
            pii_entities_anonymized=total_pii,
        )

        return ConnectorResult(
            conversations=conversations,
            total_imported=len(conversations),
            total_pii_anonymized=total_pii,
            errors=errors,
        )

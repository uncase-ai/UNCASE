"""WhatsApp export connector — parse WhatsApp chat exports into conversations."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from uncase.connectors.base import BaseConnector, ConnectorResult
from uncase.core.privacy.scanner import PIIScanner
from uncase.logging import get_logger
from uncase.schemas.conversation import Conversation, ConversationTurn

logger = get_logger(__name__)

# WhatsApp export line patterns:
# [DD/MM/YYYY, HH:MM:SS] Name: Message
# DD/MM/YYYY, HH:MM - Name: Message
# M/D/YY, H:MM AM/PM - Name: Message
_WA_PATTERNS = [
    # Pattern 1: [DD/MM/YYYY, HH:MM:SS] Name: Message
    re.compile(r"\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^:]+):\s*(.*)"),
    # Pattern 2: DD/MM/YYYY, HH:MM - Name: Message
    re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*-\s*([^:]+):\s*(.*)"),
]

# System message patterns to skip
_SYSTEM_PATTERNS = [
    re.compile(r"Messages and calls are end-to-end encrypted", re.IGNORECASE),
    re.compile(r"created group", re.IGNORECASE),
    re.compile(r"added you", re.IGNORECASE),
    re.compile(r"changed the subject", re.IGNORECASE),
    re.compile(r"changed this group", re.IGNORECASE),
    re.compile(r"left$", re.IGNORECASE),
    re.compile(r"<Media omitted>", re.IGNORECASE),
    re.compile(r"image omitted", re.IGNORECASE),
    re.compile(r"video omitted", re.IGNORECASE),
    re.compile(r"audio omitted", re.IGNORECASE),
    re.compile(r"sticker omitted", re.IGNORECASE),
    re.compile(r"document omitted", re.IGNORECASE),
    re.compile(r"GIF omitted", re.IGNORECASE),
    re.compile(r"Contact card omitted", re.IGNORECASE),
]


def _is_system_message(text: str) -> bool:
    """Check if a message is a WhatsApp system message."""
    return any(pattern.search(text) for pattern in _SYSTEM_PATTERNS)


def _parse_wa_line(line: str) -> tuple[str, str, str, str] | None:
    """Try to parse a WhatsApp export line.

    Returns (date_str, time_str, sender, message) or None.
    """
    for pattern in _WA_PATTERNS:
        match = pattern.match(line)
        if match:
            return match.group(1), match.group(2), match.group(3).strip(), match.group(4)
    return None


class WhatsAppConnector(BaseConnector):
    """Parse WhatsApp chat export files into Conversation objects.

    Handles multiple WhatsApp export formats (iOS/Android).
    Multi-line messages are concatenated with the previous message.
    System messages are automatically skipped.
    PII is scanned and anonymized before conversations are returned.

    Usage:
        connector = WhatsAppConnector()
        result = await connector.ingest(file_content)
        # result.conversations contains privacy-compliant conversations
    """

    def __init__(
        self,
        *,
        pii_confidence: float = 0.85,
        max_conversations: int = 100,
        min_turns: int = 3,
    ) -> None:
        self._scanner = PIIScanner(confidence_threshold=pii_confidence)
        self._max_conversations = max_conversations
        self._min_turns = min_turns

    def connector_name(self) -> str:
        return "WhatsApp Export"

    def supported_formats(self) -> list[str]:
        return ["txt", "text/plain"]

    async def ingest(self, raw_input: str | bytes, **kwargs: object) -> ConnectorResult:
        """Parse a WhatsApp export and return anonymized conversations."""
        text = raw_input if isinstance(raw_input, str) else raw_input.decode("utf-8", errors="replace")
        lines = text.splitlines()

        # Phase 1: Parse all messages
        messages: list[dict[str, str]] = []
        for line in lines:
            parsed = _parse_wa_line(line)
            if parsed:
                date_str, time_str, sender, message = parsed
                if not _is_system_message(message):
                    messages.append(
                        {
                            "date": date_str,
                            "time": time_str,
                            "sender": sender,
                            "message": message,
                        }
                    )
            elif messages and line.strip():
                # Continuation of previous message
                messages[-1]["message"] += f"\n{line.strip()}"

        if not messages:
            return ConnectorResult(errors=["No valid WhatsApp messages found in input"])

        # Phase 2: Group into conversations by message count
        # (every 20 messages = new conversation)
        conversation_groups: list[list[dict[str, str]]] = []
        current_group: list[dict[str, str]] = [messages[0]]

        for msg in messages[1:]:
            current_group.append(msg)
            if len(current_group) >= 20:
                conversation_groups.append(current_group)
                current_group = []

        if current_group:
            conversation_groups.append(current_group)

        # Phase 3: Convert to Conversation objects with PII anonymization
        conversations: list[Conversation] = []
        total_pii = 0
        skipped = 0

        for group in conversation_groups[: self._max_conversations]:
            if len(group) < self._min_turns:
                skipped += 1
                continue

            # Get unique senders
            senders = list(dict.fromkeys(msg["sender"] for msg in group))

            turns: list[ConversationTurn] = []
            for i, msg in enumerate(group):
                # Scan and anonymize message content
                scan_result = self._scanner.scan_and_anonymize(msg["message"])
                total_pii += scan_result.entity_count

                # Anonymize sender names too
                sender_scan = self._scanner.scan_and_anonymize(msg["sender"])
                total_pii += sender_scan.entity_count

                turns.append(
                    ConversationTurn(
                        turno=i + 1,
                        rol=sender_scan.anonymized_text,
                        contenido=scan_result.anonymized_text,
                        herramientas_usadas=[],
                        metadata={"original_date": msg["date"], "original_time": msg["time"]},
                    )
                )

            # Anonymize role names in the roles list
            anonymized_senders = []
            for sender in senders:
                sender_scan = self._scanner.scan_and_anonymize(sender)
                anonymized_senders.append(sender_scan.anonymized_text)

            conv = Conversation(
                conversation_id=uuid.uuid4().hex,
                seed_id="",
                dominio="",
                idioma="es",
                turnos=turns,
                es_sintetica=False,
                created_at=datetime.now(UTC),
                metadata={
                    "source": "whatsapp",
                    "connector": self.connector_name(),
                    "original_message_count": str(len(group)),
                    "roles": ",".join(anonymized_senders),
                    "pii_entities_anonymized": str(total_pii),
                },
            )
            conversations.append(conv)

        logger.info(
            "whatsapp_import_complete",
            total_messages=len(messages),
            conversations_created=len(conversations),
            conversations_skipped=skipped,
            pii_entities_anonymized=total_pii,
        )

        return ConnectorResult(
            conversations=conversations,
            total_imported=len(conversations),
            total_skipped=skipped,
            total_pii_anonymized=total_pii,
        )

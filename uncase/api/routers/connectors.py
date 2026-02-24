"""Connector API endpoints — import data from external sources."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db
from uncase.connectors.webhook import WebhookConnector
from uncase.connectors.whatsapp import WhatsAppConnector
from uncase.core.privacy.scanner import PIIScanner
from uncase.schemas.connector import ConnectorImportResponse, PIIEntityResponse, PIIScanResponse, WebhookPayload

router = APIRouter(prefix="/api/v1/connectors", tags=["connectors"])

logger = structlog.get_logger(__name__)


@router.post("/whatsapp", response_model=ConnectorImportResponse)
async def import_whatsapp(
    file: Annotated[UploadFile, File(description="WhatsApp chat export (.txt)")],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ConnectorImportResponse:
    """Import conversations from a WhatsApp chat export file.

    Accepts a .txt file exported from WhatsApp. The connector automatically:
    - Detects message format (iOS/Android variants)
    - Skips system messages (group changes, media omitted, etc.)
    - Groups messages into conversations
    - Scans ALL text for PII (email, phone, SSN, etc.)
    - Anonymizes detected PII with placeholder tokens
    """
    content = await file.read()
    connector = WhatsAppConnector()
    result = await connector.ingest(content)

    logger.info(
        "whatsapp_import_api",
        filename=file.filename,
        conversations=result.total_imported,
        pii_anonymized=result.total_pii_anonymized,
    )

    return ConnectorImportResponse(
        conversations=result.conversations,
        total_imported=result.total_imported,
        total_skipped=result.total_skipped,
        total_pii_anonymized=result.total_pii_anonymized,
        errors=result.errors,
        warnings=result.warnings,
    )


@router.post("/webhook", response_model=ConnectorImportResponse)
async def receive_webhook(
    payload: WebhookPayload,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ConnectorImportResponse:
    """Receive conversation data from external systems.

    Accepts a JSON payload with a 'conversations' array. Each conversation
    must have a 'turns' array with 'role' and 'content' fields.
    All text is scanned for PII and anonymized before storage.
    """
    import json

    connector = WebhookConnector()
    result = await connector.ingest(json.dumps(payload.model_dump()))

    logger.info(
        "webhook_import_api",
        conversations=result.total_imported,
        pii_anonymized=result.total_pii_anonymized,
    )

    return ConnectorImportResponse(
        conversations=result.conversations,
        total_imported=result.total_imported,
        total_skipped=result.total_skipped,
        total_pii_anonymized=result.total_pii_anonymized,
        errors=result.errors,
        warnings=result.warnings,
    )


@router.post("/scan-pii", response_model=PIIScanResponse)
async def scan_text_for_pii(
    text: str,
) -> PIIScanResponse:
    """Scan a text for PII without importing.

    Useful for previewing what PII would be detected and anonymized
    before running a full import.
    """
    scanner = PIIScanner()
    result = scanner.scan_and_anonymize(text)

    return PIIScanResponse(
        text_length=len(text),
        pii_found=result.pii_found,
        entity_count=result.entity_count,
        entities=[
            PIIEntityResponse(
                category=e.category,
                start=e.start,
                end=e.end,
                score=e.score,
                source=e.source,
            )
            for e in result.entities
        ],
        anonymized_preview=result.anonymized_text,
        scanner_mode="regex+presidio" if scanner.has_presidio else "regex_only",
    )


@router.get("")
async def list_connectors() -> list[dict[str, object]]:
    """List all available data connectors."""
    return [
        {
            "name": "WhatsApp Export",
            "slug": "whatsapp",
            "description": "Import conversations from WhatsApp chat export files (.txt)",
            "supported_formats": ["txt"],
            "endpoint": "/api/v1/connectors/whatsapp",
            "method": "POST",
            "accepts": "file upload",
        },
        {
            "name": "Webhook",
            "slug": "webhook",
            "description": "Receive conversation data from external systems via JSON",
            "supported_formats": ["json"],
            "endpoint": "/api/v1/connectors/webhook",
            "method": "POST",
            "accepts": "JSON body",
        },
        {
            "name": "PII Scanner",
            "slug": "scan-pii",
            "description": "Scan text for PII without importing",
            "supported_formats": ["text"],
            "endpoint": "/api/v1/connectors/scan-pii",
            "method": "POST",
            "accepts": "text body",
        },
    ]

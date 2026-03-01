"""Connector API endpoints — import data from external sources."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, File, Header, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db
from uncase.connectors.huggingface import HuggingFaceConnector
from uncase.connectors.webhook import WebhookConnector
from uncase.connectors.whatsapp import WhatsAppConnector
from uncase.core.privacy.scanner import PIIScanner
from uncase.schemas.connector import (
    ConnectorImportResponse,
    HFDatasetInfoResponse,
    HFUploadRequest,
    HFUploadResponse,
    PIIEntityResponse,
    PIIScanResponse,
    WebhookPayload,
)

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


@router.get("/huggingface/search", response_model=list[HFDatasetInfoResponse])
async def search_hf_datasets(
    query: Annotated[str, Query(description="Search query for datasets")],
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 20,
) -> list[HFDatasetInfoResponse]:
    """Search Hugging Face Hub for datasets.

    Returns dataset metadata sorted by download count.
    No authentication required for public datasets.
    """
    connector = HuggingFaceConnector()
    results = await connector.search_datasets(query=query, limit=limit)

    logger.info("hf_search_api", query=query, results=len(results))

    return [
        HFDatasetInfoResponse(
            repo_id=ds.repo_id,
            description=ds.description,
            downloads=ds.downloads,
            likes=ds.likes,
            tags=ds.tags,
            last_modified=ds.last_modified,
            size_bytes=ds.size_bytes,
        )
        for ds in results
    ]


@router.post("/huggingface/import", response_model=ConnectorImportResponse)
async def import_hf_dataset(
    repo_id: Annotated[str, Query(description="HuggingFace dataset repo (user/dataset)")],
    split: Annotated[str, Query(description="Dataset split to import")] = "train",
    token: Annotated[str | None, Header(alias="X-HF-Token", description="HuggingFace API token")] = None,
) -> ConnectorImportResponse:
    """Import a dataset from Hugging Face Hub.

    Downloads the specified split, parses rows with 'messages' format,
    and converts them to UNCASE conversations.
    """
    connector = HuggingFaceConnector(token=token)
    result = await connector.download_dataset(repo_id=repo_id, split=split, token=token)

    logger.info(
        "hf_import_api",
        repo_id=repo_id,
        split=split,
        imported=result.total_imported,
        skipped=result.total_skipped,
    )

    return ConnectorImportResponse(
        conversations=result.conversations,
        total_imported=result.total_imported,
        total_skipped=result.total_skipped,
        total_pii_anonymized=result.total_pii_anonymized,
        errors=result.errors,
        warnings=result.warnings,
    )


@router.post("/huggingface/upload", response_model=HFUploadResponse)
async def upload_to_hf(
    request: HFUploadRequest,
) -> HFUploadResponse:
    """Upload conversations to Hugging Face as a JSONL dataset.

    Creates or updates a HuggingFace dataset repository with the
    selected conversations in chat format.
    """
    # For now, use conversation_ids as placeholder data
    # In production, this would fetch conversations from the DB
    conversations: list[dict[str, object]] = [{"conversation_id": cid} for cid in request.conversation_ids]

    connector = HuggingFaceConnector(token=request.token)
    result = await connector.upload_dataset(
        conversations=conversations,
        repo_id=request.repo_id,
        token=request.token,
        private=request.private,
    )

    logger.info(
        "hf_upload_api",
        repo_id=request.repo_id,
        conversations=len(request.conversation_ids),
    )

    return HFUploadResponse(
        repo_id=result.repo_id,
        url=result.url,
        commit_hash=result.commit_hash,
        files_uploaded=result.files_uploaded,
    )


@router.get("/huggingface/repos", response_model=list[HFDatasetInfoResponse])
async def list_hf_repos(
    token: Annotated[str, Header(alias="X-HF-Token", description="HuggingFace API token")],
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 20,
) -> list[HFDatasetInfoResponse]:
    """List datasets owned by the authenticated HuggingFace user.

    Requires a valid HuggingFace API token in the X-HF-Token header.
    """
    connector = HuggingFaceConnector(token=token)
    results = await connector.list_user_repos(token=token, limit=limit)

    return [
        HFDatasetInfoResponse(
            repo_id=ds.repo_id,
            description=ds.description,
            downloads=ds.downloads,
            likes=ds.likes,
            tags=ds.tags,
            last_modified=ds.last_modified,
            size_bytes=ds.size_bytes,
        )
        for ds in results
    ]


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
            "name": "Hugging Face Hub",
            "slug": "huggingface",
            "description": "Search, import, and upload datasets on Hugging Face Hub",
            "supported_formats": ["jsonl", "csv", "parquet"],
            "endpoint": "/api/v1/connectors/huggingface",
            "method": "GET/POST",
            "accepts": "query params / JSON body",
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

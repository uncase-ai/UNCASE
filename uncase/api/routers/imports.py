"""File import API endpoints — CSV and JSONL ingestion."""

from __future__ import annotations

import structlog
from fastapi import APIRouter, UploadFile

from uncase.core.parser.csv_parser import CSVConversationParser
from uncase.core.parser.jsonl_parser import JSONLConversationParser
from uncase.schemas.import_result import ImportErrorDetail, ImportResult

router = APIRouter(prefix="/api/v1/import", tags=["import"])

logger = structlog.get_logger(__name__)


@router.post("/csv", response_model=ImportResult)
async def import_csv(file: UploadFile) -> ImportResult:
    """Upload and parse a CSV file into conversations."""
    content = await file.read()
    raw = content.decode("utf-8")

    parser = CSVConversationParser()
    errors: list[ImportErrorDetail] = []

    # Let ImportParsingError / ImportFormatError bubble to middleware handler
    conversations = await parser.parse(raw)

    logger.info(
        "csv_imported",
        filename=file.filename,
        conversations_imported=len(conversations),
        conversations_failed=len(errors),
    )
    return ImportResult(
        conversations_imported=len(conversations),
        conversations_failed=len(errors),
        errors=errors,
        conversations=conversations,
    )


@router.post("/jsonl", response_model=ImportResult)
async def import_jsonl(file: UploadFile, source_format: str = "auto") -> ImportResult:
    """Upload and parse a JSONL file into conversations."""
    content = await file.read()
    raw = content.decode("utf-8")

    parser = JSONLConversationParser()
    errors: list[ImportErrorDetail] = []

    # Let ImportParsingError / ImportFormatError bubble to middleware handler
    conversations = await parser.parse(raw, format=source_format)

    logger.info(
        "jsonl_imported",
        filename=file.filename,
        source_format=source_format,
        conversations_imported=len(conversations),
        conversations_failed=len(errors),
    )
    return ImportResult(
        conversations_imported=len(conversations),
        conversations_failed=len(errors),
        errors=errors,
        conversations=conversations,
    )

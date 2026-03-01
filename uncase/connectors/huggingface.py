"""Hugging Face Hub connector — search, download, and upload datasets."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from uncase.connectors.base import BaseConnector, ConnectorResult
from uncase.logging import get_logger

logger = get_logger(__name__)


@dataclass
class HFDatasetInfo:
    """Metadata for a Hugging Face dataset."""

    repo_id: str
    description: str | None = None
    downloads: int = 0
    likes: int = 0
    tags: list[str] = field(default_factory=list)
    last_modified: str = ""
    size_bytes: int | None = None


@dataclass
class HFUploadResult:
    """Result of uploading a dataset to Hugging Face."""

    repo_id: str
    url: str
    commit_hash: str
    files_uploaded: int


class HuggingFaceConnector(BaseConnector):
    """Hugging Face Hub connector — search, download, upload datasets.

    Uses the huggingface_hub library to interact with the Hub API.
    Token is optional for public datasets but required for private repos.
    """

    def __init__(self, token: str | None = None) -> None:
        self._token = token

    def _get_api(self) -> Any:
        """Lazy-import and instantiate HfApi."""
        from huggingface_hub import HfApi

        return HfApi(token=self._token)

    # ── Search ────────────────────────────────────────────────────

    async def search_datasets(
        self,
        query: str,
        limit: int = 20,
    ) -> list[HFDatasetInfo]:
        """Search Hugging Face Hub for datasets matching a query.

        Returns a list of dataset metadata sorted by downloads.
        """
        api = self._get_api()

        try:
            results = list(api.list_datasets(
                search=query,
                sort="downloads",
                direction=-1,
                limit=limit,
            ))
        except Exception as exc:
            logger.error("hf_search_failed", query=query, error=str(exc))
            return []

        datasets = []
        for ds in results:
            datasets.append(HFDatasetInfo(
                repo_id=ds.id,
                description=getattr(ds, "description", None) or getattr(ds, "card_data", {}).get("description"),
                downloads=getattr(ds, "downloads", 0) or 0,
                likes=getattr(ds, "likes", 0) or 0,
                tags=list(getattr(ds, "tags", []) or []),
                last_modified=str(getattr(ds, "last_modified", "")),
                size_bytes=getattr(ds, "size_in_bytes", None),
            ))

        logger.info("hf_search_complete", query=query, results=len(datasets))
        return datasets

    # ── Download / Import ────────────────────────────────────────

    async def download_dataset(
        self,
        repo_id: str,
        split: str = "train",
        token: str | None = None,
    ) -> ConnectorResult:
        """Download a dataset from Hugging Face and convert to Conversations.

        Supports JSONL and Parquet formats. Expects each row to have
        a 'messages' field with chat-format data.
        """
        effective_token = token or self._token

        try:
            from datasets import load_dataset

            ds = load_dataset(repo_id, split=split, token=effective_token)
        except Exception as exc:
            logger.error("hf_download_failed", repo_id=repo_id, error=str(exc))
            return ConnectorResult(errors=[f"Failed to download {repo_id}: {exc}"])

        # Convert to Conversation objects
        from uncase.schemas.conversation import Conversation, ConversationTurn

        conversations: list[Conversation] = []
        skipped = 0
        errors: list[str] = []

        for idx, row in enumerate(ds):
            messages = row.get("messages") or row.get("conversations") or row.get("text")

            if messages is None:
                skipped += 1
                continue

            # Handle string-format messages (raw JSONL text)
            if isinstance(messages, str):
                try:
                    messages = json.loads(messages)
                except json.JSONDecodeError:
                    skipped += 1
                    continue

            if not isinstance(messages, list):
                skipped += 1
                continue

            try:
                turnos = []
                for turn_num, msg in enumerate(messages, 1):
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role and content:
                        turnos.append(ConversationTurn(
                            turno=turn_num,
                            rol=role,
                            contenido=str(content),
                        ))

                if len(turnos) >= 2:
                    conversations.append(Conversation(
                        conversation_id=uuid.uuid4().hex,
                        seed_id=f"hf:{repo_id}:{idx}",
                        dominio="imported.huggingface",
                        idioma="en",
                        turnos=turnos,
                        metadata={"source": f"huggingface:{repo_id}"},
                    ))
            except Exception as exc:
                if len(errors) < 10:
                    errors.append(f"Row {idx}: {exc}")
                skipped += 1

        logger.info(
            "hf_import_complete",
            repo_id=repo_id,
            split=split,
            imported=len(conversations),
            skipped=skipped,
        )

        return ConnectorResult(
            conversations=conversations,
            total_imported=len(conversations),
            total_skipped=skipped,
            errors=errors,
        )

    # ── Upload ───────────────────────────────────────────────────

    async def upload_dataset(
        self,
        conversations: list[dict[str, object]],
        repo_id: str,
        token: str,
        private: bool = False,
    ) -> HFUploadResult:
        """Upload conversations to Hugging Face as a JSONL dataset.

        Creates or updates the repository with a train.jsonl file.
        """
        from huggingface_hub import HfApi

        api = HfApi(token=token)

        # Create repo if needed
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            exist_ok=True,
            private=private,
        )

        # Build JSONL content
        lines = []
        for conv in conversations:
            lines.append(json.dumps(conv, ensure_ascii=False))
        content = "\n".join(lines) + "\n"

        # Upload
        commit_info = api.upload_file(
            path_or_fileobj=content.encode("utf-8"),
            path_in_repo="train.jsonl",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Upload dataset via UNCASE",
        )

        result = HFUploadResult(
            repo_id=repo_id,
            url=f"https://huggingface.co/datasets/{repo_id}",
            commit_hash=getattr(commit_info, "commit_url", str(commit_info)) or "",
            files_uploaded=1,
        )

        logger.info(
            "hf_upload_complete",
            repo_id=repo_id,
            conversations=len(conversations),
        )

        return result

    # ── List user repos ──────────────────────────────────────────

    async def list_user_repos(
        self,
        token: str,
        limit: int = 20,
    ) -> list[HFDatasetInfo]:
        """List datasets owned by the authenticated user."""
        from huggingface_hub import HfApi

        api = HfApi(token=token)

        try:
            user_info = api.whoami(token=token)
            username = user_info.get("name", "")

            results = list(api.list_datasets(
                author=username,
                limit=limit,
            ))
        except Exception as exc:
            logger.error("hf_list_repos_failed", error=str(exc))
            return []

        return [
            HFDatasetInfo(
                repo_id=ds.id,
                description=getattr(ds, "description", None),
                downloads=getattr(ds, "downloads", 0) or 0,
                likes=getattr(ds, "likes", 0) or 0,
                tags=list(getattr(ds, "tags", []) or []),
                last_modified=str(getattr(ds, "last_modified", "")),
            )
            for ds in results
        ]

    # ── BaseConnector interface ──────────────────────────────────

    async def ingest(self, raw_input: str | bytes, **kwargs: object) -> ConnectorResult:
        """Ingest from Hugging Face — raw_input is the repo_id."""
        repo_id = raw_input if isinstance(raw_input, str) else raw_input.decode("utf-8")
        split = str(kwargs.get("split", "train"))
        token = kwargs.get("token")
        return await self.download_dataset(
            repo_id=repo_id,
            split=split,
            token=str(token) if token else None,
        )

    def connector_name(self) -> str:
        """Return the display name of this connector."""
        return "Hugging Face Hub"

    def supported_formats(self) -> list[str]:
        """Return the list of accepted input formats."""
        return ["jsonl", "csv", "parquet"]

"""Conversation CRUD service layer."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from uncase.db.models.conversation import ConversationModel
from uncase.exceptions import ConversationNotFoundError, ValidationError
from uncase.logging import get_logger
from uncase.schemas.conversation_api import (
    ConversationBulkCreateResponse,
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdateRequest,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class ConversationService:
    """Service for conversation CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_conversation(
        self, data: ConversationCreateRequest, *, organization_id: str | None = None
    ) -> ConversationResponse:
        """Persist a new conversation."""
        turnos_data = [t.model_dump(mode="json") for t in data.turnos]

        model = ConversationModel(
            id=uuid.uuid4().hex,
            conversation_id=data.conversation_id,
            seed_id=data.seed_id,
            dominio=data.dominio,
            idioma=data.idioma,
            turnos=turnos_data,
            num_turnos=len(data.turnos),
            es_sintetica=data.es_sintetica,
            metadata_json=data.metadata,
            status=data.status,
            rating=data.rating,
            tags=data.tags,
            notes=data.notes,
            organization_id=organization_id,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        logger.info("conversation_created", conversation_id=model.conversation_id, dominio=model.dominio)
        return self._to_response(model)

    async def bulk_create(
        self, items: list[ConversationCreateRequest], *, organization_id: str | None = None
    ) -> ConversationBulkCreateResponse:
        """Bulk-create conversations, skipping duplicates."""
        created = 0
        skipped = 0
        errors: list[str] = []

        for item in items:
            # Check for duplicate conversation_id
            existing = await self.session.execute(
                select(ConversationModel).where(ConversationModel.conversation_id == item.conversation_id)
            )
            if existing.scalar_one_or_none() is not None:
                skipped += 1
                continue

            try:
                turnos_data = [t.model_dump(mode="json") for t in item.turnos]
                model = ConversationModel(
                    id=uuid.uuid4().hex,
                    conversation_id=item.conversation_id,
                    seed_id=item.seed_id,
                    dominio=item.dominio,
                    idioma=item.idioma,
                    turnos=turnos_data,
                    num_turnos=len(item.turnos),
                    es_sintetica=item.es_sintetica,
                    metadata_json=item.metadata,
                    status=item.status,
                    rating=item.rating,
                    tags=item.tags,
                    notes=item.notes,
                    organization_id=organization_id,
                )
                self.session.add(model)
                created += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{item.conversation_id}: {exc}")

        if created > 0:
            await self.session.commit()

        logger.info("conversations_bulk_created", created=created, skipped=skipped, errors=len(errors))
        return ConversationBulkCreateResponse(created=created, skipped=skipped, errors=errors)

    async def get_conversation(self, conversation_id: str) -> ConversationResponse:
        """Get a conversation by its conversation_id."""
        model = await self._get_or_raise(conversation_id)
        return self._to_response(model)

    async def list_conversations(
        self,
        *,
        domain: str | None = None,
        language: str | None = None,
        status: str | None = None,
        seed_id: str | None = None,
        organization_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ConversationListResponse:
        """List conversations with optional filters and pagination."""
        if page < 1:
            raise ValidationError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValidationError("page_size must be between 1 and 100")

        query = select(ConversationModel)
        count_query = select(func.count()).select_from(ConversationModel)

        if domain is not None:
            query = query.where(ConversationModel.dominio == domain)
            count_query = count_query.where(ConversationModel.dominio == domain)

        if language is not None:
            query = query.where(ConversationModel.idioma == language)
            count_query = count_query.where(ConversationModel.idioma == language)

        if status is not None:
            query = query.where(ConversationModel.status == status)
            count_query = count_query.where(ConversationModel.status == status)

        if seed_id is not None:
            query = query.where(ConversationModel.seed_id == seed_id)
            count_query = count_query.where(ConversationModel.seed_id == seed_id)

        if organization_id is not None:
            query = query.where(ConversationModel.organization_id == organization_id)
            count_query = count_query.where(ConversationModel.organization_id == organization_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(ConversationModel.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(query)
        conversations = result.scalars().all()

        return ConversationListResponse(
            items=[self._to_response(c) for c in conversations],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_conversation(self, conversation_id: str, data: ConversationUpdateRequest) -> ConversationResponse:
        """Update conversation metadata (status, rating, tags, notes)."""
        model = await self._get_or_raise(conversation_id)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationError("No fields to update")

        # Map 'metadata' key to 'metadata_json' column
        if "metadata" in update_data:
            update_data["metadata_json"] = update_data.pop("metadata")

        for field, value in update_data.items():
            setattr(model, field, value)
        model.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(model)

        logger.info("conversation_updated", conversation_id=conversation_id, fields=list(update_data.keys()))
        return self._to_response(model)

    async def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation by conversation_id."""
        model = await self._get_or_raise(conversation_id)
        await self.session.delete(model)
        await self.session.commit()
        logger.info("conversation_deleted", conversation_id=conversation_id)

    # -- Helpers --

    async def _get_or_raise(self, conversation_id: str) -> ConversationModel:
        """Fetch by conversation_id or raise ConversationNotFoundError."""
        result = await self.session.execute(
            select(ConversationModel).where(ConversationModel.conversation_id == conversation_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ConversationNotFoundError(f"Conversation '{conversation_id}' not found")
        return model

    @staticmethod
    def _to_response(model: ConversationModel) -> ConversationResponse:
        """Convert a ConversationModel to a ConversationResponse."""
        return ConversationResponse.model_validate(model)

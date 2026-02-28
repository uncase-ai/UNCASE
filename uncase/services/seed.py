"""Seed CRUD service layer."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal, cast

from sqlalchemy import func, select

from uncase.db.models.seed import SeedModel
from uncase.exceptions import SeedNotFoundError, ValidationError
from uncase.logging import get_logger
from uncase.schemas.seed import SeedSchema
from uncase.schemas.seed_api import SeedCreateRequest, SeedListResponse, SeedResponse, SeedUpdateRequest

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class SeedService:
    """Service for seed CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_seed(self, data: SeedCreateRequest, *, organization_id: str | None = None) -> SeedResponse:
        """Create a new seed.

        Validates the full SeedSchema before persisting to ensure domain
        and PII consistency rules are enforced.
        """
        # Validate through SeedSchema to enforce domain/PII rules
        seed_schema = SeedSchema(
            dominio=data.dominio,
            idioma=data.idioma,
            version=cast("Literal['1.0']", data.version),
            etiquetas=data.etiquetas,
            objetivo=data.objetivo,
            tono=data.tono,
            roles=data.roles,
            descripcion_roles=data.descripcion_roles,
            pasos_turnos=data.pasos_turnos,
            parametros_factuales=data.parametros_factuales,
            privacidad=data.privacidad,
            metricas_calidad=data.metricas_calidad,
            scenarios=data.scenarios,
            organization_id=organization_id,
        )

        seed_model = SeedModel(
            id=uuid.uuid4().hex,
            dominio=seed_schema.dominio,
            idioma=seed_schema.idioma,
            version=seed_schema.version,
            etiquetas=seed_schema.etiquetas,
            objetivo=seed_schema.objetivo,
            tono=seed_schema.tono,
            roles=seed_schema.roles,
            descripcion_roles=seed_schema.descripcion_roles,
            pasos_turnos=seed_schema.pasos_turnos.model_dump(),
            parametros_factuales=seed_schema.parametros_factuales.model_dump(),
            privacidad=seed_schema.privacidad.model_dump(),
            metricas_calidad=seed_schema.metricas_calidad.model_dump(),
            scenarios=[s.model_dump() for s in seed_schema.scenarios] if seed_schema.scenarios else None,
            organization_id=organization_id,
        )
        self.session.add(seed_model)
        await self.session.commit()
        await self.session.refresh(seed_model)

        logger.info("seed_created", seed_id=seed_model.id, dominio=seed_model.dominio)
        return self._to_response(seed_model)

    async def get_seed(self, seed_id: str) -> SeedResponse:
        """Get a seed by its database ID."""
        seed_model = await self._get_seed_or_raise(seed_id)
        return self._to_response(seed_model)

    async def list_seeds(
        self,
        *,
        domain: str | None = None,
        organization_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SeedListResponse:
        """List seeds with optional domain filter and pagination."""
        if page < 1:
            raise ValidationError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValidationError("page_size must be between 1 and 100")

        query = select(SeedModel)
        count_query = select(func.count()).select_from(SeedModel)

        if domain is not None:
            query = query.where(SeedModel.dominio == domain)
            count_query = count_query.where(SeedModel.dominio == domain)

        if organization_id is not None:
            query = query.where(SeedModel.organization_id == organization_id)
            count_query = count_query.where(SeedModel.organization_id == organization_id)

        # Total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Paginated results
        offset = (page - 1) * page_size
        query = query.order_by(SeedModel.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(query)
        seeds = result.scalars().all()

        return SeedListResponse(
            items=[self._to_response(s) for s in seeds],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_seed(self, seed_id: str, data: SeedUpdateRequest) -> SeedResponse:
        """Partially update a seed. Only provided fields are changed."""
        seed_model = await self._get_seed_or_raise(seed_id)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationError("No fields to update")

        # Convert nested Pydantic models to dicts for JSON columns
        for field_name in ("pasos_turnos", "parametros_factuales", "privacidad", "metricas_calidad"):
            if field_name in update_data and update_data[field_name] is not None:
                value = update_data[field_name]
                if hasattr(value, "model_dump"):
                    update_data[field_name] = value.model_dump()

        # Scenarios is a list of Pydantic models
        if "scenarios" in update_data and update_data["scenarios"] is not None:
            update_data["scenarios"] = [s.model_dump() for s in update_data["scenarios"]]

        # If domain is being changed, validate it through SeedSchema
        if "dominio" in update_data:
            # Build a full schema dict from current model + updates to validate
            current_data = self._to_schema_dict(seed_model)
            current_data.update(update_data)
            try:
                SeedSchema.model_validate(current_data)
            except Exception as exc:
                raise ValidationError(str(exc)) from exc

        for field, value in update_data.items():
            setattr(seed_model, field, value)
        seed_model.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(seed_model)

        logger.info("seed_updated", seed_id=seed_model.id, fields=list(update_data.keys()))
        return self._to_response(seed_model)

    async def rate_seed(self, seed_id: str, new_rating: float) -> SeedResponse:
        """Submit a rating for a seed. Computes running average."""
        seed_model = await self._get_seed_or_raise(seed_id)

        old_avg = seed_model.rating or 0.0
        old_count = seed_model.rating_count or 0
        new_count = old_count + 1
        seed_model.rating = ((old_avg * old_count) + new_rating) / new_count
        seed_model.rating_count = new_count
        seed_model.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(seed_model)

        logger.info("seed_rated", seed_id=seed_id, rating=new_rating, avg=seed_model.rating, count=new_count)
        return self._to_response(seed_model)

    async def increment_run_count(self, seed_id: str, quality_score: float | None = None) -> SeedResponse:
        """Increment the run count for a seed and optionally update avg quality score."""
        seed_model = await self._get_seed_or_raise(seed_id)

        seed_model.run_count = (seed_model.run_count or 0) + 1

        if quality_score is not None:
            old_avg = seed_model.avg_quality_score or 0.0
            old_count = seed_model.run_count - 1
            seed_model.avg_quality_score = ((old_avg * old_count) + quality_score) / seed_model.run_count

        seed_model.updated_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(seed_model)

        logger.info("seed_run_counted", seed_id=seed_id, run_count=seed_model.run_count)
        return self._to_response(seed_model)

    async def delete_seed(self, seed_id: str) -> None:
        """Delete a seed by ID."""
        seed_model = await self._get_seed_or_raise(seed_id)
        await self.session.delete(seed_model)
        await self.session.commit()

        logger.info("seed_deleted", seed_id=seed_id)

    # -- Helpers --

    async def _get_seed_or_raise(self, seed_id: str) -> SeedModel:
        """Fetch a seed or raise SeedNotFoundError."""
        result = await self.session.execute(select(SeedModel).where(SeedModel.id == seed_id))
        seed_model = result.scalar_one_or_none()
        if seed_model is None:
            raise SeedNotFoundError(f"Seed '{seed_id}' not found")
        return seed_model

    @staticmethod
    def _to_response(seed_model: SeedModel) -> SeedResponse:
        """Convert a SeedModel to a SeedResponse.

        JSON columns are parsed back into their nested Pydantic models
        by SeedResponse via from_attributes.
        """
        return SeedResponse.model_validate(seed_model)

    @staticmethod
    def _to_schema_dict(seed_model: SeedModel) -> dict[str, Any]:
        """Build a dict suitable for SeedSchema validation from a SeedModel."""
        return {
            "dominio": seed_model.dominio,
            "idioma": seed_model.idioma,
            "version": seed_model.version,
            "etiquetas": seed_model.etiquetas,
            "objetivo": seed_model.objetivo,
            "tono": seed_model.tono,
            "roles": seed_model.roles,
            "descripcion_roles": seed_model.descripcion_roles,
            "pasos_turnos": seed_model.pasos_turnos,
            "parametros_factuales": seed_model.parametros_factuales,
            "privacidad": seed_model.privacidad,
            "metricas_calidad": seed_model.metricas_calidad,
            "scenarios": seed_model.scenarios,
            "organization_id": seed_model.organization_id,
        }

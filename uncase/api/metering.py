"""Fire-and-forget usage metering for API endpoints.

Usage:
    from uncase.api.metering import meter

    result = await service.create_seed(data)
    await meter(session, "seed_created", resource_id=result.id)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from uncase.logging import get_logger
from uncase.schemas.usage import UsageEventRecord
from uncase.services.usage import UsageMeteringService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


async def meter(
    session: AsyncSession,
    event_type: str,
    *,
    organization_id: str | None = None,
    resource_id: str | None = None,
    count: int = 1,
    metadata: dict[str, object] | None = None,
    ip_address: str | None = None,
) -> None:
    """Record a usage event. Non-fatal: logs but never raises."""
    try:
        service = UsageMeteringService(session)
        await service.record(
            UsageEventRecord(
                organization_id=organization_id,
                event_type=event_type,
                resource_id=resource_id,
                count=count,
                metadata=metadata,
                ip_address=ip_address,
            )
        )

        # Dispatch webhook event (fire-and-forget)
        try:
            from uncase.services.webhook import WebhookService

            webhook_service = WebhookService(session)
            await webhook_service.dispatch_event(
                event_type,
                organization_id=organization_id,
                resource_id=resource_id,
                data=metadata,
            )
        except Exception:
            logger.debug("webhook_dispatch_skipped", event_type=event_type)
    except Exception:
        logger.warning("usage_metering_failed", event_type=event_type, exc_info=True)

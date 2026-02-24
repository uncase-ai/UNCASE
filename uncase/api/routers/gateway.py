"""Gateway API endpoints — LLM chat proxy with privacy interception."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_settings
from uncase.config import UNCASESettings
from uncase.core.privacy.interceptor import PrivacyInterceptor
from uncase.exceptions import LLMConfigurationError, ProviderNotFoundError
from uncase.services.provider import ProviderService

router = APIRouter(prefix="/api/v1/gateway", tags=["gateway"])

logger = structlog.get_logger(__name__)


# -- Request / Response schemas (kept local to the router) --


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request body for the chat proxy endpoint."""

    messages: list[ChatMessage] = Field(..., min_length=1, description="Conversation messages")
    provider_id: str | None = Field(
        default=None,
        description="Provider ID to use. Falls back to the default provider.",
    )
    model: str | None = Field(
        default=None,
        description="Override the provider's default model.",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=1024, ge=1, le=32768, description="Maximum tokens in response")
    privacy_mode: str = Field(
        default="audit",
        description="Privacy interception mode: audit, warn, or block",
    )


class ChatChoice(BaseModel):
    """A single response choice."""

    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class PrivacyScanInfo(BaseModel):
    """Privacy scan summary returned with the chat response."""

    outbound_pii_found: int = Field(default=0, description="PII entities found in outbound messages")
    inbound_pii_found: int = Field(default=0, description="PII entities found in LLM response")
    mode: str = Field(default="audit", description="Privacy mode used")
    any_blocked: bool = Field(default=False, description="Whether any message was blocked")


class ChatResponse(BaseModel):
    """Response body for the chat proxy endpoint."""

    choices: list[ChatChoice] = Field(..., description="Response choices")
    model: str = Field(..., description="Model used for generation")
    provider_name: str = Field(..., description="Provider name")
    privacy: PrivacyScanInfo = Field(default_factory=PrivacyScanInfo, description="Privacy scan results")


@router.post("/chat", response_model=ChatResponse)
async def chat_proxy(
    request: ChatRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> ChatResponse:
    """Proxy a chat completion request through the LLM gateway.

    This endpoint acts as a universal proxy to any configured LLM provider.
    All traffic is scanned for PII both outbound (to the LLM) and inbound
    (from the LLM response).

    Flow:
    1. Resolve provider (explicit ID or default)
    2. Scan outbound messages for PII (audit/warn/block)
    3. Forward request to LLM via LiteLLM
    4. Scan inbound response for PII
    5. Return response with privacy scan summary
    """
    provider_service = ProviderService(session=session, settings=settings)

    # 1. Resolve provider
    try:
        if request.provider_id:
            provider = await provider_service._get_or_raise(request.provider_id)
        else:
            maybe_provider = await provider_service.get_default_provider()
            if maybe_provider is None:
                raise LLMConfigurationError("No default provider configured. Add a provider first.")
            provider = maybe_provider
    except ProviderNotFoundError:
        raise
    except LLMConfigurationError:
        raise

    # 2. Privacy interception — outbound
    interceptor = PrivacyInterceptor(mode=request.privacy_mode)
    outbound_pii_count = 0
    messages_to_send: list[dict[str, str]] = []

    for msg in request.messages:
        result = interceptor.scan_outbound(msg.content)
        outbound_pii_count += result.scan.entity_count

        if result.blocked:
            raise HTTPException(
                status_code=422,
                detail=f"PII detected in message (mode=block): {result.message}",
            )

        # Use anonymized text if available
        clean_content = result.scan.anonymized_text if result.scan.anonymized_text else msg.content
        messages_to_send.append({"role": msg.role, "content": clean_content})

    # 3. Forward to LLM
    model_to_use = request.model or provider.default_model
    api_key = provider_service.decrypt_provider_key(provider)

    try:
        import litellm

        response = await litellm.acompletion(
            model=model_to_use,
            messages=messages_to_send,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            api_key=api_key,
            api_base=provider.api_base,
        )
    except Exception as exc:
        logger.error(
            "gateway_llm_error",
            provider=provider.name,
            model=model_to_use,
            error=str(exc)[:200],
        )
        raise LLMConfigurationError(f"LLM call failed: {exc!s}") from exc

    # 4. Extract response text
    assistant_text = response.choices[0].message.content or ""
    finish_reason = response.choices[0].finish_reason or "stop"

    # 5. Privacy interception — inbound
    inbound_result = interceptor.scan_inbound(assistant_text)
    inbound_pii_count = inbound_result.scan.entity_count

    if inbound_result.blocked:
        logger.warning(
            "gateway_inbound_pii_blocked",
            provider=provider.name,
            model=model_to_use,
            pii_count=inbound_pii_count,
        )
        raise HTTPException(
            status_code=422,
            detail="PII detected in LLM response (mode=block). Response withheld.",
        )

    logger.info(
        "gateway_chat_complete",
        provider=provider.name,
        model=model_to_use,
        outbound_pii=outbound_pii_count,
        inbound_pii=inbound_pii_count,
        privacy_mode=request.privacy_mode,
    )

    return ChatResponse(
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=assistant_text),
                finish_reason=finish_reason,
            )
        ],
        model=model_to_use,
        provider_name=provider.name,
        privacy=PrivacyScanInfo(
            outbound_pii_found=outbound_pii_count,
            inbound_pii_found=inbound_pii_count,
            mode=request.privacy_mode,
            any_blocked=False,
        ),
    )

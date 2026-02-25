"""Gateway API endpoints — LLM chat proxy with privacy interception."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uncase.api.deps import get_db, get_settings
from uncase.config import UNCASESettings
from uncase.core.privacy.interceptor import PrivacyInterceptor
from uncase.exceptions import LLMConfigurationError, PIIDetectedError, ProviderNotFoundError
from uncase.services.provider import ProviderService

router = APIRouter(prefix="/api/v1/gateway", tags=["gateway"])

logger = structlog.get_logger(__name__)


# -- Request / Response schemas (kept local to the router) --


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ToolFunction(BaseModel):
    """OpenAI-compatible tool function definition."""

    name: str = Field(..., description="Function name")
    description: str = Field(default="", description="Function description")
    parameters: dict[str, object] = Field(default_factory=dict, description="JSON Schema for parameters")


class ChatTool(BaseModel):
    """OpenAI-compatible tool definition for function calling."""

    type: str = Field(default="function")
    function: ToolFunction


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
    bypass_words: list[str] | None = Field(
        default=None,
        description="Words to exclude from PII detection (e.g., bot names, place names)",
    )
    tools: list[ChatTool] | None = Field(default=None, description="Tool definitions for function calling")
    tool_choice: str | None = Field(default=None, description="Tool choice: auto, required, none, or function name")


class ChatChoice(BaseModel):
    """A single response choice."""

    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"
    tool_calls: list[dict[str, object]] | None = Field(default=None, description="Tool calls made by the model")


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


class ChatStreamChunk(BaseModel):
    """A single SSE chunk during streaming."""

    delta: str = Field(default="", description="Token text")
    index: int = Field(default=0, description="Choice index")
    tool_calls: list[dict[str, object]] | None = Field(default=None, description="Partial tool calls")


class ChatStreamComplete(BaseModel):
    """Final SSE event with full response metadata."""

    full_response: str = Field(..., description="Complete assembled response")
    finish_reason: str = Field(default="stop")
    model: str
    provider_name: str
    privacy: PrivacyScanInfo
    usage: dict[str, int] = Field(default_factory=dict, description="Token usage: input_tokens, output_tokens")


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
    interceptor = PrivacyInterceptor(
        mode=request.privacy_mode,
        bypass_words=set(request.bypass_words) if request.bypass_words else None,
    )
    outbound_pii_count = 0
    messages_to_send: list[dict[str, str]] = []

    for msg in request.messages:
        result = interceptor.scan_outbound(msg.content)
        outbound_pii_count += result.scan.entity_count

        if result.blocked:
            raise PIIDetectedError(f"PII detected in message (mode=block): {result.message}")

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
            **({"tools": [t.model_dump() for t in request.tools]} if request.tools else {}),
            **({"tool_choice": request.tool_choice} if request.tool_choice else {}),
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

    # Extract tool calls if present
    tool_calls_data: list[dict[str, object]] | None = None
    if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
        tool_calls_data = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in response.choices[0].message.tool_calls
        ]

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
        raise PIIDetectedError("PII detected in LLM response (mode=block). Response withheld.")

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
                tool_calls=tool_calls_data,
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


@router.post("/chat/stream")
async def chat_proxy_stream(
    request: ChatRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[UNCASESettings, Depends(get_settings)],
) -> StreamingResponse:
    """Stream a chat completion via SSE.

    Same as /chat but streams token-by-token using Server-Sent Events.
    Privacy: outbound scan happens before streaming starts (fail-fast).
    Inbound scan happens after streaming completes.
    Final SSE event includes privacy summary and token usage.
    """
    provider_service = ProviderService(session=session, settings=settings)

    # 1. Resolve provider (same as non-streaming)
    if request.provider_id:
        provider = await provider_service._get_or_raise(request.provider_id)
    else:
        maybe_provider = await provider_service.get_default_provider()
        if maybe_provider is None:
            raise LLMConfigurationError("No default provider configured. Add a provider first.")
        provider = maybe_provider

    # 2. Privacy interception — outbound (fail-fast before streaming starts)
    interceptor = PrivacyInterceptor(
        mode=request.privacy_mode,
        bypass_words=set(request.bypass_words) if request.bypass_words else None,
    )
    outbound_pii_count = 0
    messages_to_send: list[dict[str, str]] = []

    for msg in request.messages:
        result = interceptor.scan_outbound(msg.content)
        outbound_pii_count += result.scan.entity_count
        if result.blocked:
            raise PIIDetectedError(f"PII detected in message (mode=block): {result.message}")
        clean_content = result.scan.anonymized_text if result.scan.anonymized_text else msg.content
        messages_to_send.append({"role": msg.role, "content": clean_content})

    # 3. Prepare LLM call
    model_to_use = request.model or provider.default_model
    api_key = provider_service.decrypt_provider_key(provider)

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events from streaming LLM response."""
        full_response = ""
        finish_reason = "stop"
        usage_data: dict[str, int] = {}

        try:
            import litellm

            stream = await litellm.acompletion(
                model=model_to_use,
                messages=messages_to_send,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                api_key=api_key,
                api_base=provider.api_base,
                stream=True,
                **({"tools": [t.model_dump() for t in request.tools]} if request.tools else {}),
                **({"tool_choice": request.tool_choice} if request.tool_choice else {}),
            )

            async for chunk in stream:
                choice = chunk.choices[0] if chunk.choices else None
                if choice is None:
                    continue

                delta_content = ""
                if hasattr(choice.delta, "content") and choice.delta.content:
                    delta_content = choice.delta.content
                    full_response += delta_content

                if choice.finish_reason:
                    finish_reason = choice.finish_reason

                # Extract usage from final chunk if available
                if hasattr(chunk, "usage") and chunk.usage:
                    usage_data = {
                        "input_tokens": getattr(chunk.usage, "prompt_tokens", 0),
                        "output_tokens": getattr(chunk.usage, "completion_tokens", 0),
                    }

                if delta_content:
                    sse_chunk = ChatStreamChunk(delta=delta_content, index=0)
                    yield f"data: {sse_chunk.model_dump_json()}\n\n"

        except Exception as exc:
            logger.error("gateway_stream_error", provider=provider.name, model=model_to_use, error=str(exc)[:200])
            error_data = {"error": str(exc), "type": type(exc).__name__}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
            return

        # 4. Inbound privacy scan on full response
        inbound_pii_count = 0
        any_blocked = False
        if full_response:
            inbound_result = interceptor.scan_inbound(full_response)
            inbound_pii_count = inbound_result.scan.entity_count
            any_blocked = inbound_result.blocked

        # 5. Final event with metadata
        complete = ChatStreamComplete(
            full_response=full_response,
            finish_reason=finish_reason,
            model=model_to_use,
            provider_name=provider.name,
            privacy=PrivacyScanInfo(
                outbound_pii_found=outbound_pii_count,
                inbound_pii_found=inbound_pii_count,
                mode=request.privacy_mode,
                any_blocked=any_blocked,
            ),
            usage=usage_data,
        )
        yield f"event: done\ndata: {complete.model_dump_json()}\n\n"

        logger.info(
            "gateway_stream_complete",
            provider=provider.name,
            model=model_to_use,
            outbound_pii=outbound_pii_count,
            inbound_pii=inbound_pii_count,
            response_length=len(full_response),
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

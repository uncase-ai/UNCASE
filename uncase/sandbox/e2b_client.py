"""E2B sandbox orchestrator for parallel conversation generation.

Manages the lifecycle of E2B sandboxes: boot, upload worker script,
execute generation, collect results, and tear down. Uses asyncio.Semaphore
for concurrency control.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from uncase.exceptions import SandboxNotConfiguredError, SandboxTimeoutError
from uncase.sandbox.schemas import (
    SandboxGenerateResponse,
    SandboxGenerationSummary,
    SandboxProgress,
    SandboxSeedResult,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from uncase.config import UNCASESettings
    from uncase.schemas.conversation import Conversation
    from uncase.schemas.quality import QualityReport

logger = structlog.get_logger(__name__)

# Path to the worker script that gets uploaded to each sandbox
_WORKER_PATH = Path(__file__).parent / "worker.py"


def _parse_sandbox_conversations(raw_conversations: list[dict[str, Any]]) -> list[Conversation]:
    """Parse raw conversation dicts from sandbox output into Conversation models."""
    from uncase.schemas.conversation import Conversation, ConversationTurn

    conversations: list[Conversation] = []
    for raw in raw_conversations:
        turns = [
            ConversationTurn(
                turno=t.get("turno", i + 1),
                rol=t.get("rol", ""),
                contenido=t.get("contenido", ""),
                herramientas_usadas=t.get("herramientas_usadas", []),
                metadata=t.get("metadata", {}),
            )
            for i, t in enumerate(raw.get("turnos", []))
        ]
        if not turns:
            continue

        conversations.append(
            Conversation(
                conversation_id=raw.get("conversation_id", ""),
                seed_id=raw.get("seed_id", ""),
                dominio=raw.get("dominio", ""),
                idioma=raw.get("idioma", "es"),
                turnos=turns,
                es_sintetica=raw.get("es_sintetica", True),
                metadata=raw.get("metadata", {}),
            )
        )
    return conversations


def _parse_sandbox_reports(raw_reports: list[dict[str, Any]] | None) -> list[QualityReport] | None:
    """Parse raw quality report dicts from sandbox output into QualityReport models."""
    if raw_reports is None:
        return None

    from uncase.schemas.quality import QualityMetrics, QualityReport

    reports: list[QualityReport] = []
    for raw in raw_reports:
        metrics_data = raw.get("metrics", {})
        metrics = QualityMetrics(
            rouge_l=metrics_data.get("rouge_l", 0.0),
            fidelidad_factual=metrics_data.get("fidelidad_factual", 0.0),
            diversidad_lexica=metrics_data.get("diversidad_lexica", 0.0),
            coherencia_dialogica=metrics_data.get("coherencia_dialogica", 0.0),
            privacy_score=metrics_data.get("privacy_score", 0.0),
            memorizacion=metrics_data.get("memorizacion", 0.0),
        )
        reports.append(
            QualityReport(
                conversation_id=raw.get("conversation_id", ""),
                seed_id=raw.get("seed_id", ""),
                metrics=metrics,
                composite_score=raw.get("composite_score", 0.0),
                passed=raw.get("passed", False),
                failures=raw.get("failures", []),
            )
        )
    return reports


class E2BSandboxOrchestrator:
    """Orchestrates parallel conversation generation across E2B sandboxes.

    Each seed gets its own sandbox running the self-contained worker.py
    script. Concurrency is controlled via asyncio.Semaphore.

    Usage:
        orchestrator = E2BSandboxOrchestrator(settings=settings)
        response = await orchestrator.fan_out_generate(
            seeds=seeds,
            count_per_seed=3,
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            api_key="sk-...",
            evaluate_after=True,
        )
    """

    def __init__(self, *, settings: UNCASESettings) -> None:
        if not settings.sandbox_available:
            raise SandboxNotConfiguredError()

        self._settings = settings
        self._semaphore = asyncio.Semaphore(settings.e2b_max_parallel)
        self._worker_code = _WORKER_PATH.read_text(encoding="utf-8")

    async def _run_sandbox(
        self,
        *,
        seed_dict: dict[str, Any],
        count: int,
        model: str,
        temperature: float,
        api_key: str | None,
        api_base: str | None,
        language_override: str | None,
        evaluate_after: bool,
        sandbox_index: int,
        total_sandboxes: int,
    ) -> tuple[SandboxSeedResult, list[SandboxProgress]]:
        """Run generation inside a single E2B sandbox.

        Returns the seed result and a list of progress events.
        """
        from e2b_code_interpreter import AsyncSandbox

        seed_id = seed_dict.get("seed_id", "unknown")
        progress_events: list[SandboxProgress] = []
        start_time = time.monotonic()

        def _progress(status: str, completed: int = 0, error: str | None = None) -> SandboxProgress:
            event = SandboxProgress(
                seed_id=seed_id,
                sandbox_index=sandbox_index,
                total_sandboxes=total_sandboxes,
                status=status,
                conversations_completed=completed,
                conversations_total=count,
                error=error,
                elapsed_seconds=round(time.monotonic() - start_time, 2),
            )
            progress_events.append(event)
            return event

        _progress("queued")

        async with self._semaphore:
            sandbox: AsyncSandbox | None = None
            try:
                _progress("booting")

                logger.info(
                    "sandbox_booting",
                    seed_id=seed_id,
                    sandbox_index=sandbox_index,
                    template=self._settings.e2b_template_id,
                )

                sandbox = await AsyncSandbox.create(
                    template=self._settings.e2b_template_id,
                    api_key=self._settings.e2b_api_key,
                    timeout=self._settings.e2b_sandbox_timeout,
                )

                # Upload the worker script
                await sandbox.files.write("/home/user/worker.py", self._worker_code)

                # Build the payload for the worker
                payload = json.dumps(
                    {
                        "seed": seed_dict,
                        "count": count,
                        "model": model,
                        "temperature": temperature,
                        "api_key": api_key,
                        "api_base": api_base,
                        "language_override": language_override,
                        "evaluate_after": evaluate_after,
                    },
                    ensure_ascii=False,
                )

                # Upload payload as a file and pipe it to the worker
                await sandbox.files.write("/home/user/payload.json", payload)

                _progress("generating")

                logger.info(
                    "sandbox_executing",
                    seed_id=seed_id,
                    sandbox_index=sandbox_index,
                    model=model,
                    count=count,
                )

                # Execute: pipe payload to worker via stdin
                execution = await sandbox.commands.run(
                    "cd /home/user && python worker.py < payload.json",
                    timeout=self._settings.e2b_sandbox_timeout,
                )

                if execution.exit_code != 0:
                    error_msg = execution.stderr or f"Sandbox exited with code {execution.exit_code}"
                    logger.error(
                        "sandbox_execution_failed",
                        seed_id=seed_id,
                        exit_code=execution.exit_code,
                        stderr=execution.stderr[:500] if execution.stderr else "",
                    )
                    _progress("error", error=error_msg)
                    return SandboxSeedResult(
                        seed_id=seed_id,
                        error=error_msg,
                        duration_seconds=round(time.monotonic() - start_time, 2),
                    ), progress_events

                # Parse the JSON output
                raw_output = execution.stdout.strip()
                if not raw_output:
                    _progress("error", error="Empty output from sandbox")
                    return SandboxSeedResult(
                        seed_id=seed_id,
                        error="Empty output from sandbox",
                        duration_seconds=round(time.monotonic() - start_time, 2),
                    ), progress_events

                result_data = json.loads(raw_output)

                if result_data.get("error"):
                    _progress("error", error=result_data["error"])
                    return SandboxSeedResult(
                        seed_id=seed_id,
                        error=result_data["error"],
                        duration_seconds=round(time.monotonic() - start_time, 2),
                    ), progress_events

                # Parse conversations and reports
                conversations = _parse_sandbox_conversations(result_data.get("conversations", []))
                reports = _parse_sandbox_reports(result_data.get("reports"))

                passed_count = 0
                if reports:
                    passed_count = sum(1 for r in reports if r.passed)

                _progress("complete", completed=len(conversations))

                duration = round(time.monotonic() - start_time, 2)

                logger.info(
                    "sandbox_complete",
                    seed_id=seed_id,
                    sandbox_index=sandbox_index,
                    conversations=len(conversations),
                    passed=passed_count,
                    duration=duration,
                )

                return SandboxSeedResult(
                    seed_id=seed_id,
                    conversations=conversations,
                    reports=reports,
                    passed_count=passed_count,
                    duration_seconds=duration,
                ), progress_events

            except TimeoutError as exc:
                error_msg = f"Sandbox timed out after {self._settings.e2b_sandbox_timeout}s"
                _progress("error", error=error_msg)
                logger.error("sandbox_timeout", seed_id=seed_id, timeout=self._settings.e2b_sandbox_timeout)
                raise SandboxTimeoutError(error_msg) from exc

            except Exception as exc:
                error_msg = str(exc)
                _progress("error", error=error_msg)
                logger.error("sandbox_error", seed_id=seed_id, error=error_msg)
                return SandboxSeedResult(
                    seed_id=seed_id,
                    error=error_msg,
                    duration_seconds=round(time.monotonic() - start_time, 2),
                ), progress_events

            finally:
                if sandbox is not None:
                    with contextlib.suppress(Exception):
                        await sandbox.kill()

    async def fan_out_generate(
        self,
        *,
        seeds: list[dict[str, Any]],
        count_per_seed: int = 1,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        api_key: str | None = None,
        api_base: str | None = None,
        language_override: str | None = None,
        evaluate_after: bool = True,
        max_parallel: int | None = None,
    ) -> SandboxGenerateResponse:
        """Fan out generation across parallel E2B sandboxes.

        Creates one sandbox per seed. Each sandbox independently generates
        conversations and optionally evaluates them. Results are collected
        after all sandboxes complete.

        Args:
            seeds: List of seed dicts to generate from.
            count_per_seed: Conversations to generate per seed.
            model: LLM model to use.
            temperature: Sampling temperature.
            api_key: API key for the LLM provider.
            api_base: Optional API base URL.
            language_override: Override language for all seeds.
            evaluate_after: Run quality evaluation in each sandbox.
            max_parallel: Override max parallel sandboxes.

        Returns:
            SandboxGenerateResponse with per-seed results and summary.
        """
        if max_parallel is not None:
            self._semaphore = asyncio.Semaphore(min(max_parallel, 20))

        start_time = time.monotonic()
        total_sandboxes = len(seeds)

        logger.info(
            "sandbox_fan_out_start",
            total_seeds=total_sandboxes,
            count_per_seed=count_per_seed,
            model=model,
            max_parallel=self._semaphore._value,
        )

        # Launch all sandboxes concurrently (semaphore controls actual parallelism)
        tasks = [
            self._run_sandbox(
                seed_dict=seed,
                count=count_per_seed,
                model=model,
                temperature=temperature,
                api_key=api_key,
                api_base=api_base,
                language_override=language_override,
                evaluate_after=evaluate_after,
                sandbox_index=i,
                total_sandboxes=total_sandboxes,
            )
            for i, seed in enumerate(seeds)
        ]

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        results: list[SandboxSeedResult] = []
        for i, task_result in enumerate(task_results):
            if isinstance(task_result, BaseException):
                results.append(
                    SandboxSeedResult(
                        seed_id=seeds[i].get("seed_id", "unknown"),
                        error=str(task_result),
                        duration_seconds=0.0,
                    )
                )
            else:
                seed_result, _progress_events = task_result
                results.append(seed_result)

        # Build summary
        total_conversations = sum(len(r.conversations) for r in results)
        total_passed: int | None = None
        avg_score: float | None = None

        if evaluate_after:
            all_reports = [r for result in results if result.reports for r in result.reports]
            if all_reports:
                total_passed = sum(1 for r in all_reports if r.passed)
                avg_score = round(sum(r.composite_score for r in all_reports) / len(all_reports), 4)

        failed_seeds = sum(1 for r in results if r.error is not None)
        duration = round(time.monotonic() - start_time, 2)

        summary = SandboxGenerationSummary(
            total_seeds=total_sandboxes,
            total_conversations=total_conversations,
            total_passed=total_passed,
            avg_composite_score=avg_score,
            failed_seeds=failed_seeds,
            model_used=model,
            temperature=temperature,
            max_parallel=self._semaphore._value,
            duration_seconds=duration,
            sandbox_mode=True,
        )

        logger.info(
            "sandbox_fan_out_complete",
            total_seeds=total_sandboxes,
            total_conversations=total_conversations,
            total_passed=total_passed,
            failed_seeds=failed_seeds,
            duration=duration,
        )

        return SandboxGenerateResponse(results=results, summary=summary)

    async def fan_out_generate_stream(
        self,
        *,
        seeds: list[dict[str, Any]],
        count_per_seed: int = 1,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        api_key: str | None = None,
        api_base: str | None = None,
        language_override: str | None = None,
        evaluate_after: bool = True,
        max_parallel: int | None = None,
    ) -> AsyncGenerator[SandboxProgress | SandboxGenerateResponse, None]:
        """Stream progress events during parallel sandbox generation.

        Yields SandboxProgress events as sandboxes complete, then yields
        the final SandboxGenerateResponse.

        Usage with SSE:
            async for event in orchestrator.fan_out_generate_stream(...):
                if isinstance(event, SandboxProgress):
                    yield f"data: {event.model_dump_json()}\\n\\n"
                else:
                    yield f"event: complete\\ndata: {event.model_dump_json()}\\n\\n"
        """
        if max_parallel is not None:
            self._semaphore = asyncio.Semaphore(min(max_parallel, 20))

        start_time = time.monotonic()
        total_sandboxes = len(seeds)

        # Create tasks
        tasks = [
            asyncio.create_task(
                self._run_sandbox(
                    seed_dict=seed,
                    count=count_per_seed,
                    model=model,
                    temperature=temperature,
                    api_key=api_key,
                    api_base=api_base,
                    language_override=language_override,
                    evaluate_after=evaluate_after,
                    sandbox_index=i,
                    total_sandboxes=total_sandboxes,
                )
            )
            for i, seed in enumerate(seeds)
        ]

        results: list[SandboxSeedResult] = []
        pending = set(tasks)

        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

            for task in done:
                exc = task.exception()
                if exc is not None:
                    idx = tasks.index(task)
                    error_result = SandboxSeedResult(
                        seed_id=seeds[idx].get("seed_id", "unknown"),
                        error=str(exc),
                        duration_seconds=0.0,
                    )
                    results.append(error_result)
                    yield SandboxProgress(
                        seed_id=error_result.seed_id,
                        sandbox_index=idx,
                        total_sandboxes=total_sandboxes,
                        status="error",
                        conversations_total=count_per_seed,
                        error=str(exc),
                        elapsed_seconds=round(time.monotonic() - start_time, 2),
                    )
                else:
                    seed_result, progress_events = task.result()
                    results.append(seed_result)
                    # Yield progress events
                    for event in progress_events:
                        yield event

        # Build final response
        total_conversations = sum(len(r.conversations) for r in results)
        total_passed: int | None = None
        avg_score: float | None = None

        if evaluate_after:
            all_reports = [r for result in results if result.reports for r in result.reports]
            if all_reports:
                total_passed = sum(1 for r in all_reports if r.passed)
                avg_score = round(sum(r.composite_score for r in all_reports) / len(all_reports), 4)

        failed_seeds = sum(1 for r in results if r.error is not None)
        duration = round(time.monotonic() - start_time, 2)

        summary = SandboxGenerationSummary(
            total_seeds=total_sandboxes,
            total_conversations=total_conversations,
            total_passed=total_passed,
            avg_composite_score=avg_score,
            failed_seeds=failed_seeds,
            model_used=model,
            temperature=temperature,
            max_parallel=self._semaphore._value,
            duration_seconds=duration,
            sandbox_mode=True,
        )

        yield SandboxGenerateResponse(results=results, summary=summary)

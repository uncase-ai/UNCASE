"""Opik evaluation sandbox — ephemeral Opik instances for LLM-as-judge evaluation.

Spins up an E2B sandbox with Opik installed, runs evaluations using
Opik's built-in metrics (hallucination, coherence, relevance), and
exports the results to persistent storage before the sandbox dies.

Flow:
    1. Boot sandbox with Opik + litellm pre-installed
    2. Upload conversations and seeds as datasets
    3. Run Opik evaluate() with selected metrics
    4. Export traces and experiment results
    5. Destroy sandbox, return persistent results
"""

from __future__ import annotations

import contextlib
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from uncase.exceptions import SandboxError, SandboxNotConfiguredError
from uncase.sandbox.exporter import SandboxExporter
from uncase.sandbox.schemas import (
    OpikConversationResult,
    OpikEvaluationRequest,
    OpikEvaluationResponse,
    OpikEvaluationSummary,
    OpikMetricResult,
    SandboxJob,
    SandboxJobStatus,
    SandboxTemplate,
)

if TYPE_CHECKING:
    from uncase.config import UNCASESettings

logger = structlog.get_logger(__name__)

# Path to the Opik worker script
_OPIK_WORKER_PATH = Path(__file__).parent / "opik_worker.py"


class OpikSandboxRunner:
    """Runs Opik evaluations inside ephemeral E2B sandboxes.

    Each evaluation gets its own Opik instance running inside a sandbox.
    Results are exported before the sandbox is destroyed, giving users
    persistent evaluation data without permanent infrastructure.

    Usage:
        runner = OpikSandboxRunner(settings=settings)
        response = await runner.run_evaluation(
            OpikEvaluationRequest(
                conversations=conversations,
                seeds=seeds,
                experiment_name="batch-eval-1",
            )
        )
    """

    def __init__(self, *, settings: UNCASESettings) -> None:
        if not settings.sandbox_available:
            raise SandboxNotConfiguredError()

        self._settings = settings
        self._exporter = SandboxExporter(exports_dir=settings.uncase_exports_dir)

    async def run_evaluation(
        self,
        request: OpikEvaluationRequest,
        *,
        api_key: str | None = None,
    ) -> OpikEvaluationResponse:
        """Run a full Opik evaluation in an ephemeral sandbox.

        Args:
            request: Evaluation configuration and data.
            api_key: LLM API key for LLM-as-judge metrics.

        Returns:
            OpikEvaluationResponse with results and export status.
        """
        from e2b_code_interpreter import AsyncSandbox

        job = SandboxJob(
            template=SandboxTemplate.EVALUATION_OPIK,
            status=SandboxJobStatus.BOOTING,
        )

        logger.info(
            "opik_evaluation_starting",
            job_id=job.job_id,
            experiment_name=request.experiment_name,
            total_conversations=len(request.conversations),
            ttl_minutes=request.ttl_minutes,
        )

        sandbox = None
        start_time = time.monotonic()

        try:
            sandbox = await AsyncSandbox.create(
                template=self._settings.e2b_template_id,
                api_key=self._settings.e2b_api_key,
                timeout=request.ttl_minutes * 60,
            )

            job.status = SandboxJobStatus.RUNNING

            # Install dependencies
            logger.info("opik_sandbox_installing", job_id=job.job_id)
            await sandbox.commands.run(
                "pip install opik litellm pydantic 2>/dev/null",
                timeout=120,
            )

            # Upload the worker script
            worker_code = _build_opik_worker()
            await sandbox.files.write("/home/user/opik_worker.py", worker_code)

            # Build payload
            payload = {
                "conversations": [c.model_dump(mode="json") for c in request.conversations],
                "seeds": [s.model_dump(mode="json") for s in request.seeds],
                "experiment_name": request.experiment_name,
                "api_key": api_key or self._settings.litellm_api_key or self._settings.anthropic_api_key,
                "model": request.model or "claude-sonnet-4-20250514",
                "run_hallucination": request.run_hallucination_check,
                "run_coherence": request.run_coherence_check,
                "run_relevance": request.run_relevance_check,
            }

            await sandbox.files.write(
                "/home/user/eval_payload.json",
                json.dumps(payload, ensure_ascii=False),
            )

            # Run evaluation
            logger.info("opik_evaluation_running", job_id=job.job_id)

            execution = await sandbox.commands.run(
                "cd /home/user && python opik_worker.py < eval_payload.json",
                timeout=request.ttl_minutes * 60,
            )

            if execution.exit_code != 0:
                error_msg = execution.stderr or f"Opik worker exited with code {execution.exit_code}"
                logger.error(
                    "opik_execution_failed",
                    job_id=job.job_id,
                    exit_code=execution.exit_code,
                    stderr=error_msg[:500],
                )
                job.status = SandboxJobStatus.FAILED
                job.error = error_msg
                raise SandboxError(error_msg)

            # Parse results
            raw_output = execution.stdout.strip()
            result_data = json.loads(raw_output)

            # Export before destroying
            exported = False
            if request.export_before_destroy:
                job.status = SandboxJobStatus.EXPORTING
                logger.info("opik_exporting", job_id=job.job_id)

                # Write results to a file in sandbox for export
                await sandbox.files.write(
                    "/home/user/opik_results.json",
                    json.dumps(result_data, ensure_ascii=False),
                )

                export_result = await self._exporter.export_all(
                    sandbox=sandbox,
                    job_id=job.job_id,
                    artifact_paths={
                        "opik_results": "/home/user/opik_results.json",
                    },
                )
                exported = export_result.error is None

            # Parse into response models
            conversation_results = _parse_opik_results(result_data.get("results", []))
            summary = _build_opik_summary(
                conversation_results,
                duration=round(time.monotonic() - start_time, 2),
                request=request,
            )

            job.status = SandboxJobStatus.COMPLETED

            logger.info(
                "opik_evaluation_complete",
                job_id=job.job_id,
                total_evaluated=len(conversation_results),
                avg_opik_score=summary.avg_opik_score,
                exported=exported,
                duration=summary.duration_seconds,
            )

            return OpikEvaluationResponse(
                job=job,
                experiment_name=request.experiment_name,
                results=conversation_results,
                summary=summary,
                exported=exported,
            )

        except SandboxError:
            raise

        except Exception as exc:
            job.status = SandboxJobStatus.FAILED
            job.error = str(exc)
            logger.error("opik_evaluation_error", job_id=job.job_id, error=str(exc))
            msg = f"Opik evaluation failed: {exc}"
            raise SandboxError(msg) from exc

        finally:
            if sandbox is not None:
                with contextlib.suppress(Exception):
                    await sandbox.kill()


def _parse_opik_results(raw_results: list[dict[str, Any]]) -> list[OpikConversationResult]:
    """Parse raw Opik worker results into typed models."""
    results: list[OpikConversationResult] = []
    for raw in raw_results:
        metrics = [
            OpikMetricResult(
                metric_name=m.get("metric_name", ""),
                value=m.get("value", 0.0),
                reason=m.get("reason"),
            )
            for m in raw.get("metrics", [])
        ]

        opik_values = [m.value for m in metrics]
        opik_avg = sum(opik_values) / len(opik_values) if opik_values else 0.0

        results.append(
            OpikConversationResult(
                conversation_id=raw.get("conversation_id", ""),
                seed_id=raw.get("seed_id", ""),
                metrics=metrics,
                uncase_composite_score=raw.get("uncase_composite_score", 0.0),
                opik_avg_score=round(opik_avg, 4),
            )
        )
    return results


def _build_opik_summary(
    results: list[OpikConversationResult],
    *,
    duration: float,
    request: OpikEvaluationRequest,
) -> OpikEvaluationSummary:
    """Build aggregate summary from individual results."""
    if not results:
        return OpikEvaluationSummary(
            total_conversations=0,
            avg_uncase_composite=0.0,
            avg_opik_score=0.0,
            duration_seconds=duration,
        )

    avg_uncase = sum(r.uncase_composite_score for r in results) / len(results)
    avg_opik = sum(r.opik_avg_score for r in results) / len(results)

    # Extract per-metric averages
    metric_sums: dict[str, list[float]] = {}
    for result in results:
        for metric in result.metrics:
            metric_sums.setdefault(metric.metric_name, []).append(metric.value)

    avg_hallucination = None
    avg_coherence = None
    avg_relevance = None

    for name, values in metric_sums.items():
        avg = sum(values) / len(values)
        if "hallucination" in name.lower():
            avg_hallucination = round(avg, 4)
        elif "coherence" in name.lower():
            avg_coherence = round(avg, 4)
        elif "relevance" in name.lower():
            avg_relevance = round(avg, 4)

    passed_uncase = sum(1 for r in results if r.uncase_composite_score >= 0.65)

    return OpikEvaluationSummary(
        total_conversations=len(results),
        avg_hallucination=avg_hallucination,
        avg_coherence=avg_coherence,
        avg_relevance=avg_relevance,
        avg_uncase_composite=round(avg_uncase, 4),
        avg_opik_score=round(avg_opik, 4),
        passed_uncase=passed_uncase,
        duration_seconds=duration,
    )


def _build_opik_worker() -> str:
    """Build the self-contained Opik worker script for sandbox execution.

    The worker:
    1. Reads conversation + seed data from stdin (JSON)
    2. Initializes Opik in local mode
    3. Runs evaluation with selected metrics
    4. Outputs results as JSON to stdout
    """
    return '''"""Opik evaluation worker — runs inside E2B sandbox."""
from __future__ import annotations

import json
import sys
from typing import Any


def evaluate_conversations(payload: dict[str, Any]) -> dict[str, Any]:
    """Run Opik evaluation on conversations."""
    import opik
    from opik.evaluation.metrics import Hallucination, GEval

    conversations = payload["conversations"]
    seeds = payload["seeds"]
    experiment_name = payload.get("experiment_name", "uncase-eval")
    api_key = payload.get("api_key", "")
    model = payload.get("model", "claude-sonnet-4-20250514")
    run_hallucination = payload.get("run_hallucination", True)
    run_coherence = payload.get("run_coherence", True)
    run_relevance = payload.get("run_relevance", True)

    # Build seed lookup
    seed_map: dict[str, dict[str, Any]] = {}
    for seed in seeds:
        seed_map[seed.get("seed_id", "")] = seed

    # Configure Opik for local use (no external server needed)
    opik.configure(use_local=True)

    # Build metrics
    metrics = []
    if run_hallucination:
        metrics.append(("hallucination", Hallucination(model=model)))
    if run_coherence:
        metrics.append(("coherence", GEval(
            name="coherence",
            task_introduction="Evaluate the coherence of a multi-turn conversation.",
            evaluation_criteria=(
                "The conversation should flow naturally between turns. "
                "Each turn should logically follow from the previous one. "
                "Roles should maintain consistent behavior and knowledge."
            ),
            model=model,
        )))
    if run_relevance:
        metrics.append(("relevance", GEval(
            name="relevance",
            task_introduction="Evaluate how relevant the conversation is to its stated objective.",
            evaluation_criteria=(
                "The conversation should address the stated objective. "
                "Turns should stay on topic and contribute to the goal. "
                "The conversation should reach a meaningful conclusion."
            ),
            model=model,
        )))

    results = []
    for conv in conversations:
        conv_id = conv.get("conversation_id", "")
        seed_id = conv.get("seed_id", "")
        seed = seed_map.get(seed_id, {})

        # Build conversation text for evaluation
        turns = conv.get("turnos", [])
        conv_text = "\\n".join(
            f"{t.get('rol', 'unknown')}: {t.get('contenido', '')}"
            for t in turns
        )

        objetivo = seed.get("objetivo", "")
        contexto = seed.get("parametros_factuales", {}).get("contexto", "")
        flow = seed.get("pasos_turnos", {}).get("flujo_esperado", [])
        reference = f"Objective: {objetivo}\\nContext: {contexto}\\nExpected flow: {', '.join(flow)}"

        # Run each metric
        conv_metrics = []
        for metric_name, metric in metrics:
            try:
                if metric_name == "hallucination":
                    score = metric.score(
                        input=objetivo,
                        output=conv_text,
                        context=[contexto] + flow,
                    )
                else:
                    score = metric.score(
                        input=objetivo,
                        output=conv_text,
                    )

                conv_metrics.append({
                    "metric_name": metric_name,
                    "value": round(float(score.value), 4),
                    "reason": getattr(score, "reason", None),
                })
            except Exception as exc:
                conv_metrics.append({
                    "metric_name": metric_name,
                    "value": 0.0,
                    "reason": f"Error: {exc}",
                })

        # Compute simplified UNCASE composite
        uncase_score = _compute_uncase_composite(turns, seed)

        results.append({
            "conversation_id": conv_id,
            "seed_id": seed_id,
            "metrics": conv_metrics,
            "uncase_composite_score": uncase_score,
        })

    return {"results": results, "error": None}


def _compute_uncase_composite(turns: list[dict[str, Any]], seed: dict[str, Any]) -> float:
    """Simplified UNCASE composite score computation."""
    import re

    if not turns:
        return 0.0

    all_text = " ".join(t.get("contenido", "") for t in turns)
    tokens = re.findall(r"\\w+", all_text.lower())

    # TTR
    ttr = len(set(tokens)) / len(tokens) if tokens else 0.0

    # Coherence (role alternation)
    coherence = 1.0
    if len(turns) > 1:
        alternations = sum(
            1 for i in range(1, len(turns))
            if turns[i].get("rol") != turns[i - 1].get("rol")
        )
        coherence = min(1.0, alternations / (len(turns) - 1))

    return round(min(ttr, coherence, 0.95), 4)


def main() -> None:
    """Entry point."""
    raw_input = sys.stdin.read()
    payload = json.loads(raw_input)

    try:
        result = evaluate_conversations(payload)
    except Exception as exc:
        result = {"results": [], "error": str(exc)}

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
'''

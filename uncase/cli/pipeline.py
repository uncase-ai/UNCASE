"""Pipeline CLI — end-to-end pipeline commands."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer

pipeline_app = typer.Typer(help="End-to-end SCSF pipeline operations.")


@pipeline_app.command("run")
def run_pipeline(
    domain: str = typer.Option(..., "--domain", "-d", help="Domain namespace (e.g. 'automotive.sales')"),
    input_file: Path = typer.Option(
        ..., "--input", "-i", help="Input file with raw conversations (one per line, or JSON/JSONL)"
    ),
    count: int = typer.Option(10, "--count", "-n", help="Synthetic conversations to generate per seed"),
    model: str = typer.Option(None, "--model", "-m", help="LLM model override"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="Generation temperature"),
    train: bool = typer.Option(False, "--train", help="Train LoRA adapter after generation"),
    base_model: str = typer.Option("meta-llama/Llama-3.1-8B", "--base-model", help="Base model for LoRA"),
    use_qlora: bool = typer.Option(True, "--qlora/--no-qlora", help="Use QLoRA quantization"),
    use_dp: bool = typer.Option(False, "--dp/--no-dp", help="Enable DP-SGD differential privacy"),
    dp_epsilon: float = typer.Option(8.0, "--epsilon", help="Privacy budget epsilon"),
    output_dir: str = typer.Option("./outputs/pipeline", "--output", "-o", help="Output directory"),
) -> None:
    """Run the full end-to-end SCSF pipeline.

    Takes raw conversations from a file, creates seeds, generates synthetic
    conversations, evaluates quality, and optionally trains a LoRA adapter.
    """
    if not input_file.exists():
        typer.echo(f"Error: Input file not found: {input_file}", err=True)
        raise typer.Exit(1)

    # Read raw conversations from file
    raw_text = input_file.read_text(encoding="utf-8").strip()
    if not raw_text:
        typer.echo("Error: Input file is empty", err=True)
        raise typer.Exit(1)

    # Split by double newline (conversation separator) or treat as single
    raw_conversations = (
        [c.strip() for c in raw_text.split("\n\n") if c.strip()] if "\n\n" in raw_text else [raw_text]
    )

    typer.echo(f"UNCASE Pipeline — Domain: {domain}")
    typer.echo(f"  Input: {input_file} ({len(raw_conversations)} conversation(s))")
    typer.echo(f"  Generate: {count} synthetic per seed")
    typer.echo(f"  Train: {'Yes' if train else 'No'}")
    typer.echo()

    async def _run() -> None:
        from uncase.config import UNCASESettings
        from uncase.core.pipeline_orchestrator import PipelineOrchestrator

        settings = UNCASESettings()

        def progress_callback(stage: str, progress: float, message: str) -> None:
            bar_width = 30
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)
            typer.echo(f"\r  [{bar}] {progress:.0%} {stage}: {message}", nl=False)
            if progress >= 1.0:
                typer.echo()

        orchestrator = PipelineOrchestrator(
            settings=settings,
            progress_callback=progress_callback,
        )

        result = await orchestrator.run(
            raw_conversations=raw_conversations,
            domain=domain,
            count=count,
            model=model,
            temperature=temperature,
            train_adapter=train,
            base_model=base_model,
            use_qlora=use_qlora,
            use_dp_sgd=use_dp,
            dp_epsilon=dp_epsilon,
            output_dir=output_dir,
        )

        typer.echo()
        typer.echo("Pipeline Results:")
        typer.echo(f"  Run ID: {result.run_id}")
        typer.echo(f"  Status: {'SUCCESS' if result.success else 'FAILED'}")
        typer.echo(f"  Seeds created: {result.seeds_created}")
        typer.echo(f"  Conversations generated: {result.conversations_generated}")
        typer.echo(f"  Conversations passed: {result.conversations_passed}")
        typer.echo(f"  Pass rate: {result.pass_rate:.1%}")
        typer.echo(f"  Avg quality score: {result.avg_quality_score:.4f}")
        if result.adapter_path:
            typer.echo(f"  LoRA adapter: {result.adapter_path}")
        typer.echo(f"  Duration: {result.total_duration_seconds:.1f}s")

        typer.echo()
        typer.echo("Stages:")
        for stage in result.stages:
            status = "OK" if stage.success else "FAIL"
            typer.echo(f"  [{status}] {stage.stage} ({stage.duration_seconds:.1f}s)")
            if stage.error:
                typer.echo(f"        Error: {stage.error}")

        if not result.success:
            raise typer.Exit(1)

    asyncio.run(_run())


@pipeline_app.command("status")
def pipeline_status(
    job_id: str = typer.Argument(..., help="Job ID to check"),
) -> None:
    """Check the status of a pipeline job."""

    async def _check() -> None:
        from uncase.config import UNCASESettings
        from uncase.db.engine import get_async_session, init_engine
        from uncase.services.jobs import JobService

        settings = UNCASESettings()
        init_engine(settings)

        async for session in get_async_session():
            service = JobService(session)
            job = await service.get_job(job_id)

            typer.echo(f"Job: {job.id}")
            typer.echo(f"  Type: {job.job_type}")
            typer.echo(f"  Status: {job.status}")
            typer.echo(f"  Progress: {job.progress:.0%}")
            if job.current_stage:
                typer.echo(f"  Stage: {job.current_stage}")
            if job.status_message:
                typer.echo(f"  Message: {job.status_message}")
            if job.error_message:
                typer.echo(f"  Error: {job.error_message}")
            if job.result:
                typer.echo(f"  Result: {job.result}")

    asyncio.run(_check())

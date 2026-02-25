"""Data exporter — persists sandbox artifacts before destruction.

Handles exporting conversations, quality reports, Opik traces, and LoRA
adapters from ephemeral sandboxes to persistent storage (local filesystem
or cloud storage).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from uncase.sandbox.schemas import ExportArtifact, SandboxExportResult

if TYPE_CHECKING:
    from e2b_code_interpreter import AsyncSandbox

logger = structlog.get_logger(__name__)


class SandboxExporter:
    """Exports artifacts from a running E2B sandbox before it's destroyed.

    The exporter connects to a live sandbox, downloads specified artifacts,
    and saves them to the local exports directory (or uploads to cloud storage).

    Usage:
        exporter = SandboxExporter(exports_dir="./exports")
        result = await exporter.export_all(
            sandbox=sandbox,
            job_id="abc123",
            artifact_paths={
                "conversations": "/home/user/output/conversations.json",
                "reports": "/home/user/output/reports.json",
                "opik_traces": "/home/user/output/opik_export/",
            },
        )
    """

    def __init__(self, *, exports_dir: str = "./exports") -> None:
        self._exports_dir = Path(exports_dir)
        self._exports_dir.mkdir(parents=True, exist_ok=True)

    async def export_file(
        self,
        *,
        sandbox: AsyncSandbox,
        remote_path: str,
        local_name: str,
        job_id: str,
        artifact_type: str,
    ) -> ExportArtifact | None:
        """Download a single file from the sandbox.

        Args:
            sandbox: Live E2B sandbox instance.
            remote_path: Path inside the sandbox.
            local_name: Local filename for the export.
            job_id: Job ID for directory organization.
            artifact_type: Type label for the artifact.

        Returns:
            ExportArtifact if successful, None if the file doesn't exist.
        """
        try:
            content = await sandbox.files.read(remote_path)
        except Exception as exc:
            logger.warning(
                "export_file_not_found",
                remote_path=remote_path,
                error=str(exc),
            )
            return None

        # Create job-specific directory
        job_dir = self._exports_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        local_path = job_dir / local_name
        if isinstance(content, bytes):
            local_path.write_bytes(content)
            size = len(content)
        else:
            local_path.write_text(str(content), encoding="utf-8")
            size = len(str(content).encode("utf-8"))

        # Count records if JSON
        record_count = 0
        if local_name.endswith(".json"):
            try:
                data = json.loads(local_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    record_count = len(data)
                elif isinstance(data, dict):
                    record_count = 1
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        fmt = local_name.rsplit(".", maxsplit=1)[-1] if "." in local_name else "bin"

        logger.info(
            "artifact_exported",
            job_id=job_id,
            artifact_type=artifact_type,
            local_path=str(local_path),
            size_bytes=size,
            records=record_count,
        )

        return ExportArtifact(
            artifact_type=artifact_type,
            format=fmt,
            size_bytes=size,
            path=str(local_path),
            record_count=record_count,
        )

    async def export_all(
        self,
        *,
        sandbox: AsyncSandbox,
        job_id: str,
        artifact_paths: dict[str, str],
    ) -> SandboxExportResult:
        """Export all specified artifacts from a sandbox.

        Args:
            sandbox: Live E2B sandbox instance.
            job_id: Job ID for organization.
            artifact_paths: Mapping of artifact_type -> remote_path.

        Returns:
            SandboxExportResult with all exported artifacts.
        """
        start_time = time.monotonic()
        artifacts: list[ExportArtifact] = []
        errors: list[str] = []

        for artifact_type, remote_path in artifact_paths.items():
            # Derive local filename from remote path
            remote_name = Path(remote_path).name
            local_name = f"{artifact_type}_{remote_name}"

            artifact = await self.export_file(
                sandbox=sandbox,
                remote_path=remote_path,
                local_name=local_name,
                job_id=job_id,
                artifact_type=artifact_type,
            )

            if artifact is not None:
                artifacts.append(artifact)
            else:
                errors.append(f"Failed to export {artifact_type} from {remote_path}")

        total_size = sum(a.size_bytes for a in artifacts)
        duration = round(time.monotonic() - start_time, 2)

        error_msg = "; ".join(errors) if errors else None

        logger.info(
            "export_complete",
            job_id=job_id,
            total_artifacts=len(artifacts),
            total_size_bytes=total_size,
            errors=len(errors),
            duration=duration,
        )

        return SandboxExportResult(
            job_id=job_id,
            artifacts=artifacts,
            total_size_bytes=total_size,
            error=error_msg,
        )

    async def export_opik_data(
        self,
        *,
        sandbox: AsyncSandbox,
        job_id: str,
        experiment_name: str,
    ) -> SandboxExportResult:
        """Export Opik experiment data from a sandbox.

        Runs `opik export` inside the sandbox, then downloads the
        resulting files.

        Args:
            sandbox: Live E2B sandbox with Opik running.
            job_id: Job ID for organization.
            experiment_name: Opik experiment to export.

        Returns:
            SandboxExportResult with exported Opik data.
        """
        export_dir = "/home/user/opik_export"

        # Run opik export inside the sandbox
        logger.info("exporting_opik_data", job_id=job_id, experiment_name=experiment_name)

        execution = await sandbox.commands.run(
            f'cd /home/user && python -c "'
            f"import opik; import json; "
            f"client = opik.Opik(); "
            f"traces = client.search_traces(project_name='{experiment_name}'); "
            f"data = [t.__dict__ for t in traces]; "
            f"import pathlib; pathlib.Path('{export_dir}').mkdir(exist_ok=True); "
            f"pathlib.Path('{export_dir}/traces.json').write_text(json.dumps(data, default=str)); "
            f'"',
            timeout=60,
        )

        if execution.exit_code != 0:
            logger.error(
                "opik_export_failed",
                job_id=job_id,
                stderr=execution.stderr[:500] if execution.stderr else "",
            )

        return await self.export_all(
            sandbox=sandbox,
            job_id=job_id,
            artifact_paths={
                "opik_traces": f"{export_dir}/traces.json",
            },
        )

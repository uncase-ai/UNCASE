"""Tests for the JobModel database model."""

from __future__ import annotations

from uncase.db.models.job import JobModel


class TestJobModel:
    """Test JobModel state transitions and properties."""

    def _make_job(self, **overrides: object) -> JobModel:
        defaults: dict[str, object] = {
            "id": "test-job-001",
            "job_type": "pipeline_run",
            "status": "pending",
            "config": {"domain": "automotive.sales"},
            "progress": 0.0,
            "attempts": 0,
            "max_attempts": 3,
        }
        defaults.update(overrides)
        return JobModel(**defaults)  # type: ignore[arg-type]

    def test_initial_state(self) -> None:
        job = self._make_job()
        assert job.status == "pending"
        assert job.progress == 0.0
        assert not job.is_terminal
        assert not job.can_retry

    def test_mark_running(self) -> None:
        job = self._make_job()
        job.mark_running()
        assert job.status == "running"
        assert job.started_at is not None
        assert job.attempts == 1

    def test_mark_completed(self) -> None:
        job = self._make_job(status="running")
        result = {"conversations": 100}
        job.mark_completed(result=result)
        assert job.status == "completed"
        assert job.completed_at is not None
        assert job.progress == 1.0
        assert job.result == result

    def test_mark_completed_no_result(self) -> None:
        job = self._make_job(status="running")
        job.mark_completed()
        assert job.status == "completed"
        assert job.result is None

    def test_mark_failed(self) -> None:
        job = self._make_job(status="running", attempts=1)
        job.mark_failed("Something went wrong")
        assert job.status == "failed"
        assert job.completed_at is not None
        assert job.error_message == "Something went wrong"

    def test_mark_cancelled(self) -> None:
        job = self._make_job(status="running")
        job.mark_cancelled()
        assert job.status == "cancelled"
        assert job.completed_at is not None

    def test_is_terminal_completed(self) -> None:
        job = self._make_job(status="completed")
        assert job.is_terminal is True

    def test_is_terminal_failed(self) -> None:
        job = self._make_job(status="failed")
        assert job.is_terminal is True

    def test_is_terminal_cancelled(self) -> None:
        job = self._make_job(status="cancelled")
        assert job.is_terminal is True

    def test_is_not_terminal_pending(self) -> None:
        job = self._make_job(status="pending")
        assert job.is_terminal is False

    def test_is_not_terminal_running(self) -> None:
        job = self._make_job(status="running")
        assert job.is_terminal is False

    def test_can_retry_failed_under_limit(self) -> None:
        job = self._make_job(status="failed", attempts=1, max_attempts=3)
        assert job.can_retry is True

    def test_cannot_retry_failed_at_limit(self) -> None:
        job = self._make_job(status="failed", attempts=3, max_attempts=3)
        assert job.can_retry is False

    def test_cannot_retry_if_not_failed(self) -> None:
        job = self._make_job(status="completed", attempts=1, max_attempts=3)
        assert job.can_retry is False

    def test_cannot_retry_pending(self) -> None:
        job = self._make_job(status="pending", attempts=0, max_attempts=3)
        assert job.can_retry is False

    def test_multiple_run_attempts(self) -> None:
        job = self._make_job()
        job.mark_running()
        assert job.attempts == 1
        job.mark_failed("Error 1")
        job.status = "pending"
        job.mark_running()
        assert job.attempts == 2

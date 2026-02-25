"""SDK Pipeline — high-level API for end-to-end runs."""

from __future__ import annotations

from typing import Any

from uncase.sdk.client import UNCASEClient


class Pipeline:
    """High-level pipeline interface for ML engineers.

    Provides both sync and async interfaces for running the full
    SCSF pipeline programmatically.

    Usage:
        pipeline = Pipeline(api_key="your-key")
        result = pipeline.generate(domain="automotive.sales", count=100)

        # Async
        result = await pipeline.agenerate(domain="automotive.sales", count=100)

        # Full pipeline with training
        result = pipeline.run(
            raw_conversations=["..."],
            domain="automotive.sales",
            count=100,
            train=True,
        )
    """

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
    ) -> None:
        self._client = UNCASEClient(base_url=base_url, api_key=api_key)

    def run(
        self,
        *,
        raw_conversations: list[str],
        domain: str,
        count: int = 100,
        model: str | None = None,
        temperature: float = 0.7,
        train: bool = False,
        base_model: str = "meta-llama/Llama-3.1-8B",
        use_qlora: bool = True,
        use_dp_sgd: bool = False,
        dp_epsilon: float = 8.0,
        async_mode: bool = True,
    ) -> dict[str, Any]:
        """Run the full end-to-end pipeline (synchronous).

        Args:
            raw_conversations: Raw conversation texts.
            domain: Domain namespace.
            count: Synthetic conversations per seed.
            model: LLM model override.
            temperature: Generation temperature.
            train: Whether to train a LoRA adapter.
            base_model: Base model for LoRA.
            use_qlora: Use QLoRA quantization.
            use_dp_sgd: Enable DP-SGD.
            dp_epsilon: Privacy budget.
            async_mode: Run as background job on server.

        Returns:
            Pipeline run response with job_id.
        """
        return self._client.post(  # type: ignore[no-any-return]
            "/api/v1/pipeline/run",
            data={
                "raw_conversations": raw_conversations,
                "domain": domain,
                "count": count,
                "model": model,
                "temperature": temperature,
                "train_adapter": train,
                "base_model": base_model,
                "use_qlora": use_qlora,
                "use_dp_sgd": use_dp_sgd,
                "dp_epsilon": dp_epsilon,
                "async_mode": async_mode,
            },
        )

    async def arun(self, **kwargs: Any) -> dict[str, Any]:
        """Run the full pipeline (async)."""
        return await self._client.apost("/api/v1/pipeline/run", data=kwargs)  # type: ignore[no-any-return]

    def generate(
        self,
        *,
        seed: dict[str, Any],
        count: int = 1,
        temperature: float = 0.7,
        model: str | None = None,
        evaluate: bool = True,
    ) -> dict[str, Any]:
        """Generate synthetic conversations from a seed (synchronous).

        Args:
            seed: SeedSchema v1 as a dictionary.
            count: Number of conversations.
            temperature: Generation temperature.
            model: LLM model override.
            evaluate: Run quality evaluation.

        Returns:
            Generation response with conversations and reports.
        """
        return self._client.post(  # type: ignore[no-any-return]
            "/api/v1/generate",
            data={
                "seed": seed,
                "count": count,
                "temperature": temperature,
                "model": model,
                "evaluate_after": evaluate,
            },
        )

    async def agenerate(self, **kwargs: Any) -> dict[str, Any]:
        """Generate synthetic conversations (async)."""
        return await self._client.apost("/api/v1/generate", data=kwargs)  # type: ignore[no-any-return]

    def get_job(self, job_id: str) -> dict[str, Any]:
        """Get the status of a pipeline job."""
        return self._client.get(f"/api/v1/jobs/{job_id}")  # type: ignore[no-any-return]

    def list_seeds(self, domain: str | None = None) -> list[dict[str, Any]]:
        """List available seeds."""
        params: dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        return self._client.get("/api/v1/seeds", **params)  # type: ignore[no-any-return]

    def close(self) -> None:
        """Close the SDK client."""
        self._client.close()

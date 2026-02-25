"""SDK component wrappers — direct access to individual pipeline layers."""

from __future__ import annotations

import asyncio
from typing import Any


class SeedEngine:
    """SDK wrapper for Layer 0 — Seed Engine.

    Provides both local (in-process) and remote (API) seed creation.

    Usage:
        engine = SeedEngine()
        seed = engine.from_text("Vendedor: Hola\\nCliente: Hola", domain="automotive.sales")
    """

    def __init__(self, *, local: bool = True) -> None:
        self._local = local

    def from_text(self, raw_conversation: str, domain: str) -> dict[str, Any]:
        """Create a seed from raw conversation text.

        Args:
            raw_conversation: Raw conversation in any supported format.
            domain: Domain namespace.

        Returns:
            SeedSchema v1 as a dictionary.
        """
        if self._local:
            return asyncio.run(self._from_text_local(raw_conversation, domain))
        raise NotImplementedError("Remote seed creation requires UNCASEClient")

    async def afrom_text(self, raw_conversation: str, domain: str) -> dict[str, Any]:
        """Create a seed from text (async)."""
        return await self._from_text_local(raw_conversation, domain)

    @staticmethod
    async def _from_text_local(raw_conversation: str, domain: str) -> dict[str, Any]:
        from uncase.core.seed_engine.engine import SeedEngine as _Engine

        engine = _Engine()
        seed = await engine.create_seed(raw_conversation, domain)
        return seed.model_dump(mode="json")


class Generator:
    """SDK wrapper for Layer 3 — Synthetic Generator.

    Usage:
        gen = Generator(api_key="your-key")
        conversations = gen.generate(seed_dict, count=10)
    """

    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key
        self._model = model

    def generate(
        self,
        seed: dict[str, Any],
        *,
        count: int = 1,
        temperature: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Generate synthetic conversations (synchronous)."""
        return asyncio.run(self.agenerate(seed, count=count, temperature=temperature))

    async def agenerate(
        self,
        seed: dict[str, Any],
        *,
        count: int = 1,
        temperature: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Generate synthetic conversations (async)."""
        from uncase.config import UNCASESettings
        from uncase.schemas.seed import SeedSchema
        from uncase.services.generator import GeneratorService

        settings = UNCASESettings()
        if self._api_key:
            settings.litellm_api_key = self._api_key

        service = GeneratorService(settings=settings)
        seed_schema = SeedSchema(**seed)
        response = await service.generate(
            seed=seed_schema,
            count=count,
            temperature=temperature,
            model=self._model,
            evaluate_after=False,
        )
        return [c.model_dump(mode="json") for c in response.conversations]


class Evaluator:
    """SDK wrapper for Layer 2 — Quality Evaluator.

    Usage:
        evaluator = Evaluator()
        report = evaluator.evaluate(conversation_dict, seed_dict)
    """

    def evaluate(self, conversation: dict[str, Any], seed: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a conversation against its seed (synchronous)."""
        return asyncio.run(self.aevaluate(conversation, seed))

    async def aevaluate(self, conversation: dict[str, Any], seed: dict[str, Any]) -> dict[str, Any]:
        """Evaluate quality (async)."""
        from uncase.core.evaluator.evaluator import ConversationEvaluator
        from uncase.schemas.conversation import Conversation
        from uncase.schemas.seed import SeedSchema

        evaluator = ConversationEvaluator()
        conv = Conversation(**conversation)
        seed_schema = SeedSchema(**seed)
        report = await evaluator.evaluate(conv, seed_schema)
        return report.model_dump(mode="json")


class Trainer:
    """SDK wrapper for Layer 4 — LoRA Trainer.

    Usage:
        trainer = Trainer(base_model="meta-llama/Llama-3.1-8B")
        adapter_path = trainer.train(conversations)
    """

    def __init__(
        self,
        *,
        base_model: str = "meta-llama/Llama-3.1-8B",
        use_qlora: bool = True,
        use_dp_sgd: bool = False,
        dp_epsilon: float = 8.0,
        output_dir: str = "./outputs/lora",
    ) -> None:
        self._base_model = base_model
        self._use_qlora = use_qlora
        self._use_dp_sgd = use_dp_sgd
        self._dp_epsilon = dp_epsilon
        self._output_dir = output_dir

    def train(self, conversations: list[dict[str, Any]]) -> str:
        """Train a LoRA adapter (synchronous). Returns adapter path."""
        return asyncio.run(self.atrain(conversations))

    async def atrain(self, conversations: list[dict[str, Any]]) -> str:
        """Train a LoRA adapter (async)."""
        from uncase.core.lora_pipeline.pipeline import LoraPipeline
        from uncase.schemas.conversation import Conversation

        convs = [Conversation(**c) for c in conversations]

        pipeline = LoraPipeline(
            base_model=self._base_model,
            output_dir=self._output_dir,
            use_qlora=self._use_qlora,
            use_dp_sgd=self._use_dp_sgd,
            dp_epsilon=self._dp_epsilon,
        )

        dataset_path = await pipeline.prepare_dataset(convs)
        adapter_path = await pipeline.train(dataset_path, {})
        return str(adapter_path)

"""UNCASE Python SDK — programmatic access to the SCSF pipeline.

Usage:
    from uncase.sdk import Pipeline, SeedEngine, Generator, Evaluator, Trainer

    # Quick start
    pipeline = Pipeline(api_key="your-key")
    result = pipeline.generate(domain="automotive.sales", count=100)

    # Step by step
    engine = SeedEngine()
    seeds = engine.from_text("Vendedor: Hola\\nCliente: Hola", domain="automotive.sales")
"""

from uncase.sdk.client import UNCASEClient
from uncase.sdk.components import Evaluator, Generator, SeedEngine, Trainer
from uncase.sdk.pipeline import Pipeline

__all__ = [
    "Evaluator",
    "Generator",
    "Pipeline",
    "SeedEngine",
    "Trainer",
    "UNCASEClient",
]

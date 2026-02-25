"""Tests for SDK component wrappers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from uncase.sdk.components import Evaluator, Generator, SeedEngine, Trainer


class TestSeedEngineSDK:
    """Test SDK SeedEngine wrapper."""

    def test_init_local(self) -> None:
        engine = SeedEngine(local=True)
        assert engine._local is True

    def test_init_remote(self) -> None:
        engine = SeedEngine(local=False)
        assert engine._local is False

    def test_remote_not_implemented(self) -> None:
        engine = SeedEngine(local=False)
        with pytest.raises(NotImplementedError, match="Remote"):
            engine.from_text("test", "automotive.sales")

    async def test_afrom_text_local(self) -> None:
        mock_seed = MagicMock()
        mock_seed.model_dump.return_value = {"dominio": "automotive.sales", "idioma": "es"}

        with patch("uncase.sdk.components.SeedEngine._from_text_local", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = {"dominio": "automotive.sales", "idioma": "es"}
            engine = SeedEngine(local=True)
            result = await engine.afrom_text("Vendedor: Hola\nCliente: Buenos dias", "automotive.sales")
            assert result["dominio"] == "automotive.sales"


class TestGeneratorSDK:
    """Test SDK Generator wrapper."""

    def test_init_defaults(self) -> None:
        gen = Generator()
        assert gen._api_key is None
        assert gen._model is None

    def test_init_with_params(self) -> None:
        gen = Generator(api_key="test-key", model="gpt-4")
        assert gen._api_key == "test-key"
        assert gen._model == "gpt-4"


class TestEvaluatorSDK:
    """Test SDK Evaluator wrapper."""

    async def test_aevaluate(self) -> None:
        with patch("uncase.core.evaluator.evaluator.ConversationEvaluator") as mock_cls:
            mock_eval = mock_cls.return_value
            mock_report = MagicMock()
            mock_report.model_dump.return_value = {"passed": True, "composite_score": 0.85}
            mock_eval.evaluate = AsyncMock(return_value=mock_report)

            evaluator = Evaluator()
            # Create minimal valid data
            conv_data = {
                "seed_id": "test",
                "dominio": "automotive.sales",
                "idioma": "es",
                "turnos": [
                    {"turno": 1, "rol": "vendedor", "contenido": "Hola"},
                    {"turno": 2, "rol": "cliente", "contenido": "Buenos dias"},
                ],
                "es_sintetica": True,
            }
            seed_data = {
                "dominio": "automotive.sales",
                "idioma": "es",
                "roles": ["vendedor", "cliente"],
                "descripcion_roles": {"vendedor": "Asesor", "cliente": "Cliente"},
                "objetivo": "Test",
                "tono": "profesional",
                "pasos_turnos": {
                    "turnos_min": 2,
                    "turnos_max": 10,
                    "flujo_esperado": ["saludo"],
                },
                "parametros_factuales": {
                    "contexto": "Test",
                    "restricciones": [],
                    "herramientas": [],
                    "metadata": {},
                },
            }

            result = await evaluator.aevaluate(conv_data, seed_data)
            assert result["passed"] is True


class TestTrainerSDK:
    """Test SDK Trainer wrapper."""

    def test_init_defaults(self) -> None:
        trainer = Trainer()
        assert trainer._base_model == "meta-llama/Llama-3.1-8B"
        assert trainer._use_qlora is True
        assert trainer._use_dp_sgd is False
        assert trainer._dp_epsilon == 8.0

    def test_init_custom(self) -> None:
        trainer = Trainer(
            base_model="custom/model",
            use_qlora=False,
            use_dp_sgd=True,
            dp_epsilon=3.0,
            output_dir="./outputs/test/custom",
        )
        assert trainer._base_model == "custom/model"
        assert trainer._use_qlora is False
        assert trainer._use_dp_sgd is True
        assert trainer._dp_epsilon == 3.0
        assert trainer._output_dir == "./outputs/test/custom"

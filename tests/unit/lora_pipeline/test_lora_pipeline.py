"""Tests for the LoRA Pipeline — Layer 4 implementation.

All tests use synthetic/fictional data only and do NOT require
actual ML dependencies (torch, transformers, peft, trl, datasets, opacus).
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from uncase.core.lora_pipeline.config import (
    LoraConfig,
    PipelineConfig,
    PrivacyConfig,
    TrainingConfig,
)
from uncase.core.lora_pipeline.pipeline import (
    LoraPipeline,
    _estimate_tokens,
    _map_role,
)
from uncase.exceptions import DatasetPreparationError, MLDependencyError, TrainingError
from uncase.schemas.conversation import Conversation, ConversationTurn

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_turn(turno: int, rol: str, contenido: str) -> ConversationTurn:
    """Create a synthetic conversation turn."""
    return ConversationTurn(
        turno=turno,
        rol=rol,
        contenido=contenido,
        herramientas_usadas=[],
        metadata={},
    )


def _make_conversation(
    *,
    conversation_id: str = "test-conv-001",
    seed_id: str = "test-seed-001",
    dominio: str = "automotive.sales",
    idioma: str = "es",
    turnos: list[ConversationTurn] | None = None,
) -> Conversation:
    """Create a synthetic conversation with sensible defaults."""
    if turnos is None:
        turnos = [
            _make_turn(1, "vendedor", "Buenos dias, en que puedo ayudarle?"),
            _make_turn(2, "cliente", "Busco informacion sobre vehiculos nuevos."),
            _make_turn(
                3,
                "vendedor",
                "Con gusto, tenemos varias opciones disponibles.",
            ),
        ]
    return Conversation(
        conversation_id=conversation_id,
        seed_id=seed_id,
        dominio=dominio,
        idioma=idioma,
        turnos=turnos,
        es_sintetica=True,
        created_at="2026-02-25T00:00:00Z",
        metadata={"model": "test"},
    )


# ---------------------------------------------------------------------------
# Pipeline instantiation tests
# ---------------------------------------------------------------------------


class TestLoraPipelineInstantiation:
    """Verify LoraPipeline can be created with default and custom configs."""

    async def test_instantiation_with_defaults(self) -> None:
        pipeline = LoraPipeline()
        cfg = pipeline.config
        assert cfg.base_model == "meta-llama/Llama-3.1-8B"
        assert cfg.use_qlora is True
        assert cfg.lora.rank == 16
        assert cfg.lora.alpha == 32
        assert cfg.lora.dropout == pytest.approx(0.05)
        assert cfg.training.learning_rate == pytest.approx(2e-4)
        assert cfg.training.num_epochs == 3
        assert cfg.training.batch_size == 4
        assert cfg.privacy.use_dp_sgd is False
        assert cfg.privacy.epsilon == pytest.approx(8.0)

    async def test_instantiation_with_custom_config(self, tmp_path: Path) -> None:
        output_dir = str(tmp_path / "test-lora-output")
        pipeline = LoraPipeline(
            base_model="test-org/test-model-7B",
            output_dir=output_dir,
            lora_rank=64,
            lora_alpha=128,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj"],
            use_qlora=False,
            learning_rate=1e-3,
            num_epochs=5,
            batch_size=8,
            gradient_accumulation_steps=2,
            max_seq_length=4096,
            warmup_ratio=0.1,
            use_dp_sgd=True,
            dp_epsilon=4.0,
            dp_delta=1e-6,
            dp_max_grad_norm=0.5,
            mlflow_experiment="test-experiment",
        )
        cfg = pipeline.config
        assert cfg.base_model == "test-org/test-model-7B"
        assert cfg.output_dir == output_dir
        assert cfg.use_qlora is False
        assert cfg.mlflow_experiment == "test-experiment"
        assert cfg.lora.rank == 64
        assert cfg.lora.alpha == 128
        assert cfg.lora.dropout == pytest.approx(0.1)
        assert cfg.lora.target_modules == ["q_proj", "v_proj"]
        assert cfg.training.learning_rate == pytest.approx(1e-3)
        assert cfg.training.num_epochs == 5
        assert cfg.training.batch_size == 8
        assert cfg.training.gradient_accumulation_steps == 2
        assert cfg.training.max_seq_length == 4096
        assert cfg.training.warmup_ratio == pytest.approx(0.1)
        assert cfg.privacy.use_dp_sgd is True
        assert cfg.privacy.epsilon == pytest.approx(4.0)
        assert cfg.privacy.delta == pytest.approx(1e-6)
        assert cfg.privacy.max_grad_norm == pytest.approx(0.5)

    async def test_config_property_returns_pipeline_config(self) -> None:
        pipeline = LoraPipeline()
        assert isinstance(pipeline.config, PipelineConfig)

    async def test_config_contains_sub_configs(self) -> None:
        pipeline = LoraPipeline()
        assert isinstance(pipeline.config.lora, LoraConfig)
        assert isinstance(pipeline.config.training, TrainingConfig)
        assert isinstance(pipeline.config.privacy, PrivacyConfig)


# ---------------------------------------------------------------------------
# Role mapping tests
# ---------------------------------------------------------------------------


class TestMapRole:
    """Verify _map_role helper maps all UNCASE roles to ChatML roles."""

    async def test_vendedor_maps_to_assistant(self) -> None:
        assert _map_role("vendedor") == "assistant"

    async def test_asistente_maps_to_assistant(self) -> None:
        assert _map_role("asistente") == "assistant"

    async def test_cliente_maps_to_user(self) -> None:
        assert _map_role("cliente") == "user"

    async def test_usuario_maps_to_user(self) -> None:
        assert _map_role("usuario") == "user"

    async def test_sistema_maps_to_system(self) -> None:
        assert _map_role("sistema") == "system"

    async def test_herramienta_maps_to_assistant(self) -> None:
        assert _map_role("herramienta") == "assistant"

    async def test_english_assistant_passthrough(self) -> None:
        assert _map_role("assistant") == "assistant"

    async def test_english_user_passthrough(self) -> None:
        assert _map_role("user") == "user"

    async def test_english_system_passthrough(self) -> None:
        assert _map_role("system") == "system"

    async def test_unknown_role_defaults_to_user(self) -> None:
        assert _map_role("unknown_role") == "user"
        assert _map_role("moderador") == "user"
        assert _map_role("") == "user"


# ---------------------------------------------------------------------------
# Token estimation tests
# ---------------------------------------------------------------------------


class TestEstimateTokens:
    """Verify _estimate_tokens heuristic (4 chars per token)."""

    async def test_empty_string_returns_1(self) -> None:
        assert _estimate_tokens("") == 1

    async def test_short_text(self) -> None:
        # "Hola" = 4 chars => 4 // 4 = 1
        assert _estimate_tokens("Hola") == 1

    async def test_medium_text(self) -> None:
        # 20 chars => 20 // 4 = 5
        text = "a" * 20
        assert _estimate_tokens(text) == 5

    async def test_long_text(self) -> None:
        text = "x" * 400
        assert _estimate_tokens(text) == 100

    async def test_result_is_always_at_least_1(self) -> None:
        assert _estimate_tokens("ab") >= 1
        assert _estimate_tokens("") >= 1

    async def test_realistic_sentence(self) -> None:
        sentence = "Buenos dias, en que puedo ayudarle con su vehiculo?"
        result = _estimate_tokens(sentence)
        assert result == len(sentence) // 4


# ---------------------------------------------------------------------------
# Dataset preparation tests
# ---------------------------------------------------------------------------


class TestPrepareDataset:
    """Verify prepare_dataset converts conversations to JSONL correctly."""

    async def test_valid_conversations_creates_jsonl(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        conv = _make_conversation()

        dataset_path = await pipeline.prepare_dataset([conv])

        assert dataset_path.exists()
        assert dataset_path.suffix == ".jsonl"
        assert dataset_path.name == "train.jsonl"

    async def test_empty_list_raises_dataset_preparation_error(self) -> None:
        pipeline = LoraPipeline()
        with pytest.raises(DatasetPreparationError, match="No conversations provided"):
            await pipeline.prepare_dataset([])

    async def test_output_format_each_line_is_valid_json(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        conv = _make_conversation()

        dataset_path = await pipeline.prepare_dataset([conv])
        lines = dataset_path.read_text(encoding="utf-8").strip().split("\n")

        assert len(lines) == 1
        for line in lines:
            record = json.loads(line)
            assert "messages" in record
            assert isinstance(record["messages"], list)

    async def test_role_mapping_in_output(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        turnos = [
            _make_turn(1, "sistema", "Eres un asistente virtual."),
            _make_turn(2, "vendedor", "Bienvenido, como le puedo ayudar?"),
            _make_turn(3, "cliente", "Necesito informacion sobre precios."),
        ]
        conv = _make_conversation(turnos=turnos)

        dataset_path = await pipeline.prepare_dataset([conv])
        record = json.loads(dataset_path.read_text(encoding="utf-8").strip())

        roles = [m["role"] for m in record["messages"]]
        assert roles == ["system", "assistant", "user"]

    async def test_content_preserved_in_output(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        turnos = [
            _make_turn(1, "vendedor", "Buenos dias, en que puedo ayudarle?"),
            _make_turn(2, "cliente", "Busco informacion sobre vehiculos nuevos."),
        ]
        conv = _make_conversation(turnos=turnos)

        dataset_path = await pipeline.prepare_dataset([conv])
        record = json.loads(dataset_path.read_text(encoding="utf-8").strip())

        contents = [m["content"] for m in record["messages"]]
        assert contents[0] == "Buenos dias, en que puedo ayudarle?"
        assert contents[1] == "Busco informacion sobre vehiculos nuevos."

    async def test_multiple_conversations_produce_multiple_lines(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        convs = [
            _make_conversation(conversation_id="conv-001", seed_id="seed-001"),
            _make_conversation(conversation_id="conv-002", seed_id="seed-002"),
            _make_conversation(conversation_id="conv-003", seed_id="seed-003"),
        ]

        dataset_path = await pipeline.prepare_dataset(convs)
        lines = dataset_path.read_text(encoding="utf-8").strip().split("\n")

        assert len(lines) == 3
        for line in lines:
            record = json.loads(line)
            assert "messages" in record
            assert len(record["messages"]) == 3

    async def test_chatml_format_has_role_and_content_keys(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        conv = _make_conversation()

        dataset_path = await pipeline.prepare_dataset([conv])
        record = json.loads(dataset_path.read_text(encoding="utf-8").strip())

        for message in record["messages"]:
            assert set(message.keys()) == {"role", "content"}

    async def test_dataset_directory_created_automatically(self, tmp_path: Path) -> None:
        nested_dir = tmp_path / "deep" / "nested" / "dir"
        pipeline = LoraPipeline(output_dir=str(nested_dir))
        conv = _make_conversation()

        dataset_path = await pipeline.prepare_dataset([conv])
        assert dataset_path.parent.exists()
        assert dataset_path.parent.name == "datasets"

    async def test_herramienta_role_mapped_in_dataset(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        turnos = [
            _make_turn(1, "cliente", "Que opciones hay?"),
            _make_turn(2, "herramienta", "Resultado de busqueda: 5 vehiculos disponibles."),
            _make_turn(3, "vendedor", "Tenemos 5 opciones para usted."),
        ]
        conv = _make_conversation(turnos=turnos)

        dataset_path = await pipeline.prepare_dataset([conv])
        record = json.loads(dataset_path.read_text(encoding="utf-8").strip())

        roles = [m["role"] for m in record["messages"]]
        assert roles == ["user", "assistant", "assistant"]

    async def test_english_roles_passthrough_in_dataset(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        turnos = [
            _make_turn(1, "system", "You are a helpful assistant."),
            _make_turn(2, "user", "Hello, I need help."),
            _make_turn(3, "assistant", "Of course, how can I assist you?"),
        ]
        conv = _make_conversation(turnos=turnos, idioma="en")

        dataset_path = await pipeline.prepare_dataset([conv])
        record = json.loads(dataset_path.read_text(encoding="utf-8").strip())

        roles = [m["role"] for m in record["messages"]]
        assert roles == ["system", "user", "assistant"]

    async def test_unicode_content_preserved(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        turnos = [
            _make_turn(1, "vendedor", "Bienvenido! El precio es $25,000 MXN."),
            _make_turn(2, "cliente", "Tiene opciones mas economicas?"),
        ]
        conv = _make_conversation(turnos=turnos)

        dataset_path = await pipeline.prepare_dataset([conv])
        record = json.loads(dataset_path.read_text(encoding="utf-8").strip())

        assert "$25,000 MXN" in record["messages"][0]["content"]
        assert "economicas" in record["messages"][1]["content"]


# ---------------------------------------------------------------------------
# ML dependency error tests
# ---------------------------------------------------------------------------


def _make_ml_missing_modules() -> dict[str, None]:
    """Create a sys.modules patch dict that simulates missing ML packages.

    Sets torch, transformers, peft, trl, datasets, and opacus to None
    so that ``__import__`` raises ImportError for them.
    """
    packages = ("torch", "transformers", "peft", "trl", "datasets", "opacus")
    return dict.fromkeys(packages)


class TestTrainWithoutMLDeps:
    """Verify train() raises MLDependencyError when ML packages are absent."""

    async def test_train_raises_ml_dependency_error(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        dataset_path = tmp_path / "fake_dataset.jsonl"
        dataset_path.write_text('{"messages": []}\n', encoding="utf-8")

        with patch.dict(sys.modules, _make_ml_missing_modules()), pytest.raises(MLDependencyError):
            await pipeline.train(dataset_path, {})

    async def test_train_error_message_mentions_packages(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        dataset_path = tmp_path / "fake_dataset.jsonl"
        dataset_path.write_text('{"messages": []}\n', encoding="utf-8")

        with (
            patch.dict(sys.modules, _make_ml_missing_modules()),
            pytest.raises(MLDependencyError, match="uncase\\[ml\\]"),
        ):
            await pipeline.train(dataset_path, {})


class TestEvaluateWithoutMLDeps:
    """Verify evaluate_model() raises MLDependencyError when ML packages are absent."""

    async def test_evaluate_raises_ml_dependency_error(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        adapter_path = tmp_path / "fake_adapter"
        adapter_path.mkdir()

        with patch.dict(sys.modules, _make_ml_missing_modules()), pytest.raises(MLDependencyError):
            await pipeline.evaluate_model(adapter_path)

    async def test_evaluate_error_message_mentions_packages(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        adapter_path = tmp_path / "fake_adapter"
        adapter_path.mkdir()

        with (
            patch.dict(sys.modules, _make_ml_missing_modules()),
            pytest.raises(MLDependencyError, match="uncase\\[ml\\]"),
        ):
            await pipeline.evaluate_model(adapter_path)


# ---------------------------------------------------------------------------
# Path validation error tests
# ---------------------------------------------------------------------------


class TestTrainPathErrors:
    """Verify train() raises TrainingError for invalid paths."""

    async def test_train_nonexistent_dataset_raises_training_error(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        nonexistent = tmp_path / "does_not_exist.jsonl"

        # We need to get past the ML dependency check to test the path check.
        # Patch _check_ml_dependencies to be a no-op.
        with (
            patch(
                "uncase.core.lora_pipeline.pipeline._check_ml_dependencies",
                return_value=None,
            ),
            pytest.raises(TrainingError, match="Dataset file not found"),
        ):
            await pipeline.train(nonexistent, {})

    async def test_evaluate_nonexistent_adapter_raises_training_error(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        nonexistent = tmp_path / "no_such_adapter"

        with (
            patch(
                "uncase.core.lora_pipeline.pipeline._check_ml_dependencies",
                return_value=None,
            ),
            pytest.raises(TrainingError, match="Adapter directory not found"),
        ):
            await pipeline.evaluate_model(nonexistent)


# ---------------------------------------------------------------------------
# Exception hierarchy tests
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    """Verify LoRA pipeline exceptions inherit from UNCASEError."""

    async def test_ml_dependency_error_is_uncase_error(self) -> None:
        from uncase.exceptions import UNCASEError

        err = MLDependencyError("test")
        assert isinstance(err, UNCASEError)
        assert err.status_code == 503

    async def test_training_error_is_uncase_error(self) -> None:
        from uncase.exceptions import UNCASEError

        err = TrainingError("test")
        assert isinstance(err, UNCASEError)
        assert err.status_code == 500

    async def test_dataset_preparation_error_is_uncase_error(self) -> None:
        from uncase.exceptions import UNCASEError

        err = DatasetPreparationError("test")
        assert isinstance(err, UNCASEError)
        assert err.status_code == 500


# ---------------------------------------------------------------------------
# Integration-level: prepare_dataset produces valid training data
# ---------------------------------------------------------------------------


class TestPrepareDatasetIntegration:
    """End-to-end tests for the dataset preparation flow."""

    async def test_realistic_multi_domain_conversations(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))

        automotive_conv = _make_conversation(
            conversation_id="auto-001",
            seed_id="seed-auto-001",
            dominio="automotive.sales",
            turnos=[
                _make_turn(1, "sistema", "Contexto: concesionario de vehiculos premium."),
                _make_turn(2, "vendedor", "Bienvenido al concesionario. En que le puedo servir?"),
                _make_turn(3, "cliente", "Estoy interesado en un SUV familiar."),
                _make_turn(4, "vendedor", "Tenemos el modelo XR-500, muy popular entre familias."),
                _make_turn(5, "cliente", "Cual es el precio?"),
                _make_turn(6, "vendedor", "El precio base es de $45,000 USD con garantia de 5 anios."),
            ],
        )

        medical_conv = _make_conversation(
            conversation_id="med-001",
            seed_id="seed-med-001",
            dominio="medical.consultation",
            turnos=[
                _make_turn(1, "sistema", "Contexto: consulta medica general."),
                _make_turn(2, "asistente", "Buenos dias, soy el asistente virtual del consultorio."),
                _make_turn(3, "usuario", "Necesito agendar una cita para revision general."),
                _make_turn(4, "asistente", "Por supuesto, tenemos disponibilidad maniana a las 10am."),
            ],
        )

        dataset_path = await pipeline.prepare_dataset([automotive_conv, medical_conv])

        lines = dataset_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

        # Verify automotive conversation
        auto_record = json.loads(lines[0])
        assert len(auto_record["messages"]) == 6
        assert auto_record["messages"][0]["role"] == "system"
        assert auto_record["messages"][1]["role"] == "assistant"
        assert auto_record["messages"][2]["role"] == "user"

        # Verify medical conversation
        med_record = json.loads(lines[1])
        assert len(med_record["messages"]) == 4
        assert med_record["messages"][1]["role"] == "assistant"  # asistente -> assistant
        assert med_record["messages"][2]["role"] == "user"  # usuario -> user

    async def test_single_turn_conversation(self, tmp_path: Path) -> None:
        pipeline = LoraPipeline(output_dir=str(tmp_path / "outputs"))
        conv = _make_conversation(
            turnos=[_make_turn(1, "vendedor", "Bienvenido.")],
        )

        dataset_path = await pipeline.prepare_dataset([conv])
        record = json.loads(dataset_path.read_text(encoding="utf-8").strip())

        assert len(record["messages"]) == 1
        assert record["messages"][0]["role"] == "assistant"
        assert record["messages"][0]["content"] == "Bienvenido."

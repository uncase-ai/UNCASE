"""Tests for LoRA pipeline configuration models."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from uncase.core.lora_pipeline.config import (
    LoraConfig,
    PipelineConfig,
    PrivacyConfig,
    TrainingConfig,
)


class TestLoraConfigDefaults:
    """Verify LoraConfig default values match the spec."""

    async def test_default_rank(self) -> None:
        cfg = LoraConfig()
        assert cfg.rank == 16

    async def test_default_alpha(self) -> None:
        cfg = LoraConfig()
        assert cfg.alpha == 32

    async def test_default_dropout(self) -> None:
        cfg = LoraConfig()
        assert cfg.dropout == pytest.approx(0.05)

    async def test_default_target_modules_is_none(self) -> None:
        cfg = LoraConfig()
        assert cfg.target_modules is None


class TestLoraConfigValidation:
    """Verify LoraConfig field constraints."""

    async def test_rank_must_be_at_least_1(self) -> None:
        with pytest.raises(ValidationError):
            LoraConfig(rank=0)

    async def test_rank_must_be_at_most_256(self) -> None:
        with pytest.raises(ValidationError):
            LoraConfig(rank=257)

    async def test_rank_at_lower_bound(self) -> None:
        cfg = LoraConfig(rank=1)
        assert cfg.rank == 1

    async def test_rank_at_upper_bound(self) -> None:
        cfg = LoraConfig(rank=256)
        assert cfg.rank == 256

    async def test_dropout_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            LoraConfig(dropout=-0.01)

    async def test_dropout_must_be_at_most_1(self) -> None:
        with pytest.raises(ValidationError):
            LoraConfig(dropout=1.01)

    async def test_dropout_at_zero(self) -> None:
        cfg = LoraConfig(dropout=0.0)
        assert cfg.dropout == 0.0

    async def test_dropout_at_one(self) -> None:
        cfg = LoraConfig(dropout=1.0)
        assert cfg.dropout == 1.0

    async def test_alpha_must_be_at_least_1(self) -> None:
        with pytest.raises(ValidationError):
            LoraConfig(alpha=0)

    async def test_target_modules_accepts_list(self) -> None:
        cfg = LoraConfig(target_modules=["q_proj", "v_proj"])
        assert cfg.target_modules == ["q_proj", "v_proj"]


class TestTrainingConfigDefaults:
    """Verify TrainingConfig default values."""

    async def test_default_learning_rate(self) -> None:
        cfg = TrainingConfig()
        assert cfg.learning_rate == pytest.approx(2e-4)

    async def test_default_num_epochs(self) -> None:
        cfg = TrainingConfig()
        assert cfg.num_epochs == 3

    async def test_default_batch_size(self) -> None:
        cfg = TrainingConfig()
        assert cfg.batch_size == 4

    async def test_default_gradient_accumulation_steps(self) -> None:
        cfg = TrainingConfig()
        assert cfg.gradient_accumulation_steps == 4

    async def test_default_max_seq_length(self) -> None:
        cfg = TrainingConfig()
        assert cfg.max_seq_length == 2048

    async def test_default_warmup_ratio(self) -> None:
        cfg = TrainingConfig()
        assert cfg.warmup_ratio == pytest.approx(0.03)


class TestTrainingConfigValidation:
    """Verify TrainingConfig field constraints."""

    async def test_learning_rate_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            TrainingConfig(learning_rate=0.0)

    async def test_learning_rate_negative_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TrainingConfig(learning_rate=-1e-4)

    async def test_num_epochs_must_be_at_least_1(self) -> None:
        with pytest.raises(ValidationError):
            TrainingConfig(num_epochs=0)

    async def test_num_epochs_at_minimum(self) -> None:
        cfg = TrainingConfig(num_epochs=1)
        assert cfg.num_epochs == 1

    async def test_max_seq_length_must_be_at_least_128(self) -> None:
        with pytest.raises(ValidationError):
            TrainingConfig(max_seq_length=64)

    async def test_max_seq_length_at_minimum(self) -> None:
        cfg = TrainingConfig(max_seq_length=128)
        assert cfg.max_seq_length == 128

    async def test_batch_size_must_be_at_least_1(self) -> None:
        with pytest.raises(ValidationError):
            TrainingConfig(batch_size=0)

    async def test_warmup_ratio_must_be_between_0_and_1(self) -> None:
        with pytest.raises(ValidationError):
            TrainingConfig(warmup_ratio=-0.1)
        with pytest.raises(ValidationError):
            TrainingConfig(warmup_ratio=1.1)


class TestPrivacyConfigDefaults:
    """Verify PrivacyConfig default values."""

    async def test_default_use_dp_sgd(self) -> None:
        cfg = PrivacyConfig()
        assert cfg.use_dp_sgd is False

    async def test_default_epsilon(self) -> None:
        cfg = PrivacyConfig()
        assert cfg.epsilon == pytest.approx(8.0)

    async def test_default_delta(self) -> None:
        cfg = PrivacyConfig()
        assert cfg.delta == pytest.approx(1e-5)

    async def test_default_max_grad_norm(self) -> None:
        cfg = PrivacyConfig()
        assert cfg.max_grad_norm == pytest.approx(1.0)


class TestPrivacyConfigValidation:
    """Verify PrivacyConfig field constraints."""

    async def test_epsilon_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            PrivacyConfig(epsilon=0.0)

    async def test_delta_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            PrivacyConfig(delta=0.0)

    async def test_delta_must_be_less_than_1(self) -> None:
        with pytest.raises(ValidationError):
            PrivacyConfig(delta=1.0)

    async def test_max_grad_norm_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            PrivacyConfig(max_grad_norm=0.0)


class TestPipelineConfig:
    """Verify PipelineConfig combines sub-configs correctly."""

    async def test_default_base_model(self) -> None:
        cfg = PipelineConfig()
        assert cfg.base_model == "meta-llama/Llama-3.1-8B"

    async def test_default_output_dir(self) -> None:
        cfg = PipelineConfig()
        assert cfg.output_dir == "./outputs/lora"

    async def test_default_use_qlora(self) -> None:
        cfg = PipelineConfig()
        assert cfg.use_qlora is True

    async def test_default_mlflow_experiment_is_none(self) -> None:
        cfg = PipelineConfig()
        assert cfg.mlflow_experiment is None

    async def test_sub_configs_are_defaults(self) -> None:
        cfg = PipelineConfig()
        assert cfg.lora.rank == 16
        assert cfg.training.learning_rate == pytest.approx(2e-4)
        assert cfg.privacy.use_dp_sgd is False

    async def test_custom_sub_configs(self) -> None:
        cfg = PipelineConfig(
            base_model="custom/model",
            lora=LoraConfig(rank=64, alpha=128),
            training=TrainingConfig(num_epochs=5, learning_rate=1e-3),
            privacy=PrivacyConfig(use_dp_sgd=True, epsilon=4.0),
        )
        assert cfg.base_model == "custom/model"
        assert cfg.lora.rank == 64
        assert cfg.lora.alpha == 128
        assert cfg.training.num_epochs == 5
        assert cfg.training.learning_rate == pytest.approx(1e-3)
        assert cfg.privacy.use_dp_sgd is True
        assert cfg.privacy.epsilon == pytest.approx(4.0)

    async def test_serialization_roundtrip(self) -> None:
        original = PipelineConfig(
            base_model="test/model",
            lora=LoraConfig(rank=8, alpha=16, dropout=0.1),
            training=TrainingConfig(num_epochs=2, batch_size=8),
            privacy=PrivacyConfig(use_dp_sgd=True, epsilon=4.0),
        )
        json_str = original.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["base_model"] == "test/model"
        assert parsed["lora"]["rank"] == 8
        assert parsed["lora"]["alpha"] == 16
        assert parsed["training"]["num_epochs"] == 2
        assert parsed["training"]["batch_size"] == 8
        assert parsed["privacy"]["use_dp_sgd"] is True
        assert parsed["privacy"]["epsilon"] == pytest.approx(4.0)

    async def test_model_dump_json_returns_string(self) -> None:
        cfg = PipelineConfig()
        result = cfg.model_dump_json()
        assert isinstance(result, str)
        # Must be valid JSON
        json.loads(result)

    async def test_model_dump_contains_all_sections(self) -> None:
        cfg = PipelineConfig()
        data = cfg.model_dump()
        assert "lora" in data
        assert "training" in data
        assert "privacy" in data
        assert "base_model" in data
        assert "output_dir" in data
        assert "use_qlora" in data
        assert "mlflow_experiment" in data

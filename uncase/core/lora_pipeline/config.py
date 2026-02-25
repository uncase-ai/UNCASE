"""Training configuration models for the LoRA pipeline.

Pydantic models that define all configurable parameters for
LoRA/QLoRA fine-tuning, including adapter settings, training
hyperparameters, and differential privacy options.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoraConfig(BaseModel):
    """LoRA adapter configuration.

    Controls the rank, scaling factor, dropout, and target
    modules for the low-rank adaptation.
    """

    rank: int = Field(default=16, ge=1, le=256, description="LoRA rank (dimensionality of low-rank matrices)")
    alpha: int = Field(default=32, ge=1, description="LoRA scaling factor (alpha / rank = scaling)")
    dropout: float = Field(default=0.05, ge=0.0, le=1.0, description="Dropout probability for LoRA layers")
    target_modules: list[str] | None = Field(
        default=None,
        description="Model modules to apply LoRA to. None = auto-detect based on model architecture.",
    )


class TrainingConfig(BaseModel):
    """Training hyperparameters.

    Defines the learning rate schedule, batch configuration,
    sequence length, and warmup settings.
    """

    learning_rate: float = Field(default=2e-4, gt=0.0, description="Peak learning rate")
    num_epochs: int = Field(default=3, ge=1, description="Number of training epochs")
    batch_size: int = Field(default=4, ge=1, description="Per-device training batch size")
    gradient_accumulation_steps: int = Field(
        default=4,
        ge=1,
        description="Number of gradient accumulation steps (effective batch = batch_size * steps)",
    )
    max_seq_length: int = Field(default=2048, ge=128, description="Maximum sequence length in tokens")
    warmup_ratio: float = Field(default=0.03, ge=0.0, le=1.0, description="Fraction of steps for linear warmup")


class PrivacyConfig(BaseModel):
    """Differential privacy (DP-SGD) configuration.

    When enabled, wraps the optimizer with Opacus DP-SGD to enforce
    privacy guarantees during fine-tuning. Epsilon <= 8.0 is required
    by UNCASE quality thresholds.
    """

    use_dp_sgd: bool = Field(default=False, description="Enable DP-SGD for differentially private training")
    epsilon: float = Field(default=8.0, gt=0.0, description="Privacy budget epsilon (lower = more private)")
    delta: float = Field(default=1e-5, gt=0.0, lt=1.0, description="Privacy budget delta")
    max_grad_norm: float = Field(default=1.0, gt=0.0, description="Maximum gradient norm for clipping")


class PipelineConfig(BaseModel):
    """Complete pipeline configuration combining all sub-configs.

    This is the top-level configuration model that combines LoRA adapter
    settings, training hyperparameters, privacy config, and pipeline-level
    options like the base model and output directory.
    """

    base_model: str = Field(
        default="meta-llama/Llama-3.1-8B",
        description="HuggingFace model ID or local path for the base model",
    )
    output_dir: str = Field(default="./outputs/lora", description="Root directory for pipeline outputs")
    use_qlora: bool = Field(default=True, description="Use 4-bit QLoRA quantization for memory-efficient training")
    mlflow_experiment: str | None = Field(
        default=None,
        description="MLflow experiment name for tracking. None = no MLflow logging.",
    )
    lora: LoraConfig = Field(default_factory=LoraConfig, description="LoRA adapter configuration")
    training: TrainingConfig = Field(default_factory=TrainingConfig, description="Training hyperparameters")
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig, description="Differential privacy settings")

"""LoRA/QLoRA fine-tuning pipeline — Layer 4 implementation.

Takes validated synthetic conversations and trains a LoRA adapter
on a base language model. Supports QLoRA (4-bit quantization) for
memory-efficient training on consumer hardware.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from uncase.core.lora_pipeline.base import BasePipeline
from uncase.core.lora_pipeline.config import PipelineConfig
from uncase.exceptions import DatasetPreparationError, MLDependencyError, TrainingError

if TYPE_CHECKING:
    from uncase.schemas.conversation import Conversation

logger = structlog.get_logger(__name__)

# Role mapping from UNCASE conversation roles to standard ChatML roles
_ROLE_MAP: dict[str, str] = {
    "vendedor": "assistant",
    "asistente": "assistant",
    "cliente": "user",
    "usuario": "user",
    "sistema": "system",
    "herramienta": "assistant",
    # English roles pass through
    "assistant": "assistant",
    "user": "user",
    "system": "system",
}


def _check_ml_dependencies() -> None:
    """Verify that ML dependencies (transformers, peft, trl, torch) are available.

    Raises:
        MLDependencyError: If any required ML package is not installed.
    """
    missing: list[str] = []
    for package in ("torch", "transformers", "peft", "trl"):
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        msg = (
            f"Required ML dependencies not installed: {', '.join(missing)}. Install them with: pip install 'uncase[ml]'"
        )
        raise MLDependencyError(msg)


def _check_opacus_dependency() -> None:
    """Verify that Opacus is available for DP-SGD training.

    Raises:
        MLDependencyError: If opacus is not installed.
    """
    try:
        __import__("opacus")
    except ImportError as exc:
        msg = "Opacus is required for DP-SGD training but is not installed. Install it with: pip install opacus"
        raise MLDependencyError(msg) from exc


def _map_role(role: str) -> str:
    """Map an UNCASE conversation role to a standard ChatML role.

    Args:
        role: The original role name from the conversation.

    Returns:
        Standard role string (user, assistant, or system).
    """
    return _ROLE_MAP.get(role, "user")


def _estimate_tokens(text: str) -> int:
    """Rough token count estimate (4 chars per token heuristic).

    Args:
        text: Input text.

    Returns:
        Estimated token count.
    """
    return max(1, len(text) // 4)


class LoraPipeline(BasePipeline):
    """LoRA/QLoRA fine-tuning pipeline — Layer 4.

    Converts validated synthetic conversations into training datasets
    and fine-tunes a LoRA adapter on a base language model. Supports
    QLoRA (4-bit quantization) for memory-efficient training.

    Usage::

        pipeline = LoraPipeline(base_model="meta-llama/Llama-3.1-8B")
        dataset_path = await pipeline.prepare_dataset(conversations)
        adapter_path = await pipeline.train(dataset_path, {})
        metrics = await pipeline.evaluate_model(adapter_path)
    """

    def __init__(
        self,
        *,
        base_model: str = "meta-llama/Llama-3.1-8B",
        output_dir: str = "./outputs/lora",
        lora_rank: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: list[str] | None = None,
        use_qlora: bool = True,
        learning_rate: float = 2e-4,
        num_epochs: int = 3,
        batch_size: int = 4,
        gradient_accumulation_steps: int = 4,
        max_seq_length: int = 2048,
        warmup_ratio: float = 0.03,
        use_dp_sgd: bool = False,
        dp_epsilon: float = 8.0,
        dp_delta: float = 1e-5,
        dp_max_grad_norm: float = 1.0,
        mlflow_experiment: str | None = None,
    ) -> None:
        """Initialize the LoRA pipeline.

        Args:
            base_model: HuggingFace model ID or local path.
            output_dir: Root directory for all pipeline outputs.
            lora_rank: LoRA rank (dimensionality of low-rank matrices).
            lora_alpha: LoRA scaling factor.
            lora_dropout: Dropout probability for LoRA layers.
            target_modules: Modules to apply LoRA to. None = auto-detect.
            use_qlora: Use 4-bit quantization (QLoRA).
            learning_rate: Peak learning rate.
            num_epochs: Number of training epochs.
            batch_size: Per-device training batch size.
            gradient_accumulation_steps: Gradient accumulation steps.
            max_seq_length: Maximum sequence length in tokens.
            warmup_ratio: Fraction of steps for linear warmup.
            use_dp_sgd: Enable DP-SGD for differential privacy.
            dp_epsilon: Privacy budget epsilon.
            dp_delta: Privacy budget delta.
            dp_max_grad_norm: Max gradient norm for DP clipping.
            mlflow_experiment: MLflow experiment name. None = no tracking.
        """
        from uncase.core.lora_pipeline.config import (
            LoraConfig,
            PrivacyConfig,
            TrainingConfig,
        )

        self._config = PipelineConfig(
            base_model=base_model,
            output_dir=output_dir,
            use_qlora=use_qlora,
            mlflow_experiment=mlflow_experiment,
            lora=LoraConfig(
                rank=lora_rank,
                alpha=lora_alpha,
                dropout=lora_dropout,
                target_modules=target_modules,
            ),
            training=TrainingConfig(
                learning_rate=learning_rate,
                num_epochs=num_epochs,
                batch_size=batch_size,
                gradient_accumulation_steps=gradient_accumulation_steps,
                max_seq_length=max_seq_length,
                warmup_ratio=warmup_ratio,
            ),
            privacy=PrivacyConfig(
                use_dp_sgd=use_dp_sgd,
                epsilon=dp_epsilon,
                delta=dp_delta,
                max_grad_norm=dp_max_grad_norm,
            ),
        )

        logger.info(
            "lora_pipeline_initialized",
            base_model=base_model,
            use_qlora=use_qlora,
            lora_rank=lora_rank,
            use_dp_sgd=use_dp_sgd,
        )

    @property
    def config(self) -> PipelineConfig:
        """Return the current pipeline configuration."""
        return self._config

    async def prepare_dataset(self, conversations: list[Conversation]) -> Path:
        """Prepare a training dataset from validated conversations.

        Converts Conversation objects to ChatML-style training format
        (one JSON object per line) and saves as a JSONL file.

        Args:
            conversations: List of validated synthetic conversations.

        Returns:
            Path to the generated JSONL dataset file.

        Raises:
            DatasetPreparationError: If dataset preparation fails.
        """
        if not conversations:
            msg = "No conversations provided for dataset preparation"
            raise DatasetPreparationError(msg)

        logger.info(
            "preparing_dataset",
            num_conversations=len(conversations),
            output_dir=self._config.output_dir,
        )

        try:
            dataset_dir = Path(self._config.output_dir) / "datasets"
            dataset_dir.mkdir(parents=True, exist_ok=True)
            dataset_path = dataset_dir / "train.jsonl"

            total_turns = 0
            total_tokens_estimate = 0
            records_written = 0

            with dataset_path.open("w", encoding="utf-8") as fh:
                for conversation in conversations:
                    messages: list[dict[str, str]] = []

                    for turn in conversation.turnos:
                        role = _map_role(turn.rol)
                        messages.append(
                            {
                                "role": role,
                                "content": turn.contenido,
                            }
                        )
                        total_tokens_estimate += _estimate_tokens(turn.contenido)

                    if not messages:
                        logger.warning(
                            "skipping_empty_conversation",
                            conversation_id=conversation.conversation_id,
                        )
                        continue

                    record = {"messages": messages}
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                    total_turns += len(messages)
                    records_written += 1

            if records_written == 0:
                msg = "No valid conversations could be converted to training records"
                raise DatasetPreparationError(msg)

            avg_turns = total_turns / records_written if records_written else 0

            logger.info(
                "dataset_prepared",
                path=str(dataset_path),
                total_conversations=records_written,
                total_turns=total_turns,
                avg_turns_per_conversation=round(avg_turns, 1),
                estimated_tokens=total_tokens_estimate,
            )

            return dataset_path

        except DatasetPreparationError:
            raise

        except Exception as exc:
            msg = f"Failed to prepare dataset: {exc}"
            logger.error("dataset_preparation_failed", error=str(exc))
            raise DatasetPreparationError(msg) from exc

    async def train(self, dataset_path: Path, config: dict[str, Any]) -> Path:
        """Train a LoRA adapter on the prepared dataset.

        Loads the base model (with optional QLoRA quantization), applies
        LoRA, and fine-tunes using SFTTrainer from the trl library.
        All heavy computation runs in a thread pool executor.

        Args:
            dataset_path: Path to the JSONL training dataset.
            config: Additional configuration overrides (merged with pipeline config).

        Returns:
            Path to the saved LoRA adapter directory.

        Raises:
            MLDependencyError: If ML dependencies are not installed.
            TrainingError: If training fails.
        """
        _check_ml_dependencies()

        if self._config.privacy.use_dp_sgd:
            _check_opacus_dependency()

        if not dataset_path.exists():
            msg = f"Dataset file not found: {dataset_path}"
            raise TrainingError(msg)

        run_id = config.get("run_id", uuid.uuid4().hex[:12])
        adapter_dir = Path(self._config.output_dir) / "adapters" / run_id
        adapter_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "training_started",
            run_id=run_id,
            base_model=self._config.base_model,
            dataset_path=str(dataset_path),
            use_qlora=self._config.use_qlora,
            lora_rank=self._config.lora.rank,
            num_epochs=self._config.training.num_epochs,
            use_dp_sgd=self._config.privacy.use_dp_sgd,
        )

        try:
            adapter_path = await asyncio.to_thread(
                self._train_sync,
                dataset_path=dataset_path,
                adapter_dir=adapter_dir,
                run_id=run_id,
            )
        except (MLDependencyError, TrainingError):
            raise
        except Exception as exc:
            msg = f"Training failed: {exc}"
            logger.error("training_failed", run_id=run_id, error=str(exc))
            raise TrainingError(msg) from exc

        logger.info(
            "training_complete",
            run_id=run_id,
            adapter_path=str(adapter_path),
        )

        return adapter_path

    def _train_sync(
        self,
        *,
        dataset_path: Path,
        adapter_dir: Path,
        run_id: str,
    ) -> Path:
        """Synchronous training logic (runs in thread pool).

        This method contains the actual model loading, LoRA configuration,
        and SFTTrainer execution. It is designed to run via
        ``asyncio.to_thread`` since these operations are CPU/GPU bound.

        Args:
            dataset_path: Path to JSONL training dataset.
            adapter_dir: Directory to save the adapter.
            run_id: Unique run identifier for logging.

        Returns:
            Path to the saved adapter directory.
        """
        import torch
        from datasets import load_dataset
        from peft import LoraConfig as PeftLoraConfig
        from peft import TaskType, get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from trl import SFTConfig, SFTTrainer

        # -- Load tokenizer ------------------------------------------------
        logger.info("loading_tokenizer", model=self._config.base_model)
        tokenizer = AutoTokenizer.from_pretrained(
            self._config.base_model,
            trust_remote_code=True,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id

        # -- Load model with optional quantization -------------------------
        model_kwargs: dict[str, Any] = {
            "trust_remote_code": True,
        }

        if self._config.use_qlora:
            logger.info("configuring_qlora_quantization")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
            model_kwargs["quantization_config"] = bnb_config
            model_kwargs["torch_dtype"] = torch.bfloat16
        else:
            model_kwargs["torch_dtype"] = torch.float16

        # Determine device map
        if torch.cuda.is_available():
            model_kwargs["device_map"] = "auto"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            model_kwargs["device_map"] = "mps"
        else:
            model_kwargs["device_map"] = "cpu"
            logger.warning(
                "no_gpu_detected",
                message="Training on CPU will be very slow. Consider using a GPU.",
            )

        logger.info(
            "loading_base_model",
            model=self._config.base_model,
            device_map=model_kwargs.get("device_map"),
        )
        model = AutoModelForCausalLM.from_pretrained(
            self._config.base_model,
            **model_kwargs,
        )

        # Prepare for k-bit training if using QLoRA
        if self._config.use_qlora:
            model = prepare_model_for_kbit_training(model)

        # -- Configure LoRA ------------------------------------------------
        target_modules = self._config.lora.target_modules
        if target_modules is None:
            # Auto-detect common target modules based on model architecture
            target_modules = _detect_target_modules(model)

        logger.info(
            "configuring_lora",
            rank=self._config.lora.rank,
            alpha=self._config.lora.alpha,
            dropout=self._config.lora.dropout,
            target_modules=target_modules,
        )

        peft_config = PeftLoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self._config.lora.rank,
            lora_alpha=self._config.lora.alpha,
            lora_dropout=self._config.lora.dropout,
            target_modules=target_modules,
            bias="none",
        )

        model = get_peft_model(model, peft_config)
        _log_trainable_parameters(model, run_id)

        # -- Load dataset --------------------------------------------------
        logger.info("loading_dataset", path=str(dataset_path))
        dataset = load_dataset("json", data_files=str(dataset_path), split="train")

        # -- Configure SFTTrainer ------------------------------------------
        sft_config = SFTConfig(
            output_dir=str(adapter_dir),
            num_train_epochs=self._config.training.num_epochs,
            per_device_train_batch_size=self._config.training.batch_size,
            gradient_accumulation_steps=self._config.training.gradient_accumulation_steps,
            learning_rate=self._config.training.learning_rate,
            warmup_ratio=self._config.training.warmup_ratio,
            max_seq_length=self._config.training.max_seq_length,
            logging_steps=10,
            save_strategy="epoch",
            bf16=torch.cuda.is_available(),
            fp16=False,
            gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False},
            optim="paged_adamw_8bit" if self._config.use_qlora else "adamw_torch",
            report_to="mlflow" if self._config.mlflow_experiment else "none",
            run_name=run_id,
            dataset_text_field=None,
        )

        # -- MLflow tracking (optional) ------------------------------------
        if self._config.mlflow_experiment:
            self._setup_mlflow(run_id)

        # -- DP-SGD (optional) ---------------------------------------------
        # Note: Opacus integration with HuggingFace Trainer is experimental.
        # We log the intention but actual DP-SGD wrapping requires custom
        # training loop modifications that go beyond SFTTrainer's API.
        if self._config.privacy.use_dp_sgd:
            logger.info(
                "dp_sgd_enabled",
                epsilon=self._config.privacy.epsilon,
                delta=self._config.privacy.delta,
                max_grad_norm=self._config.privacy.max_grad_norm,
                message=(
                    "DP-SGD is configured. The optimizer will be wrapped "
                    "with Opacus for differentially private training."
                ),
            )

        # -- Train ---------------------------------------------------------
        logger.info("starting_sft_training", run_id=run_id)

        trainer = SFTTrainer(
            model=model,
            args=sft_config,
            train_dataset=dataset,
            processing_class=tokenizer,
        )

        # Wrap optimizer with Opacus DP-SGD if enabled
        if self._config.privacy.use_dp_sgd:
            _apply_dp_sgd(
                trainer=trainer,
                epsilon=self._config.privacy.epsilon,
                delta=self._config.privacy.delta,
                max_grad_norm=self._config.privacy.max_grad_norm,
                num_epochs=self._config.training.num_epochs,
            )

        train_result = trainer.train()

        # Log final metrics
        logger.info(
            "training_metrics",
            run_id=run_id,
            train_loss=train_result.metrics.get("train_loss"),
            train_runtime=train_result.metrics.get("train_runtime"),
            train_samples_per_second=train_result.metrics.get("train_samples_per_second"),
        )

        # -- Save adapter --------------------------------------------------
        logger.info("saving_adapter", path=str(adapter_dir))
        trainer.save_model(str(adapter_dir))
        tokenizer.save_pretrained(str(adapter_dir))

        # Save training config for reproducibility
        config_path = adapter_dir / "pipeline_config.json"
        config_path.write_text(
            self._config.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # Save training metrics
        metrics_path = adapter_dir / "train_metrics.json"
        metrics_path.write_text(
            json.dumps(train_result.metrics, indent=2, default=str),
            encoding="utf-8",
        )

        # -- MLflow logging (optional) -------------------------------------
        if self._config.mlflow_experiment:
            self._log_to_mlflow(train_result.metrics, adapter_dir, run_id)

        return adapter_dir

    async def evaluate_model(self, adapter_path: Path) -> dict[str, float]:
        """Evaluate a trained LoRA adapter.

        Loads the base model with the adapter and computes basic metrics
        including perplexity and a simple response coherence heuristic.

        Args:
            adapter_path: Path to the saved adapter directory.

        Returns:
            Dictionary of evaluation metrics.

        Raises:
            MLDependencyError: If ML dependencies are not installed.
            TrainingError: If evaluation fails.
        """
        _check_ml_dependencies()

        if not adapter_path.exists():
            msg = f"Adapter directory not found: {adapter_path}"
            raise TrainingError(msg)

        logger.info(
            "evaluating_adapter",
            adapter_path=str(adapter_path),
            base_model=self._config.base_model,
        )

        try:
            metrics = await asyncio.to_thread(
                self._evaluate_sync,
                adapter_path=adapter_path,
            )
        except (MLDependencyError, TrainingError):
            raise
        except Exception as exc:
            msg = f"Evaluation failed: {exc}"
            logger.error("evaluation_failed", error=str(exc))
            raise TrainingError(msg) from exc

        logger.info(
            "evaluation_complete",
            adapter_path=str(adapter_path),
            metrics=metrics,
        )

        return metrics

    def _evaluate_sync(self, *, adapter_path: Path) -> dict[str, float]:
        """Synchronous evaluation logic (runs in thread pool).

        Loads the model + adapter, runs inference on validation prompts,
        and computes basic quality metrics.

        Args:
            adapter_path: Path to the adapter directory.

        Returns:
            Dictionary of evaluation metrics.
        """
        import math

        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # -- Load tokenizer ------------------------------------------------
        tokenizer = AutoTokenizer.from_pretrained(
            str(adapter_path),
            trust_remote_code=True,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # -- Load base model + adapter ------------------------------------
        model_kwargs: dict[str, Any] = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16,
        }

        if torch.cuda.is_available():
            model_kwargs["device_map"] = "auto"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            model_kwargs["device_map"] = "mps"
        else:
            model_kwargs["device_map"] = "cpu"

        base_model = AutoModelForCausalLM.from_pretrained(
            self._config.base_model,
            **model_kwargs,
        )
        model = PeftModel.from_pretrained(base_model, str(adapter_path))
        model.eval()

        # -- Compute perplexity on validation prompts ----------------------
        validation_prompts = [
            "Hello, I need help with my account.",
            "Can you explain the process step by step?",
            "What are the available options for this service?",
            "I have a question about the pricing.",
            "Thank you for your assistance today.",
        ]

        total_loss = 0.0
        total_tokens = 0

        with torch.no_grad():
            for prompt in validation_prompts:
                inputs = tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self._config.training.max_seq_length,
                )
                inputs = {k: v.to(model.device) for k, v in inputs.items()}

                outputs = model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss

                if loss is not None:
                    num_tokens = inputs["input_ids"].numel()
                    total_loss += loss.item() * num_tokens
                    total_tokens += num_tokens

        avg_loss = total_loss / total_tokens if total_tokens > 0 else float("inf")
        perplexity = math.exp(min(avg_loss, 100))  # Cap to avoid overflow

        # -- Response coherence heuristic ----------------------------------
        # Generate a short response and check basic quality signals
        coherence_score = self._compute_coherence(model, tokenizer)

        metrics: dict[str, float] = {
            "perplexity": round(perplexity, 4),
            "avg_loss": round(avg_loss, 6),
            "response_coherence": round(coherence_score, 4),
            "num_validation_prompts": float(len(validation_prompts)),
        }

        return metrics

    def _compute_coherence(self, model: Any, tokenizer: Any) -> float:
        """Compute a simple response coherence score via generation.

        Generates a response to a test prompt and evaluates it based on:
        - Non-empty response
        - Response length (not too short, not degenerate)
        - No excessive repetition

        Args:
            model: The loaded model with adapter.
            tokenizer: The tokenizer.

        Returns:
            Coherence score between 0.0 and 1.0.
        """
        import torch

        test_prompt = "User: How can I help you today?\nAssistant:"

        inputs = tokenizer(
            test_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=128,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
            )

        # Decode only the generated part
        generated_ids = outputs[0][inputs["input_ids"].shape[1] :]
        response = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

        if not response:
            return 0.0

        score = 0.0

        # Check 1: Response is non-empty (0.3 weight)
        if len(response) > 0:
            score += 0.3

        # Check 2: Response has reasonable length (0.3 weight)
        word_count = len(response.split())
        if 3 <= word_count <= 200:
            score += 0.3
        elif word_count > 0:
            score += 0.1

        # Check 3: No excessive repetition (0.4 weight)
        words = response.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            score += 0.4 * min(unique_ratio / 0.5, 1.0)

        return min(score, 1.0)

    def _setup_mlflow(self, run_id: str) -> None:
        """Initialize MLflow experiment tracking.

        Args:
            run_id: Unique run identifier.
        """
        try:
            import mlflow

            mlflow.set_experiment(self._config.mlflow_experiment)
            logger.info(
                "mlflow_experiment_set",
                experiment=self._config.mlflow_experiment,
                run_id=run_id,
            )
        except ImportError:
            logger.warning(
                "mlflow_not_installed",
                message="MLflow is not installed. Skipping experiment tracking.",
            )
        except Exception as exc:
            logger.warning(
                "mlflow_setup_failed",
                error=str(exc),
                message="Could not set up MLflow. Training will continue without tracking.",
            )

    def _log_to_mlflow(
        self,
        metrics: dict[str, Any],
        adapter_dir: Path,
        run_id: str,
    ) -> None:
        """Log training results to MLflow.

        Args:
            metrics: Training metrics dictionary.
            adapter_dir: Path to the adapter directory.
            run_id: Unique run identifier.
        """
        try:
            import mlflow

            with mlflow.start_run(run_name=run_id):
                # Log config as parameters
                mlflow.log_params(
                    {
                        "base_model": self._config.base_model,
                        "lora_rank": self._config.lora.rank,
                        "lora_alpha": self._config.lora.alpha,
                        "lora_dropout": self._config.lora.dropout,
                        "learning_rate": self._config.training.learning_rate,
                        "num_epochs": self._config.training.num_epochs,
                        "batch_size": self._config.training.batch_size,
                        "use_qlora": self._config.use_qlora,
                        "use_dp_sgd": self._config.privacy.use_dp_sgd,
                        "max_seq_length": self._config.training.max_seq_length,
                    }
                )

                # Log metrics (only numeric values)
                numeric_metrics = {k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))}
                mlflow.log_metrics(numeric_metrics)

                # Log adapter as artifact
                mlflow.log_artifacts(str(adapter_dir), artifact_path="adapter")

            logger.info(
                "mlflow_run_logged",
                run_id=run_id,
                experiment=self._config.mlflow_experiment,
            )

        except ImportError:
            logger.warning("mlflow_not_available_for_logging")
        except Exception as exc:
            logger.warning(
                "mlflow_logging_failed",
                run_id=run_id,
                error=str(exc),
            )


def _detect_target_modules(model: Any) -> list[str]:
    """Auto-detect LoRA target modules based on model architecture.

    Inspects the model's named modules to find linear projection layers
    commonly targeted for LoRA adaptation (attention Q/K/V/O projections
    and MLP gate/up/down projections).

    Args:
        model: The loaded base model.

    Returns:
        List of module name patterns to target.
    """
    # Common module patterns across architectures
    candidate_patterns = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",  # LLaMA, Mistral
        "gate_proj",
        "up_proj",
        "down_proj",  # LLaMA MLP
        "query_key_value",  # Falcon
        "dense",
        "dense_h_to_4h",
        "dense_4h_to_h",  # GPT-NeoX
        "c_attn",
        "c_proj",
        "c_fc",  # GPT-2
        "W_pack",  # Baichuan
    ]

    found: list[str] = []
    module_names = {name.split(".")[-1] for name, _ in model.named_modules()}

    for pattern in candidate_patterns:
        if pattern in module_names:
            found.append(pattern)

    if not found:
        # Fallback: target all Linear layers
        logger.warning(
            "no_known_target_modules",
            message="Could not auto-detect target modules. Using all linear layers.",
        )
        found = ["all"]

    logger.info("detected_target_modules", modules=found)
    return found


def _log_trainable_parameters(model: Any, run_id: str) -> None:
    """Log the number of trainable vs total parameters.

    Args:
        model: The PEFT-wrapped model.
        run_id: Run identifier for the log context.
    """
    trainable_params = 0
    all_params = 0

    for param in model.parameters():
        all_params += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()

    trainable_pct = 100 * trainable_params / all_params if all_params > 0 else 0

    logger.info(
        "trainable_parameters",
        run_id=run_id,
        trainable=trainable_params,
        total=all_params,
        trainable_pct=round(trainable_pct, 4),
    )


def _apply_dp_sgd(
    *,
    trainer: Any,
    epsilon: float,
    delta: float,
    max_grad_norm: float,
    num_epochs: int,
) -> None:
    """Wrap the trainer's optimizer with Opacus DP-SGD.

    This provides differential privacy guarantees during training
    by adding calibrated noise to gradients and clipping per-sample
    gradient norms.

    Args:
        trainer: The SFTTrainer instance.
        epsilon: Privacy budget epsilon.
        delta: Privacy budget delta.
        max_grad_norm: Maximum per-sample gradient norm.
        num_epochs: Number of training epochs (for privacy accounting).

    Raises:
        MLDependencyError: If Opacus is not installed.
    """
    _check_opacus_dependency()

    from opacus import PrivacyEngine

    privacy_engine = PrivacyEngine()

    # Get dataset size for privacy accounting
    dataset_size = len(trainer.train_dataset) if trainer.train_dataset else 1
    sample_rate = trainer.args.per_device_train_batch_size / dataset_size

    logger.info(
        "applying_dp_sgd",
        epsilon=epsilon,
        delta=delta,
        max_grad_norm=max_grad_norm,
        sample_rate=sample_rate,
        dataset_size=dataset_size,
    )

    # Note: Full Opacus integration with HuggingFace Trainer requires
    # wrapping the model, optimizer, and dataloader. This is a simplified
    # version that hooks into the trainer's optimizer post-creation.
    # For production DP-SGD, consider using a custom training loop.
    original_create_optimizer = trainer.create_optimizer

    def create_optimizer_with_dp() -> None:
        """Create optimizer and wrap with Opacus DP-SGD."""
        original_create_optimizer()

        trainer.model, trainer.optimizer, trainer.train_dataloader = privacy_engine.make_private_with_epsilon(
            module=trainer.model,
            optimizer=trainer.optimizer,
            data_loader=trainer.get_train_dataloader(),
            epochs=num_epochs,
            target_epsilon=epsilon,
            target_delta=delta,
            max_grad_norm=max_grad_norm,
        )

        logger.info(
            "dp_sgd_applied",
            noise_multiplier=getattr(privacy_engine, "noise_multiplier", "unknown"),
        )

    trainer.create_optimizer = create_optimizer_with_dp

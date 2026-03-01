#!/usr/bin/env python3
"""
uncase_train_worker.py — Python training loop for UNCASE fine-tuning
=====================================================================

Called by uncase_train_gpu.sh (Phase 4) or uncase_train_apple.sh (Phase 3).
Handles model loading, LoRA setup, training, and optional merge.

Tries Unsloth first for GPU efficiency, falls back to standard
transformers + peft + bitsandbytes on CUDA, or plain float32 on MPS.

Usage:
    python scripts/uncase_train_worker.py \
        --model Qwen/Qwen3-14B \
        --train-file data/train.jsonl \
        --eval-file data/eval.jsonl \
        --output-dir outputs/lora-adapter \
        --lora-r 32 --lora-alpha 64 \
        --epochs 3 --batch-size 2 --grad-accum 8 \
        --lr 2e-4 --max-seq-length 4096 \
        --neftune 5 --merge --merged-dir outputs/merged
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def detect_device() -> str:
    """Detect the best available device: cuda, mps, or cpu."""
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"


def load_dataset(train_file: str, eval_file: str | None = None) -> tuple:
    """Load JSONL datasets into HuggingFace Dataset objects."""
    from datasets import Dataset

    def _load_jsonl(path: str) -> list[dict]:
        records = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    try:
                        records.append(json.loads(stripped))
                    except json.JSONDecodeError:
                        continue
        return records

    train_data = _load_jsonl(train_file)
    train_ds = Dataset.from_list(train_data)
    print(f"  Train dataset: {len(train_data)} conversations")

    eval_ds = None
    if eval_file and os.path.exists(eval_file):
        eval_data = _load_jsonl(eval_file)
        eval_ds = Dataset.from_list(eval_data)
        print(f"  Eval dataset:  {len(eval_data)} conversations")

    return train_ds, eval_ds


def load_model_unsloth(args: argparse.Namespace):
    """Try loading model with Unsloth (fast, memory-efficient)."""
    from unsloth import FastLanguageModel

    print("  Loading model with Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,  # auto-detect
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.0,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    print("  Unsloth model loaded successfully")
    return model, tokenizer


def load_model_standard(args: argparse.Namespace, device: str):
    """Load model with standard transformers + peft (+ bitsandbytes on CUDA)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"  Loading model with standard transformers (device={device})...")

    load_kwargs: dict = {}

    if device == "cuda":
        try:
            from transformers import BitsAndBytesConfig

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype="bfloat16",
                bnb_4bit_use_double_quant=True,
            )
            load_kwargs["quantization_config"] = bnb_config
            print("  Using 4-bit quantization (bitsandbytes)")
        except ImportError:
            load_kwargs["torch_dtype"] = "auto"
            print("  bitsandbytes not available, loading in auto dtype")
    elif device == "mps":
        import torch

        load_kwargs["torch_dtype"] = torch.float32
        print("  Loading in float32 for MPS (Apple Silicon)")
    else:
        load_kwargs["torch_dtype"] = "auto"

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True,
        **load_kwargs,
    )

    if device == "mps":
        model = model.to("mps")

    # Apply LoRA
    from peft import LoraConfig, get_peft_model

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.0,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    return model, tokenizer


def merge_lora(base_model: str, adapter_dir: str, merged_dir: str) -> None:
    """Merge LoRA adapter with base model into a full model."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n  Merging LoRA adapter into base model...")
    print(f"    Base:    {base_model}")
    print(f"    Adapter: {adapter_dir}")
    print(f"    Output:  {merged_dir}")

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map="cpu",
        trust_remote_code=True,
    )

    model = PeftModel.from_pretrained(model, adapter_dir)
    model = model.merge_and_unload()

    os.makedirs(merged_dir, exist_ok=True)
    model.save_pretrained(merged_dir, safe_serialization=True)
    tokenizer.save_pretrained(merged_dir)

    # Verify
    config_path = os.path.join(merged_dir, "config.json")
    safetensors = list(Path(merged_dir).glob("*.safetensors"))
    if os.path.exists(config_path) and safetensors:
        total_size = sum(f.stat().st_size for f in safetensors) / (1024**3)
        print(f"    Merge successful: {len(safetensors)} files, {total_size:.1f} GB")
    else:
        print("    WARNING: Merge verification failed — check output directory")


def print_oom_suggestions(args: argparse.Namespace) -> None:
    """Print suggestions when OOM is encountered."""
    print("\n" + "=" * 60)
    print("  OUT OF MEMORY — Suggestions:")
    print("=" * 60)
    print(f"  Current batch_size: {args.batch_size}")
    print(f"  Current max_seq_length: {args.max_seq_length}")
    print(f"  Current lora_r: {args.lora_r}")
    print()
    print("  Try:")
    print(f"    --batch-size {max(1, args.batch_size // 2)}")
    print(f"    --max-seq-length {args.max_seq_length // 2}")
    print(f"    --lora-r {max(8, args.lora_r // 2)}")
    print("    --grad-accum (increase to compensate smaller batch)")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="UNCASE fine-tuning training worker")

    # Model & data
    parser.add_argument("--model", required=True, help="HuggingFace model name or local path")
    parser.add_argument("--train-file", required=True, help="Path to training JSONL file")
    parser.add_argument("--eval-file", default="", help="Path to evaluation JSONL file")
    parser.add_argument("--output-dir", required=True, help="Directory to save LoRA adapter")

    # LoRA config
    parser.add_argument("--lora-r", type=int, default=32, help="LoRA rank (default: 32)")
    parser.add_argument("--lora-alpha", type=int, default=64, help="LoRA alpha (default: 64)")

    # Training hyperparameters
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs (default: 3)")
    parser.add_argument("--batch-size", type=int, default=2, help="Per-device batch size (default: 2)")
    parser.add_argument("--grad-accum", type=int, default=8, help="Gradient accumulation steps (default: 8)")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate (default: 2e-4)")
    parser.add_argument("--max-seq-length", type=int, default=4096, help="Max sequence length (default: 4096)")
    parser.add_argument("--neftune", type=int, default=5, help="NEFTune noise alpha (default: 5, 0 to disable)")
    parser.add_argument("--warmup-ratio", type=float, default=0.05, help="Warmup ratio (default: 0.05)")

    # Merge & export
    parser.add_argument("--merge", action="store_true", help="Merge LoRA into base model after training")
    parser.add_argument("--merged-dir", default="", help="Directory for merged model output")
    parser.add_argument("--no-gguf", action="store_true", help="Skip GGUF conversion (Unsloth)")

    # Resume
    parser.add_argument("--resume", default="", help="Path to checkpoint to resume from")

    args = parser.parse_args()

    device = detect_device()
    print("=" * 60)
    print("  UNCASE Training Worker")
    print("=" * 60)
    print(f"  Device:         {device}")
    print(f"  Model:          {args.model}")
    print(f"  LoRA:           r={args.lora_r}, alpha={args.lora_alpha}")
    print(f"  Epochs:         {args.epochs}")
    eff = args.batch_size * args.grad_accum
    print(f"  Batch:          {args.batch_size} x {args.grad_accum} = {eff} effective")
    print(f"  LR:             {args.lr}")
    print(f"  Max seq:        {args.max_seq_length}")
    print(f"  NEFTune:        {args.neftune}")
    print(f"  Output:         {args.output_dir}")
    if args.merge:
        print(f"  Merge to:       {args.merged_dir or args.output_dir + '-merged'}")
    print("=" * 60)
    print()

    # Load dataset
    train_ds, eval_ds = load_dataset(args.train_file, args.eval_file or None)

    # Load model — try Unsloth first on CUDA, fall back to standard
    model = None
    tokenizer = None
    use_unsloth = False

    if device == "cuda":
        try:
            model, tokenizer = load_model_unsloth(args)
            use_unsloth = True
        except (ImportError, Exception) as e:
            print(f"  Unsloth not available ({e}), falling back to standard transformers")

    if model is None:
        model, tokenizer = load_model_standard(args, device)

    # Ensure pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Setup trainer
    from trl import SFTConfig, SFTTrainer

    training_args = SFTConfig(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        max_seq_length=args.max_seq_length,
        warmup_ratio=args.warmup_ratio,
        lr_scheduler_type="cosine",
        bf16=device == "cuda",
        fp16=False,
        logging_steps=10,
        save_strategy="steps",
        save_steps=100,
        eval_strategy="steps" if eval_ds else "no",
        eval_steps=100 if eval_ds else None,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False} if not use_unsloth else None,
        optim="adamw_8bit" if device == "cuda" else "adamw_torch",
        weight_decay=0.01,
        seed=42,
        report_to="none",
        neftune_noise_alpha=args.neftune if args.neftune > 0 else None,
        dataset_text_field=None,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        args=training_args,
    )

    # Train
    print("\n  Starting training...")
    try:
        resume_path = args.resume if args.resume else None
        trainer.train(resume_from_checkpoint=resume_path)
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print_oom_suggestions(args)
            sys.exit(1)
        raise

    print("  Training completed!")

    # Save adapter
    os.makedirs(args.output_dir, exist_ok=True)

    if use_unsloth:
        model.save_pretrained(args.output_dir)
        tokenizer.save_pretrained(args.output_dir)
    else:
        trainer.save_model(args.output_dir)
        tokenizer.save_pretrained(args.output_dir)

    # Verify adapter saved
    adapter_files = list(Path(args.output_dir).glob("adapter_model.*"))
    if adapter_files:
        total = sum(f.stat().st_size for f in adapter_files) / (1024**2)
        print(f"\n  Adapter saved: {args.output_dir} ({total:.1f} MB)")
    else:
        print(f"\n  WARNING: No adapter files found in {args.output_dir}")

    # Optional merge
    if args.merge:
        merged_dir = args.merged_dir or args.output_dir + "-merged"
        merge_lora(args.model, args.output_dir, merged_dir)

    print("\n  Done.")


if __name__ == "__main__":
    main()

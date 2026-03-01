#!/usr/bin/env bash
# ============================================================
# UNCASE — Apple Silicon Fine-Tuning Script
# ============================================================
#
# For MacBook Pro with M4/M5 Pro (24GB unified memory).
# Uses MPS backend, float32 precision, conservative LoRA.
#
# Limitations vs GPU script:
#   - No bitsandbytes (CUDA-only)
#   - No Unsloth (CUDA-only)
#   - No flash-attention (CUDA-only)
#   - No quantization (QLoRA not supported on MPS)
#   - float32 only (MPS fp16 training has numerical issues)
#   - Models up to ~8B parameters (24GB unified memory)
#
# Usage:
#   # Quick hardware check
#   bash scripts/uncase_train_apple.sh --check-only
#
#   # Train a 3B model (comfortable)
#   bash scripts/uncase_train_apple.sh \
#     --dataset data/train.jsonl \
#     --model meta-llama/Llama-3.2-3B
#
#   # Train an 8B model (tight memory)
#   bash scripts/uncase_train_apple.sh \
#     --dataset data/train.jsonl \
#     --model meta-llama/Llama-3.1-8B \
#     --lora-r 8 --epochs 2 --max-seq-length 1024
#
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Logging ---
log()  { echo "[$(date +'%H:%M:%S')] $*"; }
warn() { echo "[$(date +'%H:%M:%S')] WARN: $*"; }
die()  { echo "[$(date +'%H:%M:%S')] FATAL: $*"; exit 1; }

# --- Defaults ---
MODEL="meta-llama/Llama-3.2-3B"
DATASET=""
EVAL_DATASET=""
HF_REPO=""
OUTPUT_DIR="./outputs/apple-silicon"
MERGED_DIR=""
LORA_R=""
LORA_ALPHA=""
EPOCHS=""
BATCH_SIZE=""
GRAD_ACCUM=""
LEARNING_RATE=""
MAX_SEQ_LENGTH=""
NEFTUNE=""
SYSTEM_PROMPT_FILE=""

CHECK_ONLY=false
DRY_RUN=false
SKIP_CLEANING=false
DO_MERGE=false
HF_PRIVATE=false

# --- Parse CLI flags ---
while [ $# -gt 0 ]; do
    case "$1" in
        --model)            shift; MODEL="${1:?--model requires an argument}" ;;
        --model=*)          MODEL="${1#--model=}" ;;
        --dataset)          shift; DATASET="${1:?--dataset requires an argument}" ;;
        --dataset=*)        DATASET="${1#--dataset=}" ;;
        --eval-dataset)     shift; EVAL_DATASET="${1:?--eval-dataset requires an argument}" ;;
        --eval-dataset=*)   EVAL_DATASET="${1#--eval-dataset=}" ;;
        --hf-repo)          shift; HF_REPO="${1:?--hf-repo requires an argument}" ;;
        --hf-repo=*)        HF_REPO="${1#--hf-repo=}" ;;
        --output-dir)       shift; OUTPUT_DIR="${1:?--output-dir requires an argument}" ;;
        --output-dir=*)     OUTPUT_DIR="${1#--output-dir=}" ;;
        --merged-dir)       shift; MERGED_DIR="${1:?--merged-dir requires an argument}" ;;
        --merged-dir=*)     MERGED_DIR="${1#--merged-dir=}" ;;
        --lora-r)           shift; LORA_R="${1:?--lora-r requires an argument}" ;;
        --lora-r=*)         LORA_R="${1#--lora-r=}" ;;
        --lora-alpha)       shift; LORA_ALPHA="${1:?--lora-alpha requires an argument}" ;;
        --lora-alpha=*)     LORA_ALPHA="${1#--lora-alpha=}" ;;
        --epochs)           shift; EPOCHS="${1:?--epochs requires an argument}" ;;
        --epochs=*)         EPOCHS="${1#--epochs=}" ;;
        --batch-size)       shift; BATCH_SIZE="${1:?--batch-size requires an argument}" ;;
        --batch-size=*)     BATCH_SIZE="${1#--batch-size=}" ;;
        --grad-accum)       shift; GRAD_ACCUM="${1:?--grad-accum requires an argument}" ;;
        --grad-accum=*)     GRAD_ACCUM="${1#--grad-accum=}" ;;
        --lr)               shift; LEARNING_RATE="${1:?--lr requires an argument}" ;;
        --lr=*)             LEARNING_RATE="${1#--lr=}" ;;
        --max-seq-length)   shift; MAX_SEQ_LENGTH="${1:?--max-seq-length requires an argument}" ;;
        --max-seq-length=*) MAX_SEQ_LENGTH="${1#--max-seq-length=}" ;;
        --neftune)          shift; NEFTUNE="${1:?--neftune requires an argument}" ;;
        --neftune=*)        NEFTUNE="${1#--neftune=}" ;;
        --system-prompt)    shift; SYSTEM_PROMPT_FILE="${1:?--system-prompt requires an argument}" ;;
        --system-prompt=*)  SYSTEM_PROMPT_FILE="${1#--system-prompt=}" ;;
        --check-only)       CHECK_ONLY=true ;;
        --skip-cleaning)    SKIP_CLEANING=true ;;
        --merge)            DO_MERGE=true ;;
        --hf-private)       HF_PRIVATE=true ;;
        --dry-run)          DRY_RUN=true ;;
        --help|-h)
            echo "Usage: bash $(basename "$0") [OPTIONS]"
            echo ""
            echo "Apple Silicon fine-tuning for UNCASE (24GB M4/M5 Pro)."
            echo ""
            echo "Model & Data:"
            echo "  --model NAME           Model name (default: meta-llama/Llama-3.2-3B)"
            echo "  --dataset PATH         Training JSONL file (required unless --check-only)"
            echo "  --eval-dataset PATH    Evaluation JSONL file"
            echo "  --hf-repo USER/REPO    HuggingFace repo for upload"
            echo "  --output-dir PATH      Output directory (default: ./outputs/apple-silicon)"
            echo ""
            echo "Training:"
            echo "  --epochs N             Training epochs (default: auto from advisor)"
            echo "  --lr RATE              Learning rate (default: auto)"
            echo "  --lora-r N             LoRA rank (default: 8)"
            echo "  --lora-alpha N         LoRA alpha (default: 16)"
            echo "  --batch-size N         Batch size (default: 1)"
            echo "  --max-seq-length N     Max sequence length (default: 1024)"
            echo ""
            echo "Pipeline:"
            echo "  --check-only           Hardware check only, no training"
            echo "  --skip-cleaning        Skip data cleaning pipeline"
            echo "  --merge                Merge LoRA into base after training"
            echo "  --dry-run              Validate only, no execution"
            exit 0
            ;;
        *)  warn "Unknown flag: $1" ;;
    esac
    shift
done

# ============================================================
# PHASE 0: System Validation
# ============================================================

log "============================================================"
log "  UNCASE Apple Silicon Fine-Tuning"
log "============================================================"

# Verify macOS
if [ "$(uname)" != "Darwin" ]; then
    die "This script is for macOS only. Use uncase_train_gpu.sh for Linux GPU servers."
fi

# Verify Apple Silicon
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    die "Apple Silicon required (found: $ARCH). Intel Macs are not supported."
fi

CPU_BRAND=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "unknown")
log "CPU: $CPU_BRAND"

# Check unified memory
TOTAL_MEM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
TOTAL_MEM_GB=$((TOTAL_MEM_BYTES / 1073741824))
log "Unified memory: ${TOTAL_MEM_GB} GB"

# Available memory estimate
AVAILABLE_MEM_GB=$((TOTAL_MEM_GB - 10))  # Reserve ~10GB for system + apps
if [ "$AVAILABLE_MEM_GB" -lt 8 ]; then
    warn "Very low available memory (~${AVAILABLE_MEM_GB} GB for training)"
fi
log "Estimated available for training: ~${AVAILABLE_MEM_GB} GB"

# Check MPS backend
MPS_AVAILABLE=$(python3 -c "
import torch
print('true' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'false')
" 2>/dev/null || echo "false")

if [ "$MPS_AVAILABLE" != "true" ]; then
    warn "MPS backend not available. Training will use CPU (very slow)."
    warn "Install PyTorch >= 2.1 for MPS support."
else
    log "MPS backend: available"
fi

# Torch version
TORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)" 2>/dev/null || echo "not installed")
log "PyTorch: $TORCH_VERSION"

# Disk space
DISK_FREE_GB=$(df -g . | tail -1 | awk '{print $4}')
log "Disk free: ${DISK_FREE_GB} GB"
if [ "$DISK_FREE_GB" -lt 20 ]; then
    warn "Low disk space (${DISK_FREE_GB}GB). Need ~20GB for model + outputs."
fi

# Compatibility matrix
log ""
log "Model compatibility (${TOTAL_MEM_GB}GB unified memory):"
log "  3B models:    OK (comfortable, ~3GB model)"
log "  7-8B models:  OK (tight, LoRA rank <= 8, batch = 1)"
if [ "$TOTAL_MEM_GB" -ge 36 ]; then
    log "  13-14B models: POSSIBLE (very tight, may OOM)"
else
    log "  13-14B models: NOT RECOMMENDED (will likely OOM)"
fi
log ""

if [ "$CHECK_ONLY" = "true" ]; then
    log "Hardware check complete (--check-only)."
    exit 0
fi

# Validate dataset is specified
if [ -z "$DATASET" ]; then
    die "No dataset specified. Use --dataset PATH"
fi

# ============================================================
# PHASE 1: Environment Setup
# ============================================================

log "=== PHASE 1: Environment Setup ==="

# Create output structure
ADAPTER_DIR="${OUTPUT_DIR}/lora-adapter"
LOGS_DIR="${OUTPUT_DIR}/logs"
CLEANED_DIR="${OUTPUT_DIR}/cleaned"
mkdir -p "$ADAPTER_DIR" "$LOGS_DIR" "$CLEANED_DIR"

LOG_FILE="${LOGS_DIR}/train-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

if [ "$DRY_RUN" = "false" ]; then
    log "Installing dependencies..."

    # Core training deps (skip CUDA-only packages silently)
    pip install -q torch torchvision 2>/dev/null || true
    pip install -q transformers peft trl accelerate datasets huggingface_hub safetensors 2>/dev/null || \
        die "Failed to install training dependencies"

    # Explicitly skip CUDA-only packages
    # bitsandbytes: CUDA-only quantization
    # unsloth: CUDA-only optimization
    # flash-attn: CUDA-only attention

    log "Dependencies installed (skipped CUDA-only packages: bitsandbytes, unsloth, flash-attn)"
fi

# ============================================================
# PHASE 2: Dataset Preparation
# ============================================================

log ""
log "=== PHASE 2: Dataset Preparation ==="

if [ ! -f "$DATASET" ]; then
    die "Dataset file not found: $DATASET"
fi

TRAIN_COUNT=$(wc -l < "$DATASET" | xargs)
log "Dataset: $TRAIN_COUNT conversations"

if [ "$TRAIN_COUNT" -gt 5000 ]; then
    warn "Large dataset ($TRAIN_COUNT conversations) — training will be slow on Apple Silicon."
    warn "Consider using a subset or a GPU server for datasets > 5K."
fi

ADVISOR_JSON="${CLEANED_DIR}/advisor.json"

if [ "$SKIP_CLEANING" = "true" ]; then
    log "Skipping data cleaning (--skip-cleaning)"
    CLEAN_TRAIN="$DATASET"
    CLEAN_EVAL="${EVAL_DATASET}"
elif [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would clean dataset: $DATASET"
    CLEAN_TRAIN="$DATASET"
    CLEAN_EVAL="${EVAL_DATASET}"
else
    # Detect model size from name
    MODEL_SIZE="3"
    if echo "$MODEL" | grep -qiE "3b|3B|2\.7|2\.8"; then
        MODEL_SIZE="3"
    elif echo "$MODEL" | grep -qiE "7b|7B|8b|8B"; then
        MODEL_SIZE="8"
    elif echo "$MODEL" | grep -qiE "13b|13B|14b|14B"; then
        MODEL_SIZE="14"
    fi

    PREPARE_ARGS="--input $DATASET --output-dir $CLEANED_DIR"
    PREPARE_ARGS="$PREPARE_ARGS --advise --vram $AVAILABLE_MEM_GB --model-size $MODEL_SIZE"
    PREPARE_ARGS="$PREPARE_ARGS --dedup --filter-patterns --validate-tools"

    if [ -z "$EVAL_DATASET" ]; then
        PREPARE_ARGS="$PREPARE_ARGS --split --eval-ratio 0.1"
    fi

    if [ -n "$SYSTEM_PROMPT_FILE" ] && [ -f "$SYSTEM_PROMPT_FILE" ]; then
        PREPARE_ARGS="$PREPARE_ARGS --system-prompt $SYSTEM_PROMPT_FILE"
    fi

    log "Running data quality pipeline..."
    # shellcheck disable=SC2086
    python3 "${SCRIPT_DIR}/uncase_prepare_dataset.py" $PREPARE_ARGS

    CLEAN_TRAIN="${CLEANED_DIR}/train.jsonl"
    CLEAN_EVAL="${CLEANED_DIR}/eval.jsonl"

    if [ ! -f "$CLEAN_TRAIN" ]; then
        warn "Cleaned train file not found, using original dataset"
        CLEAN_TRAIN="$DATASET"
    fi
fi

# Read advisor recommendations
if [ -f "$ADVISOR_JSON" ]; then
    log "Reading training advisor recommendations..."
    ADV_EPOCHS=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['epochs_max'])" 2>/dev/null || echo "")
    ADV_LR=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['learning_rate'])" 2>/dev/null || echo "")
    ADV_LORA_R=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['lora_r'])" 2>/dev/null || echo "")
    ADV_LORA_ALPHA=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['lora_alpha'])" 2>/dev/null || echo "")
    ADV_NEFTUNE=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['neftune_noise'])" 2>/dev/null || echo "")

    [ -z "$EPOCHS" ]        && [ -n "$ADV_EPOCHS" ]     && EPOCHS="$ADV_EPOCHS"
    [ -z "$LEARNING_RATE" ] && [ -n "$ADV_LR" ]         && LEARNING_RATE="$ADV_LR"
    [ -z "$LORA_R" ]        && [ -n "$ADV_LORA_R" ]     && LORA_R="$ADV_LORA_R"
    [ -z "$LORA_ALPHA" ]    && [ -n "$ADV_LORA_ALPHA" ] && LORA_ALPHA="$ADV_LORA_ALPHA"
    [ -z "$NEFTUNE" ]       && [ -n "$ADV_NEFTUNE" ]    && NEFTUNE="$ADV_NEFTUNE"
fi

# Apple Silicon conservative defaults (override advisor if too aggressive)
EPOCHS="${EPOCHS:-3}"
LEARNING_RATE="${LEARNING_RATE:-1e-4}"
BATCH_SIZE="${BATCH_SIZE:-1}"
GRAD_ACCUM="${GRAD_ACCUM:-16}"
NEFTUNE="${NEFTUNE:-5}"

# Force conservative LoRA for limited memory
LORA_R="${LORA_R:-8}"
LORA_ALPHA="${LORA_ALPHA:-16}"

# Cap LoRA rank for Apple Silicon
if [ "$LORA_R" -gt 16 ]; then
    warn "LoRA rank $LORA_R is high for Apple Silicon. Capping at 16."
    LORA_R=16
    LORA_ALPHA=32
fi

# Cap sequence length for memory
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-1024}"
if [ "$MAX_SEQ_LENGTH" -gt 2048 ]; then
    warn "Max seq length $MAX_SEQ_LENGTH may cause OOM on Apple Silicon. Capping at 2048."
    MAX_SEQ_LENGTH=2048
fi

# Warn about large models
if echo "$MODEL" | grep -qiE "13b|14b|32b|70b"; then
    warn "Model $MODEL is very large for ${TOTAL_MEM_GB}GB unified memory."
    warn "Expect OOM errors. Consider using a 3B or 7B model instead."
fi

# ============================================================
# PHASE 3: Training
# ============================================================

log ""
log "=== PHASE 3: Training ==="

EFFECTIVE=$((BATCH_SIZE * GRAD_ACCUM))
log "Training configuration:"
log "  Model:          $MODEL"
log "  Device:         MPS (Apple Silicon)"
log "  Memory:         ${TOTAL_MEM_GB}GB unified (${AVAILABLE_MEM_GB}GB available)"
log "  LoRA:           r=$LORA_R, alpha=$LORA_ALPHA"
log "  Epochs:         $EPOCHS"
log "  Batch:          ${BATCH_SIZE} x ${GRAD_ACCUM} = ${EFFECTIVE} effective"
log "  LR:             $LEARNING_RATE"
log "  Max seq:        $MAX_SEQ_LENGTH"
log "  NEFTune:        $NEFTUNE"
log "  Precision:      float32 (MPS requirement)"
log ""

if [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would train with above configuration"
else
    TRAIN_ARGS="--model $MODEL"
    TRAIN_ARGS="$TRAIN_ARGS --train-file ${CLEAN_TRAIN:-$DATASET}"
    if [ -n "${CLEAN_EVAL:-}" ] && [ -f "${CLEAN_EVAL:-}" ]; then
        TRAIN_ARGS="$TRAIN_ARGS --eval-file $CLEAN_EVAL"
    elif [ -n "$EVAL_DATASET" ] && [ -f "$EVAL_DATASET" ]; then
        TRAIN_ARGS="$TRAIN_ARGS --eval-file $EVAL_DATASET"
    fi
    TRAIN_ARGS="$TRAIN_ARGS --output-dir $ADAPTER_DIR"
    TRAIN_ARGS="$TRAIN_ARGS --lora-r $LORA_R --lora-alpha $LORA_ALPHA"
    TRAIN_ARGS="$TRAIN_ARGS --epochs $EPOCHS --batch-size $BATCH_SIZE --grad-accum $GRAD_ACCUM"
    TRAIN_ARGS="$TRAIN_ARGS --lr $LEARNING_RATE --max-seq-length $MAX_SEQ_LENGTH"
    TRAIN_ARGS="$TRAIN_ARGS --neftune $NEFTUNE --no-gguf"

    if [ "$DO_MERGE" = "true" ]; then
        MERGED_DIR="${MERGED_DIR:-${OUTPUT_DIR}/merged}"
        TRAIN_ARGS="$TRAIN_ARGS --merge --merged-dir $MERGED_DIR"
        warn "Merge enabled — expect temporary 2x memory spike during merge"
    fi

    log "Starting training (this may take a while on Apple Silicon)..."
    log ""

    set +e
    # shellcheck disable=SC2086
    python3 "${SCRIPT_DIR}/uncase_train_worker.py" $TRAIN_ARGS
    TRAIN_EXIT=$?
    set -e

    if [ "$TRAIN_EXIT" -ne 0 ]; then
        if [ "$TRAIN_EXIT" -eq 1 ]; then
            die "Training failed (likely OOM). Try: --lora-r 8 --batch-size 1 --max-seq-length 512"
        else
            die "Training failed with exit code $TRAIN_EXIT"
        fi
    fi
fi

# ============================================================
# PHASE 4: Validation & Export
# ============================================================

log ""
log "=== PHASE 4: Validation & Export ==="

if [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would validate and optionally upload"
else
    # Verify adapter
    if [ -f "$ADAPTER_DIR/adapter_model.safetensors" ] || [ -f "$ADAPTER_DIR/adapter_model.bin" ]; then
        ADAPTER_SIZE=$(du -sh "$ADAPTER_DIR" | cut -f1)
        log "Adapter saved: $ADAPTER_DIR ($ADAPTER_SIZE)"
    else
        warn "No adapter files found — training may have failed silently"
    fi

    # Upload to HuggingFace
    if [ -n "$HF_REPO" ] && [ -n "${HF_TOKEN:-}" ]; then
        UPLOAD_DIR="$ADAPTER_DIR"
        if [ -n "$MERGED_DIR" ] && [ -f "$MERGED_DIR/config.json" ]; then
            UPLOAD_DIR="$MERGED_DIR"
        fi

        PRIVATE_FLAG=""
        if [ "$HF_PRIVATE" = "true" ]; then
            PRIVATE_FLAG="private=True,"
        fi

        log "Uploading to HuggingFace: $HF_REPO..."
        python3 -c "
from huggingface_hub import HfApi
import os
api = HfApi(token=os.environ['HF_TOKEN'])
api.create_repo(repo_id='$HF_REPO', repo_type='model', exist_ok=True, ${PRIVATE_FLAG})
api.upload_folder(
    folder_path='$UPLOAD_DIR',
    repo_id='$HF_REPO',
    repo_type='model',
    commit_message='UNCASE Apple Silicon fine-tuned model',
)
print('Upload complete')
" 2>/dev/null && log "Upload complete: https://huggingface.co/$HF_REPO" || \
            warn "HuggingFace upload failed"
    elif [ -n "$HF_REPO" ]; then
        warn "HF_TOKEN not set, skipping upload"
    fi
fi

# Final summary
log ""
log "============================================================"
log "  UNCASE APPLE SILICON TRAINING COMPLETE"
log "============================================================"
log "  Device:         ${CPU_BRAND}"
log "  Memory:         ${TOTAL_MEM_GB}GB unified"
log "  Model:          $MODEL"
log "  Adapter:        $ADAPTER_DIR"
if [ -n "$MERGED_DIR" ] && [ -f "$MERGED_DIR/config.json" 2>/dev/null ]; then
    log "  Merged:         $MERGED_DIR"
fi
if [ -n "$HF_REPO" ]; then
    log "  HF Repo:        $HF_REPO"
fi
log "  Log:            $LOG_FILE"
log "============================================================"

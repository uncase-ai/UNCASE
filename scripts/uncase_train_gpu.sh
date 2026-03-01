#!/usr/bin/env bash
# ============================================================
# UNCASE — Generic GPU Fine-Tuning Pipeline
# ============================================================
#
# Universal training orchestrator for any model, dataset, and
# cloud GPU provider (vast.ai, Lambda, RunPod, local).
#
# Phases:
#   0: Configuration & CLI Parsing
#   1: System Prerequisites
#   2: Python Dependencies
#   3: Dataset Download & Preparation + Training Advisor
#   4: Fine-Tuning (adaptive parameters)
#   5: Merge LoRA → Full Model
#   6: Upload to HuggingFace
#   7-10: Service Deployment (optional, behind --deploy flag)
#
# Usage:
#   bash scripts/uncase_train_gpu.sh \
#     --model Qwen/Qwen3-14B \
#     --dataset data/train.jsonl \
#     --hf-repo myuser/my-model-v1 \
#     --output-dir ./outputs
#
#   # Dry run (validate everything, no execution):
#   bash scripts/uncase_train_gpu.sh --dry-run --dataset data/train.jsonl
#
#   # Skip training, deploy existing model:
#   bash scripts/uncase_train_gpu.sh --skip-training --skip-merge \
#     --model-path /path/to/merged --deploy
#
# ============================================================

set -euo pipefail

# ============================================================
# PHASE 0: Configuration & CLI Parsing
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Logging ---
log()  { echo "[$(date +'%H:%M:%S')] $*"; }
warn() { echo "[$(date +'%H:%M:%S')] WARN: $*"; }
die()  { echo "[$(date +'%H:%M:%S')] FATAL: $*"; exit 1; }

# --- PID tracking for cleanup ---
MY_PID=$$
MY_PPID=$PPID
VLLM_PID=""
FASTAPI_PID=""
TUNNEL_PID=""

cleanup() {
    log "Cleaning up..."
    [ -n "$TUNNEL_PID" ]  && kill "$TUNNEL_PID"  2>/dev/null || true
    [ -n "$FASTAPI_PID" ] && kill "$FASTAPI_PID" 2>/dev/null || true
    [ -n "$VLLM_PID" ]    && kill "$VLLM_PID"    2>/dev/null || true
    wait 2>/dev/null || true
    log "Cleanup complete."
}

trap cleanup EXIT INT TERM

safe_kill() {
    local pattern="$1"
    local pids
    pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    for pid in $pids; do
        if [ "$pid" = "$MY_PID" ] || [ "$pid" = "$MY_PPID" ] || [ "$pid" = "1" ]; then
            continue
        fi
        local cmd
        cmd=$(ps -p "$pid" -o args= 2>/dev/null || true)
        if [ -n "$cmd" ]; then
            log "  Terminating PID $pid: ${cmd:0:80}"
            kill -15 "$pid" 2>/dev/null || true
        fi
    done
}

wait_for_service() {
    local name="$1"
    local url="$2"
    local max_seconds="${3:-120}"
    local interval=5
    local max_retries=$((max_seconds / interval))

    log "Waiting for $name ($url, max ${max_seconds}s)..."
    for i in $(seq 1 "$max_retries"); do
        if curl -sf "$url" > /dev/null 2>&1; then
            log "$name is ready! (${i}x${interval}s)"
            return 0
        fi
        sleep "$interval"
    done
    warn "$name did not respond after ${max_seconds}s"
    return 1
}

# --- Defaults ---
MODEL="Qwen/Qwen3-14B"
DATASET=""
EVAL_DATASET=""
HF_REPO=""
OUTPUT_DIR="./outputs/lora-adapter"
MERGED_DIR=""
LORA_R=""
LORA_ALPHA=""
EPOCHS=""
BATCH_SIZE=""
GRAD_ACCUM=""
LEARNING_RATE=""
MAX_SEQ_LENGTH=""
NEFTUNE=""
WARMUP_RATIO="0.05"

SYSTEM_PROMPT_FILE=""
SKIP_TRAINING=false
SKIP_MERGE=false
SKIP_DEPLOY=true
SKIP_TUNNEL=true
SKIP_CLEANING=false
DRY_RUN=false
HF_PRIVATE=false
USE_UV=false
RESUME_CHECKPOINT=""
MODEL_PATH=""

VLLM_PORT=8001
FASTAPI_PORT=8081
SERVED_MODEL="uncase-model"

CF_TUNNEL_CRED=""
CF_TUNNEL_ID=""
CF_TUNNEL_DOMAIN=""

# --- Load .env if present ---
if [ -f ".env" ]; then
    log "Loading .env file..."
    set -a
    # shellcheck source=/dev/null
    source .env
    set +a
fi

# Map UNCASE_TRAIN_* env vars to defaults
MODEL="${UNCASE_TRAIN_MODEL:-$MODEL}"
DATASET="${UNCASE_TRAIN_DATASET:-$DATASET}"
HF_REPO="${UNCASE_TRAIN_HF_REPO:-$HF_REPO}"
OUTPUT_DIR="${UNCASE_TRAIN_OUTPUT_DIR:-$OUTPUT_DIR}"

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
        --model-path)       shift; MODEL_PATH="${1:?--model-path requires an argument}" ;;
        --model-path=*)     MODEL_PATH="${1#--model-path=}" ;;
        --resume)           shift; RESUME_CHECKPOINT="${1:?--resume requires an argument}" ;;
        --resume=*)         RESUME_CHECKPOINT="${1#--resume=}" ;;
        --served-model)     shift; SERVED_MODEL="${1:?--served-model requires an argument}" ;;
        --served-model=*)   SERVED_MODEL="${1#--served-model=}" ;;
        --vllm-port)        shift; VLLM_PORT="${1:?--vllm-port requires an argument}" ;;
        --vllm-port=*)      VLLM_PORT="${1#--vllm-port=}" ;;
        --api-port)         shift; FASTAPI_PORT="${1:?--api-port requires an argument}" ;;
        --api-port=*)       FASTAPI_PORT="${1#--api-port=}" ;;
        --skip-training)    SKIP_TRAINING=true ;;
        --skip-merge)       SKIP_MERGE=true ;;
        --skip-cleaning)    SKIP_CLEANING=true ;;
        --deploy)           SKIP_DEPLOY=false ;;
        --tunnel)           SKIP_TUNNEL=false ;;
        --hf-private)       HF_PRIVATE=true ;;
        --use-uv)           USE_UV=true ;;
        --dry-run)          DRY_RUN=true ;;
        --help|-h)
            echo "Usage: bash $(basename "$0") [OPTIONS]"
            echo ""
            echo "Model & Data:"
            echo "  --model NAME           HuggingFace model (default: Qwen/Qwen3-14B)"
            echo "  --dataset PATH         Training dataset JSONL file (required)"
            echo "  --eval-dataset PATH    Evaluation dataset JSONL file"
            echo "  --hf-repo USER/REPO    HuggingFace repo for upload"
            echo "  --output-dir PATH      LoRA adapter output (default: ./outputs/lora-adapter)"
            echo "  --merged-dir PATH      Merged model output directory"
            echo "  --system-prompt PATH   System prompt file to inject"
            echo ""
            echo "Training Hyperparameters (auto-configured by advisor if omitted):"
            echo "  --epochs N             Number of training epochs"
            echo "  --lr RATE              Learning rate (e.g., 2e-4)"
            echo "  --lora-r N             LoRA rank"
            echo "  --lora-alpha N         LoRA alpha"
            echo "  --batch-size N         Per-device batch size"
            echo "  --grad-accum N         Gradient accumulation steps"
            echo "  --max-seq-length N     Maximum sequence length"
            echo "  --neftune N            NEFTune noise alpha (0 to disable)"
            echo ""
            echo "Pipeline Control:"
            echo "  --skip-training        Skip fine-tuning (Phase 4)"
            echo "  --skip-merge           Skip LoRA merge (Phase 5)"
            echo "  --skip-cleaning        Skip data cleaning pipeline"
            echo "  --deploy               Enable service deployment (Phases 7-10)"
            echo "  --tunnel               Enable Cloudflare tunnel"
            echo "  --model-path PATH      Use pre-merged model (implies --skip-training --skip-merge)"
            echo "  --resume PATH          Resume from checkpoint"
            echo "  --hf-private           Upload as private HF repo"
            echo "  --use-uv              Use uv instead of pip"
            echo "  --dry-run              Validate everything, no execution"
            echo ""
            echo "Deployment:"
            echo "  --vllm-port PORT       vLLM port (default: 8001)"
            echo "  --api-port PORT        FastAPI port (default: 8081)"
            echo "  --served-model NAME    vLLM served model name"
            exit 0
            ;;
        *)  warn "Unknown flag: $1" ;;
    esac
    shift
done

# --- Derived values ---
if [ -n "$MODEL_PATH" ]; then
    MERGED_DIR="$MODEL_PATH"
    SKIP_TRAINING=true
    SKIP_MERGE=true
    log "Using pre-existing model: $MODEL_PATH"
fi

if [ -z "$MERGED_DIR" ]; then
    MERGED_DIR="${OUTPUT_DIR}-merged"
fi

# --- Enable logging to file ---
LOG_FILE="/tmp/uncase-train-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

log "============================================================"
log "  UNCASE GPU Fine-Tuning Pipeline"
log "============================================================"
log "  Model:       $MODEL"
log "  Dataset:     ${DATASET:-'(not specified)'}"
log "  Output:      $OUTPUT_DIR"
log "  HF Repo:     ${HF_REPO:-'(none)'}"
log "  Dry run:     $DRY_RUN"
log "  Log file:    $LOG_FILE"
log "============================================================"

if [ -z "$DATASET" ] && [ "$SKIP_TRAINING" = "false" ]; then
    die "No dataset specified. Use --dataset PATH or --skip-training"
fi

# ============================================================
# PHASE 1: System Prerequisites
# ============================================================

log ""
log "=== PHASE 1: System Prerequisites ==="

# Check OS
if [ "$(uname)" != "Linux" ]; then
    warn "This script is designed for Linux GPU servers."
    warn "For macOS, use uncase_train_apple.sh instead."
    if [ "$DRY_RUN" = "false" ]; then
        die "Unsupported OS: $(uname)"
    fi
fi

# Install system dependencies
if command -v apt-get &>/dev/null && [ "$DRY_RUN" = "false" ]; then
    log "Installing system dependencies..."
    apt-get update -qq
    apt-get install -y -qq git curl wget jq tmux htop build-essential > /dev/null 2>&1
    apt-get install -y -qq nvtop 2>/dev/null || true
fi

# GPU detection
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1 | xargs)
    GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l | xargs)
    GPU_VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1 | xargs)
    CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | xargs)

    log "GPU detected:"
    log "  Name:  $GPU_NAME"
    log "  Count: $GPU_COUNT"
    log "  VRAM:  ${GPU_VRAM} MB"
    log "  Driver: $CUDA_VERSION"
else
    GPU_NAME="none"
    GPU_COUNT=0
    GPU_VRAM=0
    warn "No NVIDIA GPU detected (nvidia-smi not found)"
fi

# Python version check
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    die "Python >= 3.10 required (found $PYTHON_VERSION)"
fi
log "Python: $PYTHON_VERSION"

# Disk space check
DISK_FREE_GB=$(df -BG . | tail -1 | awk '{print $4}' | tr -d 'G')
if [ "$DISK_FREE_GB" -lt 100 ]; then
    warn "Low disk space: ${DISK_FREE_GB}GB free (recommend 100GB+ for 14B models)"
fi
log "Disk free: ${DISK_FREE_GB}GB"

# ============================================================
# PHASE 2: Python Dependencies
# ============================================================

log ""
log "=== PHASE 2: Python Dependencies ==="

if [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would install: torch, trl, peft, accelerate, bitsandbytes, transformers, datasets"
else
    PIP_CMD="pip install"
    if [ "$USE_UV" = "true" ]; then
        if ! command -v uv &>/dev/null; then
            log "Installing uv..."
            pip install uv
        fi
        PIP_CMD="uv pip install"
    fi

    # Check PyTorch CUDA
    HAS_TORCH_CUDA=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "false")
    if [ "$HAS_TORCH_CUDA" != "True" ]; then
        log "Installing PyTorch with CUDA support..."
        $PIP_CMD torch --index-url https://download.pytorch.org/whl/cu121 2>/dev/null || \
        $PIP_CMD torch
    fi

    log "Installing training dependencies..."
    $PIP_CMD trl peft accelerate bitsandbytes transformers datasets huggingface_hub safetensors hf_transfer

    # Flash attention (optional)
    log "Attempting flash-attn install..."
    $PIP_CMD flash-attn --no-build-isolation 2>/dev/null || \
        warn "flash-attn installation failed (non-critical, continuing)"

    # Unsloth (optional)
    log "Attempting Unsloth install..."
    $PIP_CMD unsloth 2>/dev/null || \
        warn "Unsloth installation failed (will use standard transformers)"

    # Verify GPU access from Python
    HAS_TORCH_CUDA=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "false")
    if [ "$HAS_TORCH_CUDA" = "True" ]; then
        log "PyTorch CUDA verification: OK"
    else
        warn "PyTorch cannot access CUDA — training may be slow"
    fi
fi

# ============================================================
# PHASE 3: Dataset Download & Preparation + Training Advisor
# ============================================================

log ""
log "=== PHASE 3: Dataset Preparation ==="

CLEANED_DIR="${OUTPUT_DIR}/cleaned"
ADVISOR_JSON="${CLEANED_DIR}/advisor.json"

if [ "$SKIP_TRAINING" = "true" ]; then
    log "Skipping dataset preparation (--skip-training)"
elif [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would prepare dataset: $DATASET"
    if [ -f "$DATASET" ]; then
        TRAIN_COUNT=$(wc -l < "$DATASET" | xargs)
        log "  Dataset lines: $TRAIN_COUNT"
    fi
else
    # --- Locate dataset ---
    if [ -f "$DATASET" ]; then
        log "Dataset found: $DATASET"
    else
        # Try HuggingFace download
        log "Dataset not found locally, attempting HuggingFace download..."
        python3 -c "
from huggingface_hub import hf_hub_download
import os
try:
    path = hf_hub_download(repo_id='$DATASET', filename='train.jsonl', repo_type='dataset')
    print(path)
except:
    try:
        path = hf_hub_download(repo_id='$DATASET', filename='data/train.jsonl', repo_type='dataset')
        print(path)
    except Exception as e:
        print(f'DOWNLOAD_FAILED: {e}')
" > /tmp/uncase_dataset_path.txt 2>/dev/null

        DOWNLOADED_PATH=$(cat /tmp/uncase_dataset_path.txt)
        if [[ "$DOWNLOADED_PATH" == DOWNLOAD_FAILED* ]]; then
            die "Dataset not found: $DATASET"
        fi
        DATASET="$DOWNLOADED_PATH"
        log "Downloaded dataset to: $DATASET"
    fi

    # Validate JSON
    log "Validating dataset format..."
    INVALID_LINES=$(python3 -c "
import json, sys
count = 0
with open('$DATASET') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line: continue
        try:
            obj = json.loads(line)
            if 'messages' not in obj:
                count += 1
        except:
            count += 1
print(count)
")
    if [ "$INVALID_LINES" -gt 0 ]; then
        warn "$INVALID_LINES lines have invalid format (missing 'messages' key)"
    fi

    TRAIN_COUNT=$(wc -l < "$DATASET" | xargs)
    log "Dataset: $TRAIN_COUNT conversations"

    if [ "$TRAIN_COUNT" -lt 10 ]; then
        die "Dataset too small ($TRAIN_COUNT < 10 conversations)"
    fi

    # --- Run data quality pipeline ---
    if [ "$SKIP_CLEANING" = "true" ]; then
        log "Skipping data cleaning (--skip-cleaning)"
        CLEAN_TRAIN="$DATASET"
        CLEAN_EVAL="${EVAL_DATASET}"
    else
        PREPARE_ARGS="--input $DATASET --output-dir $CLEANED_DIR --advise --vram ${GPU_VRAM:-48}"

        # Enable cleaning steps
        PREPARE_ARGS="$PREPARE_ARGS --dedup --filter-patterns --validate-tools"

        # Split if no eval dataset
        if [ -z "$EVAL_DATASET" ]; then
            PREPARE_ARGS="$PREPARE_ARGS --split --eval-ratio 0.1"
        fi

        # System prompt injection
        if [ -n "$SYSTEM_PROMPT_FILE" ] && [ -f "$SYSTEM_PROMPT_FILE" ]; then
            PREPARE_ARGS="$PREPARE_ARGS --system-prompt $SYSTEM_PROMPT_FILE"
        fi

        # Estimate model size from name for advisor
        MODEL_SIZE="14"
        if echo "$MODEL" | grep -qiE "3b|3B|2\.7|2\.8"; then
            MODEL_SIZE="3"
        elif echo "$MODEL" | grep -qiE "7b|7B|8b|8B"; then
            MODEL_SIZE="8"
        elif echo "$MODEL" | grep -qiE "13b|13B|14b|14B"; then
            MODEL_SIZE="14"
        elif echo "$MODEL" | grep -qiE "32b|32B|34b|34B"; then
            MODEL_SIZE="32"
        elif echo "$MODEL" | grep -qiE "70b|70B|72b|72B"; then
            MODEL_SIZE="70"
        fi
        PREPARE_ARGS="$PREPARE_ARGS --model-size $MODEL_SIZE"

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

    # --- Read advisor recommendations ---
    if [ -f "$ADVISOR_JSON" ]; then
        log "Reading training advisor recommendations..."

        # Read advisor values (used as defaults if user didn't specify)
        ADV_EPOCHS=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['epochs_max'])" 2>/dev/null || echo "")
        ADV_LR=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['learning_rate'])" 2>/dev/null || echo "")
        ADV_LORA_R=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['lora_r'])" 2>/dev/null || echo "")
        ADV_LORA_ALPHA=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['lora_alpha'])" 2>/dev/null || echo "")
        ADV_MAX_SEQ=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['max_seq_length'])" 2>/dev/null || echo "")
        ADV_BATCH=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['batch_size'])" 2>/dev/null || echo "")
        ADV_GRAD_ACCUM=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['grad_accum'])" 2>/dev/null || echo "")
        ADV_NEFTUNE=$(python3 -c "import json; d=json.load(open('$ADVISOR_JSON')); print(d['recommendation']['neftune_noise'])" 2>/dev/null || echo "")

        # Apply advisor values as defaults (CLI flags override)
        [ -z "$EPOCHS" ]         && [ -n "$ADV_EPOCHS" ]      && EPOCHS="$ADV_EPOCHS"
        [ -z "$LEARNING_RATE" ]  && [ -n "$ADV_LR" ]          && LEARNING_RATE="$ADV_LR"
        [ -z "$LORA_R" ]         && [ -n "$ADV_LORA_R" ]      && LORA_R="$ADV_LORA_R"
        [ -z "$LORA_ALPHA" ]     && [ -n "$ADV_LORA_ALPHA" ]  && LORA_ALPHA="$ADV_LORA_ALPHA"
        [ -z "$MAX_SEQ_LENGTH" ] && [ -n "$ADV_MAX_SEQ" ]     && MAX_SEQ_LENGTH="$ADV_MAX_SEQ"
        [ -z "$BATCH_SIZE" ]     && [ -n "$ADV_BATCH" ]       && BATCH_SIZE="$ADV_BATCH"
        [ -z "$GRAD_ACCUM" ]     && [ -n "$ADV_GRAD_ACCUM" ]  && GRAD_ACCUM="$ADV_GRAD_ACCUM"
        [ -z "$NEFTUNE" ]        && [ -n "$ADV_NEFTUNE" ]     && NEFTUNE="$ADV_NEFTUNE"
    fi
fi

# --- Apply final defaults for any still-unset parameters ---
EPOCHS="${EPOCHS:-3}"
LEARNING_RATE="${LEARNING_RATE:-2e-4}"
LORA_R="${LORA_R:-32}"
LORA_ALPHA="${LORA_ALPHA:-64}"
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-4096}"
NEFTUNE="${NEFTUNE:-5}"

# VRAM-based batch size defaults
if [ -z "$BATCH_SIZE" ] || [ -z "$GRAD_ACCUM" ]; then
    VRAM_MB="${GPU_VRAM:-0}"
    if [ "$VRAM_MB" -ge 80000 ]; then
        BATCH_SIZE="${BATCH_SIZE:-6}"; GRAD_ACCUM="${GRAD_ACCUM:-2}"
    elif [ "$VRAM_MB" -ge 44000 ]; then
        BATCH_SIZE="${BATCH_SIZE:-4}"; GRAD_ACCUM="${GRAD_ACCUM:-4}"
    elif [ "$VRAM_MB" -ge 22000 ]; then
        BATCH_SIZE="${BATCH_SIZE:-2}"; GRAD_ACCUM="${GRAD_ACCUM:-8}"
    else
        BATCH_SIZE="${BATCH_SIZE:-1}"; GRAD_ACCUM="${GRAD_ACCUM:-16}"
    fi
fi

# ============================================================
# PHASE 4: Fine-Tuning
# ============================================================

log ""
log "=== PHASE 4: Fine-Tuning ==="

if [ "$SKIP_TRAINING" = "true" ]; then
    log "Skipping training (--skip-training)"
elif [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would train with:"
    log "  Model:          $MODEL"
    log "  LoRA:           r=$LORA_R, alpha=$LORA_ALPHA"
    log "  Epochs:         $EPOCHS"
    EFFECTIVE=$((BATCH_SIZE * GRAD_ACCUM))
    log "  Batch:          ${BATCH_SIZE} x ${GRAD_ACCUM} = ${EFFECTIVE} effective"
    log "  LR:             $LEARNING_RATE"
    log "  Max seq:        $MAX_SEQ_LENGTH"
    log "  NEFTune:        $NEFTUNE"
    log "  Output:         $OUTPUT_DIR"
else
    # Free VRAM
    log "Freeing GPU memory..."
    safe_kill "vllm.entrypoints" 2>/dev/null || true
    python3 -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true
    sleep 3

    EFFECTIVE=$((BATCH_SIZE * GRAD_ACCUM))
    log "Training configuration:"
    log "  Model:          $MODEL"
    log "  LoRA:           r=$LORA_R, alpha=$LORA_ALPHA"
    log "  Epochs:         $EPOCHS"
    log "  Batch:          ${BATCH_SIZE} x ${GRAD_ACCUM} = ${EFFECTIVE} effective"
    log "  LR:             $LEARNING_RATE"
    log "  Max seq:        $MAX_SEQ_LENGTH"
    log "  NEFTune:        $NEFTUNE"
    log "  Dataset:        ${CLEAN_TRAIN:-$DATASET}"

    TRAIN_ARGS="--model $MODEL"
    TRAIN_ARGS="$TRAIN_ARGS --train-file ${CLEAN_TRAIN:-$DATASET}"
    if [ -n "${CLEAN_EVAL:-}" ] && [ -f "${CLEAN_EVAL:-}" ]; then
        TRAIN_ARGS="$TRAIN_ARGS --eval-file $CLEAN_EVAL"
    elif [ -n "$EVAL_DATASET" ] && [ -f "$EVAL_DATASET" ]; then
        TRAIN_ARGS="$TRAIN_ARGS --eval-file $EVAL_DATASET"
    fi
    TRAIN_ARGS="$TRAIN_ARGS --output-dir $OUTPUT_DIR"
    TRAIN_ARGS="$TRAIN_ARGS --lora-r $LORA_R --lora-alpha $LORA_ALPHA"
    TRAIN_ARGS="$TRAIN_ARGS --epochs $EPOCHS --batch-size $BATCH_SIZE --grad-accum $GRAD_ACCUM"
    TRAIN_ARGS="$TRAIN_ARGS --lr $LEARNING_RATE --max-seq-length $MAX_SEQ_LENGTH"
    TRAIN_ARGS="$TRAIN_ARGS --neftune $NEFTUNE --warmup-ratio $WARMUP_RATIO"
    TRAIN_ARGS="$TRAIN_ARGS --no-gguf"

    if [ -n "$RESUME_CHECKPOINT" ]; then
        TRAIN_ARGS="$TRAIN_ARGS --resume $RESUME_CHECKPOINT"
    fi

    set +e
    # shellcheck disable=SC2086
    python3 "${SCRIPT_DIR}/uncase_train_worker.py" $TRAIN_ARGS
    TRAIN_EXIT=$?
    set -e

    if [ "$TRAIN_EXIT" -ne 0 ]; then
        warn "Training exited with code $TRAIN_EXIT"
        if [ -d "$OUTPUT_DIR" ] && [ -f "$OUTPUT_DIR/adapter_config.json" ]; then
            log "Partial adapter found, continuing with existing checkpoint..."
        else
            die "Training failed and no adapter found"
        fi
    fi

    # Verify adapter
    if [ -f "$OUTPUT_DIR/adapter_model.safetensors" ] || [ -f "$OUTPUT_DIR/adapter_model.bin" ]; then
        ADAPTER_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
        log "Adapter saved: $OUTPUT_DIR ($ADAPTER_SIZE)"
    else
        die "Adapter files not found in $OUTPUT_DIR"
    fi
fi

# ============================================================
# PHASE 5: Merge LoRA → Full Model
# ============================================================

log ""
log "=== PHASE 5: Merge LoRA ==="

if [ "$SKIP_MERGE" = "true" ]; then
    log "Skipping merge (--skip-merge)"
elif [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would merge $OUTPUT_DIR into $MERGED_DIR"
else
    log "Merging LoRA adapter with base model..."
    log "  Base:    $MODEL"
    log "  Adapter: $OUTPUT_DIR"
    log "  Output:  $MERGED_DIR"

    python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
from uncase_train_worker import merge_lora
merge_lora('$MODEL', '$OUTPUT_DIR', '$MERGED_DIR')
"

    if [ -f "$MERGED_DIR/config.json" ]; then
        SAFETENSOR_COUNT=$(find "$MERGED_DIR" -name "*.safetensors" | wc -l | xargs)
        MERGED_SIZE=$(du -sh "$MERGED_DIR" | cut -f1)
        log "Merge successful: $SAFETENSOR_COUNT safetensor files, $MERGED_SIZE total"
    else
        die "Merge verification failed — config.json not found in $MERGED_DIR"
    fi
fi

# ============================================================
# PHASE 6: Upload to HuggingFace
# ============================================================

log ""
log "=== PHASE 6: Upload to HuggingFace ==="

if [ -z "$HF_REPO" ]; then
    log "No --hf-repo specified, skipping upload"
elif [ -z "${HF_TOKEN:-}" ]; then
    warn "HF_TOKEN not set, skipping HuggingFace upload"
elif [ "$DRY_RUN" = "true" ]; then
    log "(dry run) Would upload to $HF_REPO"
else
    UPLOAD_DIR="$OUTPUT_DIR"
    if [ -d "$MERGED_DIR" ] && [ -f "$MERGED_DIR/config.json" ]; then
        UPLOAD_DIR="$MERGED_DIR"
    fi

    PRIVATE_FLAG=""
    if [ "$HF_PRIVATE" = "true" ]; then
        PRIVATE_FLAG="private=True,"
    fi

    log "Uploading to $HF_REPO..."
    set +e
    python3 -c "
from huggingface_hub import HfApi
import os

api = HfApi(token=os.environ['HF_TOKEN'])
api.create_repo(repo_id='$HF_REPO', repo_type='model', exist_ok=True, ${PRIVATE_FLAG})
api.upload_folder(
    folder_path='$UPLOAD_DIR',
    repo_id='$HF_REPO',
    repo_type='model',
    commit_message='UNCASE fine-tuned model upload',
)
print('Upload complete: $HF_REPO')
"
    UPLOAD_EXIT=$?
    set -e

    if [ "$UPLOAD_EXIT" -ne 0 ]; then
        warn "HuggingFace upload failed (continuing with deployment)"
    else
        log "Upload complete: https://huggingface.co/$HF_REPO"
    fi
fi

# ============================================================
# PHASES 7-10: Service Deployment (Optional)
# ============================================================

if [ "$SKIP_DEPLOY" = "true" ]; then
    log ""
    log "=== Skipping deployment (use --deploy to enable) ==="
elif [ "$DRY_RUN" = "true" ]; then
    log ""
    log "(dry run) Would deploy:"
    log "  vLLM:    port $VLLM_PORT"
    log "  FastAPI: port $FASTAPI_PORT"
    log "  Model:   ${MERGED_DIR}"
else
    log ""
    log "=== PHASE 8: Service Deployment ==="

    DEPLOY_MODEL="$MERGED_DIR"
    if [ ! -f "$DEPLOY_MODEL/config.json" ]; then
        die "No merged model found at $DEPLOY_MODEL for deployment"
    fi

    # --- GPU-specific vLLM config ---
    VLLM_GPU_UTIL="0.90"
    VLLM_EXTRA_ARGS=""
    case "${GPU_NAME:-unknown}" in
        *A40*)
            VLLM_GPU_UTIL="0.92"
            ;;
        *A6000*)
            VLLM_GPU_UTIL="0.90"
            ;;
        *A100*)
            VLLM_GPU_UTIL="0.90"
            ;;
        *H100*)
            VLLM_GPU_UTIL="0.92"
            ;;
        *PRO*6000*|*RTX*6000*)
            VLLM_GPU_UTIL="0.92"
            ;;
    esac

    # Launch vLLM
    log "Starting vLLM..."
    export VLLM_USE_V1=0
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model "$DEPLOY_MODEL" \
        --served-model-name "$SERVED_MODEL" \
        --max-model-len "$MAX_SEQ_LENGTH" \
        --dtype bfloat16 \
        --gpu-memory-utilization "$VLLM_GPU_UTIL" \
        --enforce-eager \
        --host 0.0.0.0 \
        --port "$VLLM_PORT" \
        $VLLM_EXTRA_ARGS \
        > /tmp/uncase-vllm.log 2>&1 &
    VLLM_PID=$!
    log "vLLM PID: $VLLM_PID"

    wait_for_service "vLLM" "http://localhost:${VLLM_PORT}/health" 300 || \
        warn "vLLM may not be ready yet, check /tmp/uncase-vllm.log"

    # --- Cloudflare Tunnel (optional) ---
    if [ "$SKIP_TUNNEL" = "false" ] && [ -n "${CF_TUNNEL_CRED:-}" ]; then
        log ""
        log "=== PHASE 9: Cloudflare Tunnel ==="

        if ! command -v cloudflared &>/dev/null; then
            log "Installing cloudflared..."
            wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
                -O /usr/local/bin/cloudflared
            chmod +x /usr/local/bin/cloudflared
        fi

        mkdir -p /root/.cloudflared
        echo "$CF_TUNNEL_CRED" > /root/.cloudflared/credentials.json

        nohup cloudflared tunnel run "$CF_TUNNEL_ID" > /tmp/uncase-tunnel.log 2>&1 &
        TUNNEL_PID=$!
        log "Cloudflare tunnel PID: $TUNNEL_PID"
    fi

    # --- Summary ---
    log ""
    log "=== PHASE 10: Summary ==="

    VRAM_USED=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader | head -1 2>/dev/null || echo "N/A")

    log ""
    log "============================================================"
    log "  UNCASE DEPLOYMENT READY"
    log "============================================================"
    log "  Model:    $DEPLOY_MODEL"
    log "  GPU:      ${GPU_NAME:-N/A} (${GPU_COUNT:-0}x)"
    log "  VRAM:     $VRAM_USED"
    log "  vLLM:     http://localhost:${VLLM_PORT} (PID: $VLLM_PID)"
    if [ -n "$TUNNEL_PID" ]; then
        log "  Tunnel:   PID $TUNNEL_PID"
    fi
    log ""
    log "  Logs:"
    log "    Training: $LOG_FILE"
    log "    vLLM:     /tmp/uncase-vllm.log"
    log "============================================================"

    # Keep script alive for services
    log ""
    log "Services running. Press Ctrl+C to stop."
    wait
fi

# ============================================================
# Final Summary (non-deploy mode)
# ============================================================

if [ "$SKIP_DEPLOY" = "true" ] && [ "$DRY_RUN" = "false" ]; then
    log ""
    log "============================================================"
    log "  UNCASE TRAINING COMPLETE"
    log "============================================================"
    log "  Model:          $MODEL"
    log "  LoRA adapter:   $OUTPUT_DIR"
    if [ "$SKIP_MERGE" = "false" ]; then
        log "  Merged model:   $MERGED_DIR"
    fi
    if [ -n "$HF_REPO" ]; then
        log "  HF repo:        $HF_REPO"
    fi
    log "  Log file:       $LOG_FILE"
    log "============================================================"
fi

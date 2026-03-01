#!/usr/bin/env bash
# ================================================================
#  TREFA Mariana v9 — Pipeline de Entrenamiento Completo
# ================================================================
#
#  Ejecutar en la VM con GPU (vast.ai, RTX 5880 Ada 49GB):
#    bash train_v9.sh
#
#  Pipeline:
#    1. Parar vLLM para liberar VRAM
#    2. Limpiar dataset v8 → v9
#    3. Entrenar con Unsloth (QLoRA, Qwen3-14B)
#    4. Merge LoRA + base → modelo completo
#    5. Push a HuggingFace
#    6. Reiniciar vLLM con modelo nuevo
#
# ================================================================

set -euo pipefail

# ─── Configuración ─────────────────────────────────────────────

HF_REPO="mmoralesf/qwen3-14B-mariana-v9"
BASE_MODEL="unsloth/Qwen3-14B"

TRAIN_FILE="/app/datasets/v9_train.jsonl"
EVAL_FILE="/app/datasets/v9_eval.jsonl"
LORA_OUTPUT="/app/modelos/qwen3-14b-lora-v9"
MERGED_OUTPUT="/app/modelos/qwen3-14b-mariana-v9"

# Hiperparámetros
EPOCHS=2
BATCH_SIZE=2
GRAD_ACCUM=8         # effective batch = 16
LEARNING_RATE="2e-4"
LORA_R=32
LORA_ALPHA=64
MAX_SEQ_LENGTH=4096
NEFTUNE_NOISE=5
WARMUP_RATIO="0.05"

# vLLM
VLLM_PORT=8001
FASTAPI_PORT=8081
SERVED_MODEL="trefa-lora"

# ─── Utilidades ────────────────────────────────────────────────

log() { echo "[$(date +%H:%M:%S)] $*"; }
die() { log "ERROR: $*"; exit 1; }

# ─── 1. Parar servicios para liberar VRAM ──────────────────────

log "=== PASO 1: Liberando VRAM ==="

# Parar vLLM
if pgrep -f "vllm.entrypoints" > /dev/null 2>&1; then
    log "Parando vLLM..."
    pkill -f "vllm.entrypoints" || true
    sleep 5
fi

# Parar FastAPI
if pgrep -f "uvicorn app.main" > /dev/null 2>&1; then
    log "Parando FastAPI..."
    pkill -f "uvicorn app.main" || true
    sleep 2
fi

# Verificar VRAM libre
VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
log "VRAM usada: ${VRAM_USED}MB"
if [ "$VRAM_USED" -gt 1000 ]; then
    log "ADVERTENCIA: VRAM no se liberó completamente (${VRAM_USED}MB)"
    log "Esperando 10s..."
    sleep 10
    VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    log "VRAM ahora: ${VRAM_USED}MB"
fi

# ─── 2. Limpiar dataset ───────────────────────────────────────

log "=== PASO 2: Limpiando dataset v8 → v9 ==="

if [ ! -f "/app/datasets/v8_train.jsonl" ]; then
    die "No se encontró /app/datasets/v8_train.jsonl — sube el dataset primero"
fi

cd /app/datasets
python3 limpiar_dataset_v9.py \
    --input v8_train.jsonl \
    --eval-input v8_eval.jsonl \
    --output v9_train.jsonl \
    --eval-output v9_eval.jsonl

TRAIN_COUNT=$(wc -l < "$TRAIN_FILE" | tr -d ' ')
log "Dataset v9: ${TRAIN_COUNT} conversaciones de entrenamiento"

if [ "$TRAIN_COUNT" -lt 100 ]; then
    die "Dataset demasiado pequeño (${TRAIN_COUNT} < 100). Revisa la limpieza."
fi

# ─── 3. Entrenar con Unsloth ──────────────────────────────────

log "=== PASO 3: Entrenamiento con Unsloth ==="
log "  Modelo:     $BASE_MODEL"
log "  LoRA:       r=$LORA_R, alpha=$LORA_ALPHA"
log "  Epochs:     $EPOCHS"
log "  Batch:      ${BATCH_SIZE} x ${GRAD_ACCUM} = $((BATCH_SIZE * GRAD_ACCUM))"
log "  LR:         $LEARNING_RATE"
log "  NEFTune:    $NEFTUNE_NOISE"
log "  Dataset:    $TRAIN_FILE ($TRAIN_COUNT convos)"

cd /app

python3 training/train_qwen3_vast.py \
    --model "$BASE_MODEL" \
    --train-file "$TRAIN_FILE" \
    --eval-file "$EVAL_FILE" \
    --output-dir "$LORA_OUTPUT" \
    --merged-dir "$MERGED_OUTPUT" \
    --max-seq-length "$MAX_SEQ_LENGTH" \
    --lora-r "$LORA_R" \
    --lora-alpha "$LORA_ALPHA" \
    --epochs "$EPOCHS" \
    --batch-size "$BATCH_SIZE" \
    --grad-accum "$GRAD_ACCUM" \
    --lr "$LEARNING_RATE" \
    --neftune "$NEFTUNE_NOISE" \
    --no-gguf

log "Entrenamiento completado"

# ─── 4. Push a HuggingFace ────────────────────────────────────

log "=== PASO 4: Subiendo a HuggingFace ==="

if [ -z "${HF_TOKEN:-}" ]; then
    log "ADVERTENCIA: HF_TOKEN no definido, saltando push a HF"
else
    log "Subiendo LoRA adapter a $HF_REPO..."
    python3 -c "
from huggingface_hub import HfApi
import os

api = HfApi(token=os.environ['HF_TOKEN'])

# Subir LoRA adapter
api.upload_folder(
    folder_path='$LORA_OUTPUT',
    repo_id='$HF_REPO',
    repo_type='model',
    commit_message='v9: reentrenamiento con dataset limpio (max 3 opciones, saludos obligatorios, sin tool leaks)',
)
print('LoRA adapter subido a $HF_REPO')
"
    log "Push completado"
fi

# ─── 5. Reiniciar servicios ───────────────────────────────────

log "=== PASO 5: Reiniciando servicios ==="

# Verificar que el modelo merged existe
if [ ! -f "$MERGED_OUTPUT/config.json" ]; then
    die "Modelo merged no encontrado en $MERGED_OUTPUT"
fi

# Iniciar vLLM
log "Iniciando vLLM con modelo v9..."
export VLLM_USE_V1=0
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model "$MERGED_OUTPUT" \
    --served-model-name "$SERVED_MODEL" \
    --max-model-len "$MAX_SEQ_LENGTH" \
    --dtype bfloat16 \
    --gpu-memory-utilization 0.90 \
    --enforce-eager \
    --host 0.0.0.0 \
    --port "$VLLM_PORT" \
    > /tmp/vllm.log 2>&1 &

VLLM_PID=$!
log "vLLM PID: $VLLM_PID"

# Esperar a que vLLM esté listo
log "Esperando a que vLLM cargue el modelo..."
for i in $(seq 1 60); do
    if curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
        log "vLLM listo (${i}s)"
        break
    fi
    sleep 5
done

if ! curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
    die "vLLM no respondió después de 5 minutos"
fi

# Iniciar FastAPI
log "Iniciando FastAPI..."
export TREFA_VLLM_BASE_URL="http://localhost:${VLLM_PORT}"
export TREFA_VLLM_PORT="$VLLM_PORT"
export TREFA_VLLM_API_KEY="EMPTY"
export PYTHONPATH=/app

nohup python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$FASTAPI_PORT" \
    > /tmp/fastapi.log 2>&1 &

FASTAPI_PID=$!
log "FastAPI PID: $FASTAPI_PID"
sleep 5

# Verificar health
HEALTH=$(curl -s "http://localhost:${FASTAPI_PORT}/health" 2>/dev/null || echo '{"status":"error"}')
log "Health: $HEALTH"

# ─── Resumen ──────────────────────────────────────────────────

VRAM_USED=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader | head -1)

log ""
log "================================================================"
log "  ENTRENAMIENTO v9 COMPLETADO"
log "================================================================"
log "  Dataset:    $TRAIN_FILE ($TRAIN_COUNT convos)"
log "  LoRA:       $LORA_OUTPUT"
log "  Merged:     $MERGED_OUTPUT"
log "  HF repo:    $HF_REPO"
log "  VRAM:       $VRAM_USED"
log "  vLLM:       http://localhost:${VLLM_PORT} (PID: $VLLM_PID)"
log "  FastAPI:    http://localhost:${FASTAPI_PORT} (PID: $FASTAPI_PID)"
log "================================================================"

#!/bin/bash
# ============================================================
# TREFA - vast.ai entry script - Qwen3-32B fine-tuned
# Template: PyTorch (Vast) | GPU: 2x A40 (90GB total)
#
# Env vars (configurar en vast.ai):
#   HF_TOKEN (obligatoria)
#   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (opcionales)
# ============================================================
set -euo pipefail
exec > >(tee -a /tmp/trefa-startup.log) 2>&1

log() { echo "[$(date +'%H:%M:%S')] $1"; }
log "=== TREFA 32B Setup (Tensor Parallel) ==="

# --- Config ---
BASE_REPO="Qwen/Qwen3-32B"
LORA_REPO="mmoralesf/qwen3-32B-mariana"
BASE_DIR="/app/modelos/qwen3-32b-base"
LORA_DIR="/app/modelos/qwen3-32b-mariana"
MERGED_DIR="/app/modelos/qwen3-32b-merged"
VLLM_PORT=8001
FASTAPI_PORT=8081
MCP_PORT=3001
GIT_REPO="https://github.com/marianomoralesr/mcp-server.git"

export OPENBLAS_NUM_THREADS=1
export HF_HUB_ENABLE_HF_TRANSFER=1

# Auto-detectar GPUs
GPU_COUNT=$(python3 -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo "1")
TENSOR_PARALLEL=${TENSOR_PARALLEL:-$GPU_COUNT}
log "GPUs detectadas: $GPU_COUNT (TP=$TENSOR_PARALLEL)"

if [ -z "${HF_TOKEN:-}" ]; then
    log "ERROR: HF_TOKEN no definido"
    exit 1
fi
export HF_TOKEN
mkdir -p /app/modelos

# ============================================================
# 1. DEPS
# ============================================================
log "Instalando dependencias..."
pip install -q vllm==0.7.3 peft accelerate transformers huggingface_hub hf_transfer 2>&1 | tail -3
pip install -q httpx structlog pydantic-settings uvicorn fastapi 2>&1 | tail -3

NODE_VER=$(node -v 2>/dev/null | grep -oP '\d+' | head -1 || echo "0")
if [ "$NODE_VER" -lt 18 ]; then
    log "Instalando Node.js 20..."
    apt-get update -qq 2>&1 | tail -1
    apt-get remove -y nodejs npm libnode-dev libnode72 2>/dev/null || true
    dpkg --configure -a 2>/dev/null || true
    curl -fsSL https://deb.nodesource.com/setup_20.x 2>/dev/null | bash - 2>&1 | tail -3
    apt-get install -y nodejs 2>&1 | tail -3
    hash -r
fi
log "Deps OK (vllm $(pip show vllm 2>/dev/null | grep Version | cut -d' ' -f2), node $(node -v 2>/dev/null || echo N/A))"

# ============================================================
# 2. DESCARGAR + MERGE
# ============================================================
if [ ! -f "$MERGED_DIR/config.json" ]; then

    if [ ! -f "$BASE_DIR/config.json" ] || [ "$(ls $BASE_DIR/model-*.safetensors 2>/dev/null | wc -l)" -lt 10 ]; then
        log "Descargando base: $BASE_REPO (~65GB)..."
        rm -rf "$BASE_DIR"
        huggingface-cli download "$BASE_REPO" --local-dir "$BASE_DIR" --local-dir-use-symlinks False
    fi
    log "Base: $(du -sh $BASE_DIR | cut -f1)"

    if [ ! -f "$LORA_DIR/adapter_config.json" ]; then
        log "Descargando LoRA: $LORA_REPO..."
        huggingface-cli download "$LORA_REPO" --local-dir "$LORA_DIR" --local-dir-use-symlinks False
    fi
    log "LoRA: $(du -sh $LORA_DIR | cut -f1)"

    log "Mergeando modelo (~64GB RAM)..."
    python3 -u << 'MERGE'
import torch, os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
BASE = "/app/modelos/qwen3-32b-base"
LORA = "/app/modelos/qwen3-32b-mariana"
OUT  = "/app/modelos/qwen3-32b-merged"
print("[merge] Tokenizer...")
tok = AutoTokenizer.from_pretrained(LORA, trust_remote_code=True, use_fast=True)
print("[merge] Base model (bf16, CPU, ~64GB RAM)...")
base = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.bfloat16, device_map="cpu", trust_remote_code=True)
print("[merge] LoRA adapter...")
model = PeftModel.from_pretrained(base, LORA)
print("[merge] Merge...")
model = model.merge_and_unload()
os.makedirs(OUT, exist_ok=True)
model.save_pretrained(OUT, safe_serialization=True)
tok.save_pretrained(OUT)
print("[merge] OK")
MERGE

    [ ! -f "$MERGED_DIR/config.json" ] && log "ERROR: Merge falló" && exit 1
    log "Merge OK: $(du -sh $MERGED_DIR | cut -f1)"
    rm -rf "$BASE_DIR"
else
    log "Modelo mergeado: $(du -sh $MERGED_DIR | cut -f1)"
fi

# ============================================================
# 3. REPOS + BUILD
# ============================================================
if [ ! -d "/app/app" ]; then
    log "Clonando inference-server..."
    git clone -q -b inference-server "$GIT_REPO" /tmp/ir && cp -r /tmp/ir/* /app/ && rm -rf /tmp/ir
fi

if [ ! -d "/app/mcp-server/.git" ]; then
    log "Clonando mcp-server..."
    rm -rf /app/mcp-server && git clone -q -b main "$GIT_REPO" /app/mcp-server
fi

cd /app/mcp-server && npm install --silent 2>&1 | tail -2 && npm run build 2>&1 | tail -2

if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    printf "SUPABASE_URL=%s\nSUPABASE_SERVICE_ROLE_KEY=%s\nPORT=%s\n" \
        "$SUPABASE_URL" "$SUPABASE_SERVICE_ROLE_KEY" "$MCP_PORT" > /app/mcp-server/.env
fi

pip install -q -r /app/app/requirements.txt 2>&1 | tail -2
mkdir -p /app/datasets /app/generated

# ============================================================
# 4. SERVICIOS
# ============================================================
cd /app

log "MCP Server (puerto $MCP_PORT)..."
cd /app/mcp-server && nohup npm run start:http > /tmp/mcp-server.log 2>&1 & MCP_PID=$!; cd /app

log "vLLM (puerto $VLLM_PORT, TP=$TENSOR_PARALLEL)..."
python3 -m vllm.entrypoints.openai.api_server \
    --model "$MERGED_DIR" \
    --served-model-name trefa-lora \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --gpu-memory-utilization 0.90 \
    --tensor-parallel-size "$TENSOR_PARALLEL" \
    --enforce-eager \
    --host 0.0.0.0 \
    --port "$VLLM_PORT" > /tmp/vllm.log 2>&1 &
VLLM_PID=$!

log "Esperando vLLM (32B con TP=$TENSOR_PARALLEL, puede tardar 5-10 min)..."
for i in $(seq 1 180); do
    curl -sf "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1 && log "vLLM listo!" && break
    kill -0 "$VLLM_PID" 2>/dev/null || { log "ERROR: vLLM crasheó"; tail -30 /tmp/vllm.log; exit 1; }
    [ $((i % 12)) -eq 0 ] && log "  cargando... ($((i*5))s)"
    sleep 5
done

log "FastAPI (puerto $FASTAPI_PORT)..."
TREFA_VLLM_PORT=$VLLM_PORT PYTHONPATH=/app python3 -m uvicorn app.main:app \
    --host 0.0.0.0 --port "$FASTAPI_PORT" > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!
sleep 3

# ============================================================
# 5. TEST
# ============================================================
log "=== Test ==="
curl -s "http://localhost:${VLLM_PORT}/v1/models" | python3 -c "import sys,json;print('Modelo:',json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null || log "WARN: /v1/models falló"
curl -s "http://localhost:${FASTAPI_PORT}/health" | python3 -c "import sys,json;print('Health:',json.load(sys.stdin)['status'])" 2>/dev/null || log "WARN: /health falló"
curl -s -X POST "http://localhost:${VLLM_PORT}/v1/chat/completions" -H "Content-Type: application/json" \
    -d '{"model":"trefa-lora","messages":[{"role":"user","content":"hola"}],"max_tokens":30}' \
    | python3 -c "import sys,json;print('Chat:',json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || log "WARN: chat falló"

log "=========================================="
log "  TREFA 32B ACTIVO (TP=$TENSOR_PARALLEL)"
log "  MCP=$MCP_PID :$MCP_PORT | vLLM=$VLLM_PID :$VLLM_PORT | FastAPI=$FASTAPI_PID :$FASTAPI_PORT"
log "=========================================="

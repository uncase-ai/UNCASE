#!/usr/bin/env bash
# ============================================================
# TREFA — Deploy Together v11 (GPU vast.ai)
#
# Descarga adaptadores LoRA entrenados en Together AI desde HF,
# mergea con modelo base Qwen3-14B, y despliega:
#   vLLM + MCP Server + FastAPI + Cloudflare Tunnel
#
# NO entrena — solo descarga, mergea y sirve.
#
# Repos HF:
#   Base:      Qwen/Qwen3-14B
#   LoRA:      mmoralesf/qwen3-14B-v11
#   Merged:    mmoralesf/qwen3-14B-v11-merged
#
# Puertos:
#   vLLM    → 8001
#   MCP     → 3001
#   FastAPI → 8081
#
# Uso:
#   bash deploy_together_v11.sh
#
#   # Si ya tienes el modelo mergeado descargado:
#   bash deploy_together_v11.sh --skip-merge
#
#   # Si ya tienes el modelo mergeado local:
#   bash deploy_together_v11.sh --model-path /app/modelos/mi-modelo
#
#   # Sin tunnel:
#   bash deploy_together_v11.sh --skip-tunnel
# ============================================================

set -euo pipefail
exec > >(tee -a /tmp/trefa-deploy.log) 2>&1

# ─── Detener servicios de vast.ai que consumen VRAM ──────────

if command -v supervisorctl &>/dev/null; then
    supervisorctl stop vllm 2>/dev/null || true
    supervisorctl stop ray 2>/dev/null || true
    sleep 3
    python3 -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true
fi

# ─── Funciones ───────────────────────────────────────────────

log()  { echo "[$(date +'%H:%M:%S')] $1"; }
warn() { echo "[$(date +'%H:%M:%S')] WARN: $1"; }
die()  { echo "[$(date +'%H:%M:%S')] FATAL: $1"; cleanup_on_error; exit 1; }

MY_PID=$$
MY_PPID=$PPID

VLLM_PID=""
MCP_PID=""
FASTAPI_PID=""
CF_PID=""

cleanup_on_error() {
    log "Limpiando tras error..."
    [ -n "$CF_PID" ]      && kill "$CF_PID"      2>/dev/null || true
    [ -n "$FASTAPI_PID" ] && kill "$FASTAPI_PID"  2>/dev/null || true
    [ -n "$MCP_PID" ]     && kill "$MCP_PID"      2>/dev/null || true
    [ -n "$VLLM_PID" ]    && kill "$VLLM_PID"     2>/dev/null || true
    wait 2>/dev/null || true
}

cleanup() {
    log "Deteniendo servicios..."
    [ -n "$CF_PID" ]      && kill "$CF_PID"      2>/dev/null || true
    [ -n "$FASTAPI_PID" ] && kill "$FASTAPI_PID"  2>/dev/null || true
    [ -n "$MCP_PID" ]     && kill "$MCP_PID"      2>/dev/null || true
    [ -n "$VLLM_PID" ]    && kill "$VLLM_PID"     2>/dev/null || true
    wait 2>/dev/null || true
    log "Todos los servicios detenidos."
}

trap cleanup EXIT INT TERM

wait_for_service() {
    local name="$1"
    local host="$2"
    local port="$3"
    local max_wait="${4:-60}"
    local elapsed=0

    while [ $elapsed -lt "$max_wait" ]; do
        if curl -sf "http://${host}:${port}/health" > /dev/null 2>&1; then
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    return 1
}

safe_kill() {
    local pattern="$1"
    local pids
    pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    for pid in $pids; do
        [ "$pid" = "$MY_PID" ] || [ "$pid" = "$MY_PPID" ] && continue
        log "  Matando $pattern (PID $pid)"
        kill -15 "$pid" 2>/dev/null || true
    done
}

# ─── Parse flags ─────────────────────────────────────────────

SKIP_MERGE=false
SKIP_TUNNEL=false
MODEL_PATH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-merge)    SKIP_MERGE=true ;;
        --skip-tunnel)   SKIP_TUNNEL=true ;;
        --model-path)    MODEL_PATH="$2"; shift ;;
        *)               warn "Flag desconocido: $1" ;;
    esac
    shift
done

# ─── Constantes ──────────────────────────────────────────────

VLLM_PORT=8001
MCP_PORT=3001
FASTAPI_PORT=8081
BASE_MODEL="Qwen/Qwen3-14B"
HF_LORA_REPO="mmoralesf/qwen3-14B-v11"
HF_MERGED_REPO="mmoralesf/qwen3-14B-v11-merged"
SERVED_MODEL="trefa-v11"

BASE_DIR="/app/modelos/qwen3-14b-base"
LORA_DIR="/app/modelos/qwen3-14b-v11"
MERGED_DIR="/app/modelos/qwen3-14b-v11-merged"

GIT_REPO="https://github.com/marianomoralesr/mcp-server.git"
INFERENCE_BRANCH="inference-server"

CF_TUNNEL_ID="d15177d1-cb8c-4ed9-b8de-ff52c8f3d749"
CF_TUNNEL_DOMAIN="api.trefa.mx"

# Si --model-path fue dado, usar esa ruta como MERGED_DIR
if [ -n "$MODEL_PATH" ]; then
    MERGED_DIR="$MODEL_PATH"
    SKIP_MERGE=true
    log "Usando modelo pre-existente: $MERGED_DIR"
fi

# ─── Variables de entorno (hardcoded defaults) ───────────────

export HF_TOKEN="${HF_TOKEN:-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}"
export HF_HUB_ENABLE_HF_TRANSFER=1
export OPENBLAS_NUM_THREADS=1
export SUPABASE_URL="${SUPABASE_URL:-https://mhlztgilrmgebkyqowxz.supabase.co}"
export SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1obHp0Z2lscm1nZWJreXFvd3h6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjEyMjkyMCwiZXhwIjoyMDgxNjk4OTIwfQ.E4GbZ4KR9NfyPnbNS1Ic6bi3xzW1-9sBNC15BTRpDzg}"

log "╔══════════════════════════════════════════════════════════════╗"
log "║       TREFA Mariana v11 — Deploy Together (sin training)     ║"
log "╚══════════════════════════════════════════════════════════════╝"
log ""
log "Config:"
log "  Base model:     $BASE_MODEL"
log "  LoRA repo:      $HF_LORA_REPO"
log "  Merged repo:    $HF_MERGED_REPO"
log "  Merged dir:     $MERGED_DIR"
log "  Served model:   $SERVED_MODEL"
log "  Skip merge:     $SKIP_MERGE"
log "  Skip tunnel:    $SKIP_TUNNEL"
log ""

# ============================================================
# FASE 1: Dependencias del sistema
# ============================================================

log "=== FASE 1: Dependencias del sistema ==="

apt-get update -qq 2>&1 | tail -1
apt-get install -y -qq git curl wget jq tmux htop openssh-server build-essential 2>&1 | tail -3

# Cloudflare
if ! command -v cloudflared &>/dev/null; then
    log "Instalando cloudflared..."
    curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
fi

# Verificar GPU
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "N/A")
    GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "1")
    VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs || echo "0")
    CUDA_VER=$(nvidia-smi 2>/dev/null | grep -oP 'CUDA Version: \K[\d.]+' || echo "?")
    log "GPU: ${GPU_NAME} x${GPU_COUNT} — ${VRAM_TOTAL}MB VRAM — CUDA ${CUDA_VER}"
else
    warn "nvidia-smi no disponible"
    VRAM_TOTAL=0
fi

log "Fase 1 completada"

# ============================================================
# FASE 2: Dependencias Python
# ============================================================

log "=== FASE 2: Dependencias Python ==="

pip install --upgrade pip setuptools wheel 2>&1 | tail -1

# PyTorch (si no viene con CUDA)
TORCH_CUDA=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
if [ "$TORCH_CUDA" != "True" ]; then
    log "Instalando PyTorch con CUDA..."
    pip install torch torchvision torchaudio 2>&1 | tail -3
fi

log "Instalando PEFT + dependencias de merge y deploy..."
pip install peft accelerate bitsandbytes 2>&1 | tail -3
pip install datasets transformers sentencepiece protobuf 2>&1 | tail -3
pip install huggingface_hub safetensors hf_transfer 2>&1 | tail -3
pip install vllm 2>&1 | tail -3
# Login HuggingFace
log "Login a HuggingFace..."
huggingface-cli login --token "$HF_TOKEN" 2>&1 | tail -1 || warn "HF login falló"

# Verificar GPU desde Python
log "Verificando GPU desde Python..."
python3 << 'GPU_CHECK'
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1e9
    free = torch.cuda.mem_get_info()[0] / 1e9
    print(f"  GPU: {gpu}")
    print(f"  VRAM: {vram:.1f} GB total, {free:.1f} GB libre")
else:
    print("  CUDA no disponible desde Python")
GPU_CHECK

log "Fase 2 completada"

# ============================================================
# FASE 3: Descargar y mergear modelo
# ============================================================

log "=== FASE 3: Descargar y mergear modelo ==="

if [ "$SKIP_MERGE" = true ] && [ -f "$MERGED_DIR/config.json" ]; then
    log "Merge saltado — modelo ya existe en $MERGED_DIR"

elif [ -n "$MODEL_PATH" ] && [ -f "$MERGED_DIR/config.json" ]; then
    log "Usando modelo pre-existente: $MERGED_DIR"

else
    # Siempre descargar base + LoRA adapters y mergear localmente
    # (el repo merged en HF puede estar desactualizado)
    log "Descargando base + LoRA adapters para merge local..."

    # Limpiar merged previo si existe (puede ser versión vieja)
    if [ -d "$MERGED_DIR" ]; then
        log "Limpiando merged previo: $MERGED_DIR"
        rm -rf "$MERGED_DIR"
    fi

    # Descargar base
    if [ ! -f "$BASE_DIR/config.json" ]; then
        log "Descargando modelo base: $BASE_MODEL (~28GB)..."
        huggingface-cli download "$BASE_MODEL" \
            --local-dir "$BASE_DIR" \
            --local-dir-use-symlinks False 2>&1 | tail -5
    else
        log "Base ya existe en $BASE_DIR"
    fi

    # Descargar LoRA (siempre re-descargar para asegurar versión más reciente)
    log "Descargando LoRA adapter: $HF_LORA_REPO..."
    rm -rf "$LORA_DIR"
    mkdir -p "$LORA_DIR"
    huggingface-cli download "$HF_LORA_REPO" \
        --local-dir "$LORA_DIR" \
        --local-dir-use-symlinks False 2>&1 | tail -5

    # Verificar
    [ ! -f "$BASE_DIR/config.json" ] && die "Base no encontrada en $BASE_DIR"
    [ ! -f "$LORA_DIR/adapter_config.json" ] && die "LoRA no encontrado en $LORA_DIR — verifica que $HF_LORA_REPO exista y tenga adapter_config.json"

    # Merge
    log "Mergeando LoRA con modelo base..."
    log "  Base: $BASE_DIR"
    log "  LoRA: $LORA_DIR"
    log "  Output: $MERGED_DIR"
    log "  NOTA: Qwen3-14B bf16 requiere ~28GB RAM para merge en CPU"

    python3 << MERGE_SCRIPT
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_DIR = "$BASE_DIR"
LORA_DIR = "$LORA_DIR"
MERGED_DIR = "$MERGED_DIR"

print("[merge] Cargando tokenizer desde LoRA...")
tok = AutoTokenizer.from_pretrained(LORA_DIR, trust_remote_code=True, use_fast=True)

print("[merge] Cargando modelo base Qwen3-14B (bf16, CPU, ~28GB RAM)...")
base = AutoModelForCausalLM.from_pretrained(
    BASE_DIR,
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    trust_remote_code=True,
)

print("[merge] Cargando LoRA adapter...")
model = PeftModel.from_pretrained(base, LORA_DIR)

print("[merge] Mergeando pesos...")
model = model.merge_and_unload()

print(f"[merge] Guardando en {MERGED_DIR}...")
os.makedirs(MERGED_DIR, exist_ok=True)
model.save_pretrained(MERGED_DIR, safe_serialization=True)
tok.save_pretrained(MERGED_DIR)

print("[merge] Merge completado!")
MERGE_SCRIPT

    # Verificar merge
    if [ -f "$MERGED_DIR/config.json" ]; then
        SAFETENSORS=$(ls "$MERGED_DIR"/model*.safetensors 2>/dev/null | wc -l)
        MERGED_SIZE=$(du -sh "$MERGED_DIR" 2>/dev/null | cut -f1 || echo "?")
        log "Merge verificado: $MERGED_DIR ($MERGED_SIZE, $SAFETENSORS shards)"
    else
        die "Merge falló — config.json no encontrado en $MERGED_DIR"
    fi

    # Limpiar base para liberar disco (~28GB)
    log "Limpiando modelo base para liberar disco..."
    rm -rf "$BASE_DIR"

    # Upload merged a HF para uso futuro
    log "Subiendo modelo mergeado a $HF_MERGED_REPO..."
    set +e
    python3 << UPLOAD_SCRIPT
import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
from huggingface_hub import HfApi, create_repo

api = HfApi()
repo = "$HF_MERGED_REPO"

try:
    create_repo(repo, repo_type="model", exist_ok=True)
except Exception as e:
    print(f"[upload] WARN: {e}")

out_dir = "$MERGED_DIR"
files = [f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))]
total_size = sum(os.path.getsize(os.path.join(out_dir, f)) for f in files)
print(f"[upload] {len(files)} archivos ({total_size / 1e9:.1f} GB) → {repo}")

api.upload_folder(
    folder_path=out_dir,
    repo_id=repo,
    repo_type="model",
    commit_message="v11: Qwen3-14B + LoRA Together AI mariana v11 (bf16) — merged",
)
print(f"[upload] OK! https://huggingface.co/{repo}")
UPLOAD_SCRIPT
    set -e
fi

log "Fase 3 completada"

# ============================================================
# FASE 4: Node.js y repositorio
# ============================================================

log "=== FASE 4: Node.js y repositorios ==="

# Node.js 20+
NODE_VER=$(node -v 2>/dev/null | grep -oP '\d+' | head -1 || echo "0")
if [ "$NODE_VER" -lt 18 ]; then
    log "Instalando Node.js 20..."
    apt-get update -qq 2>&1 | tail -1
    apt-get remove -y nodejs npm libnode-dev libnode72 2>/dev/null || true
    dpkg --configure -a 2>/dev/null || true
    curl -fsSL https://deb.nodesource.com/setup_20.x 2>/dev/null | bash - 2>&1 | tail -3
    apt-get install -y nodejs 2>&1 | tail -3
    hash -r
    log "Node.js $(node -v) / npm $(npm -v) instalados"
else
    log "Node.js $(node -v 2>/dev/null) OK"
fi

# Clonar repositorio
if [ ! -d "/app/app" ]; then
    log "Clonando repositorio (branch $INFERENCE_BRANCH)..."
    git clone -q -b "$INFERENCE_BRANCH" "$GIT_REPO" /tmp/ir
    cp -r /tmp/ir/* /app/ 2>/dev/null || true
    cp -r /tmp/ir/.env* /app/ 2>/dev/null || true
    rm -rf /tmp/ir
fi

# MCP Server
if [ ! -f "/app/mcp-server/package.json" ]; then
    log "Clonando MCP Server..."
    rm -rf /app/mcp-server
    git clone -q -b "$INFERENCE_BRANCH" "$GIT_REPO" /tmp/mcp-tmp
    if [ -d "/tmp/mcp-tmp/mcp-server" ]; then
        mv /tmp/mcp-tmp/mcp-server /app/mcp-server
    else
        mv /tmp/mcp-tmp /app/mcp-server
    fi
    rm -rf /tmp/mcp-tmp
fi

# Build MCP Server
log "Instalando y compilando MCP Server..."
cd /app/mcp-server && npm install --silent 2>&1 | tail -2 && npm run build 2>&1 | tail -2
cd /app

# .env MCP
if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    printf "SUPABASE_URL=%s\nSUPABASE_SERVICE_ROLE_KEY=%s\nPORT=%s\n" \
        "$SUPABASE_URL" "$SUPABASE_SERVICE_ROLE_KEY" "$MCP_PORT" > /app/mcp-server/.env
    [ -n "${MCP_API_KEY:-}" ] && echo "API_KEY=${MCP_API_KEY}" >> /app/mcp-server/.env
    log ".env de MCP generado"
else
    warn "SUPABASE_URL/KEY no definidos — MCP Server puede fallar"
fi

# Dependencias FastAPI
if [ -f "/app/app/requirements.txt" ]; then
    log "Instalando dependencias FastAPI..."
    pip install -q -r /app/app/requirements.txt 2>&1 | tail -2
fi

mkdir -p /app/datasets /app/generated

log "Fase 4 completada"

# ============================================================
# FASE 5: Desplegar servicios
# ============================================================

log "=== FASE 5: Desplegar servicios ==="

cd /app

# Limpieza de procesos previos
log "Limpiando procesos TREFA previos..."
safe_kill "vllm.entrypoints.openai.api_server"
safe_kill "uvicorn app.main:app"
safe_kill "npm.*start:http"
safe_kill "node.*mcp-server.*dist"
sleep 2

# Forzar SIGKILL si quedaron
for pattern in "vllm.entrypoints.openai.api_server" "uvicorn app.main:app"; do
    remaining=$(pgrep -f "$pattern" 2>/dev/null || true)
    for pid in $remaining; do
        [ "$pid" = "$MY_PID" ] || [ "$pid" = "$MY_PPID" ] && continue
        log "  SIGKILL forzado PID $pid"
        kill -9 "$pid" 2>/dev/null || true
    done
done
sleep 1

# Liberar caché CUDA
python3 -c "
import gc; gc.collect()
try:
    import torch; torch.cuda.empty_cache()
except: pass
" 2>/dev/null || true

# GPU auto-detection para vLLM
MAX_MODEL_LEN=4096
GPU_MEMORY_UTILIZATION=0.90

if command -v nvidia-smi &>/dev/null; then
    GPU_NAME_DETECT=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "")
    case "$GPU_NAME_DETECT" in
        *A40*|*a40*)
            MAX_MODEL_LEN=8192; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: A40 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *A6000*|*a6000*|*5880*|*6000*Ada*)
            MAX_MODEL_LEN=8192; GPU_MEMORY_UTILIZATION=0.85
            log "GPU config: A6000/6000 Ada — max_model_len=$MAX_MODEL_LEN"
            ;;
        *A100*|*a100*)
            MAX_MODEL_LEN=16384; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: A100 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *H100*|*h100*)
            MAX_MODEL_LEN=32768; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: H100 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *RTX*PRO*6000*|*RTX*6000*Blackwell*)
            MAX_MODEL_LEN=16384; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: RTX PRO 6000 Blackwell — max_model_len=$MAX_MODEL_LEN"
            ;;
        *)
            MAX_MODEL_LEN=8192; GPU_MEMORY_UTILIZATION=0.85
            log "GPU ($GPU_NAME_DETECT), defaults moderados"
            ;;
    esac
fi

# Verificar modelo
if [ ! -f "$MERGED_DIR/config.json" ]; then
    die "Modelo mergeado no encontrado en $MERGED_DIR — no se puede iniciar vLLM"
fi

MERGED_SIZE=$(du -sh "$MERGED_DIR" 2>/dev/null | cut -f1 || echo "?")
log "Modelo para deploy: $MERGED_DIR ($MERGED_SIZE)"

# ─── 5a. vLLM ───────────────────────────────────────────────

log "5a. Iniciando vLLM (puerto $VLLM_PORT)..."

if [ -f /opt/supervisor-scripts/vllm.sh ]; then
    chmod -x /opt/supervisor-scripts/vllm.sh 2>/dev/null || true
    supervisorctl stop vllm 2>/dev/null || true
fi

ulimit -u unlimited 2>/dev/null || true
ulimit -n 65535 2>/dev/null || true

tmux kill-session -t vllm 2>/dev/null || true
tmux new-session -d -s vllm "\
    VLLM_USE_V1=0 python3 -m vllm.entrypoints.openai.api_server \
        --model '$MERGED_DIR' \
        --served-model-name '$SERVED_MODEL' \
        --port $VLLM_PORT \
        --dtype bfloat16 \
        --enforce-eager \
        --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \
        --max-model-len $MAX_MODEL_LEN \
        --trust-remote-code \
        --host 0.0.0.0 \
    2>&1 | tee /tmp/vllm.log"

sleep 5
VLLM_PID=$(pgrep -f "vllm.entrypoints.openai.api_server" 2>/dev/null | head -1 || echo "")
log "vLLM tmux session creada (PID: ${VLLM_PID:-pendiente})"

# Esperar vLLM (hasta 10 minutos)
for i in $(seq 1 120); do
    if curl -sf "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
        log "vLLM listo! ($((i * 5))s)"
        break
    fi
    if ! pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null 2>&1; then
        log "ERROR: vLLM crasheó. Últimas líneas:"
        tail -30 /tmp/vllm.log 2>/dev/null || true
        die "vLLM no pudo iniciar — revisa /tmp/vllm.log"
    fi
    [ $((i % 12)) -eq 0 ] && log "  vLLM cargando... ($((i * 5))s)"
    sleep 5
done

# Verificar modelo
if curl -sf "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
    MODEL_CHECK=$(curl -s "http://localhost:${VLLM_PORT}/v1/models" \
        | python3 -c "import sys,json;print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null || echo "FAIL")
    log "vLLM modelo cargado: $MODEL_CHECK"

    # Test rápido
    RESPONSE=$(curl -s -X POST "http://localhost:${VLLM_PORT}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{"model":"'"$SERVED_MODEL"'","messages":[{"role":"user","content":"hola"}],"max_tokens":50}')
    CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'][:100])" 2>/dev/null || echo "FAIL")
    log "vLLM test: $CONTENT"
else
    warn "vLLM no respondió después de 10 minutos"
fi

VLLM_PID=$(pgrep -f "vllm.entrypoints.openai.api_server" 2>/dev/null | head -1 || echo "")

# ─── 5b. MCP Server ─────────────────────────────────────────

log "5b. Iniciando MCP Server (puerto $MCP_PORT)..."

tmux kill-session -t mcp 2>/dev/null || true
tmux new-session -d -s mcp "cd /app/mcp-server && npm run start:http 2>&1 | tee /tmp/mcp-server.log"

sleep 3
MCP_PID=$(pgrep -f "node.*mcp-server" 2>/dev/null | head -1 || echo "")

if curl -sf "http://localhost:${MCP_PORT}/health" > /dev/null 2>&1; then
    log "MCP Server listo (PID: ${MCP_PID:-?})"
else
    warn "MCP Server no respondió en /health"
fi

# ─── 5c. FastAPI ─────────────────────────────────────────────

log "5c. Iniciando FastAPI (puerto $FASTAPI_PORT)..."

tmux kill-session -t fastapi 2>/dev/null || true
tmux new-session -d -s fastapi "\
    cd /app && \
    TREFA_VLLM_BASE_URL=http://localhost:${VLLM_PORT} \
    TREFA_VLLM_PORT=${VLLM_PORT} \
    TREFA_VLLM_API_KEY=EMPTY \
    TREFA_DEFAULT_LORA=${SERVED_MODEL} \
    TREFA_MCP_SERVER_URL=http://localhost:${MCP_PORT} \
    PYTHONPATH=/app \
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${FASTAPI_PORT} \
    2>&1 | tee /tmp/fastapi.log"

sleep 5
FASTAPI_PID=$(pgrep -f "uvicorn app.main:app" 2>/dev/null | head -1 || echo "")

if wait_for_service "FastAPI" localhost "$FASTAPI_PORT" 30; then
    log "FastAPI listo (PID: ${FASTAPI_PID:-?})"
else
    warn "FastAPI no respondió — revisar /tmp/fastapi.log"
    tail -15 /tmp/fastapi.log 2>/dev/null || true
fi

log "Fase 5 completada"

# ============================================================
# FASE 6: Cloudflare Tunnel
# ============================================================

log "=== FASE 6: Cloudflare Tunnel ==="

CF_CRED_FILE="/root/.cloudflared/${CF_TUNNEL_ID}.json"
CF_URL=""

if [ "$SKIP_TUNNEL" = true ]; then
    log "Tunnel saltado (--skip-tunnel)"
elif [ -n "${CF_TUNNEL_CRED:-}" ]; then
    log "Configurando Cloudflare Tunnel (${CF_TUNNEL_DOMAIN})..."

    pkill -f "cloudflared tunnel" 2>/dev/null || true
    sleep 1
    rm -rf /root/.cloudflared
    mkdir -p /root/.cloudflared

    echo "$CF_TUNNEL_CRED" > "$CF_CRED_FILE"
    chmod 600 "$CF_CRED_FILE"

    cat > /root/.cloudflared/config.yml << CFEOF
tunnel: ${CF_TUNNEL_ID}
credentials-file: ${CF_CRED_FILE}
ingress:
  - hostname: ${CF_TUNNEL_DOMAIN}
    service: http://localhost:${FASTAPI_PORT}
    originRequest:
      noTLSVerify: true
  - service: http_status:404
CFEOF

    tmux kill-session -t tunnel 2>/dev/null || true
    tmux new-session -d -s tunnel "cloudflared tunnel run trefa-vllm 2>&1 | tee /tmp/cloudflared.log"

    sleep 5
    CF_PID=$(pgrep -f "cloudflared tunnel" 2>/dev/null | head -1 || echo "")

    if [ -n "$CF_PID" ]; then
        CF_URL="https://${CF_TUNNEL_DOMAIN}"
        log "Cloudflare Tunnel activo (PID=$CF_PID)"
        log "  ${CF_URL} → localhost:${FASTAPI_PORT}"

        sleep 5
        if curl -sf "${CF_URL}/health" > /dev/null 2>&1; then
            log "  Tunnel verificado OK: ${CF_URL}/health"
        else
            warn "  Tunnel no verificado aún — puede necesitar más tiempo"
        fi
    else
        warn "Cloudflare Tunnel no arrancó — ver /tmp/cloudflared.log"
        tail -10 /tmp/cloudflared.log 2>/dev/null || true
    fi
else
    log "CF_TUNNEL_CRED no definido — tunnel desactivado"
fi

log "Fase 6 completada"

# ============================================================
# FASE 7: Resumen final
# ============================================================

log "=== FASE 7: Resumen ==="

# SSH
if ! pgrep -x sshd > /dev/null 2>&1; then
    mkdir -p /var/run/sshd /root/.ssh
    chmod 700 /root/.ssh
    sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config 2>/dev/null || true
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config 2>/dev/null || true
    /usr/sbin/sshd 2>/dev/null || true
fi

# Estados
VLLM_STATUS="OFF"
VLLM_PID=$(pgrep -f "vllm.entrypoints.openai.api_server" 2>/dev/null | head -1 || echo "")
[ -n "$VLLM_PID" ] && VLLM_STATUS="OK (PID $VLLM_PID)"

MCP_STATUS="OFF"
MCP_PID=$(pgrep -f "node.*mcp-server" 2>/dev/null | head -1 || echo "")
[ -n "$MCP_PID" ] && MCP_STATUS="OK (PID $MCP_PID)"

FASTAPI_STATUS="OFF"
FASTAPI_PID=$(pgrep -f "uvicorn app.main:app" 2>/dev/null | head -1 || echo "")
[ -n "$FASTAPI_PID" ] && FASTAPI_STATUS="OK (PID $FASTAPI_PID)"

CF_STATUS="OFF"
CF_PID=$(pgrep -f "cloudflared tunnel" 2>/dev/null | head -1 || echo "")
[ -n "$CF_PID" ] && CF_STATUS="OK (PID $CF_PID)"

SSH_STATUS="OFF"
pgrep -x sshd > /dev/null 2>&1 && SSH_STATUS="OK"

VRAM_INFO="N/A"
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "N/A")
    USED_MB=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs || echo "?")
    TOTAL_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs || echo "?")
    VRAM_INFO="${USED_MB}MB / ${TOTAL_MB}MB"
fi

MERGED_SIZE=$(du -sh "$MERGED_DIR" 2>/dev/null | cut -f1 || echo "N/A")
DISK_FREE=$(df -h /app 2>/dev/null | awk 'NR==2{print $4}' || echo "N/A")

log ""
log "╔══════════════════════════════════════════════════════════════╗"
log "║       TREFA Mariana v11 — DEPLOY TOGETHER COMPLETO          ║"
log "╠══════════════════════════════════════════════════════════════╣"
log "║                                                              ║"
log "║  MODELO (Together AI)                                        ║"
log "║    LoRA repo:    $HF_LORA_REPO"
log "║    Merged repo:  $HF_MERGED_REPO"
log "║    Merged dir:   $MERGED_DIR ($MERGED_SIZE)"
log "║    Served as:    $SERVED_MODEL"
log "║                                                              ║"
log "║  GPU                                                         ║"
log "║    Device:       ${GPU_NAME:-N/A}"
log "║    VRAM:         $VRAM_INFO"
log "║    Disco libre:  $DISK_FREE"
log "║                                                              ║"
log "║  SERVICIOS                                                   ║"
log "║    vLLM:         :$VLLM_PORT  → $VLLM_STATUS"
log "║    MCP Server:   :$MCP_PORT  → $MCP_STATUS"
log "║    FastAPI:      :$FASTAPI_PORT  → $FASTAPI_STATUS"
log "║    Tunnel:       $CF_STATUS"
log "║    SSH:          $SSH_STATUS"
log "║                                                              ║"
log "║  ENDPOINTS                                                   ║"
log "║    vLLM:         http://localhost:${VLLM_PORT}/v1"
log "║    FastAPI:      http://localhost:${FASTAPI_PORT}"
if [ -n "$CF_URL" ]; then
log "║    Público:      ${CF_URL}"
log "║    Health:       ${CF_URL}/health"
fi
log "║                                                              ║"
log "║  TMUX SESSIONS                                               ║"
log "║    tmux attach -t vllm      (logs vLLM)"
log "║    tmux attach -t mcp       (logs MCP)"
log "║    tmux attach -t fastapi   (logs FastAPI)"
if [ -n "$CF_URL" ]; then
log "║    tmux attach -t tunnel    (logs Cloudflare)"
fi
log "║                                                              ║"
log "╚══════════════════════════════════════════════════════════════╝"
log ""
log "Deploy completado. Servicios corriendo en background."
log "Para detener: tmux kill-server"
log ""

# Mantener script vivo
wait

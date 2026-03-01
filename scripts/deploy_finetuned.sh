#!/bin/bash
# ============================================================
# TREFA - Deploy Fine-Tuned Qwen3-32B con vLLM (Tensor Parallel)
# Descarga base + LoRA, mergea, y sirve con vLLM + FastAPI
#
# Optimizado para 2x A40 (45GB VRAM cada una, 90GB total)
# Usa tensor parallelism para distribuir el modelo en ambas GPUs
#
# Asume que las dependencias ya están instaladas:
#   torch, transformers, peft, accelerate, vllm, huggingface_hub
#
# Variables de entorno requeridas:
#   HF_TOKEN                    (obligatoria)
#   GITHUB_TOKEN                (opcional, repo es público)
#   SUPABASE_URL                (opcional, para MCP Server)
#   SUPABASE_SERVICE_ROLE_KEY   (opcional, para MCP Server)
#   CF_TUNNEL_CRED              (opcional, JSON credenciales Cloudflare Tunnel → api.trefa.mx)
#
# Puertos:
#   vLLM    → 8001 (evita conflicto con Caddy de vast.ai en 8000)
#   MCP     → 3001
#   FastAPI → 8081 (evita conflicto con Jupyter de vast.ai en 8080)
# ============================================================

set -euo pipefail

LOG_FILE="/tmp/trefa-finetuned.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# ============================================================
# Fase 1: Validar env vars + detectar GPU
# ============================================================
log "=== TREFA Fine-Tuned Deploy (Qwen3-32B + Tensor Parallel) ==="

if [ -z "${HF_TOKEN:-}" ]; then
    log "ERROR: HF_TOKEN no está definido."
    exit 1
fi
export HF_TOKEN
export HF_HUB_ENABLE_HF_TRANSFER=1


if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    log "WARN: SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no definidos. MCP Server puede fallar."
fi

# --- Desactivar vLLM de vast.ai (si existe) ---
if [ -f /opt/supervisor-scripts/vllm.sh ]; then
    log "Desactivando vLLM de vast.ai..."
    chmod -x /opt/supervisor-scripts/vllm.sh 2>/dev/null || true
    supervisorctl stop vllm 2>/dev/null || true
fi

# --- Limpiar GPU de procesos huérfanos ---
log "Limpiando GPU de procesos previos..."
fuser -k /dev/nvidia* 2>/dev/null || true
sleep 3

# --- Fijar límites de threads/procesos ---
ulimit -u unlimited 2>/dev/null || true
ulimit -n 65535 2>/dev/null || true
export OPENBLAS_NUM_THREADS=1

# --- Auto-detección de GPU ---
detect_gpu() {
    if ! command -v nvidia-smi &>/dev/null; then
        log "WARN: nvidia-smi no encontrado"
        echo "unknown"
        return
    fi
    local gpu_name
    gpu_name=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
    if [ -z "$gpu_name" ]; then
        echo "unknown"
        return
    fi
    log "GPU detectada: $gpu_name"
    echo "$gpu_name"
}

detect_gpu_count() {
    if ! command -v nvidia-smi &>/dev/null; then
        echo "1"
        return
    fi
    local count
    count=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader,nounits 2>/dev/null | wc -l | xargs)
    if [ -z "$count" ] || [ "$count" -eq 0 ]; then
        echo "1"
        return
    fi
    echo "$count"
}

configure_gpu() {
    local gpu_name="$1"
    local gpu_count="$2"
    case "$gpu_name" in
        *A40*|*a40*)
            log "Configurando para A40 (45GB VRAM) x${gpu_count}"
            DEFAULT_MAX_MODEL_LEN=8192
            DEFAULT_GPU_MEM=0.90
            ;;
        *5090*)
            log "Configurando para RTX 5090 (32GB VRAM) x${gpu_count}"
            DEFAULT_MAX_MODEL_LEN=4096
            DEFAULT_GPU_MEM=0.85
            ;;
        *A6000*|*a6000*)
            log "Configurando para A6000 (48GB VRAM) x${gpu_count}"
            DEFAULT_MAX_MODEL_LEN=8192
            DEFAULT_GPU_MEM=0.85
            ;;
        *A100*|*a100*)
            log "Configurando para A100 (40/80GB VRAM) x${gpu_count}"
            DEFAULT_MAX_MODEL_LEN=16384
            DEFAULT_GPU_MEM=0.90
            ;;
        *H100*|*h100*)
            log "Configurando para H100 (80GB VRAM) x${gpu_count}"
            DEFAULT_MAX_MODEL_LEN=32768
            DEFAULT_GPU_MEM=0.90
            ;;
        *)
            log "GPU no reconocida, usando defaults conservadores"
            DEFAULT_MAX_MODEL_LEN=8192
            DEFAULT_GPU_MEM=0.85
            ;;
    esac
    MAX_MODEL_LEN=${MAX_MODEL_LEN:-$DEFAULT_MAX_MODEL_LEN}
    GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-$DEFAULT_GPU_MEM}
    DTYPE=${DTYPE:-"bfloat16"}
    TENSOR_PARALLEL=${TENSOR_PARALLEL:-$gpu_count}
    log "  MAX_MODEL_LEN=$MAX_MODEL_LEN"
    log "  GPU_MEMORY_UTILIZATION=$GPU_MEMORY_UTILIZATION"
    log "  DTYPE=$DTYPE"
    log "  TENSOR_PARALLEL=$TENSOR_PARALLEL (GPUs: $gpu_count)"
}

GPU_NAME=$(detect_gpu)
GPU_COUNT=$(detect_gpu_count)
configure_gpu "$GPU_NAME" "$GPU_COUNT"

# --- Instalar dependencias Python ---
log "Instalando dependencias Python..."
pip install --upgrade peft accelerate transformers huggingface_hub hf_transfer vllm 2>&1 | tail -5

# ============================================================
# Fase 2: Descargar modelos (base + LoRA adapter)
# ============================================================
BASE_MODEL_ID="Qwen/Qwen3-32B"
LORA_REPO_ID="mmoralesf/qwen3-32B-mariana"

BASE_DIR="/app/modelos/qwen3-32b-base"
LORA_DIR="/app/modelos/qwen3-32b-mariana"
MERGED_DIR="/app/modelos/qwen3-32b-merged"

mkdir -p /app/modelos

if [ ! -f "$BASE_DIR/config.json" ]; then
    log "Descargando modelo base: $BASE_MODEL_ID (~65GB)..."
    huggingface-cli download "$BASE_MODEL_ID" \
        --local-dir "$BASE_DIR" \
        --local-dir-use-symlinks False
    log "Modelo base descargado en $BASE_DIR"
else
    log "Modelo base encontrado en $BASE_DIR"
fi

if [ ! -d "$LORA_DIR" ] || [ -z "$(ls -A $LORA_DIR 2>/dev/null)" ]; then
    log "Descargando LoRA adapter: $LORA_REPO_ID..."
    huggingface-cli download "$LORA_REPO_ID" \
        --local-dir "$LORA_DIR" \
        --local-dir-use-symlinks False
    log "LoRA adapter descargado en $LORA_DIR"
else
    log "LoRA adapter encontrado en $LORA_DIR"
fi

# ============================================================
# Fase 3: Merge LoRA → modelo completo
# ============================================================
if [ -f "$MERGED_DIR/config.json" ]; then
    log "Modelo mergeado encontrado en $MERGED_DIR, saltando merge."
else
    log "Mergeando LoRA con modelo base..."
    log "  Base: $BASE_DIR"
    log "  LoRA: $LORA_DIR"
    log "  Output: $MERGED_DIR"
    log "  NOTA: Qwen3-32B requiere ~64GB RAM para merge en CPU"

    python3 << 'MERGE_SCRIPT'
import torch
import os
import shutil
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_DIR = "/app/modelos/qwen3-32b-base"
LORA_DIR = "/app/modelos/qwen3-32b-mariana"
MERGED_DIR = "/app/modelos/qwen3-32b-merged"

print("[merge] Cargando tokenizer (fast)...")
tokenizer = AutoTokenizer.from_pretrained(BASE_DIR, trust_remote_code=True, use_fast=True)

print("[merge] Cargando modelo base Qwen3-32B (bf16, ~64GB RAM)...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_DIR,
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    trust_remote_code=True,
)

print("[merge] Cargando LoRA adapter...")
model = PeftModel.from_pretrained(base_model, LORA_DIR)

print("[merge] Mergeando pesos...")
model = model.merge_and_unload()

print(f"[merge] Guardando modelo mergeado en {MERGED_DIR}...")
os.makedirs(MERGED_DIR, exist_ok=True)
model.save_pretrained(MERGED_DIR, safe_serialization=True)
tokenizer.save_pretrained(MERGED_DIR)

print("[merge] Merge completado.")
MERGE_SCRIPT

    if [ ! -f "$MERGED_DIR/config.json" ]; then
        log "ERROR: Merge falló - config.json no encontrado en $MERGED_DIR"
        exit 1
    fi
    log "Merge completado exitosamente."
fi

# ============================================================
# Fase 4: Clonar repositorios
# ============================================================
log "Preparando repositorios..."
mkdir -p /app

GIT_REPO_URL="https://github.com/marianomoralesr/mcp-server.git"

if [ ! -d "/app/app" ]; then
    log "Clonando inference-server..."
    git clone -b inference-server "$GIT_REPO_URL" /tmp/inference-repo
    cp -r /tmp/inference-repo/* /app/
    rm -rf /tmp/inference-repo
fi

if [ ! -d "/app/mcp-server/.git" ]; then
    log "Clonando mcp-server..."
    rm -rf /app/mcp-server
    git clone -b main "$GIT_REPO_URL" /app/mcp-server
fi

# --- Asegurar Node.js 20+ (TypeScript necesita nullish coalescing) ---
NODE_VERSION=$(node -v 2>/dev/null | grep -oP '\d+' | head -1 || echo "0")
if [ "$NODE_VERSION" -lt 18 ]; then
    log "Node.js v${NODE_VERSION} es muy viejo, instalando Node 20..."
    apt-get remove -y nodejs npm libnode-dev libnode72 2>/dev/null || true
    dpkg --configure -a 2>/dev/null || true
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    hash -r
    log "Node.js $(node -v) / npm $(npm -v) instalados."
else
    log "Node.js $(node -v) OK."
fi

# ============================================================
# Fase 5: Setup MCP Server
# ============================================================
log "Configurando MCP Server..."
cd /app/mcp-server
npm install
npm run build

if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    cat > /app/mcp-server/.env <<EOF
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
PORT=${MCP_PORT:-3001}
EOF
    if [ -n "${MCP_API_KEY:-}" ]; then
        echo "API_KEY=${MCP_API_KEY}" >> /app/mcp-server/.env
    fi
    log ".env de MCP generado."
else
    log "WARN: Credenciales Supabase no definidas, MCP .env no generado."
fi

# --- Dependencias de FastAPI ---
log "Instalando dependencias de FastAPI..."
pip install -r /app/app/requirements.txt

mkdir -p /app/datasets /app/generated

# ============================================================
# Fase 6: Health check + Cleanup
# ============================================================
wait_for_service() {
    local name="$1" url="$2" max_retries="$3" interval="$4"
    log "Esperando a $name..."
    for i in $(seq 1 "$max_retries"); do
        if curl -sf "$url" > /dev/null 2>&1; then
            log "$name listo."
            return 0
        fi
        if [ "$((i % 10))" -eq 0 ]; then
            log "  $name: intento $i/$max_retries..."
        fi
        sleep "$interval"
    done
    log "ERROR: $name no respondió después de $max_retries intentos."
    return 1
}

MCP_PID=""
VLLM_PID=""
FASTAPI_PID=""

cleanup() {
    log "Deteniendo servicios..."
    [ -n "$FASTAPI_PID" ] && kill "$FASTAPI_PID" 2>/dev/null || true
    [ -n "$VLLM_PID" ] && kill "$VLLM_PID" 2>/dev/null || true
    [ -n "$MCP_PID" ] && kill "$MCP_PID" 2>/dev/null || true
    pkill -f "cloudflared tunnel" 2>/dev/null || true
    wait 2>/dev/null || true
    log "Todos los servicios detenidos."
}

trap cleanup EXIT INT TERM

# ============================================================
# Fase 7: Iniciar servicios
# ============================================================

VLLM_PORT=${VLLM_PORT:-8001}
FASTAPI_PORT=${TREFA_FASTAPI_PORT:-8081}

# --- MCP Server (puerto 3001) ---
log "Iniciando MCP Server en puerto ${MCP_PORT:-3001}..."
cd /app/mcp-server
nohup npm run start:http > /tmp/mcp-server.log 2>&1 &
MCP_PID=$!
cd /app

if ! wait_for_service "MCP Server" "http://localhost:${MCP_PORT:-3001}/health" 30 2; then
    log "WARN: MCP Server no respondió, continuando..."
fi

# --- vLLM (puerto 8001, evita Caddy en 8000) ---
# VLLM_USE_V1=0: engine legacy, más estable con torch 2.9+
# --enforce-eager: desactiva CUDA graphs (evita segfault)
# --tensor-parallel-size: distribuye modelo entre GPUs
export VLLM_USE_V1=0
log "Arrancando vLLM en puerto $VLLM_PORT (Qwen3-32B merged, TP=$TENSOR_PARALLEL, MAX_MODEL_LEN=$MAX_MODEL_LEN, GPU_MEM=$GPU_MEMORY_UTILIZATION)..."
python3 -m vllm.entrypoints.openai.api_server \
    --model "$MERGED_DIR" \
    --served-model-name trefa-lora \
    --max-model-len "$MAX_MODEL_LEN" \
    --dtype "$DTYPE" \
    --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
    --tensor-parallel-size "$TENSOR_PARALLEL" \
    --enforce-eager \
    --host 0.0.0.0 \
    --port "$VLLM_PORT" > /tmp/vllm.log 2>&1 &
VLLM_PID=$!

# Qwen3-32B tarda más en cargar con TP, 300 intentos x 5s = 25 min max
if ! wait_for_service "vLLM" "http://localhost:${VLLM_PORT}/v1/models" 300 5; then
    log "ERROR: vLLM no arrancó. Últimas líneas del log:"
    tail -50 /tmp/vllm.log 2>/dev/null || true
    exit 1
fi

# --- FastAPI (puerto 8081, evita Jupyter en 8080) ---
log "Iniciando FastAPI en puerto $FASTAPI_PORT..."
cd /app
TREFA_VLLM_BASE_URL="http://localhost:${VLLM_PORT}" \
TREFA_VLLM_PORT=$VLLM_PORT python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$FASTAPI_PORT" > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!

if ! wait_for_service "FastAPI" "http://localhost:${FASTAPI_PORT}/health" 30 2; then
    log "ERROR: FastAPI no arrancó. Últimas líneas del log:"
    tail -30 /tmp/fastapi.log 2>/dev/null || true
    exit 1
fi

# ============================================================
# Fase 8: Monitor
# ============================================================
log "============================================"
log "Todos los servicios activos."
log "  MCP Server  PID=$MCP_PID  (puerto ${MCP_PORT:-3001})"
log "  vLLM        PID=$VLLM_PID  (puerto $VLLM_PORT) → modelo: trefa-lora (Qwen3-32B, TP=$TENSOR_PARALLEL)"
log "  FastAPI     PID=$FASTAPI_PID  (puerto $FASTAPI_PORT)"
log "============================================"
log "Verificación rápida:"
log "  curl http://localhost:${VLLM_PORT}/v1/models"
log "  curl http://localhost:${FASTAPI_PORT}/health"
log "============================================"

# ============================================================
# Fase 9: Cloudflare Tunnel (api.trefa.mx)
# ============================================================
CF_TUNNEL_ID="d15177d1-cb8c-4ed9-b8de-ff52c8f3d749"
CF_TUNNEL_DOMAIN="api.trefa.mx"
CF_CRED_FILE="/root/.cloudflared/${CF_TUNNEL_ID}.json"

if [ -n "${CF_TUNNEL_CRED:-}" ]; then
    log "Configurando Cloudflare Tunnel (${CF_TUNNEL_DOMAIN})..."

    # Instalar cloudflared
    if ! command -v cloudflared &>/dev/null; then
        log "Instalando cloudflared..."
        curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
            -o /usr/local/bin/cloudflared
        chmod +x /usr/local/bin/cloudflared
    fi

    # Limpiar config anterior
    pkill -f "cloudflared tunnel" 2>/dev/null || true
    sleep 1
    rm -rf /root/.cloudflared
    mkdir -p /root/.cloudflared

    # Escribir credenciales y config
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

    # Iniciar tunnel
    nohup cloudflared tunnel run trefa-vllm > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    sleep 3

    if kill -0 "$CF_PID" 2>/dev/null; then
        log "Cloudflare Tunnel activo (PID=$CF_PID)"
        log "  https://${CF_TUNNEL_DOMAIN} → localhost:${FASTAPI_PORT}"
    else
        log "WARN: Cloudflare Tunnel no arrancó. Ver /tmp/cloudflared.log"
    fi
else
    log "CF_TUNNEL_CRED no definido, tunnel desactivado."
fi

log "Monitoreando procesos..."

wait -n "$VLLM_PID" "$MCP_PID" "$FASTAPI_PID" 2>/dev/null
EXIT_CODE=$?

for proc_info in "VLLM:$VLLM_PID" "MCP:$MCP_PID" "FastAPI:$FASTAPI_PID"; do
    name="${proc_info%%:*}"
    pid="${proc_info##*:}"
    if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
        log "ALERTA: $name (PID $pid) terminó inesperadamente."
    fi
done

log "Proceso terminó con código $EXIT_CODE. Saliendo..."
exit "$EXIT_CODE"

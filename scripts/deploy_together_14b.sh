#!/bin/bash
# ============================================================
# TREFA — Deploy Mariana v8 (Deploy-only, modelo pre-mergeado)
#
# El modelo ya está descargado y mergeado en disco.
# Este script solo:
#   1. Limpia procesos colgados y libera VRAM
#   2. Verifica que el modelo exista
#   3. Instala dependencias
#   4. Despliega vLLM + MCP Server + FastAPI
#   5. Configura Cloudflare Tunnel (opcional)
#
# GPU: 1x A6000/A40 (48GB VRAM) o similar
#
# Env vars requeridas:
#   HF_TOKEN                     (obligatoria)
#   CF_TUNNEL_CRED               (opcional) — JSON de credenciales Cloudflare Tunnel
#                                  Activa tunnel fijo en api.trefa.mx
#   SUPABASE_URL                 (opcional, para MCP Server)
#   SUPABASE_SERVICE_ROLE_KEY    (opcional, para MCP Server)
#
# Flags:
#   --skip-tunnel       No crea Cloudflare Tunnel
#
# Puertos:
#   vLLM    → 8001
#   MCP     → 3001
#   FastAPI → 8081
#
# Uso:
#   export HF_TOKEN=hf_xxx
#   bash deploy_together_14b.sh
#
#   # Sin tunnel
#   bash deploy_together_14b.sh --skip-tunnel
# ============================================================

set -euo pipefail
exec > >(tee -a /tmp/trefa-deploy.log) 2>&1

log() { echo "[$(date +'%H:%M:%S')] $1"; }

# ============================================================
# 0. PARSE FLAGS
# ============================================================
SKIP_TUNNEL=false

for arg in "$@"; do
    case "$arg" in
        --skip-tunnel)    SKIP_TUNNEL=true ;;
        *) log "WARN: Flag desconocido: $arg" ;;
    esac
done

# ============================================================
# 1. CONFIG
# ============================================================
log "=== TREFA Mariana v8 — Deploy Pipeline ==="

LORA_REPO="mmoralesf/qwen3-14B-mariana-v8"
MERGED_DIR="/app/modelos/qwen3-14b-mariana-v8"

VLLM_PORT=${VLLM_PORT:-8001}
FASTAPI_PORT=${TREFA_FASTAPI_PORT:-8081}
MCP_PORT=${MCP_PORT:-3001}
GIT_REPO="https://github.com/marianomoralesr/mcp-server.git"

export OPENBLAS_NUM_THREADS=1
export HF_HUB_ENABLE_HF_TRANSFER=1

# Validar token
if [ -z "${HF_TOKEN:-}" ]; then
    log "ERROR: HF_TOKEN no definido"
    exit 1
fi
export HF_TOKEN

log "Config:"
log "  Modelo:       $LORA_REPO"
log "  Directorio:   $MERGED_DIR"
log "  Skip tunnel:  $SKIP_TUNNEL"

# ============================================================
# 2. LIMPIEZA DE PROCESOS Y VRAM
# ============================================================
log "Limpiando procesos previos y VRAM..."

# PID de este script — NUNCA matarnos a nosotros mismos
MY_PID=$$
MY_PPID=$PPID

# Solo matar procesos nuestros (TREFA/inference), nunca procesos del sistema
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
            log "  Terminando PID $pid: ${cmd:0:80}"
            kill -15 "$pid" 2>/dev/null || true
        fi
    done
}

# Matar servicios TREFA anteriores (patrones específicos)
safe_kill "vllm.entrypoints.openai.api_server"
safe_kill "uvicorn app.main:app"
safe_kill "npm.*start:http"
safe_kill "node.*mcp-server.*dist"

# Esperar a que terminen con SIGTERM
sleep 2

# Verificar si quedó alguno vivo, solo entonces usar SIGKILL
for pattern in "vllm.entrypoints.openai.api_server" "uvicorn app.main:app"; do
    remaining=$(pgrep -f "$pattern" 2>/dev/null || true)
    for pid in $remaining; do
        [ "$pid" = "$MY_PID" ] || [ "$pid" = "$MY_PPID" ] && continue
        log "  SIGKILL forzado PID $pid (no respondió a SIGTERM)"
        kill -9 "$pid" 2>/dev/null || true
    done
done

# Liberar VRAM de procesos Python/vLLM en GPU (NO matar todo lo que use la GPU)
if command -v nvidia-smi &>/dev/null; then
    GPU_PIDS=$(nvidia-smi --query-compute-apps=pid,name --format=csv,noheader,nounits 2>/dev/null || true)
    while IFS=',' read -r pid name; do
        pid=$(echo "$pid" | xargs)
        name=$(echo "$name" | xargs)
        [ -z "$pid" ] && continue
        [ "$pid" = "$MY_PID" ] || [ "$pid" = "$MY_PPID" ] && continue
        case "$name" in
            *python*|*vllm*|*torch*|*triton*)
                log "  GPU: terminando PID $pid ($name)"
                kill -15 "$pid" 2>/dev/null || true
                ;;
            *)
                log "  GPU: ignorando PID $pid ($name) — no es TREFA"
                ;;
        esac
    done <<< "$GPU_PIDS"
fi

sleep 2

# Verificar estado de VRAM
if command -v nvidia-smi &>/dev/null; then
    USED_MB=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
    TOTAL_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
    log "  VRAM: ${USED_MB:-?}MB / ${TOTAL_MB:-?}MB usados"
    if [ "${USED_MB:-0}" -gt 500 ]; then
        log "  WARN: Aún hay ${USED_MB}MB ocupados (puede ser otro proceso legítimo)"
    else
        log "  VRAM libre OK"
    fi
fi

# Liberar caché de Python/CUDA en memoria (seguro, no mata nada)
if command -v python3 &>/dev/null; then
    python3 -c "
import gc; gc.collect()
try:
    import torch; torch.cuda.empty_cache()
except: pass
" 2>/dev/null || true
fi

log "Limpieza completada"

# ============================================================
# 3. VERIFICAR / DESCARGAR MODELO
# ============================================================
mkdir -p /app/modelos

log "Verificando modelo en $MERGED_DIR..."

if [ ! -f "$MERGED_DIR/config.json" ]; then
    log "Modelo no encontrado localmente. Descargando de HuggingFace: $LORA_REPO..."
    pip install -q huggingface_hub hf_transfer 2>&1 | tail -2
    mkdir -p "$MERGED_DIR"
    huggingface-cli download "$LORA_REPO" \
        --local-dir "$MERGED_DIR" \
        --local-dir-use-symlinks False

    if [ ! -f "$MERGED_DIR/config.json" ]; then
        log "ERROR: Descarga falló — config.json no encontrado después de descargar"
        exit 1
    fi
    log "Descarga completada"
fi

SAFETENSORS=$(ls "$MERGED_DIR"/model-*.safetensors 2>/dev/null | wc -l)
if [ "$SAFETENSORS" -lt 1 ]; then
    log "WARN: No se encontraron archivos model-*.safetensors"
    log "  Buscando otros formatos de peso..."
    ls "$MERGED_DIR"/*.safetensors "$MERGED_DIR"/*.bin 2>/dev/null | head -10 || true
fi

MERGED_SIZE=$(du -sh "$MERGED_DIR" 2>/dev/null | cut -f1 || echo "?")
log "Modelo verificado: $MERGED_DIR ($MERGED_SIZE)"

# ============================================================
# 4. DEPS
# ============================================================
log "Instalando dependencias..."
pip install -q vllm 2>&1 | tail -3
pip install -q httpx structlog pydantic-settings uvicorn fastapi 2>&1 | tail -3
log "Deps OK"

# --- Node.js ---
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

# ============================================================
# 5. REPOS + BUILD
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
# 6. DEPLOY (vLLM + MCP + FastAPI)
# ============================================================
cd /app

MCP_PID=""
VLLM_PID=""
FASTAPI_PID=""
CF_PID=""

cleanup() {
    log "Deteniendo servicios..."
    [ -n "$CF_PID" ] && kill "$CF_PID" 2>/dev/null || true
    [ -n "$FASTAPI_PID" ] && kill "$FASTAPI_PID" 2>/dev/null || true
    [ -n "$VLLM_PID" ] && kill "$VLLM_PID" 2>/dev/null || true
    [ -n "$MCP_PID" ] && kill "$MCP_PID" 2>/dev/null || true
    wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# MCP Server
log "MCP Server (puerto $MCP_PORT)..."
cd /app/mcp-server && nohup npm run start:http > /tmp/mcp-server.log 2>&1 & MCP_PID=$!; cd /app

# vLLM
log "vLLM (puerto $VLLM_PORT)..."
VLLM_USE_V1=0 python3 -m vllm.entrypoints.openai.api_server \
    --model "$MERGED_DIR" \
    --served-model-name trefa-lora \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --gpu-memory-utilization 0.90 \
    --enforce-eager \
    --host 0.0.0.0 \
    --port "$VLLM_PORT" > /tmp/vllm.log 2>&1 &
VLLM_PID=$!

log "Esperando vLLM (PID=$VLLM_PID)..."
for i in $(seq 1 120); do
    if curl -sf "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
        log "vLLM listo!"
        break
    fi
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
        log "ERROR: vLLM crasheó. Log:"
        tail -30 /tmp/vllm.log
        exit 1
    fi
    [ $((i % 12)) -eq 0 ] && log "  cargando... ($((i*5))s)"
    sleep 5
done

# FastAPI
log "FastAPI (puerto $FASTAPI_PORT)..."
TREFA_VLLM_PORT=$VLLM_PORT PYTHONPATH=/app python3 -m uvicorn app.main:app \
    --host 0.0.0.0 --port "$FASTAPI_PORT" > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!
sleep 3

# ============================================================
# 7. VERIFICACIÓN
# ============================================================
log "=== Verificación ==="

# Modelo cargado
MODEL_CHECK=$(curl -s "http://localhost:${VLLM_PORT}/v1/models" \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null || echo "FAIL")
log "  Modelo:  $MODEL_CHECK"

# Health FastAPI
HEALTH=$(curl -s "http://localhost:${FASTAPI_PORT}/health" \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "FAIL")
log "  Health:  $HEALTH"

# Test rápido: ¿se presenta como Mariana?
RESPONSE=$(curl -s -X POST "http://localhost:${VLLM_PORT}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"model":"trefa-lora","messages":[{"role":"user","content":"hola"}],"max_tokens":80}')
CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "FAIL")
log "  Chat:    $CONTENT"

# ============================================================
# 8. CLOUDFLARE TUNNEL (api.trefa.mx)
# ============================================================
CF_TUNNEL_ID="d15177d1-cb8c-4ed9-b8de-ff52c8f3d749"
CF_TUNNEL_DOMAIN="api.trefa.mx"
CF_CRED_FILE="/root/.cloudflared/${CF_TUNNEL_ID}.json"
CF_URL=""

if [ "$SKIP_TUNNEL" = false ] && [ -n "${CF_TUNNEL_CRED:-}" ]; then
    log "Configurando Cloudflare Tunnel (${CF_TUNNEL_DOMAIN})..."

    # Instalar cloudflared si no existe
    if ! command -v cloudflared &>/dev/null; then
        log "  Instalando cloudflared..."
        curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
            -o /usr/local/bin/cloudflared
        chmod +x /usr/local/bin/cloudflared
    fi

    # Limpiar tunnel anterior
    pkill -f "cloudflared tunnel" 2>/dev/null || true
    sleep 1
    rm -rf /root/.cloudflared
    mkdir -p /root/.cloudflared

    # Escribir credenciales desde env
    echo "$CF_TUNNEL_CRED" > "$CF_CRED_FILE"
    chmod 600 "$CF_CRED_FILE"

    # Configuracion del tunnel: api.trefa.mx → FastAPI local
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
        CF_URL="https://${CF_TUNNEL_DOMAIN}"
        log "  Cloudflare Tunnel activo (PID=$CF_PID)"
        log "  ${CF_URL} → localhost:${FASTAPI_PORT}"
    else
        log "WARN: Cloudflare Tunnel no arrancó"
        log "  Ver /tmp/cloudflared.log"
        tail -10 /tmp/cloudflared.log 2>/dev/null || true
    fi

elif [ "$SKIP_TUNNEL" = true ]; then
    log "Tunnel saltado (--skip-tunnel)"
else
    log "CF_TUNNEL_CRED no definido — tunnel desactivado"
    log "  Para activarlo: export CF_TUNNEL_CRED='{\"AccountTag\":\"...\",\"TunnelSecret\":\"...\",\"TunnelID\":\"...\"}'"
fi

# ============================================================
# 9. RESUMEN DE CONFIGURACION
# ============================================================

# Recopilar info
VRAM_INFO="N/A"
GPU_NAME="N/A"
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "N/A")
    USED_MB=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs || echo "?")
    TOTAL_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs || echo "?")
    VRAM_INFO="${USED_MB}MB / ${TOTAL_MB}MB"
fi

MERGED_SIZE=$(du -sh "$MERGED_DIR" 2>/dev/null | cut -f1 || echo "N/A")
DISK_FREE=$(df -h /app 2>/dev/null | awk 'NR==2{print $4}' || echo "N/A")
UPTIME_NOW=$(date '+%Y-%m-%d %H:%M:%S')

MCP_STATUS="OFF"
[ -n "$MCP_PID" ] && kill -0 "$MCP_PID" 2>/dev/null && MCP_STATUS="OK (PID $MCP_PID)"
VLLM_STATUS="OFF"
[ -n "$VLLM_PID" ] && kill -0 "$VLLM_PID" 2>/dev/null && VLLM_STATUS="OK (PID $VLLM_PID)"
FASTAPI_STATUS="OFF"
[ -n "$FASTAPI_PID" ] && kill -0 "$FASTAPI_PID" 2>/dev/null && FASTAPI_STATUS="OK (PID $FASTAPI_PID)"
CF_STATUS="OFF"
[ -n "$CF_PID" ] && kill -0 "$CF_PID" 2>/dev/null && CF_STATUS="OK (PID $CF_PID)"

log ""
log "╔══════════════════════════════════════════════════════════════╗"
log "║                  TREFA Mariana v8 — DEPLOY COMPLETO         ║"
log "╠══════════════════════════════════════════════════════════════╣"
log "║                                                              ║"
log "║  MODELO                                                      ║"
log "║    Repo:       $LORA_REPO"
log "║    Merged:     $MERGED_DIR ($MERGED_SIZE)"
log "║    Served as:  trefa-lora"
log "║                                                              ║"
log "║  GPU                                                         ║"
log "║    Device:     $GPU_NAME"
log "║    VRAM:       $VRAM_INFO"
log "║    Disco:      $DISK_FREE libres"
log "║                                                              ║"
log "║  SERVICIOS                                                   ║"
log "║    vLLM:       :$VLLM_PORT  → $VLLM_STATUS"
log "║    FastAPI:    :$FASTAPI_PORT  → $FASTAPI_STATUS"
log "║    MCP:        :$MCP_PORT  → $MCP_STATUS"
log "║    Tunnel:     $CF_STATUS"
log "║                                                              ║"
log "║  ENDPOINTS                                                   ║"
log "║    Local:      http://localhost:${FASTAPI_PORT}"
if [ -n "$CF_URL" ]; then
log "║    Publico:    ${CF_URL}"
log "║    Health:     ${CF_URL}/health"
log "║    Chat UI:    ${CF_URL}/ui"
log "║    API Docs:   ${CF_URL}/docs"
log "║    vLLM:       ${CF_URL}/v1/chat/completions"
else
log "║    Publico:    (no configurado)"
log "║    Health:     http://localhost:${FASTAPI_PORT}/health"
log "║    Chat UI:    http://localhost:${FASTAPI_PORT}/ui"
log "║    API Docs:   http://localhost:${FASTAPI_PORT}/docs"
fi
log "║                                                              ║"
log "║  ENV                                                         ║"
log "║    HF_TOKEN:        $([ -n "${HF_TOKEN:-}" ] && echo 'SET' || echo 'MISSING')"
log "║    CF_TUNNEL_CRED:  $([ -n "${CF_TUNNEL_CRED:-}" ] && echo 'SET' || echo 'NOT SET')"
log "║    SUPABASE_URL:    $([ -n "${SUPABASE_URL:-}" ] && echo 'SET' || echo 'NOT SET')"
log "║                                                              ║"
log "║  LOGS                                                        ║"
log "║    vLLM:       /tmp/vllm.log"
log "║    FastAPI:    /tmp/fastapi.log"
log "║    MCP:        /tmp/mcp-server.log"
log "║    Tunnel:     /tmp/cloudflared.log"
log "║    Deploy:     /tmp/trefa-deploy.log"
log "║                                                              ║"
log "║  Inicio:       $UPTIME_NOW"
log "╚══════════════════════════════════════════════════════════════╝"
log ""

# Mantener el script corriendo — monitorear todos los procesos
WAIT_PIDS="$VLLM_PID $MCP_PID $FASTAPI_PID"
[ -n "$CF_PID" ] && WAIT_PIDS="$WAIT_PIDS $CF_PID"
wait -n $WAIT_PIDS 2>/dev/null
EXIT_CODE=$?

log ""
log "=== ALERTA: Un proceso terminó inesperadamente ==="
for proc_info in "vLLM:$VLLM_PID:/tmp/vllm.log" "FastAPI:$FASTAPI_PID:/tmp/fastapi.log" "MCP:$MCP_PID:/tmp/mcp-server.log" "Tunnel:$CF_PID:/tmp/cloudflared.log"; do
    IFS=':' read -r name pid logfile <<< "$proc_info"
    if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
        log "  CAIDO: $name (PID $pid)"
        log "  Ultimas lineas de $logfile:"
        tail -5 "$logfile" 2>/dev/null | while IFS= read -r line; do log "    $line"; done
    else
        [ -n "$pid" ] && log "  OK:    $name (PID $pid)"
    fi
done

log "Proceso terminó con código $EXIT_CODE"
exit "$EXIT_CODE"

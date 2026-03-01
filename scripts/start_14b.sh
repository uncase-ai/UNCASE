#!/bin/bash
set -euo pipefail

log() { echo "[$(date +'%H:%M:%S')] $1"; }

# ============================================================
# 1. Matar todo lo que estorbe
# ============================================================
log "Limpiando procesos previos nuestros..."
# NO tocar supervisor ni vLLM de vast.ai - usamos puerto 8001
pkill -9 -f "uvicorn" 2>/dev/null || true
sleep 1

# ============================================================
# 2. Limpiar env vars de vast.ai que interfieren
# ============================================================
unset VLLM_ARGS 2>/dev/null || true
unset VLLM_MODEL 2>/dev/null || true

# ============================================================
# 3. Verificar que el modelo mergeado existe
# ============================================================
MODEL_DIR="/app/modelos/qwen3-14b-merged"
if [ ! -f "$MODEL_DIR/config.json" ]; then
    log "ERROR: Modelo mergeado no encontrado en $MODEL_DIR"
    exit 1
fi
log "Modelo encontrado: $MODEL_DIR"

# ============================================================
# 4. Iniciar MCP Server
# ============================================================
log "Iniciando MCP Server (puerto 3001)..."
cd /app/mcp-server
nohup npm run start:http > /tmp/mcp-server.log 2>&1 &
MCP_PID=$!
cd /app
sleep 2

# ============================================================
# 5. Iniciar vLLM
# ============================================================
log "Iniciando vLLM (puerto 8000)..."
VLLM_USE_V1=0 python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_DIR" \
    --served-model-name trefa-lora \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --gpu-memory-utilization 0.90 \
    --enforce-eager \
    --host 0.0.0.0 \
    --port 8001 > /tmp/vllm.log 2>&1 &
VLLM_PID=$!

log "Esperando vLLM (PID=$VLLM_PID)..."
for i in $(seq 1 120); do
    if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
        log "vLLM listo!"
        break
    fi
    if ! kill -0 $VLLM_PID 2>/dev/null; then
        log "ERROR: vLLM se cayó. Log:"
        tail -30 /tmp/vllm.log
        exit 1
    fi
    [ $((i % 10)) -eq 0 ] && log "  intento $i/120..."
    sleep 5
done

# Verificar modelo
MODEL_CHECK=$(curl -s http://localhost:8001/v1/models | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['data'][0]['id'])" 2>/dev/null || echo "FAIL")
if [ "$MODEL_CHECK" != "trefa-lora" ]; then
    log "ERROR: Modelo incorrecto: $MODEL_CHECK (esperado: trefa-lora)"
    log "Matando vLLM ajeno y reintentando no es opción. Revisa /tmp/vllm.log"
    exit 1
fi
log "Modelo verificado: $MODEL_CHECK"

# ============================================================
# 6. Iniciar FastAPI
# ============================================================
log "Iniciando FastAPI (puerto 8081)..."
cd /app
TREFA_VLLM_PORT=8001 PYTHONPATH=/app python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8081 > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!
sleep 3

if ! curl -sf http://localhost:8081/health > /dev/null 2>&1; then
    log "ERROR: FastAPI no arrancó. Log:"
    tail -20 /tmp/fastapi.log
    exit 1
fi

# ============================================================
# 7. Test directo a vLLM
# ============================================================
log "Test: enviando mensaje a vLLM..."
RESPONSE=$(curl -s -X POST http://localhost:8001/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"trefa-lora","messages":[{"role":"user","content":"hola"}],"max_tokens":30}')
CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "FAIL")
log "Respuesta vLLM: $CONTENT"

# ============================================================
# 8. Resumen
# ============================================================
log "============================================"
log "Todo activo:"
log "  MCP     PID=$MCP_PID     puerto 3001"
log "  vLLM    PID=$VLLM_PID    puerto 8001  modelo=trefa-lora"
log "  FastAPI PID=$FASTAPI_PID puerto 8081"
log "============================================"
log "Probar: curl -s http://localhost:8081/v1/chat -H 'Content-Type: application/json' -d '{\"message\":\"hola\",\"session_id\":\"test\"}'"
log "Logs:   tail -f /tmp/vllm.log"

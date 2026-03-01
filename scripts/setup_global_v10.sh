#!/usr/bin/env bash
# ============================================================
# TREFA — Setup Global v11 (GPU vast.ai)
#
# Script completo que configura una máquina GPU desde cero:
#   Fase 0: Bootstrap y configuración
#   Fase 1: Dependencias del sistema
#   Fase 2: Dependencias Python para fine-tuning
#   Fase 3: Descargar modelo base y dataset
#   Fase 4: Fine-tuning con LoRA bf16 (LoRA)
#   Fase 5: Merge de adaptadores
#   Fase 6: Upload a HuggingFace
#   Fase 7: Node.js y repositorio MCP
#   Fase 8: Desplegar servicios (vLLM + MCP + FastAPI)
#   Fase 9: Cloudflare Tunnel (api.trefa.mx)
#   Fase 10: SSH y resumen final
#
# GPU: 1x RTX PRO 6000 (96GB), A6000/A40 (48GB), A100/H100 (80GB) o similar
#
# Env vars requeridas:
#   HF_TOKEN                     (default incluido para dev)
#
# Env vars opcionales:
#   CF_TUNNEL_CRED               JSON de credenciales Cloudflare Tunnel
#   SUPABASE_URL                 URL del proyecto Supabase
#   SUPABASE_SERVICE_ROLE_KEY    Service role key de Supabase
#
# Flags:
#   --skip-training     Saltar fase 4 (fine-tuning)
#   --skip-merge        Saltar fase 5 (merge adaptadores)
#   --skip-tunnel       No crear Cloudflare Tunnel
#   --model-path PATH   Usar modelo mergeado ya existente
#
# Puertos:
#   vLLM    → 8001
#   MCP     → 3001
#   FastAPI → 8081
#
# Uso:
#   export HF_TOKEN=hf_xxx
#   bash setup_global_v11.sh
#
#   # Sin training (deploy con modelo pre-existente):
#   bash setup_global_v11.sh --skip-training --skip-merge
#
#   # Con modelo local ya mergeado:
#   bash setup_global_v11.sh --skip-training --skip-merge --model-path /app/modelos/mi-modelo
# ============================================================

# ============================================================
# FASE 0: Bootstrap y configuración
# ============================================================

set -euo pipefail
exec > >(tee -a /tmp/trefa-setup.log) 2>&1

# --- Detener servicios de vast.ai que consumen VRAM ---
if command -v supervisorctl &>/dev/null; then
    supervisorctl stop vllm 2>/dev/null || true
    supervisorctl stop ray 2>/dev/null || true
    sleep 3
    python3 -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true
fi

# --- Funciones de logging ---
log()  { echo "[$(date +'%H:%M:%S')] $1"; }
warn() { echo "[$(date +'%H:%M:%S')] WARN: $1"; }
die()  { echo "[$(date +'%H:%M:%S')] FATAL: $1"; cleanup_on_error; exit 1; }

# --- PIDs para cleanup ---
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

# --- wait_for_service: espera con reintentos ---
wait_for_service() {
    local name="$1"
    local host="$2"
    local port="$3"
    local max_seconds="${4:-120}"
    local interval=5
    local max_retries=$((max_seconds / interval))

    log "Esperando a $name (${host}:${port}, max ${max_seconds}s)..."
    for i in $(seq 1 "$max_retries"); do
        if curl -sf "http://${host}:${port}/health" > /dev/null 2>&1; then
            log "$name listo!"
            return 0
        fi
        [ $((i % 12)) -eq 0 ] && log "  $name: cargando... ($((i * interval))s)"
        sleep "$interval"
    done
    warn "$name no respondió después de ${max_seconds}s"
    return 1
}

# --- safe_kill: matar procesos sin afectar este script ---
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

# --- Parse de flags ---
SKIP_TRAINING=false
SKIP_MERGE=false
SKIP_TUNNEL=false
MODEL_PATH=""

while [ $# -gt 0 ]; do
    case "$1" in
        --skip-training)  SKIP_TRAINING=true ;;
        --skip-merge)     SKIP_MERGE=true ;;
        --skip-tunnel)    SKIP_TUNNEL=true ;;
        --model-path)
            shift
            MODEL_PATH="${1:?--model-path requiere un argumento}"
            ;;
        --model-path=*)
            MODEL_PATH="${1#--model-path=}"
            ;;
        *)  warn "Flag desconocido: $1" ;;
    esac
    shift
done

# --- Constantes ---
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

DATASET_DIR="/app/datasets"
TRAIN_FILE="${DATASET_DIR}/merged_v10_together_train_filtered.jsonl"
HF_DATASET_REPO="mmoralesf/v11-qwen3-mariana"

GIT_REPO="https://github.com/marianomoralesr/mcp-server.git"
INFERENCE_BRANCH="inference-server"

CF_TUNNEL_ID="d15177d1-cb8c-4ed9-b8de-ff52c8f3d749"
CF_TUNNEL_DOMAIN="api.trefa.mx"

# Si --model-path fue dado, usar esa ruta como MERGED_DIR
if [ -n "$MODEL_PATH" ]; then
    MERGED_DIR="$MODEL_PATH"
    SKIP_TRAINING=true
    SKIP_MERGE=true
    log "Usando modelo pre-existente: $MERGED_DIR"
fi

# --- Variables de entorno (hardcoded defaults para no tener que exportar cada vez) ---
export HF_TOKEN="${HF_TOKEN:-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}"
export HF_HUB_ENABLE_HF_TRANSFER=1
export OPENBLAS_NUM_THREADS=1
export SUPABASE_URL="${SUPABASE_URL:-https://mhlztgilrmgebkyqowxz.supabase.co}"
export SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1obHp0Z2lscm1nZWJreXFvd3h6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjEyMjkyMCwiZXhwIjoyMDgxNjk4OTIwfQ.E4GbZ4KR9NfyPnbNS1Ic6bi3xzW1-9sBNC15BTRpDzg}"

log "╔══════════════════════════════════════════════════════════════╗"
log "║           TREFA Mariana v11 — Setup Global GPU              ║"
log "╚══════════════════════════════════════════════════════════════╝"
log ""
log "Config:"
log "  Base model:     $BASE_MODEL"
log "  LoRA repo:      $HF_LORA_REPO"
log "  Merged repo:    $HF_MERGED_REPO"
log "  Merged dir:     $MERGED_DIR"
log "  Skip training:  $SKIP_TRAINING"
log "  Skip merge:     $SKIP_MERGE"
log "  Skip tunnel:    $SKIP_TUNNEL"
log ""

# ============================================================
# FASE 1: Dependencias del sistema
# ============================================================

log "=== FASE 1: Dependencias del sistema ==="

apt-get update -qq 2>&1 | tail -1
apt-get install -y -qq \
    git curl wget jq tmux htop nvtop \
    openssh-server \
    build-essential cmake pkg-config libssl-dev \
    2>&1 | tail -5
log "Paquetes base instalados"

# --- cloudflared ---
if ! command -v cloudflared &>/dev/null; then
    log "Instalando cloudflared..."
    curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
        -o /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
    log "cloudflared $(cloudflared --version 2>&1 | head -1) instalado"
else
    log "cloudflared ya instalado"
fi

# --- Verificar CUDA ---
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "N/A")
    GPU_COUNT=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader 2>/dev/null | wc -l | xargs || echo "1")
    VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs || echo "0")
    CUDA_VER=$(nvidia-smi 2>/dev/null | grep -oP "CUDA Version: \K[\d.]+" || echo "?")
    log "GPU: ${GPU_NAME} x${GPU_COUNT} — ${VRAM_TOTAL}MB VRAM — CUDA ${CUDA_VER}"
else
    warn "nvidia-smi no encontrado — asegúrate de tener drivers NVIDIA"
    GPU_NAME="N/A"
    GPU_COUNT=1
    VRAM_TOTAL=0
fi

# --- Python ---
PYTHON_VER=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' || echo "0.0")
log "Python: $PYTHON_VER"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    log "Python 3.10+ verificado OK"
else
    warn "Se recomienda Python 3.10+. Versión actual: $PYTHON_VER"
fi

log "Fase 1 completada"

# ============================================================
# FASE 2: Dependencias Python para fine-tuning
# ============================================================

log "=== FASE 2: Dependencias Python ==="

pip install --upgrade pip setuptools wheel 2>&1 | tail -2

# Verificar si PyTorch ya incluye CUDA
TORCH_CUDA=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
if [ "$TORCH_CUDA" != "True" ]; then
    log "Instalando PyTorch con CUDA..."
    pip install torch torchvision torchaudio 2>&1 | tail -3
fi

log "Instalando PEFT + dependencias de training (LoRA bf16, sin Unsloth)..."
pip install trl peft accelerate bitsandbytes 2>&1 | tail -3
pip install flash-attn --no-build-isolation 2>&1 | tail -3 || log "flash-attn no disponible, usando atencion estandar"
pip install datasets transformers sentencepiece protobuf 2>&1 | tail -3
pip install huggingface_hub safetensors hf_transfer 2>&1 | tail -3
pip install vllm 2>&1 | tail -3
# Login HuggingFace
log "Login a HuggingFace..."
huggingface-cli login --token "$HF_TOKEN" 2>&1 | tail -1

# Verificar GPU con Python
log "Verificando GPU desde Python..."
python3 << 'GPU_CHECK'
import torch
if not torch.cuda.is_available():
    print("  ERROR: CUDA no disponible desde PyTorch")
    import sys; sys.exit(1)
gpu_name = torch.cuda.get_device_name(0)
vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"  PyTorch GPU: {gpu_name}")
print(f"  PyTorch VRAM: {vram_gb:.1f} GB")
print(f"  PyTorch CUDA: {torch.version.cuda}")
print(f"  PyTorch version: {torch.__version__}")
GPU_CHECK

log "Fase 2 completada"

# ============================================================
# FASE 3: Descargar modelo base y dataset
# ============================================================

log "=== FASE 3: Modelo base y dataset ==="

mkdir -p /app/modelos "$DATASET_DIR" /app/generated

# --- Modelo base (solo si vamos a entrenar) ---
if [ "$SKIP_TRAINING" = false ]; then
    if [ ! -f "$BASE_DIR/config.json" ]; then
        log "Descargando modelo base: $BASE_MODEL..."
        huggingface-cli download "$BASE_MODEL" \
            --local-dir "$BASE_DIR" \
            --local-dir-use-symlinks False
        log "Modelo base descargado en $BASE_DIR"
    else
        log "Modelo base ya existe en $BASE_DIR"
    fi
fi

# --- Dataset ---
if [ "$SKIP_TRAINING" = false ]; then
    # Buscar dataset local primero
    FOUND_DATASET=false

    if [ -f "$TRAIN_FILE" ]; then
        log "Dataset encontrado: $TRAIN_FILE"
        FOUND_DATASET=true
    fi

    # Buscar en el directorio del repo clonado
    if [ "$FOUND_DATASET" = false ] && [ -f "/app/datasets/merged_v10_together_train.jsonl" ]; then
        TRAIN_FILE="/app/datasets/merged_v10_together_train.jsonl"
        log "Dataset encontrado en repo: $TRAIN_FILE"
        FOUND_DATASET=true
    fi

    # Buscar cualquier dataset v10
    if [ "$FOUND_DATASET" = false ]; then
        V10_FILES=$(ls /app/datasets/*v10*train*.jsonl 2>/dev/null || true)
        if [ -n "$V10_FILES" ]; then
            TRAIN_FILE=$(echo "$V10_FILES" | head -1)
            log "Dataset v10 encontrado: $TRAIN_FILE"
            FOUND_DATASET=true
        fi
    fi

    # Descargar desde HuggingFace si no se encontró localmente
    if [ "$FOUND_DATASET" = false ]; then
        log "Descargando dataset desde HuggingFace: $HF_DATASET_REPO..."
        mkdir -p "${DATASET_DIR}/hf_download"
        set +e
        huggingface-cli download "$HF_DATASET_REPO" \
            --local-dir "${DATASET_DIR}/hf_download" \
            --local-dir-use-symlinks False 2>&1 | tail -5
        HF_DL_EXIT=$?
        if [ $HF_DL_EXIT -ne 0 ]; then
            log "Reintentando como dataset repo..."
            huggingface-cli download "$HF_DATASET_REPO" \
                --repo-type dataset \
                --local-dir "${DATASET_DIR}/hf_download" \
                --local-dir-use-symlinks False 2>&1 | tail -5
        fi
        set -e

        # Buscar train file descargado
        for candidate in \
            "${DATASET_DIR}/hf_download/merged_v10_together_train.jsonl" \
            "${DATASET_DIR}/hf_download/merged_v10_final_train.jsonl" \
            "${DATASET_DIR}/hf_download/train.jsonl"; do
            if [ -f "$candidate" ]; then
                cp "$candidate" "$TRAIN_FILE"
                log "Dataset train copiado de HF: $(basename "$candidate")"
                FOUND_DATASET=true
                break
            fi
        done

        # Si no encontró por nombre exacto, buscar cualquier *train*.jsonl
        if [ "$FOUND_DATASET" = false ]; then
            HF_TRAIN=$(find "${DATASET_DIR}/hf_download" -name "*train*.jsonl" -type f 2>/dev/null | head -1)
            if [ -n "$HF_TRAIN" ]; then
                cp "$HF_TRAIN" "$TRAIN_FILE"
                log "Dataset train copiado de HF: $(basename "$HF_TRAIN")"
                FOUND_DATASET=true
            fi
        fi

        # Copiar eval si existe
        for candidate in \
            "${DATASET_DIR}/hf_download/merged_v10_together_eval.jsonl" \
            "${DATASET_DIR}/hf_download/merged_v10_final_eval.jsonl" \
            "${DATASET_DIR}/hf_download/eval.jsonl"; do
            if [ -f "$candidate" ]; then
                cp "$candidate" "${DATASET_DIR}/merged_v10_together_eval.jsonl"
                log "Dataset eval copiado de HF: $(basename "$candidate")"
                break
            fi
        done

        # Buscar eval genérico
        if [ ! -f "${DATASET_DIR}/merged_v10_together_eval.jsonl" ]; then
            HF_EVAL=$(find "${DATASET_DIR}/hf_download" -name "*eval*.jsonl" -type f 2>/dev/null | head -1)
            if [ -n "$HF_EVAL" ]; then
                cp "$HF_EVAL" "${DATASET_DIR}/merged_v10_together_eval.jsonl"
                log "Dataset eval copiado de HF: $(basename "$HF_EVAL")"
            fi
        fi
    fi

    if [ "$FOUND_DATASET" = false ]; then
        warn "Dataset no encontrado localmente ni en HuggingFace ($HF_DATASET_REPO)"
        warn "El training fallará si no se proporciona dataset"
    else
        # Validar dataset
        TRAIN_COUNT=$(wc -l < "$TRAIN_FILE" | tr -d ' ')
        log "Dataset: $TRAIN_FILE ($TRAIN_COUNT líneas)"

        # Validar JSON
        INVALID_LINES=$(python3 -c "
import json, sys
invalid = 0
with open('$TRAIN_FILE') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line: continue
        try:
            obj = json.loads(line)
            if 'messages' not in obj:
                invalid += 1
        except json.JSONDecodeError:
            invalid += 1
print(invalid)
" 2>/dev/null || echo "-1")

        if [ "$INVALID_LINES" = "0" ]; then
            log "Dataset validado: todas las líneas OK"
        elif [ "$INVALID_LINES" = "-1" ]; then
            warn "No se pudo validar el dataset"
        else
            warn "Dataset tiene $INVALID_LINES líneas inválidas"
        fi

        # --- Inyectar system prompt real (reemplazar __SYSTEM_PROMPT__) ---
        log "Inyectando system prompt real en dataset (reemplazando __SYSTEM_PROMPT__)..."

        # Escribir system prompt a archivo temporal
        cat > /tmp/mariana_system_prompt.txt << 'SYSPROMPT_EOF'
Eres Mariana, asesora virtual de Autos TREFA, agencia de autos seminuevos con sucursales en Monterrey, Guadalupe, Saltillo y Reynosa, Mexico. Tu canal es WhatsApp.

PERSONALIDAD:
- Calida, profesional, empatica. Hablas como persona real: "Con mucho gusto te apoyo", "Que gusto saludarte".
- Espanol mexicano coloquial (tuteo). Maximo 1-2 emojis por mensaje.
- Respuestas de 1-3 parrafos cortos. SIEMPRE cierra con pregunta o siguiente paso claro.
- Nunca llames a TREFA "lote" o "tienda" — siempre "agencia de autos seminuevos".

REGLAS:
1. SIEMPRE usa herramientas para consultar datos reales. NUNCA inventes precios, disponibilidad ni especificaciones.
2. Si NO hay el auto que busca, usa buscar_alternativas AUTOMATICAMENTE antes de decir "no tenemos".
3. Incluye info financiera al presentar vehiculos: precio, enganche minimo, mensualidad.
4. Solicita el nombre del cliente de forma natural si no lo conoces: "Con quien tengo el gusto?" o "Me compartes tu nombre?".
5. Nunca compartas IDs internos, slugs tecnicos ni nombres de herramientas al cliente.
6. Formato precios: $XXX,XXX MXN. URLs: https://autostrefa.mx/inventario/{slug}
7. NO negocies precios (son finales). NO garantices credito ("sujeto a aprobacion"). NO inventes promociones.
8. NO des consejos legales, fiscales o mecanicos. Refiere al asesor.
9. Si preguntan si eres IA, se honesta: "Soy Mariana, asistente virtual de Autos TREFA".
10. Protege la privacidad del cliente.

OBJETIVO COMERCIAL:
Lleva cada conversacion hacia uno de dos cierres:
1. Iniciar tramite de credito en linea (foraneos y decididos)
2. Agendar cita en sucursal (contado, indecisos, locales)

FLUJO: Descubrimiento (1-2 preguntas max) -> Busqueda -> Presentacion (2-3 opciones) -> Profundizacion -> Conversion (datos de contacto o cita).

DATOS CLAVE TREFA:
- Garantia: 12 meses en motor y transmision, hasta $100,000 MXN
- Inspeccion de 150 puntos + certificado legal (REPUVE, SAT, TransUnion, TotalCheck)
- Financiamiento: multiples bancos, proceso 100% digital, pre-aprobacion en 24h
- Enganche minimo: 20%. Plazos: 12, 24, 36, 48, 60 meses
- Trade-in: modelos 2016+ con menos de 120,000 km
- Devolucion: 7 dias naturales o 500 km
- Documentos para credito: INE, comprobante domicilio (3 meses), 3 estados de cuenta, 3 recibos de nomina
- NO aceptamos meses sin intereses (MSI)
- Promocion del mes: placas ($6,100) + gestoria + 12 meses garantia

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "buscar_vehiculos", "description": "Busca vehiculos en el inventario de Autos TREFA. Filtrar por marca, modelo, ano, precio, tipo de carroceria, transmision, combustible.", "parameters": {"type": "object", "properties": {"marca": {"type": "string", "description": "Marca del vehiculo (ej: Toyota, Honda, Mazda)"}, "modelo": {"type": "string", "description": "Modelo especifico (ej: Corolla, Civic, CX-5)"}, "año_minimo": {"type": "number", "description": "Ano minimo del vehiculo"}, "año_maximo": {"type": "number", "description": "Ano maximo del vehiculo"}, "precio_minimo": {"type": "number", "description": "Precio minimo en MXN"}, "precio_maximo": {"type": "number", "description": "Precio maximo en MXN"}, "tipo_carroceria": {"type": "string", "description": "Tipo: SUV, Sedan, Hatchback, Pickup, Van"}, "transmision": {"type": "string", "description": "Automatica o Manual"}, "combustible": {"type": "string", "description": "Gasolina, Diesel, Hibrido, Electrico"}, "ubicacion": {"type": "string", "description": "Sucursal: Monterrey, Guadalupe, Saltillo, Reynosa"}, "kilometraje_max": {"type": "number", "description": "Kilometraje maximo"}, "limite": {"type": "number", "description": "Numero maximo de resultados (default: 5)"}}}}}
{"type": "function", "function": {"name": "obtener_vehiculo", "description": "Obtiene informacion detallada de un vehiculo especifico incluyendo especificaciones, precio, garantia, mensualidades y disponibilidad.", "parameters": {"type": "object", "properties": {"id": {"type": "number", "description": "ID numerico del vehiculo"}, "slug": {"type": "string", "description": "Slug URL del vehiculo"}}}}}
{"type": "function", "function": {"name": "buscar_alternativas", "description": "Busca vehiculos alternativos cuando no hay el modelo exacto. Identifica marcas equivalentes y busca en rango de precio cercano.", "parameters": {"type": "object", "properties": {"marca_original": {"type": "string", "description": "Marca que el cliente buscaba"}, "modelo_original": {"type": "string", "description": "Modelo que buscaba"}, "presupuesto": {"type": "number", "description": "Presupuesto maximo en MXN"}, "tipo_uso": {"type": "string", "description": "Para que usara: familia, trabajo, ciudad, carretera"}, "carroceria": {"type": "string", "description": "Tipo de carroceria preferido"}, "ubicacion": {"type": "string", "description": "Sucursal preferida"}}, "required": ["marca_original", "presupuesto"]}}}
{"type": "function", "function": {"name": "comparar_vehiculos", "description": "Compara 2-4 vehiculos lado a lado con tabla comparativa, analisis y recomendacion.", "parameters": {"type": "object", "properties": {"vehiculo_ids": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 4, "description": "IDs de los vehiculos a comparar"}}, "required": ["vehiculo_ids"]}}}
{"type": "function", "function": {"name": "estadisticas_inventario", "description": "Obtiene estadisticas generales del inventario actual: marcas, cantidad, rango de precios.", "parameters": {"type": "object", "properties": {}}}}
{"type": "function", "function": {"name": "calcular_financiamiento", "description": "Calcula mensualidades estimadas para un vehiculo dado precio, enganche y plazo.", "parameters": {"type": "object", "properties": {"precio_vehiculo": {"type": "number", "description": "Precio del vehiculo en MXN"}, "vehiculo_id": {"type": "number", "description": "ID del vehiculo en base de datos"}, "enganche_porcentaje": {"type": "number", "description": "Porcentaje de enganche (10-90, default 20)"}, "plazo_meses": {"type": "number", "description": "Plazo en meses (12, 24, 36, 48, 60, default 48)"}, "tasa_anual": {"type": "number", "description": "Tasa de interes anual en % (default 15)"}}}}}
{"type": "function", "function": {"name": "buscar_informacion", "description": "Busca informacion en la base de conocimiento de TREFA sobre politicas, procesos, garantias, etc.", "parameters": {"type": "object", "properties": {"pregunta": {"type": "string", "description": "Pregunta o tema a buscar"}, "categoria": {"type": "string", "enum": ["faq", "politicas", "procesos", "financiamiento", "garantias", "general"]}}, "required": ["pregunta"]}}}
{"type": "function", "function": {"name": "obtener_info_negocio", "description": "Obtiene informacion del negocio: horarios, ubicaciones, contacto, garantias, financiamiento, documentos, proceso de compra.", "parameters": {"type": "object", "properties": {"tema": {"type": "string", "enum": ["horarios", "ubicaciones", "contacto", "garantias", "financiamiento", "documentos_requeridos", "proceso_compra", "devoluciones", "intercambio", "servicios"]}}, "required": ["tema"]}}}
{"type": "function", "function": {"name": "obtener_faqs", "description": "Obtiene preguntas frecuentes, opcionalmente filtradas por categoria.", "parameters": {"type": "object", "properties": {"categoria": {"type": "string", "description": "Categoria: financiamiento, garantias, proceso"}}}}}
{"type": "function", "function": {"name": "solicitar_datos_contacto", "description": "Registra o actualiza los datos de contacto del cliente en el sistema.", "parameters": {"type": "object", "properties": {"nombre": {"type": "string", "description": "Nombre completo del cliente"}, "telefono": {"type": "string", "description": "Telefono del cliente"}, "email": {"type": "string", "description": "Correo electronico del cliente"}, "vehiculo_interes": {"type": "string", "description": "Vehiculo de interes del cliente"}, "comentarios": {"type": "string", "description": "Comentarios adicionales"}}, "required": ["nombre"]}}}
{"type": "function", "function": {"name": "enviar_cotizacion_email", "description": "Envia cotizacion del vehiculo al correo del cliente.", "parameters": {"type": "object", "properties": {"email_destino": {"type": "string", "description": "Correo del destinatario"}, "nombre_cliente": {"type": "string", "description": "Nombre del cliente"}, "vehiculo_id": {"type": "number", "description": "ID del vehiculo a cotizar"}, "enganche_porcentaje": {"type": "number", "description": "Porcentaje de enganche (default 20)"}, "plazo_meses": {"type": "number", "description": "Plazo en meses (default 48)"}}, "required": ["email_destino", "nombre_cliente", "vehiculo_id"]}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
SYSPROMPT_EOF

        # Escribir script de inyección
        cat > /tmp/inject_system_prompt.py << 'INJECT_EOF'
#!/usr/bin/env python3
"""Inject real system prompt into __SYSTEM_PROMPT__ placeholders in JSONL."""
import json, sys, os

with open("/tmp/mariana_system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

for filepath in sys.argv[1:]:
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} no existe")
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    replaced = 0
    already_ok = 0
    total = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        total += 1
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        changed = False
        for m in obj.get("messages", []):
            if m.get("role") == "system" and m.get("content", "").strip() == "__SYSTEM_PROMPT__":
                m["content"] = SYSTEM_PROMPT
                changed = True
        if changed:
            replaced += 1
            lines[i] = json.dumps(obj, ensure_ascii=False) + "\n"
        else:
            # Check if it already has a real system prompt
            for m in obj.get("messages", []):
                if m.get("role") == "system" and len(m.get("content", "")) > 100:
                    already_ok += 1
                    break

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"  {os.path.basename(filepath)}: {replaced} inyectados, {already_ok} ya tenían prompt, {total} total")
INJECT_EOF

        # Ejecutar inyección en train
        python3 /tmp/inject_system_prompt.py "$TRAIN_FILE"

        # Ejecutar inyección en eval si existe
        EVAL_INJECT="${DATASET_DIR}/merged_v10_together_eval.jsonl"
        if [ -f "$EVAL_INJECT" ]; then
            python3 /tmp/inject_system_prompt.py "$EVAL_INJECT"
        fi
    fi
fi

# --- Si skip-training+merge, verificar/descargar modelo mergeado ---
if [ "$SKIP_TRAINING" = true ] && [ "$SKIP_MERGE" = true ]; then
    if [ ! -f "$MERGED_DIR/config.json" ]; then
        log "Modelo mergeado no encontrado localmente. Descargando de HuggingFace: $HF_MERGED_REPO..."
        mkdir -p "$MERGED_DIR"
        huggingface-cli download "$HF_MERGED_REPO" \
            --local-dir "$MERGED_DIR" \
            --local-dir-use-symlinks False 2>&1 | tail -5

        if [ ! -f "$MERGED_DIR/config.json" ]; then
            # Intentar con el repo LoRA
            log "Merged no encontrado, intentando LoRA repo: $HF_LORA_REPO..."
            huggingface-cli download "$HF_LORA_REPO" \
                --local-dir "$MERGED_DIR" \
                --local-dir-use-symlinks False 2>&1 | tail -5
        fi

        if [ ! -f "$MERGED_DIR/config.json" ]; then
            die "No se encontró modelo en $MERGED_DIR ni en HuggingFace"
        fi
        log "Descarga completada"
    else
        log "Modelo mergeado encontrado en $MERGED_DIR"
    fi
fi

log "Fase 3 completada"

# ============================================================
# FASE 4: Fine-tuning con LoRA bf16
# ============================================================

log "=== FASE 4: Fine-tuning ==="

if [ "$SKIP_TRAINING" = true ]; then
    log "Fine-tuning saltado (--skip-training)"
else
    # Limpiar procesos GPU previos
    log "Limpiando GPU para training..."
    safe_kill "vllm.entrypoints.openai.api_server"
    safe_kill "uvicorn app.main:app"
    sleep 3

    # Liberar VRAM
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
            esac
        done <<< "$GPU_PIDS"
        sleep 3
    fi

    # Auto-detectar batch size y grad_accum según VRAM (effective batch = batch_size * grad_accum)
    BATCH_SIZE=2
    GRAD_ACCUM=8
    VRAM_GB=$(python3 -c "
import torch
if torch.cuda.is_available():
    print(f'{torch.cuda.get_device_properties(0).total_memory / 1e9:.0f}')
else:
    print('0')
" 2>/dev/null || echo "0")

    if [ "$VRAM_GB" -ge 80 ]; then
        BATCH_SIZE=6
        GRAD_ACCUM=2
        log "VRAM ${VRAM_GB}GB: batch_size=6, grad_accum=2 (effective=12)"
    elif [ "$VRAM_GB" -ge 44 ]; then
        BATCH_SIZE=4
        GRAD_ACCUM=4
        log "VRAM ${VRAM_GB}GB: batch_size=4, grad_accum=4 (effective=16)"
    elif [ "$VRAM_GB" -ge 22 ]; then
        BATCH_SIZE=2
        GRAD_ACCUM=8
        log "VRAM ${VRAM_GB}GB: batch_size=2, grad_accum=8 (effective=16)"
    else
        BATCH_SIZE=1
        GRAD_ACCUM=16
        log "VRAM ${VRAM_GB}GB: batch_size=1, grad_accum=16 (effective=16)"
    fi

    # Buscar eval file
    EVAL_FILE=""
    EVAL_ARG=""
    for candidate in \
        "${DATASET_DIR}/merged_v10_together_eval.jsonl" \
        "${DATASET_DIR}/v10_real_eval.jsonl" \
        "${DATASET_DIR}/trefa_eval.jsonl"; do
        if [ -f "$candidate" ]; then
            EVAL_FILE="$candidate"
            EVAL_ARG="--eval-file $EVAL_FILE"
            log "Eval dataset: $EVAL_FILE"
            break
        fi
    done
    [ -z "$EVAL_FILE" ] && log "Sin eval dataset, entrenando solo con train"

    # Siempre refrescar training script desde el repo clonado para evitar versiones viejas cacheadas
    if [ -d "/app/mcp-server/training" ]; then
        log "Actualizando training script desde /app/mcp-server/training..."
        mkdir -p /app/training
        cp -f /app/mcp-server/training/train_qwen3_vast.py /app/training/train_qwen3_vast.py
    fi

    # Verificar que el script de training existe
    TRAIN_SCRIPT=""
    for candidate in "/app/training/train_qwen3_vast.py" "/app/mcp-server/training/train_qwen3_vast.py"; do
        if [ -f "$candidate" ]; then
            TRAIN_SCRIPT="$candidate"
            break
        fi
    done

    if [ -z "$TRAIN_SCRIPT" ]; then
        # Clonar repo para obtener el script
        log "Clonando $INFERENCE_BRANCH para training script..."
        rm -rf /tmp/ir-train
        git clone -q -b "$INFERENCE_BRANCH" "$GIT_REPO" /tmp/ir-train && cp -r /tmp/ir-train/* /app/ && rm -rf /tmp/ir-train
        for candidate in "/app/training/train_qwen3_vast.py" "/app/mcp-server/training/train_qwen3_vast.py"; do
            [ -f "$candidate" ] && TRAIN_SCRIPT="$candidate" && break
        done
    fi

    if [ -z "$TRAIN_SCRIPT" ]; then
        warn "Script de training no encontrado. Saltando training."
        SKIP_TRAINING=true
    fi

    if [ "$SKIP_TRAINING" = false ]; then
        log "Iniciando training..."
        log "  Script:     $TRAIN_SCRIPT"
        log "  Modelo:     $BASE_MODEL"
        log "  Dataset:    $TRAIN_FILE"
        log "  Output:     $LORA_DIR"
        log "  LoRA:       r=32, alpha=64"
        log "  Epochs:     2"
        log "  Batch:      ${BATCH_SIZE} x ${GRAD_ACCUM} = $((BATCH_SIZE * GRAD_ACCUM))"
        log "  LR:         2e-4"
        log "  NEFTune:    5"

        # Ejecutar training (no usar set -e para que no mate el script entero)
        set +e
        python3 "$TRAIN_SCRIPT" \
            --model "$BASE_MODEL" \
            --train-file "$TRAIN_FILE" \
            $EVAL_ARG \
            --output-dir "$LORA_DIR" \
            --merged-dir "$MERGED_DIR" \
            --max-seq-length 4096 \
            --lora-r 32 \
            --lora-alpha 64 \
            --epochs 2 \
            --batch-size "$BATCH_SIZE" \
            --grad-accum "$GRAD_ACCUM" \
            --lr 2e-4 \
            --neftune 5 \
            --no-gguf
        TRAIN_EXIT=$?
        set -e

        if [ $TRAIN_EXIT -eq 0 ]; then
            log "Training completado exitosamente"
            # Verificar output
            if [ -f "$LORA_DIR/adapter_model.safetensors" ] || [ -f "$LORA_DIR/adapter_model.bin" ]; then
                log "LoRA adapter verificado en $LORA_DIR"
            else
                warn "adapter_model no encontrado en $LORA_DIR — verificar manualmente"
            fi
        else
            warn "Training falló con código $TRAIN_EXIT"
            warn "Continuando con modelo pre-existente si disponible..."
            # Intentar usar modelo mergeado existente
            if [ -f "$MERGED_DIR/config.json" ]; then
                log "Modelo mergeado pre-existente encontrado, continuando"
                SKIP_MERGE=true
            else
                warn "No hay modelo mergeado disponible — el deploy puede fallar"
            fi
        fi
    fi
fi

log "Fase 4 completada"

# ============================================================
# FASE 5: Merge de adaptadores
# ============================================================

log "=== FASE 5: Merge de adaptadores ==="

if [ "$SKIP_MERGE" = true ]; then
    log "Merge saltado (--skip-merge)"
elif [ -f "$MERGED_DIR/config.json" ]; then
    log "Modelo mergeado ya existe en $MERGED_DIR, saltando merge"
else
    # Verificar que tenemos los inputs
    if [ ! -f "$BASE_DIR/config.json" ]; then
        # Descargar base si no existe
        log "Descargando modelo base para merge: Qwen/Qwen3-14B..."
        huggingface-cli download "Qwen/Qwen3-14B" \
            --local-dir "$BASE_DIR" \
            --local-dir-use-symlinks False 2>&1 | tail -5
    fi

    if [ ! -d "$LORA_DIR" ] || [ -z "$(ls -A "$LORA_DIR" 2>/dev/null)" ]; then
        if [ "$SKIP_TRAINING" = true ]; then
            # Solo descargar de HF si no se entrenó localmente (deploy-only mode)
            log "Descargando LoRA adapter: $HF_LORA_REPO..."
            huggingface-cli download "$HF_LORA_REPO" \
                --local-dir "$LORA_DIR" \
                --local-dir-use-symlinks False 2>&1 | tail -5
        else
            die "LoRA adapter no encontrado en $LORA_DIR — el training debió generarlo en Fase 4"
        fi
    fi

    log "Mergeando LoRA con modelo base..."
    log "  Base: $BASE_DIR"
    log "  LoRA: $LORA_DIR"
    log "  Output: $MERGED_DIR"
    log "  NOTA: Qwen3-14B requiere ~28GB RAM para merge en CPU"

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
fi

log "Fase 5 completada"

# ============================================================
# FASE 6: Upload a HuggingFace
# ============================================================

log "=== FASE 6: Upload a HuggingFace ==="

if [ "$SKIP_TRAINING" = true ] && [ "$SKIP_MERGE" = true ]; then
    log "Upload saltado (modelo no fue entrenado/mergeado localmente)"
elif [ ! -f "$MERGED_DIR/config.json" ]; then
    warn "No hay modelo mergeado para subir"
else
    log "Subiendo modelo mergeado a $HF_MERGED_REPO..."

    set +e
    python3 << UPLOAD_SCRIPT
import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
from huggingface_hub import HfApi, create_repo

api = HfApi()
repo = "$HF_MERGED_REPO"

print(f"[upload] Creando/verificando repo: {repo}")
try:
    create_repo(repo, repo_type="model", exist_ok=True)
except Exception as e:
    print(f"[upload] WARN al crear repo: {e}")

out_dir = "$MERGED_DIR"
files = [f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))]
total_size = sum(os.path.getsize(os.path.join(out_dir, f)) for f in files)
print(f"[upload] Archivos: {len(files)} ({total_size / 1e9:.1f} GB)")
print(f"[upload] Subiendo a {repo}...")

api.upload_folder(
    folder_path=out_dir,
    repo_id=repo,
    repo_type="model",
    commit_message="v11: Qwen3-14B + LoRA mariana v11 (bf16) — modelo mergeado para vLLM",
)

print(f"[upload] Listo! https://huggingface.co/{repo}")
UPLOAD_SCRIPT
    UPLOAD_EXIT=$?
    set -e

    if [ $UPLOAD_EXIT -eq 0 ]; then
        log "Upload completado"
    else
        warn "Upload falló con código $UPLOAD_EXIT — continuando con deploy local"
    fi
fi

log "Fase 6 completada"

# ============================================================
# FASE 7: Node.js y repositorio MCP
# ============================================================

log "=== FASE 7: Node.js y repositorios ==="

# --- Node.js 20+ ---
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

# --- Clonar repositorio (branch inference-server) ---
if [ ! -d "/app/app" ]; then
    log "Clonando repositorio (branch $INFERENCE_BRANCH)..."
    git clone -q -b "$INFERENCE_BRANCH" "$GIT_REPO" /tmp/ir
    cp -r /tmp/ir/* /app/ 2>/dev/null || true
    cp -r /tmp/ir/.env* /app/ 2>/dev/null || true
    rm -rf /tmp/ir
fi

# --- Preparar mcp-server (ya viene del clone anterior) ---
if [ ! -f "/app/mcp-server/package.json" ]; then
    log "MCP Server no encontrado en clone, extrayendo de $INFERENCE_BRANCH..."
    rm -rf /app/mcp-server
    git clone -q -b "$INFERENCE_BRANCH" "$GIT_REPO" /tmp/mcp-tmp
    if [ -d "/tmp/mcp-tmp/mcp-server" ]; then
        mv /tmp/mcp-tmp/mcp-server /app/mcp-server
    else
        mv /tmp/mcp-tmp /app/mcp-server
    fi
    rm -rf /tmp/mcp-tmp
fi

# --- Build MCP Server ---
log "Instalando y compilando MCP Server..."
cd /app/mcp-server && npm install --silent 2>&1 | tail -2 && npm run build 2>&1 | tail -2
cd /app

# --- .env de MCP Server ---
if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    printf "SUPABASE_URL=%s\nSUPABASE_SERVICE_ROLE_KEY=%s\nPORT=%s\n" \
        "$SUPABASE_URL" "$SUPABASE_SERVICE_ROLE_KEY" "$MCP_PORT" > /app/mcp-server/.env
    [ -n "${MCP_API_KEY:-}" ] && echo "API_KEY=${MCP_API_KEY}" >> /app/mcp-server/.env
    log ".env de MCP generado"
else
    warn "SUPABASE_URL/KEY no definidos — MCP Server puede fallar"
fi

# --- Dependencias FastAPI ---
if [ -f "/app/app/requirements.txt" ]; then
    log "Instalando dependencias FastAPI..."
    pip install -q -r /app/app/requirements.txt 2>&1 | tail -2
fi

mkdir -p /app/datasets /app/generated

log "Fase 7 completada"

# ============================================================
# FASE 8: Desplegar servicios
# ============================================================

log "=== FASE 8: Desplegar servicios ==="

cd /app

# --- Limpieza de procesos previos ---
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

# --- GPU auto-detection para vLLM ---
MAX_MODEL_LEN=4096
GPU_MEMORY_UTILIZATION=0.90

if command -v nvidia-smi &>/dev/null; then
    GPU_NAME_DETECT=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "")
    case "$GPU_NAME_DETECT" in
        *A40*|*a40*)
            MAX_MODEL_LEN=8192; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: A40 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *A6000*|*a6000*|*5880*)
            MAX_MODEL_LEN=8192; GPU_MEMORY_UTILIZATION=0.85
            log "GPU config: A6000/5880 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *"RTX PRO 6"*|*"RTX PRO6"*)
            MAX_MODEL_LEN=16384; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: RTX PRO 6000 (96GB) — max_model_len=$MAX_MODEL_LEN"
            ;;
        *A100*|*a100*)
            MAX_MODEL_LEN=16384; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: A100 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *H100*|*h100*)
            MAX_MODEL_LEN=32768; GPU_MEMORY_UTILIZATION=0.90
            log "GPU config: H100 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *5090*)
            MAX_MODEL_LEN=4096; GPU_MEMORY_UTILIZATION=0.85
            log "GPU config: RTX 5090 — max_model_len=$MAX_MODEL_LEN"
            ;;
        *)
            MAX_MODEL_LEN=4096; GPU_MEMORY_UTILIZATION=0.85
            log "GPU no reconocida ($GPU_NAME_DETECT), defaults conservadores"
            ;;
    esac
fi

# --- Verificar que el modelo mergeado existe ---
if [ ! -f "$MERGED_DIR/config.json" ]; then
    die "Modelo mergeado no encontrado en $MERGED_DIR — no se puede iniciar vLLM"
fi

MERGED_SIZE=$(du -sh "$MERGED_DIR" 2>/dev/null | cut -f1 || echo "?")
log "Modelo para deploy: $MERGED_DIR ($MERGED_SIZE)"

# ============================================================
# 8a. vLLM
# ============================================================

log "8a. Iniciando vLLM (puerto $VLLM_PORT)..."

# Desactivar vLLM de vast.ai si existe
if [ -f /opt/supervisor-scripts/vllm.sh ]; then
    chmod -x /opt/supervisor-scripts/vllm.sh 2>/dev/null || true
    supervisorctl stop vllm 2>/dev/null || true
fi

# Fijar límites
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

# Obtener PID real de vLLM (tmux inicia un shell)
sleep 5
VLLM_PID=$(pgrep -f "vllm.entrypoints.openai.api_server" 2>/dev/null | head -1 || echo "")
log "vLLM tmux session creada (PID: ${VLLM_PID:-pendiente})"

# Esperar vLLM con reintentos (hasta 10 minutos para modelos grandes)
for i in $(seq 1 120); do
    if curl -sf "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
        log "vLLM listo! ($((i * 5))s)"
        break
    fi
    # Verificar que el proceso sigue vivo
    if ! pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null 2>&1; then
        log "ERROR: vLLM crasheó. Últimas líneas del log:"
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

    # Test de chat rápido
    RESPONSE=$(curl -s -X POST "http://localhost:${VLLM_PORT}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{"model":"'"$SERVED_MODEL"'","messages":[{"role":"user","content":"hola"}],"max_tokens":50}')
    CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'][:100])" 2>/dev/null || echo "FAIL")
    log "vLLM test: $CONTENT"
else
    warn "vLLM no respondió después de 10 minutos"
fi

# Actualizar PID
VLLM_PID=$(pgrep -f "vllm.entrypoints.openai.api_server" 2>/dev/null | head -1 || echo "")

# ============================================================
# 8b. MCP Server
# ============================================================

log "8b. Iniciando MCP Server (puerto $MCP_PORT)..."

tmux kill-session -t mcp 2>/dev/null || true
tmux new-session -d -s mcp "cd /app/mcp-server && npm run start:http 2>&1 | tee /tmp/mcp-server.log"

sleep 3
MCP_PID=$(pgrep -f "node.*mcp-server" 2>/dev/null | head -1 || echo "")

if curl -sf "http://localhost:${MCP_PORT}/health" > /dev/null 2>&1; then
    log "MCP Server listo (PID: ${MCP_PID:-?})"
else
    warn "MCP Server no respondió en /health — puede no estar configurado"
fi

# ============================================================
# 8c. FastAPI Backend
# ============================================================

log "8c. Iniciando FastAPI (puerto $FASTAPI_PORT)..."

tmux kill-session -t fastapi 2>/dev/null || true
tmux new-session -d -s fastapi "\
    cd /app && \
    TREFA_VLLM_BASE_URL=http://localhost:${VLLM_PORT} \
    TREFA_VLLM_PORT=${VLLM_PORT} \
    TREFA_VLLM_API_KEY=EMPTY \
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

log "Fase 8 completada"

# ============================================================
# FASE 9: Cloudflare Tunnel
# ============================================================

log "=== FASE 9: Cloudflare Tunnel ==="

CF_CRED_FILE="/root/.cloudflared/${CF_TUNNEL_ID}.json"
CF_URL=""

if [ "$SKIP_TUNNEL" = true ]; then
    log "Tunnel saltado (--skip-tunnel)"
elif [ -n "${CF_TUNNEL_CRED:-}" ]; then
    log "Configurando Cloudflare Tunnel (${CF_TUNNEL_DOMAIN})..."

    # Limpiar tunnel anterior
    pkill -f "cloudflared tunnel" 2>/dev/null || true
    sleep 1
    rm -rf /root/.cloudflared
    mkdir -p /root/.cloudflared

    # Escribir credenciales
    echo "$CF_TUNNEL_CRED" > "$CF_CRED_FILE"
    chmod 600 "$CF_CRED_FILE"

    # Config del tunnel
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

    # Iniciar tunnel en tmux
    tmux kill-session -t tunnel 2>/dev/null || true
    tmux new-session -d -s tunnel "cloudflared tunnel run trefa-vllm 2>&1 | tee /tmp/cloudflared.log"

    sleep 5
    CF_PID=$(pgrep -f "cloudflared tunnel" 2>/dev/null | head -1 || echo "")

    if [ -n "$CF_PID" ]; then
        CF_URL="https://${CF_TUNNEL_DOMAIN}"
        log "Cloudflare Tunnel activo (PID=$CF_PID)"
        log "  ${CF_URL} → localhost:${FASTAPI_PORT}"

        # Test público (puede tardar unos segundos en propagarse)
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
    log "  Para activar: export CF_TUNNEL_CRED='{\"AccountTag\":\"...\",\"TunnelSecret\":\"...\",\"TunnelID\":\"...\"}'"
fi

log "Fase 9 completada"

# ============================================================
# FASE 10: SSH y resumen final
# ============================================================

log "=== FASE 10: SSH y resumen ==="

# --- SSH ---
if ! pgrep -x sshd > /dev/null 2>&1; then
    log "Configurando SSH..."
    mkdir -p /var/run/sshd /root/.ssh
    chmod 700 /root/.ssh

    # Permitir root login
    sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config 2>/dev/null || true
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config 2>/dev/null || true

    # Agregar clave pública si se proporciona
    if [ -n "${SSH_PUBLIC_KEY:-}" ]; then
        echo "$SSH_PUBLIC_KEY" >> /root/.ssh/authorized_keys
        chmod 600 /root/.ssh/authorized_keys
        log "Clave pública SSH agregada"
    fi

    /usr/sbin/sshd 2>/dev/null || true
    if pgrep -x sshd > /dev/null 2>&1; then
        log "SSH activo en puerto 22"
    else
        warn "SSH no pudo iniciar"
    fi
else
    log "SSH ya está activo"
fi

# --- Recopilar estados ---
VLLM_STATUS="OFF"
pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null 2>&1 && VLLM_STATUS="OK"
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
UPTIME_NOW=$(date '+%Y-%m-%d %H:%M:%S')

log ""
log "╔══════════════════════════════════════════════════════════════╗"
log "║           TREFA Mariana v11 — SETUP COMPLETO                ║"
log "╠══════════════════════════════════════════════════════════════╣"
log "║                                                              ║"
log "║  MODELO                                                      ║"
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
log "║    Chat UI:      ${CF_URL}/ui"
log "║    API Docs:     ${CF_URL}/docs"
else
log "║    Público:      (no configurado)"
fi
log "║                                                              ║"
log "║  ENV                                                         ║"
log "║    HF_TOKEN:          $([ -n "${HF_TOKEN:-}" ] && echo 'SET' || echo 'MISSING')"
log "║    CF_TUNNEL_CRED:    $([ -n "${CF_TUNNEL_CRED:-}" ] && echo 'SET' || echo 'NOT SET')"
log "║    SUPABASE_URL:      $([ -n "${SUPABASE_URL:-}" ] && echo 'SET' || echo 'NOT SET')"
log "║                                                              ║"
log "║  TMUX SESSIONS                                               ║"
log "║    tmux attach -t vllm      (logs vLLM)"
log "║    tmux attach -t mcp       (logs MCP)"
log "║    tmux attach -t fastapi   (logs FastAPI)"
if [ -n "$CF_URL" ]; then
log "║    tmux attach -t tunnel    (logs Cloudflare)"
fi
log "║                                                              ║"
log "║  LOGS                                                        ║"
log "║    Setup:       /tmp/trefa-setup.log"
log "║    vLLM:        /tmp/vllm.log"
log "║    MCP:         /tmp/mcp-server.log"
log "║    FastAPI:     /tmp/fastapi.log"
log "║    Tunnel:      /tmp/cloudflared.log"
log "║                                                              ║"
log "║  VERIFICACIÓN                                                ║"
log "║    curl localhost:${VLLM_PORT}/v1/models"
log "║    curl localhost:${FASTAPI_PORT}/health"
log "║    curl localhost:${MCP_PORT}/health"
log "║                                                              ║"
log "║  Inicio:        $UPTIME_NOW"
log "╚══════════════════════════════════════════════════════════════╝"
log ""

# ============================================================
# Health check final
# ============================================================

log "=== Health Check Final ==="

CHECKS_OK=0
CHECKS_TOTAL=0

check_service() {
    local name="$1"
    local url="$2"
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if curl -sf "$url" > /dev/null 2>&1; then
        log "  OK:   $name ($url)"
        CHECKS_OK=$((CHECKS_OK + 1))
    else
        warn "  FAIL: $name ($url)"
    fi
}

check_service "vLLM"     "http://localhost:${VLLM_PORT}/v1/models"
check_service "FastAPI"  "http://localhost:${FASTAPI_PORT}/health"
check_service "MCP"      "http://localhost:${MCP_PORT}/health"
if [ -n "$CF_URL" ]; then
    check_service "Tunnel" "${CF_URL}/health"
fi

if pgrep -x sshd > /dev/null 2>&1; then
    log "  OK:   SSH (puerto 22)"
    CHECKS_OK=$((CHECKS_OK + 1))
fi
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))

log ""
log "Health: $CHECKS_OK/$CHECKS_TOTAL servicios OK"
log ""
log "Setup completo. Los servicios corren en tmux sessions."
log "Para monitorear: tmux ls"
log ""

# Mantener el script corriendo — monitorear procesos principales
WAIT_PIDS=""
[ -n "$VLLM_PID" ]    && WAIT_PIDS="$WAIT_PIDS $VLLM_PID"
[ -n "$FASTAPI_PID" ] && WAIT_PIDS="$WAIT_PIDS $FASTAPI_PID"
[ -n "$MCP_PID" ]     && WAIT_PIDS="$WAIT_PIDS $MCP_PID"

if [ -n "$WAIT_PIDS" ]; then
    log "Monitoreando procesos principales..."
    # shellcheck disable=SC2086
    wait -n $WAIT_PIDS 2>/dev/null
    EXIT_CODE=$?

    log ""
    log "=== ALERTA: Un proceso terminó inesperadamente ==="
    for proc_info in \
        "vLLM:$(pgrep -f 'vllm.entrypoints' 2>/dev/null | head -1 || echo ''):/tmp/vllm.log" \
        "FastAPI:$(pgrep -f 'uvicorn app.main' 2>/dev/null | head -1 || echo ''):/tmp/fastapi.log" \
        "MCP:$(pgrep -f 'node.*mcp-server' 2>/dev/null | head -1 || echo ''):/tmp/mcp-server.log" \
        ; do
        IFS=':' read -r name pid logfile <<< "$proc_info"
        if [ -z "$pid" ]; then
            log "  CAIDO: $name"
            log "  Últimas líneas de $logfile:"
            tail -5 "$logfile" 2>/dev/null | while IFS= read -r line; do log "    $line"; done
        else
            log "  OK:    $name (PID $pid)"
        fi
    done

    log "Proceso terminó con código ${EXIT_CODE:-?}"
    exit "${EXIT_CODE:-1}"
else
    log "No hay PIDs directos para monitorear (servicios en tmux)"
    log "Usa 'tmux ls' para verificar"
fi

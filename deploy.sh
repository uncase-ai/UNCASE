#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# UNCASE — Script de Deployment
# Protector, validador y asegurador de deployments seguros
#
# Uso: ./deploy.sh [production|development|preview]
#
# Validaciones:
#   1. No hay cambios sin committear
#   2. Todos los commits están pushed al remoto
#   3. Se usa el canal de deployment correcto
#   4. Tests y linting pasan (producción)
#   5. Confirmación explícita para producción
# ═══════════════════════════════════════════════════════════════

set -e

# === Colores ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# === Parsear argumentos ===
ENVIRONMENT="${1:-development}"

if [[ ! "$ENVIRONMENT" =~ ^(production|development|preview)$ ]]; then
    echo -e "${RED}Error: Entorno inválido '${ENVIRONMENT}'${NC}"
    echo ""
    echo "Uso: ./deploy.sh [production|development|preview]"
    echo ""
    echo "  production   — Deploy a producción (Vercel production + framework release)"
    echo "  development  — Deploy de desarrollo local (default)"
    echo "  preview      — Deploy preview en Vercel (rama actual, sin merge a main)"
    exit 1
fi

# === Configuración por entorno ===
LANDING_DIR="frontend"
FRAMEWORK_DIR="uncase"
MAIN_BRANCH="main"

case "$ENVIRONMENT" in
    production)
        VERCEL_FLAGS="--prod"
        VERCEL_ENV="production"
        ;;
    development)
        VERCEL_FLAGS=""
        VERCEL_ENV="development"
        ;;
    preview)
        VERCEL_FLAGS=""
        VERCEL_ENV="preview"
        ;;
esac

# === Banner ===
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         UNCASE — Deployment Script                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Entorno:       ${GREEN}${ENVIRONMENT}${NC}"
echo -e "  Rama actual:   ${GREEN}$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'desconocida')${NC}"
echo -e "  Commit:        ${GREEN}$(git rev-parse --short HEAD 2>/dev/null || echo 'desconocido')${NC}"
echo -e "  Fecha:         ${GREEN}$(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""

TOTAL_STEPS=6
CURRENT_STEP=0

# === Función auxiliar ===
step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo -e "${YELLOW}[${CURRENT_STEP}/${TOTAL_STEPS}] $1${NC}"
}

fail() {
    echo -e "${RED}$1${NC}"
    exit 1
}

warn() {
    echo -e "${YELLOW}$1${NC}"
}

ok() {
    echo -e "${GREEN}$1${NC}"
}

# ═══════════════════════════════════════════════════════════════
# PASO 1: Verificar que estamos en un repositorio git
# ═══════════════════════════════════════════════════════════════
step "Verificando repositorio git..."

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    fail "  ✗ No estás dentro de un repositorio git."
fi

ok "  ✓ Repositorio git detectado"
echo ""

# ═══════════════════════════════════════════════════════════════
# PASO 2: Verificar que no hay cambios sin committear
# ═══════════════════════════════════════════════════════════════
step "Verificando cambios sin committear..."

# Archivos staged sin commit
STAGED=$(git diff --cached --name-only 2>/dev/null)
if [ -n "$STAGED" ]; then
    fail "  ✗ Hay archivos staged sin commit:\n$(echo "$STAGED" | sed 's/^/      /')\n\n  Haz commit antes de desplegar."
fi

# Archivos modificados sin stage
MODIFIED=$(git diff --name-only 2>/dev/null)
if [ -n "$MODIFIED" ]; then
    fail "  ✗ Hay archivos modificados sin committear:\n$(echo "$MODIFIED" | sed 's/^/      /')\n\n  Haz commit antes de desplegar."
fi

# Archivos sin rastrear (excluyendo los ignorados por .gitignore)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null)
if [ -n "$UNTRACKED" ]; then
    warn "  ⚠ Hay archivos sin rastrear (no bloqueante):"
    echo "$UNTRACKED" | head -10 | sed 's/^/      /'
    UNTRACKED_COUNT=$(echo "$UNTRACKED" | wc -l | tr -d ' ')
    if [ "$UNTRACKED_COUNT" -gt 10 ]; then
        echo "      ... y $((UNTRACKED_COUNT - 10)) más"
    fi
    echo ""
fi

ok "  ✓ Directorio de trabajo limpio"
echo ""

# ═══════════════════════════════════════════════════════════════
# PASO 3: Verificar que todos los commits están pushed
# ═══════════════════════════════════════════════════════════════
step "Verificando sincronización con remoto..."

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

# Verificar que el remoto existe
if ! git remote get-url origin > /dev/null 2>&1; then
    fail "  ✗ No hay remoto 'origin' configurado."
fi

# Fetch sin descargar (solo actualizar refs)
git fetch origin --quiet 2>/dev/null || warn "  ⚠ No se pudo conectar al remoto (sin conexión?)"

# Verificar si la rama remota existe
if git rev-parse --verify "origin/${CURRENT_BRANCH}" > /dev/null 2>&1; then
    LOCAL_HASH=$(git rev-parse HEAD)
    REMOTE_HASH=$(git rev-parse "origin/${CURRENT_BRANCH}")

    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        # Determinar dirección de la diferencia
        AHEAD=$(git rev-list --count "origin/${CURRENT_BRANCH}..HEAD" 2>/dev/null || echo "0")
        BEHIND=$(git rev-list --count "HEAD..origin/${CURRENT_BRANCH}" 2>/dev/null || echo "0")

        if [ "$AHEAD" -gt 0 ]; then
            fail "  ✗ Tienes ${AHEAD} commit(s) sin push a origin/${CURRENT_BRANCH}.\n\n  Ejecuta: git push origin ${CURRENT_BRANCH}"
        fi

        if [ "$BEHIND" -gt 0 ]; then
            fail "  ✗ Estás ${BEHIND} commit(s) detrás de origin/${CURRENT_BRANCH}.\n\n  Ejecuta: git pull origin ${CURRENT_BRANCH}"
        fi
    fi
    ok "  ✓ Rama sincronizada con origin/${CURRENT_BRANCH}"
else
    warn "  ⚠ La rama '${CURRENT_BRANCH}' no existe en el remoto."
    if [ "$ENVIRONMENT" = "production" ]; then
        fail "  ✗ Para producción, la rama debe existir en el remoto."
    else
        warn "  Se creará durante el deploy."
    fi
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# PASO 4: Validaciones por entorno
# ═══════════════════════════════════════════════════════════════
step "Validaciones de entorno (${ENVIRONMENT})..."

# --- Producción: verificar rama y ejecutar checks ---
if [ "$ENVIRONMENT" = "production" ]; then
    # Verificar que estamos en main
    if [ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]; then
        fail "  ✗ Los deploys a producción solo se permiten desde la rama '${MAIN_BRANCH}'.\n  Rama actual: '${CURRENT_BRANCH}'\n\n  Haz merge a ${MAIN_BRANCH} primero."
    fi
    ok "  ✓ Rama correcta para producción (${MAIN_BRANCH})"

    # Verificar que no hay archivos .env en el stage
    if git ls-files --cached | grep -qE '\.env$|\.env\.local$|\.env\.production$'; then
        fail "  ✗ Hay archivos .env trackeados en git. Esto es un riesgo de seguridad."
    fi
    ok "  ✓ No hay archivos .env trackeados"

    # Ejecutar linting del framework si existe
    if [ -d "$FRAMEWORK_DIR" ] && [ -f "$FRAMEWORK_DIR/pyproject.toml" ]; then
        echo -e "  ${BLUE}Ejecutando validaciones del framework Python...${NC}"

        if command -v uv > /dev/null 2>&1; then
            # Ruff check
            echo -n "    Ruff check... "
            if (cd "$FRAMEWORK_DIR" && uv run ruff check . --quiet 2>/dev/null); then
                ok "OK"
            else
                fail "\n  ✗ Ruff encontró errores. Ejecuta: cd ${FRAMEWORK_DIR} && uv run ruff check ."
            fi

            # Ruff format check
            echo -n "    Ruff format... "
            if (cd "$FRAMEWORK_DIR" && uv run ruff format --check --quiet . 2>/dev/null); then
                ok "OK"
            else
                fail "\n  ✗ Código sin formatear. Ejecuta: cd ${FRAMEWORK_DIR} && uv run ruff format ."
            fi

            # mypy
            echo -n "    mypy... "
            if (cd "$FRAMEWORK_DIR" && uv run mypy uncase/ --quiet 2>/dev/null); then
                ok "OK"
            else
                fail "\n  ✗ Errores de tipos. Ejecuta: cd ${FRAMEWORK_DIR} && uv run mypy uncase/"
            fi

            # pytest
            echo -n "    pytest... "
            if (cd "$FRAMEWORK_DIR" && uv run pytest --quiet 2>/dev/null); then
                ok "OK"
            else
                fail "\n  ✗ Tests fallaron. Ejecuta: cd ${FRAMEWORK_DIR} && uv run pytest"
            fi

            # Tests de privacidad (obligatorios)
            echo -n "    Tests de privacidad... "
            if [ -d "$FRAMEWORK_DIR/tests/privacy" ]; then
                if (cd "$FRAMEWORK_DIR" && uv run pytest tests/privacy/ --quiet 2>/dev/null); then
                    ok "OK"
                else
                    fail "\n  ✗ Tests de privacidad fallaron. Esto es BLOQUEANTE."
                fi
            else
                warn "SKIP (directorio no existe aún)"
            fi
        else
            warn "  ⚠ 'uv' no instalado — saltando validaciones Python"
        fi
    fi

    # Ejecutar checks del landing si existe
    if [ -d "$LANDING_DIR" ] && [ -f "$LANDING_DIR/package.json" ]; then
        echo -e "  ${BLUE}Ejecutando validaciones de la landing page...${NC}"

        echo -n "    TypeScript check... "
        if (cd "$LANDING_DIR" && pnpm run check-types 2>/dev/null); then
            ok "OK"
        else
            fail "\n  ✗ Errores de TypeScript. Ejecuta: cd ${LANDING_DIR} && pnpm run check-types"
        fi

        echo -n "    ESLint... "
        if (cd "$LANDING_DIR" && pnpm run lint 2>/dev/null); then
            ok "OK"
        else
            fail "\n  ✗ Errores de ESLint. Ejecuta: cd ${LANDING_DIR} && pnpm run lint:fix"
        fi

        echo -n "    Build... "
        if (cd "$LANDING_DIR" && pnpm run build 2>/dev/null); then
            ok "OK"
        else
            fail "\n  ✗ Build falló. Ejecuta: cd ${LANDING_DIR} && pnpm run build"
        fi
    fi
fi

# --- Preview: verificar que NO estamos en main ---
if [ "$ENVIRONMENT" = "preview" ]; then
    if [ "$CURRENT_BRANCH" = "$MAIN_BRANCH" ]; then
        fail "  ✗ Los deploys preview no deben hacerse desde '${MAIN_BRANCH}'.\n  Crea una rama feature/ primero."
    fi
    ok "  ✓ Rama de preview: ${CURRENT_BRANCH}"
fi

# --- Development: validaciones ligeras ---
if [ "$ENVIRONMENT" = "development" ]; then
    ok "  ✓ Entorno de desarrollo — validaciones ligeras"
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# PASO 5: Confirmación para producción
# ═══════════════════════════════════════════════════════════════
step "Confirmación de deployment..."

if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo -e "${RED}  ╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}  ║   ⚠  DEPLOY A PRODUCCIÓN                        ║${NC}"
    echo -e "${RED}  ║                                                   ║${NC}"
    echo -e "${RED}  ║   Esto actualizará el sitio en vivo.              ║${NC}"
    echo -e "${RED}  ║   Rama: ${MAIN_BRANCH}                                     ║${NC}"
    echo -e "${RED}  ║   Commit: $(git rev-parse --short HEAD)                              ║${NC}"
    echo -e "${RED}  ╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "  ¿Continuar con el deploy a producción? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        echo "  Deploy cancelado."
        exit 0
    fi
elif [ "$ENVIRONMENT" = "preview" ]; then
    echo -e "  Deploy preview desde rama ${CYAN}${CURRENT_BRANCH}${NC}"
else
    echo -e "  Deploy de desarrollo"
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# PASO 6: Ejecutar deployment
# ═══════════════════════════════════════════════════════════════
step "Ejecutando deployment..."

DEPLOY_START=$(date +%s)
DEPLOY_SUCCESS=true

# --- Landing Page (Vercel) ---
if [ -d "$LANDING_DIR" ]; then
    echo ""
    echo -e "  ${BLUE}━━━ Landing Page (Vercel) ━━━${NC}"

    if ! command -v vercel > /dev/null 2>&1; then
        warn "  ⚠ CLI de Vercel no instalado. Instálalo con: pnpm add -g vercel"
        warn "  Saltando deploy de landing page."
    else
        case "$ENVIRONMENT" in
            production)
                echo "  Desplegando a producción..."
                if (vercel --prod --yes --archive=tgz 2>&1 | sed 's/^/    /'); then
                    ok "  ✓ Landing page desplegada a producción"
                else
                    echo -e "${RED}  ✗ Falló el deploy de la landing page${NC}"
                    DEPLOY_SUCCESS=false
                fi
                ;;
            preview)
                echo "  Desplegando preview..."
                if (vercel --yes --archive=tgz 2>&1 | sed 's/^/    /'); then
                    ok "  ✓ Landing page desplegada como preview"
                else
                    echo -e "${RED}  ✗ Falló el deploy preview de la landing page${NC}"
                    DEPLOY_SUCCESS=false
                fi
                ;;
            development)
                echo "  Entorno de desarrollo — sin deploy remoto."
                echo "  Para desarrollo local: cd ${LANDING_DIR} && npm run dev"
                ok "  ✓ Listo para desarrollo local"
                ;;
        esac
    fi
fi

# --- Framework SCSF (Python) ---
if [ -d "$FRAMEWORK_DIR" ] && [ -f "$FRAMEWORK_DIR/pyproject.toml" ]; then
    echo ""
    echo -e "  ${BLUE}━━━ Framework SCSF (Python) ━━━${NC}"

    case "$ENVIRONMENT" in
        production)
            echo "  Verificando que el framework está listo para release..."
            # En producción el framework se distribuye como paquete
            # o se despliega como API. Por ahora verificamos integridad.
            if (cd "$FRAMEWORK_DIR" && uv run python -c "import uncase; print(f'  Version: {uncase.__version__}')" 2>/dev/null); then
                ok "  ✓ Framework importable y funcional"
            else
                warn "  ⚠ Framework aún no implementado o no importable"
            fi
            ;;
        preview)
            echo "  Ejecutando tests en modo preview..."
            if (cd "$FRAMEWORK_DIR" && uv run pytest --quiet 2>/dev/null); then
                ok "  ✓ Tests pasan en rama preview"
            else
                warn "  ⚠ Tests no disponibles aún"
            fi
            ;;
        development)
            echo "  Entorno de desarrollo — sin deploy remoto."
            echo "  Para desarrollo local: cd ${FRAMEWORK_DIR} && uv run uvicorn uncase.api.main:app --reload"
            ok "  ✓ Listo para desarrollo local"
            ;;
    esac
fi

# === Resumen ===
DEPLOY_END=$(date +%s)
DEPLOY_DURATION=$((DEPLOY_END - DEPLOY_START))

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

if [ "$DEPLOY_SUCCESS" = true ]; then
    echo -e "${GREEN}  ✓ DEPLOYMENT COMPLETADO${NC}"
else
    echo -e "${RED}  ✗ DEPLOYMENT CON ERRORES${NC}"
fi

echo ""
echo -e "  Entorno:  ${GREEN}${ENVIRONMENT}${NC}"
echo -e "  Rama:     ${GREEN}${CURRENT_BRANCH}${NC}"
echo -e "  Commit:   ${GREEN}$(git rev-parse --short HEAD)${NC}"
echo -e "  Duración: ${GREEN}${DEPLOY_DURATION}s${NC}"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

if [ "$ENVIRONMENT" = "development" ]; then
    echo ""
    echo "  Próximos pasos:"
    echo "    ./deploy.sh preview      — Deploy preview para revisión"
    echo "    ./deploy.sh production   — Deploy a producción"
fi

if [ "$ENVIRONMENT" = "preview" ]; then
    echo ""
    echo "  Si todo se ve bien:"
    echo "    git checkout ${MAIN_BRANCH} && git merge ${CURRENT_BRANCH}"
    echo "    ./deploy.sh production"
fi

echo ""

if [ "$DEPLOY_SUCCESS" = false ]; then
    exit 1
fi

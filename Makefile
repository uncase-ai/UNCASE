# ═══════════════════════════════════════════════════════════════
# UNCASE — Makefile
# Interfaz unificada de comandos para desarrollo
#
# Uso: make <target>
#       make help        — Ver todos los comandos disponibles
# ═══════════════════════════════════════════════════════════════

.DEFAULT_GOAL := help
.PHONY: help install dev dev-all api test test-unit test-integration test-privacy test-ml lint format typecheck check migrate docker-build docker-up docker-down docker-logs clean

# ── Instalación ──────────────────────────────────────────────

install: ## Instalar dependencias core
	uv sync

dev: ## Instalar dependencias core + dev
	uv sync --extra dev

dev-all: ## Instalar todas las dependencias (core + dev + ml + privacy)
	uv sync --extra all

# ── Servidor ─────────────────────────────────────────────────

api: ## Levantar servidor API en modo desarrollo (con reload)
	uv run uvicorn uncase.api.main:app --reload --port 8000

# ── Tests ────────────────────────────────────────────────────

test: ## Ejecutar toda la suite de tests
	uv run pytest

test-unit: ## Ejecutar solo tests unitarios
	uv run pytest tests/unit/

test-integration: ## Ejecutar solo tests de integración
	uv run pytest tests/integration/

test-privacy: ## Ejecutar suite de privacidad (obligatoria antes de PR)
	uv run pytest tests/privacy/

test-ml: ## Ejecutar tests de ML (requiere extras [ml])
	uv run pytest tests/ml/ -m ml

# ── Calidad de código ────────────────────────────────────────

lint: ## Ejecutar linter (ruff check)
	uv run ruff check .

format: ## Formatear código (ruff format)
	uv run ruff format .

typecheck: ## Verificar tipos (mypy)
	uv run mypy uncase/

check: lint typecheck test ## Ejecutar lint + typecheck + tests (pre-PR completo)
	@echo "✓ Todas las verificaciones pasaron"

# ── Base de datos ────────────────────────────────────────────

migrate: ## Ejecutar migraciones de Alembic
	uv run alembic upgrade head

# ── Docker ───────────────────────────────────────────────────

docker-build: ## Construir imagen Docker
	docker compose build

docker-up: ## Levantar servicios (API + PostgreSQL)
	docker compose up -d

docker-down: ## Detener todos los servicios
	docker compose down

docker-logs: ## Ver logs de la API
	docker compose logs -f api

# ── Limpieza ─────────────────────────────────────────────────

clean: ## Limpiar artefactos de build y cache
	rm -rf dist/ build/ *.egg-info/
	rm -rf .mypy_cache/ .pytest_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ── Ayuda ────────────────────────────────────────────────────

help: ## Mostrar esta ayuda
	@echo ""
	@echo "  UNCASE — Comandos disponibles"
	@echo "  ─────────────────────────────"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

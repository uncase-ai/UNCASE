# ═══════════════════════════════════════════════════════════════
# UNCASE — Makefile
# Unified command interface for development
#
# Usage: make <target>
#        make help        — Show all available commands
# ═══════════════════════════════════════════════════════════════

.DEFAULT_GOAL := help
.PHONY: help install dev dev-all api test test-unit test-integration test-privacy test-ml lint format typecheck check docs docs-all docs-changelog migrate docker-build docker-build-api docker-build-dashboard docker-up docker-fresh docker-down docker-logs docker-logs-dashboard clean

# ── Installation ─────────────────────────────────────────────

install: ## Install core dependencies
	uv sync

dev: ## Install core + dev dependencies
	uv sync --extra dev

dev-all: ## Install all dependencies (core + dev + ml + privacy)
	uv sync --extra all

# ── Server ───────────────────────────────────────────────────

api: ## Start API server in development mode (with reload)
	uv run uvicorn uncase.api.main:app --reload --port 8000

# ── Tests ────────────────────────────────────────────────────

test: ## Run the full test suite
	uv run pytest

test-unit: ## Run unit tests only
	uv run pytest tests/unit/

test-integration: ## Run integration tests only
	uv run pytest tests/integration/

test-privacy: ## Run privacy suite (mandatory before PR)
	uv run pytest tests/privacy/

test-ml: ## Run ML tests (requires [ml] extras)
	uv run pytest tests/ml/ -m ml

# ── Code Quality ─────────────────────────────────────────────

lint: ## Run linter (ruff check)
	uv run ruff check .

format: ## Format code (ruff format)
	uv run ruff format .

typecheck: ## Type check (mypy)
	uv run mypy uncase/

check: lint typecheck test ## Run lint + typecheck + tests (full pre-PR check)
	@echo "All checks passed"

# ── Documentation ────────────────────────────────────────────

docs: ## Run doc-agent to translate/update documentation
	uv run python scripts/doc-agent.py

docs-all: ## Translate all documentation files
	uv run python scripts/doc-agent.py --all

docs-changelog: ## Generate changelog entry from recent commits
	uv run python scripts/doc-agent.py --changelog

# ── Database ─────────────────────────────────────────────────

migrate: ## Run Alembic migrations
	uv run alembic upgrade head

# ── Docker ───────────────────────────────────────────────────

docker-build: ## Build all Docker images (API + Dashboard) — no cache
	docker compose build --no-cache api dashboard

docker-build-api: ## Build only the API image — no cache
	docker compose build --no-cache api

docker-build-dashboard: ## Build only the Dashboard image — no cache
	docker compose build --no-cache dashboard

docker-up: ## Start services (API + PostgreSQL + Dashboard)
	docker compose up -d

docker-fresh: ## Full rebuild and restart (down → build → up)
	docker compose down
	docker compose build --no-cache api dashboard
	docker compose up -d

docker-down: ## Stop all services
	docker compose down

docker-logs: ## View API logs
	docker compose logs -f api

docker-logs-dashboard: ## View Dashboard logs
	docker compose logs -f dashboard

# ── Cleanup ──────────────────────────────────────────────────

clean: ## Clean build artifacts and cache
	rm -rf dist/ build/ *.egg-info/
	rm -rf .mypy_cache/ .pytest_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ── Help ─────────────────────────────────────────────────────

help: ## Show this help
	@echo ""
	@echo "  UNCASE — Available commands"
	@echo "  ───────────────────────────"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

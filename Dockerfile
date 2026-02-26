# ═══════════════════════════════════════════════════════════════
# UNCASE — Dockerfile multi-stage
#
# Build:
#   docker build -t uncase .
#   docker build --build-arg INSTALL_EXTRAS=all -t uncase:full .
#   docker build --build-arg BASE_IMAGE=nvidia/cuda:12.4.1-runtime-ubuntu22.04 -t uncase:gpu .
#
# Run:
#   docker run -p 8000:8000 --env-file .env uncase
# ═══════════════════════════════════════════════════════════════

ARG BASE_IMAGE=python:3.12-slim

# ── Stage 1: Builder ──────────────────────────────────────────
FROM ${BASE_IMAGE} AS builder

ARG INSTALL_EXTRAS=""

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /build

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copiar solo archivos de dependencias primero (cache layer)
COPY pyproject.toml uv.lock* README.md ./

# Instalar dependencias (sin el paquete aún)
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    if [ -n "${INSTALL_EXTRAS}" ]; then \
        uv sync --frozen --no-install-project --extra ${INSTALL_EXTRAS}; \
    else \
        uv sync --frozen --no-install-project; \
    fi

# Copiar código fuente, Alembic migrations, and entrypoint
COPY uncase/ ./uncase/
COPY alembic/ ./alembic/
COPY alembic.ini ./
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    uv sync --frozen

# ── Stage 2: Runtime ─────────────────────────────────────────
FROM ${BASE_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UNCASE_ENV=production \
    UNCASE_LOG_LEVEL=INFO

WORKDIR /app

# Crear usuario non-root
RUN groupadd --gid 1000 uncase && \
    useradd --uid 1000 --gid uncase --shell /bin/bash --create-home uncase

# Copiar entorno virtual desde builder
COPY --from=builder --chown=uncase:uncase /build/.venv /app/.venv
COPY --from=builder --chown=uncase:uncase /build/uncase /app/uncase
COPY --from=builder --chown=uncase:uncase /build/alembic /app/alembic
COPY --from=builder --chown=uncase:uncase /build/alembic.ini /app/alembic.ini

# Copiar entrypoint
COPY --chown=uncase:uncase entrypoint.sh /app/entrypoint.sh

# Asegurar que el venv está en el PATH
ENV PATH="/app/.venv/bin:$PATH"

# Cambiar a usuario non-root
USER uncase

EXPOSE ${PORT:-8000}

ENTRYPOINT ["/app/entrypoint.sh"]
CMD uvicorn uncase.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-4}

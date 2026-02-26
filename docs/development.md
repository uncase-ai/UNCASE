# Development Guide

## Prerequisites

- Python >= 3.11
- Node.js >= 20 (for the dashboard)
- PostgreSQL 16+ (or Docker)
- `uv` package manager (recommended)

## Setup

```bash
git clone https://github.com/uncase-ai/uncase.git
cd uncase
cp .env.example .env
make dev-all                   # Install all dependencies
make migrate                   # Run database migrations
make api                       # Start API server (port 8000)

# In a separate terminal:
cd frontend && npm run dev     # Start dashboard (port 3000)
```

## Makefile Commands

```bash
make help          # All commands
make install       # Core dependencies
make dev           # + dev tools
make dev-all       # Everything
make api           # Start development server
make test          # Full test suite (970 tests)
make test-privacy  # Mandatory privacy tests
make lint          # Ruff linter
make format        # Ruff formatter
make typecheck     # mypy strict mode
make check         # lint + typecheck + tests (pre-PR gate)
make migrate       # Run database migrations
make docker-up     # Start Docker stack
make docker-down   # Stop Docker stack
make clean         # Remove build artifacts
```

## CLI Reference

```bash
uncase --help                          # All available commands
uncase --version                       # Framework version

uncase seed validate seeds.json        # Validate seeds against SeedSchema v1
uncase seed show seeds.json            # Display seeds in table format

uncase template list                   # List all 10 export formats
uncase template export data.json llama # Export for Llama fine-tuning
uncase template preview data.json chatml # Preview rendering

uncase import csv data.csv -o out.json     # Import from CSV
uncase import jsonl data.jsonl -o out.json # Import from JSONL

uncase tool list                       # List registered tools
uncase tool show buscar_inventario     # Tool details

uncase evaluate run convs.json seeds.json  # Run quality evaluation
```

## Testing

```bash
uv run pytest                          # Full suite (970 tests)
uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/       # Integration tests
uv run pytest tests/privacy/           # Privacy tests (mandatory)
uv run pytest -x -k "test_name"        # Single test
uv run pytest --cov=uncase             # With coverage report
```

## Code Quality

- **Linter/Formatter**: Ruff (replaces black, isort, flake8)
- **Type checker**: mypy (strict mode)
- **Line length**: 120 characters
- **Docstrings**: Google style
- **Type hints**: Required on all public functions
- **Logging**: structlog (JSON structured), never `print()`
- **Security**: Zero real data in tests, custom exceptions only, no stack traces in production

## Pre-PR Checklist

Every pull request must pass:

```bash
make check                     # Runs all three:
# 1. uv run ruff check .      — Zero lint errors
# 2. uv run mypy uncase/      — Zero type errors
# 3. uv run pytest            — All tests pass

uv run pytest tests/privacy/   # MANDATORY: Privacy suite must pass
```

## Deployment

```bash
./deploy.sh development       # Local development
./deploy.sh preview           # Vercel preview branch
./deploy.sh production        # Production (requires confirmation)
```

The deploy script validates: clean git state, all commits pushed, correct branch, TypeScript + ESLint pass, production build succeeds.

## Contributing

UNCASE is looking for contributors across multiple areas:

### For Developers

- **New connectors**: Slack, Intercom, Zendesk, Salesforce, Telegram
- **New domain tools**: Healthcare (HL7/FHIR), legal (case management), finance (trading)
- **Layer 4 implementation**: LoRA/QLoRA training pipeline with DP-SGD
- **Test coverage**: Integration tests for connectors, gateway, and provider service

### For Domain Experts

- **Seed libraries**: Curated seed collections for specific industries
- **Quality thresholds**: Domain-specific metric calibration
- **Tool definitions**: Industry-specific tool schemas and simulators

### For Researchers

- **Privacy metrics**: Novel memorization detection techniques
- **Quality metrics**: Beyond ROUGE-L — semantic similarity, factual grounding
- **Differential privacy**: Optimal epsilon values per domain

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Run `make check` before submitting
4. Run `uv run pytest tests/privacy/` (mandatory)
5. Submit a PR with a clear description

See [CLAUDE.md](../CLAUDE.md) for detailed coding conventions.

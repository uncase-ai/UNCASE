# UNCASE: Investor-Readiness Analysis & Development Plan

**Date**: 2026-02-25
**Version**: 1.0
**Status**: Active development — pre-seed phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Assessment](#current-state-assessment)
3. [Hard Truths](#hard-truths)
4. [What Would Make This Investable](#what-would-make-this-investable)
5. [Development Plan: Investor-Ready MVP](#development-plan-investor-ready-mvp)
6. [Technical Inventory](#technical-inventory)
7. [Risk Matrix](#risk-matrix)

---

## Executive Summary

UNCASE (Unbiased Neutral Convention for Agnostic Seed Engineering) is an open-source framework for generating synthetic conversational training data for fine-tuning LLMs in regulated industries (healthcare, finance, legal, manufacturing) without exposing real PII.

**What exists today**: A working API (71 endpoints), a polished frontend (28 pages, 137 components), a partially implemented 5-layer pipeline (Layers 1-3 working, Layers 0 and 4 are abstract protocols only), PII detection (regex + Presidio), multi-LLM support (via LiteLLM), Docker deployment, CI/CD, and a landing page on Vercel.

**What's missing**: The two endpoints of the pipeline (safe ingestion of real conversations and actual model training), differential privacy implementation, real authentication, background job processing, and proof it works at scale.

**Gap to investable**: 8-12 weeks of focused development on the right priorities.

---

## Current State Assessment

### Architecture: 5-Layer SCSF Pipeline

| Layer | Name | Status | LOC | Reality |
|-------|------|--------|-----|---------|
| 0 | Seed Engine | **PROTOCOL ONLY** | ~26 | Abstract class, no implementation |
| 1 | Parser/Validator | **PARTIAL** | ~300 | CSV + JSONL parsers working, format detection functional |
| 2 | Quality Evaluator | **COMPLETE** | ~800 | All 5 metrics implemented: ROUGE-L, Fidelity, Diversity, Coherence, Privacy |
| 3 | Synthetic Generator | **COMPLETE** | ~700 | LiteLLM multi-provider, feedback loop, retry logic |
| 4 | LoRA Pipeline | **PROTOCOL ONLY** | ~31 | Abstract class, no training code |

### Backend Metrics

- **Python source files**: 201
- **Source LOC**: 19,136
- **Test files**: 117
- **Test functions**: 309
- **Test coverage**: 45% overall (target: 80% core, 90% schemas)
- **API endpoints**: 71
- **Database migrations**: 6 (Alembic)
- **Dependencies**: 44 core packages

### Frontend Metrics

- **Component files**: 137 (.tsx)
- **Page routes**: 28
- **Source LOC**: 23,925
- **API client modules**: 17
- **Production dependencies**: 22

### Infrastructure

- **Backend**: FastAPI + PostgreSQL (async) + Docker (multi-stage, GPU support)
- **Frontend**: Next.js 16 + React 19 + Tailwind CSS 4 + shadcn/ui on Vercel
- **CI/CD**: GitHub Actions (lint, type check, tests on Python 3.11/3.12/3.13)
- **Release**: Tag-based PyPI publish + Homebrew formula generation

---

## Hard Truths

### 1. The Core Value Proposition Is Unfinished

The pitch is: "Turn real conversations into trained LoRA models with zero PII exposure."

- **Layer 0 (Seed Engine)**: 26 lines. Abstract protocol. The first step of the pipeline — ingesting real conversations and stripping PII to create seeds — is not implemented.
- **Layer 4 (LoRA Pipeline)**: 31 lines. Abstract protocol. The final step — producing a trained model — doesn't exist.

The product cannot do the two things it promises. What exists is the middle (generation + evaluation), which is useful but not the differentiator.

### 2. Privacy Claims Are Aspirational, Not Proven

The whitepaper mentions:
- **DP-SGD with epsilon <= 8.0**: Zero implementation code.
- **Extraction attack success rate < 1%**: No attack testing framework.
- **Memorization metric < 0.01**: Schema field exists, no actual detection logic.

The PII scanner (regex + Presidio) detects surface-level PII. But differential privacy guarantees required for HIPAA, GDPR, and SOX compliance are completely absent. The `UNCASE_DP_EPSILON` environment variable exists in .env but is never read by any code.

### 3. Test Coverage Is a Liability

- Overall: 45% (should be 80%+)
- Services (business logic): 19-32%
- Tools executor: 19%
- Templates: 25-46%
- Security utilities: 32%

Critical business logic has the least coverage. This signals "move fast, fix later" — fine for a prototype, bad for a framework handling regulated data.

### 4. Authentication Is Insufficient for Target Market

Current auth: API key stored in browser localStorage. No JWT, no OAuth, no SSO, no MFA, no session management, no token refresh, no role-based access beyond basic string-parsed "scopes."

Regulated industries require SAML/SSO (healthcare), MFA (finance), and fine-grained RBAC (legal). Current auth is appropriate for a developer beta, not the market being targeted.

### 5. No Background Job Processing

No Celery, no RQ, no Temporal, no Airflow. Long-running operations (generation, evaluation, training) are synchronous HTTP requests or fire-and-forget patterns. No job submission, progress tracking, retry, or completion notification. Cannot queue 10,000 generations or track a multi-hour training run.

### 6. Frontend Is a Dashboard Without a Workflow

The UI is polished but operates primarily on localStorage demo data. Most pages load mock data and optionally call the API. No guided path from "I have conversations" to "I have a trained model." It's a collection of admin pages, not a product experience.

### 7. No Proof It Works At Scale

Zero load testing. No benchmarks. No case studies. No evidence that the quality thresholds (ROUGE-L >= 0.65, Fidelity >= 0.90) were validated against real-world outcomes. No demonstration of generating N conversations and achieving measurable results.

---

## What Would Make This Investable

### Tier 1: Must-Have (Without These, Don't Pitch)

| # | Item | Why | Effort |
|---|------|-----|--------|
| 1 | **Implement Layer 0 (Seed Engine)** | Can't ingest real conversations without it | 2 weeks |
| 2 | **Implement Layer 4 (LoRA Pipeline)** | Can't produce the promised output without it | 2 weeks |
| 3 | **End-to-end demo** | 100 conversations → seeds → 1,000 synthetic → evaluate → train → show model | 1 week |
| 4 | **Implement DP-SGD or remove the claim** | Making unsubstantiated privacy claims to regulated industries is a legal liability | 1 week |
| 5 | **Real authentication** | JWT + refresh tokens + RBAC (admin/developer/viewer) + org-scoped isolation | 2 weeks |
| 6 | **Background job system** | Celery + Redis for generation, evaluation, training. Progress tracking via WebSocket. | 2 weeks |

### Tier 2: Strongly Expected (Investors Will Ask)

| # | Item | Why | Effort |
|---|------|-----|--------|
| 7 | **SOC 2 Type I readiness** | Audit logging, encryption at rest, access control docs, incident response plan, data retention | 2 weeks |
| 8 | **Benchmarks & validation** | Run evaluator on public datasets, publish results, compare to baselines | 1 week |
| 9 | **Multi-tenancy with hard isolation** | Row-level security in PostgreSQL, separate data per org | 1 week |
| 10 | **Rate limiting** | Per API key limits to prevent abuse and cost overrun | 3 days |
| 11 | **Observability** | Prometheus metrics, Grafana dashboards, alerting, distributed tracing | 1 week |
| 12 | **Test coverage to 80%+** | Core business logic needs proper test coverage | 2 weeks |

### Tier 3: Differentiation (What Makes Investors Excited)

| # | Item | Why | Effort |
|---|------|-----|--------|
| 13 | **Privacy certification / formal verification** | Academic partner to verify DP guarantees | 4-8 weeks |
| 14 | **Pre-built domain packages** | 50 curated seeds per domain, lower time-to-value | 2 weeks |
| 15 | **Model marketplace** | Share trained LoRA adapters (not data), creates network effect | 4 weeks |
| 16 | **Compliance-as-code templates** | HIPAA, GDPR, SOX config profiles with pre-set thresholds and audit hooks | 2 weeks |
| 17 | **Python SDK** | `from uncase import Pipeline; p.generate(1000)` — ML engineers want code, not dashboards | 1 week |

---

## Development Plan: Investor-Ready MVP

### Phase 1: Complete the Pipeline (Weeks 1-3)

**Week 1-2: Layer 0 — Seed Engine Implementation**
- [ ] WhatsApp export parser (chat.txt format)
- [ ] CSV transcript parser (call center format)
- [ ] JSON/JSONL raw conversation ingestion
- [ ] Automatic PII detection + anonymization during ingestion
- [ ] Seed extraction: identify roles, domain, tone, objectives from raw data
- [ ] SeedSchema v1 output with full metadata
- [ ] Integration tests with sample data from all 3 formats

**Week 2-3: Layer 4 — LoRA Pipeline Implementation**
- [ ] HuggingFace transformers + peft integration
- [ ] Data preparation: conversations → tokenized training format
- [ ] LoRA configuration: rank, alpha, dropout, target modules
- [ ] QLoRA support: 4-bit quantization via bitsandbytes
- [ ] Training loop with MLflow experiment tracking
- [ ] Checkpoint saving and model export
- [ ] Basic DP-SGD integration via Opacus (SGD with calibrated noise)
- [ ] Epsilon accounting and privacy budget tracking
- [ ] Model evaluation after training (perplexity, task-specific metrics)

**Week 3: End-to-End Integration**
- [ ] Pipeline orchestrator: seed → generate → evaluate → train in one call
- [ ] CLI command: `uncase pipeline run --domain automotive.sales --count 1000`
- [ ] API endpoint: `POST /api/v1/pipeline/run` with job tracking
- [ ] Record demo: 100 raw → 1,000 synthetic → trained LoRA adapter

### Phase 2: Infrastructure (Weeks 4-5)

**Week 4: Background Job System**
- [ ] Celery + Redis integration
- [ ] Job types: generation, evaluation, training, import
- [ ] Job model in PostgreSQL (status, progress, result, error)
- [ ] API endpoints: submit job, get status, list jobs, cancel job
- [ ] WebSocket or SSE progress updates to frontend
- [ ] Retry logic with exponential backoff
- [ ] Frontend: job queue page with real-time status

**Week 5: Authentication & Authorization**
- [ ] JWT access + refresh token pair
- [ ] Token refresh endpoint with rotation
- [ ] RBAC: admin, developer, viewer roles per organization
- [ ] Permission middleware on all endpoints
- [ ] Organization-scoped data isolation (all queries filtered by org_id)
- [ ] Password hashing (argon2, already available)
- [ ] Login/register API endpoints
- [ ] Frontend: login page, token storage, auto-refresh

### Phase 3: Quality & Trust (Weeks 6-7)

**Week 6: Test Coverage Push**
- [ ] Core coverage from 45% → 80%
- [ ] Service layer tests (usage, webhooks, knowledge, providers)
- [ ] Template system tests (all 10 formats)
- [ ] Tools executor tests
- [ ] Security utility tests
- [ ] Integration tests for full pipeline
- [ ] Privacy suite expansion: test against MITRE PII datasets

**Week 7: Benchmarks & Validation**
- [ ] Select 3 public conversation datasets
- [ ] Run full pipeline on each dataset
- [ ] Measure: generation quality, PII detection accuracy, training convergence
- [ ] Compare synthetic quality to baselines (random, template-based)
- [ ] Publish results in technical blog post / benchmark document
- [ ] Create reproducible benchmark script

### Phase 4: Enterprise Readiness (Weeks 8-9)

**Week 8: Security & Compliance**
- [ ] Audit logging: who accessed what data, when, from where
- [ ] Rate limiting per API key (configurable tiers)
- [ ] Row-level security in PostgreSQL
- [ ] Data retention policies (auto-delete configurable per org)
- [ ] Encryption at rest for sensitive fields (API keys, conversation content)
- [ ] CSRF protection on mutation endpoints
- [ ] Security headers (HSTS, CSP, X-Frame-Options)

**Week 9: Observability**
- [ ] Prometheus metrics endpoint (/metrics)
- [ ] Key metrics: request latency, LLM call duration, job queue depth, error rates
- [ ] Grafana dashboard templates (included in repo)
- [ ] Health check improvements: deep checks for DB, Redis, LLM providers
- [ ] Structured audit trail (separate from app logs)
- [ ] Cost tracking: LLM API spend per org, per job

### Phase 5: Demo & Distribution (Weeks 10-12)

**Week 10: Python SDK**
- [ ] `uncase-sdk` package (separate from server)
- [ ] Programmatic API: `Pipeline`, `SeedEngine`, `Generator`, `Evaluator`, `Trainer`
- [ ] Notebook-friendly: works in Jupyter, Colab
- [ ] Async and sync interfaces
- [ ] Published to PyPI

**Week 11: Domain Packages**
- [ ] 50 curated seeds: automotive.sales
- [ ] 50 curated seeds: medical.consultation
- [ ] 50 curated seeds: finance.advisory
- [ ] Compliance profile: HIPAA (medical)
- [ ] Compliance profile: GDPR (all domains)
- [ ] Quick-start: `uncase quickstart automotive --count 500`

**Week 12: Demo & Documentation**
- [ ] End-to-end demo video: automotive domain (5 min)
- [ ] End-to-end demo video: medical domain (5 min)
- [ ] API documentation with request/response examples
- [ ] Architecture guide with data flow diagrams
- [ ] Deployment guide (Docker, Kubernetes, cloud)
- [ ] Benchmark results document
- [ ] Investor pitch deck with technical appendix

---

## Technical Inventory

### Backend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | >= 3.11 |
| Package Manager | uv | Latest |
| API Framework | FastAPI | 0.115.0 |
| Server | Uvicorn | 0.32.0 |
| Validation | Pydantic v2 | 2.10.0 |
| LLM Interface | LiteLLM | 1.55.0 |
| Database | PostgreSQL + asyncpg | 16 / 0.30.0 |
| ORM | SQLAlchemy (async) | 2.0.36 |
| Migrations | Alembic | 1.14.0 |
| Logging | structlog | 24.4.0 |
| CLI | Typer | 0.15.0 |
| HTTP Client | httpx | 0.28.0 |
| Security | argon2-cffi, cryptography | 23.1.0 / 43.0.0 |
| ML (optional) | transformers, peft, trl, torch | Latest |
| Privacy (optional) | spacy, presidio-analyzer | Latest |
| ML Tracking (optional) | MLflow | Latest |
| Sandbox (optional) | E2B | Latest |

### Frontend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js (App Router) | 16.1.1 |
| UI Library | React | 19.2.3 |
| Language | TypeScript (strict) | 5.9.3 |
| Styling | Tailwind CSS | 4.1.18 |
| Components | shadcn/ui + Radix UI | Latest |
| Icons | Lucide React | 0.562.0 |
| Animation | Motion | 12.29.2 |
| Charts | Recharts | 2.15.4 |
| Theming | next-themes | 0.4.6 |

### API Endpoint Summary

| Category | Endpoints | Status |
|----------|-----------|--------|
| Health | 2 | Working |
| Organizations | 6 | Working |
| API Keys | 4 | Working |
| Seeds | 5 | Working |
| Conversations | 4 | Working |
| Generation | 3 | Working |
| Evaluation | 4 | Working |
| Templates | 4 | Working |
| Tools | 5 | Working |
| Plugins | 4 | Working |
| Gateway (LLM proxy) | 2 | Working |
| Knowledge Base | 5 | Working |
| Usage Metering | 4 | Working |
| Webhooks | 8 | Working |
| Connectors | 3 | Working |
| Sandbox (E2B) | 4 | Working |
| Pipeline (orchestrator) | 0 | **Not implemented** |
| Training (LoRA) | 0 | **Not implemented** |
| Jobs (background) | 0 | **Not implemented** |

---

## Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Layer 0/4 take longer than estimated | Medium | High | Start with minimal viable implementation, expand iteratively |
| DP-SGD integration proves unstable with LLM fine-tuning | Medium | High | Implement basic noise injection first, iterate toward formal guarantees |
| Test coverage push reveals architectural bugs | Medium | Medium | Allocate buffer week, prioritize critical path tests |
| LLM API costs during benchmarking | Low | Medium | Use Ollama for local testing, reserve cloud LLMs for final benchmarks |
| Celery/Redis adds operational complexity | Low | Low | Provide Docker Compose profile for full stack |
| JWT auth migration breaks existing users | Low | Medium | Keep API key auth as fallback, add JWT as primary |
| Competition ships similar product | Medium | High | Focus on privacy differentiator (DP-SGD), not feature count |
| Regulatory landscape changes | Low | High | Design compliance profiles as pluggable modules |

---

## Success Metrics for Investor Readiness

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Pipeline completeness | 3/5 layers | 5/5 layers | Week 3 |
| Test coverage (core/) | 45% | 80%+ | Week 7 |
| End-to-end demo | None | 2 domains recorded | Week 12 |
| Authentication | API key only | JWT + RBAC | Week 5 |
| Background jobs | None | Celery + Redis | Week 4 |
| DP-SGD implementation | None | Basic Opacus integration | Week 3 |
| Benchmarks published | None | 3 datasets | Week 7 |
| Python SDK | None | PyPI package | Week 10 |
| Domain seed packages | 0 seeds | 150 seeds (3 domains) | Week 11 |

---

*This document is a living artifact. Update as milestones are completed.*

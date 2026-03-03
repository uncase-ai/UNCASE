"""Demo sandbox orchestrator — short-lived industry-specific UNCASE instances.

Spins up fully configured E2B sandboxes with the UNCASE API pre-loaded,
demo seeds for a specific domain, and a time-to-live auto-destroy timer.
Users get instant access without installation.
"""

from __future__ import annotations

import contextlib
import json
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import structlog

from uncase.exceptions import SandboxError, SandboxNotConfiguredError
from uncase.sandbox.schemas import (
    DemoSandboxRequest,
    DemoSandboxResponse,
    SandboxJob,
    SandboxJobStatus,
    SandboxTemplate,
)

if TYPE_CHECKING:
    from uncase.config import UNCASESettings

logger = structlog.get_logger(__name__)

# Demo seed templates per domain — minimal seeds for quick demonstration
_DEMO_SEEDS: dict[str, dict[str, object]] = {
    "automotive.sales": {
        "dominio": "automotive.sales",
        "idioma": "es",
        "roles": ["vendedor", "cliente"],
        "descripcion_roles": {
            "vendedor": "Sales representative at a car dealership",
            "cliente": "Potential buyer looking for a new vehicle",
        },
        "objetivo": "Guide the customer through a vehicle purchase consultation",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 12,
            "flujo_esperado": [
                "Greeting and needs assessment",
                "Vehicle presentation and features",
                "Test drive discussion",
                "Pricing and financing options",
                "Closing or follow-up scheduling",
            ],
        },
        "parametros_factuales": {
            "contexto": "Premium car dealership offering sedans, SUVs, and electric vehicles",
            "restricciones": [
                "Financing available from 12 to 72 months",
                "Trade-in values based on market data",
                "All vehicles include manufacturer warranty",
            ],
            "herramientas": ["inventory_lookup", "financing_calculator", "trade_in_estimator"],
        },
    },
    "medical.consultation": {
        "dominio": "medical.consultation",
        "idioma": "es",
        "roles": ["medico", "paciente"],
        "descripcion_roles": {
            "medico": "Primary care physician conducting a consultation",
            "paciente": "Adult patient with symptoms seeking medical advice",
        },
        "objetivo": "Conduct a thorough medical consultation from intake to treatment plan",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 8,
            "turnos_max": 14,
            "flujo_esperado": [
                "Patient intake and greeting",
                "Symptom assessment and medical history",
                "Physical examination discussion",
                "Diagnosis explanation",
                "Treatment plan and prescriptions",
                "Follow-up scheduling",
            ],
        },
        "parametros_factuales": {
            "contexto": "General practice clinic with lab and imaging capabilities",
            "restricciones": [
                "Follow evidence-based medical guidelines",
                "Always recommend follow-up for chronic conditions",
                "Prescriptions must include dosage and duration",
            ],
            "herramientas": ["patient_records", "lab_orders", "prescription_system"],
        },
    },
    "legal.advisory": {
        "dominio": "legal.advisory",
        "idioma": "es",
        "roles": ["abogado", "cliente"],
        "descripcion_roles": {
            "abogado": "Licensed attorney providing legal consultation",
            "cliente": "Individual seeking legal advice on a matter",
        },
        "objetivo": "Provide initial legal consultation and outline next steps",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 12,
            "flujo_esperado": [
                "Client intake and case overview",
                "Fact gathering and documentation review",
                "Legal analysis and applicable laws",
                "Strategy options and risk assessment",
                "Next steps and engagement terms",
            ],
        },
        "parametros_factuales": {
            "contexto": "General practice law firm handling civil and commercial matters",
            "restricciones": [
                "Attorney-client privilege applies",
                "All advice is general until formal engagement",
                "Conflict of interest check required",
            ],
            "herramientas": ["case_management", "legal_research", "document_review"],
        },
    },
    "finance.advisory": {
        "dominio": "finance.advisory",
        "idioma": "es",
        "roles": ["asesor", "cliente"],
        "descripcion_roles": {
            "asesor": "Certified financial advisor providing investment guidance",
            "cliente": "Individual seeking financial planning advice",
        },
        "objetivo": "Conduct a financial assessment and provide investment recommendations",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 12,
            "flujo_esperado": [
                "Client profiling and financial goals",
                "Current portfolio assessment",
                "Risk profiling questionnaire",
                "Investment recommendations",
                "Action plan and next steps",
            ],
        },
        "parametros_factuales": {
            "contexto": "Independent financial advisory firm with multi-asset capabilities",
            "restricciones": [
                "All recommendations must align with risk profile",
                "Regulatory disclosures required",
                "Past performance does not guarantee future results",
            ],
            "herramientas": ["portfolio_analyzer", "risk_calculator", "market_data"],
        },
    },
    "industrial.support": {
        "dominio": "industrial.support",
        "idioma": "es",
        "roles": ["tecnico", "operador"],
        "descripcion_roles": {
            "tecnico": "Technical support specialist for industrial equipment",
            "operador": "Plant operator reporting an equipment issue",
        },
        "objetivo": "Diagnose and resolve an industrial equipment issue",
        "tono": "profesional",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 12,
            "flujo_esperado": [
                "Issue identification and error codes",
                "Equipment and environment assessment",
                "Diagnostic steps and troubleshooting",
                "Resolution guidance or escalation",
                "Preventive maintenance recommendations",
            ],
        },
        "parametros_factuales": {
            "contexto": "Manufacturing plant with CNC machines, PLCs, and SCADA systems",
            "restricciones": [
                "Safety protocols must be followed before any intervention",
                "Lockout/tagout procedures are mandatory",
                "Equipment warranty terms must be verified",
            ],
            "herramientas": ["diagnostic_tool", "equipment_manual", "spare_parts_catalog"],
        },
    },
    "education.tutoring": {
        "dominio": "education.tutoring",
        "idioma": "es",
        "roles": ["tutor", "estudiante"],
        "descripcion_roles": {
            "tutor": "Subject matter expert providing academic tutoring",
            "estudiante": "Student seeking help with coursework",
        },
        "objetivo": "Guide the student through a learning topic with explanations and practice",
        "tono": "amigable",
        "pasos_turnos": {
            "turnos_min": 6,
            "turnos_max": 14,
            "flujo_esperado": [
                "Topic introduction and student background",
                "Concept explanation with examples",
                "Practice exercise presentation",
                "Student attempt and feedback",
                "Summary and next study recommendations",
            ],
        },
        "parametros_factuales": {
            "contexto": "Online tutoring platform for university-level courses",
            "restricciones": [
                "Adapt explanations to student level",
                "Encourage active learning over passive instruction",
                "Provide additional resources for further study",
            ],
            "herramientas": ["whiteboard", "quiz_generator", "resource_library"],
        },
    },
}


class DemoSandboxOrchestrator:
    """Manages short-lived demo sandboxes for industry verticals.

    Spins up a fully configured UNCASE instance inside an E2B sandbox
    with pre-loaded seeds, a running API, and a time-to-live auto-destroy.

    Usage:
        demo = DemoSandboxOrchestrator(settings=settings)
        response = await demo.create_demo(
            DemoSandboxRequest(domain="automotive.sales", ttl_minutes=30)
        )
        # response.api_url -> "https://8000-<sandbox_id>.e2b.app"
    """

    def __init__(self, *, settings: UNCASESettings) -> None:
        if not settings.sandbox_available:
            raise SandboxNotConfiguredError()

        self._settings = settings

    async def create_demo(self, request: DemoSandboxRequest) -> DemoSandboxResponse:
        """Create a demo sandbox for the specified domain.

        Args:
            request: Demo sandbox configuration.

        Returns:
            DemoSandboxResponse with access URLs and job tracking.
        """
        from e2b_code_interpreter import AsyncSandbox

        # Resolve template from domain
        template_map: dict[str, SandboxTemplate] = {
            "automotive.sales": SandboxTemplate.DEMO_AUTOMOTIVE,
            "medical.consultation": SandboxTemplate.DEMO_MEDICAL,
            "legal.advisory": SandboxTemplate.DEMO_LEGAL,
            "finance.advisory": SandboxTemplate.DEMO_FINANCE,
            "industrial.support": SandboxTemplate.DEMO_INDUSTRIAL,
            "education.tutoring": SandboxTemplate.DEMO_EDUCATION,
        }
        template = template_map.get(request.domain, SandboxTemplate.DEMO_AUTOMOTIVE)

        job = SandboxJob(
            template=template,
            status=SandboxJobStatus.BOOTING,
        )

        logger.info(
            "demo_sandbox_creating",
            job_id=job.job_id,
            domain=request.domain,
            ttl_minutes=request.ttl_minutes,
        )

        sandbox = None
        try:
            sandbox = await AsyncSandbox.create(
                template=self._settings.e2b_template_id,
                api_key=self._settings.e2b_api_key,
                timeout=request.ttl_minutes * 60,
            )

            job.status = SandboxJobStatus.RUNNING

            # Write demo seeds
            demo_seed = _DEMO_SEEDS.get(request.domain, _DEMO_SEEDS["automotive.sales"])
            seeds_data = []
            for i in range(request.preload_seeds):
                seed = dict(demo_seed)
                seed["seed_id"] = f"demo-{request.domain.replace('.', '-')}-{i + 1}"
                if request.language != "es":
                    seed["idioma"] = request.language
                seeds_data.append(seed)

            await sandbox.files.write(
                "/home/user/demo_seeds.json",
                json.dumps(seeds_data, ensure_ascii=False),
            )

            # Write a minimal API startup script
            api_script = _build_demo_api_script(request.domain, seeds_data)
            await sandbox.files.write("/home/user/demo_api.py", api_script)

            # Write a bootstrap script that installs deps and starts the API
            # in one shot — avoids E2B SDK request timeout on long pip installs.
            bootstrap_script = (
                "#!/bin/bash\n"
                "set -e\n"
                "pip install --no-cache-dir -q fastapi uvicorn pydantic 2>&1\n"
                "cd /home/user && python demo_api.py > api.log 2>&1\n"
            )
            await sandbox.files.write("/home/user/bootstrap.sh", bootstrap_script)

            # Start the bootstrap in the background using the SDK's
            # built-in background execution (E2B v2 API).
            logger.info("demo_sandbox_installing", job_id=job.job_id)
            await sandbox.commands.run(
                "chmod +x /home/user/bootstrap.sh && /home/user/bootstrap.sh",
                background=True,
            )

            # Wait for the API to be ready (poll health endpoint).
            # Allow up to 150s (50 polls × 3s) to accommodate pip install
            # on the "base" template which can take 60-90s.
            import asyncio

            api_ready = False
            for attempt in range(50):
                check = await sandbox.commands.run(
                    "curl -sf http://localhost:8000/health || true",
                    timeout=5,
                )
                if check.stdout and "ok" in check.stdout:
                    api_ready = True
                    logger.info(
                        "demo_sandbox_health_ok",
                        job_id=job.job_id,
                        attempts=attempt + 1,
                    )
                    break
                await asyncio.sleep(3)

            if not api_ready:
                # Grab bootstrap output to diagnose the failure
                log_result = await sandbox.commands.run(
                    "cat /home/user/api.log 2>/dev/null; echo '---'; ps aux 2>/dev/null | head -20",
                    timeout=5,
                )
                log_tail = (log_result.stdout or "")[:1000]
                logger.error(
                    "demo_sandbox_api_not_ready",
                    job_id=job.job_id,
                    log_tail=log_tail,
                )
                msg = f"Demo API did not start within 150s. Log: {log_tail[:300]}"
                raise SandboxError(msg)

            # Build URLs — E2B v2 get_host() returns hostname only
            # (e.g. "8000-abc123.e2b.app"), so we must prepend the scheme.
            sandbox_host_fn = getattr(sandbox, "get_host", None)
            if callable(sandbox_host_fn):
                hostname = sandbox_host_fn(8000)
                host = f"https://{hostname}"
            else:
                # Legacy fallback — should not happen with E2B v2
                sandbox_id = getattr(sandbox, "sandbox_id", "unknown")
                host = f"https://8000-{sandbox_id}.e2b.app"

            api_url = host
            docs_url = f"{host}/docs"

            expires_at = datetime.now(UTC) + timedelta(minutes=request.ttl_minutes)

            job.api_url = api_url
            job.sandbox_url = host
            job.expires_at = expires_at
            job.status = SandboxJobStatus.RUNNING

            logger.info(
                "demo_sandbox_ready",
                job_id=job.job_id,
                api_url=api_url,
                domain=request.domain,
                seeds=len(seeds_data),
                expires_at=expires_at.isoformat(),
            )

            return DemoSandboxResponse(
                job=job,
                api_url=api_url,
                docs_url=docs_url,
                expires_at=expires_at,
                preloaded_seeds=len(seeds_data),
                domain=request.domain,
            )

        except Exception as exc:
            job.status = SandboxJobStatus.FAILED
            job.error = str(exc)

            logger.error("demo_sandbox_failed", job_id=job.job_id, error=str(exc))

            if sandbox is not None:
                with contextlib.suppress(Exception):
                    await sandbox.kill()

            msg = f"Failed to create demo sandbox: {exc}"
            raise SandboxError(msg) from exc


def _build_demo_api_script(domain: str, seeds: list[dict[str, object]]) -> str:
    """Build a comprehensive FastAPI script for the demo sandbox.

    This creates an API with pre-loaded seeds that covers all endpoints
    the UNCASE dashboard calls, with correct response formats matching
    the TypeScript interfaces in frontend/src/types/api.ts.
    """
    return f'''"""UNCASE Demo API — {domain}

Comprehensive demo API that mirrors the full UNCASE backend response
formats so the dashboard works end-to-end without fallback.
"""
import json
import random
import uuid
import uvicorn
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="UNCASE Demo — {domain}",
    description="Live demo sandbox for {domain} domain",
    version="demo",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NOW = datetime.now(timezone.utc).isoformat()
DEMO_SEEDS = json.loads("""{json.dumps(seeds, ensure_ascii=False)}""")
GENERATED_CONVERSATIONS: list[dict] = []
EVALUATION_REPORTS: list[dict] = []


# ─── Request models ───

class GenerateRequest(BaseModel):
    seed_id: str | None = None
    count: int = Field(default=1, ge=1, le=5)


class SeedCreate(BaseModel):
    dominio: str = "{domain}"
    idioma: str = "es"
    roles: list[str] = ["agent", "user"]
    descripcion_roles: dict[str, str] = {{}}
    objetivo: str = ""
    tono: str = "profesional"
    pasos_turnos: dict = {{}}
    parametros_factuales: dict = {{}}


# ─── Health ───

@app.get("/health")
async def health():
    return {{"status": "ok", "domain": "{domain}", "mode": "demo"}}

@app.get("/health/db")
async def health_db():
    return {{"status": "ok", "version": "demo", "database": "connected"}}


# ─── Seeds (SeedListResponse format) ───

@app.get("/api/v1/seeds")
async def list_seeds(page: int = 1, page_size: int = 25, domain: str | None = None):
    filtered = [s for s in DEMO_SEEDS if not domain or s.get("dominio") == domain]
    start = (page - 1) * page_size
    items = filtered[start:start + page_size]
    # Return both "items" (SeedListResponse) and "seeds" (bootstrap compat)
    return {{
        "items": items,
        "seeds": items,
        "total": len(filtered),
        "page": page,
        "page_size": page_size,
    }}

@app.get("/api/v1/seeds/{{seed_id}}")
async def get_seed(seed_id: str):
    for seed in DEMO_SEEDS:
        if seed.get("seed_id") == seed_id:
            return seed
    raise HTTPException(status_code=404, detail="Seed not found")

@app.post("/api/v1/seeds")
async def create_seed(request: SeedCreate):
    seed = request.model_dump()
    seed["seed_id"] = f"demo-{{uuid.uuid4().hex[:8]}}"
    seed["version"] = "1.0"
    seed["etiquetas"] = []
    seed["privacidad"] = {{
        "pii_eliminado": True,
        "metodo_anonimizacion": "presidio",
        "nivel_confianza": 0.85,
        "campos_sensibles_detectados": [],
    }}
    seed["metricas_calidad"] = {{
        "rouge_l_min": 0.65,
        "fidelidad_min": 0.90,
        "diversidad_lexica_min": 0.55,
        "coherencia_dialogica_min": 0.85,
    }}
    seed["organization_id"] = None
    seed["created_at"] = NOW
    seed["updated_at"] = NOW
    DEMO_SEEDS.append(seed)
    return seed

@app.delete("/api/v1/seeds/{{seed_id}}")
async def delete_seed(seed_id: str):
    for i, seed in enumerate(DEMO_SEEDS):
        if seed.get("seed_id") == seed_id:
            DEMO_SEEDS.pop(i)
            return None
    raise HTTPException(status_code=404, detail="Seed not found")

@app.post("/api/v1/seeds/{{seed_id}}/rate")
async def rate_seed(seed_id: str):
    for seed in DEMO_SEEDS:
        if seed.get("seed_id") == seed_id:
            seed["rating"] = 4.5
            seed["rating_count"] = seed.get("rating_count", 0) + 1
            return seed
    raise HTTPException(status_code=404, detail="Seed not found")


# ─── Generation ───

@app.post("/api/v1/generate")
async def generate(request: GenerateRequest):
    seed = None
    if request.seed_id:
        for s in DEMO_SEEDS:
            if s.get("seed_id") == request.seed_id:
                seed = s
                break
    if not seed:
        seed = DEMO_SEEDS[0] if DEMO_SEEDS else None
    if not seed:
        raise HTTPException(status_code=400, detail="No seeds available")

    roles = seed.get("roles", ["agent", "user"])
    flujo = seed.get("pasos_turnos", {{}}).get("flujo_esperado", ["Start", "End"])
    conversations = []
    for _ in range(request.count):
        turns = []
        n_turns = random.randint(
            seed.get("pasos_turnos", {{}}).get("turnos_min", 4),
            seed.get("pasos_turnos", {{}}).get("turnos_max", 8),
        )
        for t in range(n_turns):
            role = roles[t % len(roles)]
            step = flujo[min(t, len(flujo) - 1)] if flujo else "conversation"
            turns.append({{
                "turno": t + 1,
                "rol": role,
                "contenido": f"[Demo] {{step}} — turn {{t + 1}} by {{role}}",
                "herramientas_usadas": [],
                "metadata": {{}},
            }})
        conv = {{
            "conversation_id": uuid.uuid4().hex[:16],
            "seed_id": seed.get("seed_id", "unknown"),
            "dominio": seed.get("dominio", "{domain}"),
            "idioma": seed.get("idioma", "es"),
            "turnos": turns,
            "es_sintetica": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {{"mode": "demo"}},
        }}
        conversations.append(conv)
        GENERATED_CONVERSATIONS.append(conv)
    return {{
        "conversations": conversations,
        "reports": None,
        "generation_summary": {{
            "total_generated": len(conversations),
            "total_passed": None,
            "avg_composite_score": None,
            "model_used": "demo-mock",
            "temperature": 0.7,
            "duration_seconds": 0.1,
        }},
    }}


# ─── Conversations ───

@app.get("/api/v1/conversations")
async def list_conversations():
    return {{"items": GENERATED_CONVERSATIONS, "total": len(GENERATED_CONVERSATIONS)}}


# ─── Tools (ToolDefinition[] / CustomToolListResponse) ───

@app.get("/api/v1/tools")
async def list_tools():
    tools = []
    for seed in DEMO_SEEDS:
        herramientas = seed.get("parametros_factuales", {{}}).get("herramientas", [])
        for tool_name in herramientas:
            if not any(t["name"] == tool_name for t in tools):
                tools.append({{
                    "name": tool_name,
                    "description": f"Demo tool: {{tool_name}}",
                    "input_schema": {{"type": "object", "properties": {{}}}},
                    "output_schema": {{}},
                    "domains": [seed.get("dominio", "{domain}")],
                    "category": "domain",
                    "requires_auth": False,
                    "execution_mode": "simulated",
                    "version": "1.0",
                    "metadata": {{}},
                }})
    return tools

@app.get("/api/v1/tools/{{tool_name}}")
async def get_tool(tool_name: str):
    for seed in DEMO_SEEDS:
        herramientas = seed.get("parametros_factuales", {{}}).get("herramientas", [])
        if tool_name in herramientas:
            return {{
                "name": tool_name,
                "description": f"Demo tool: {{tool_name}}",
                "input_schema": {{"type": "object", "properties": {{}}}},
                "output_schema": {{}},
                "domains": [seed.get("dominio", "{domain}")],
                "category": "domain",
                "requires_auth": False,
                "execution_mode": "simulated",
                "version": "1.0",
                "metadata": {{}},
            }}
    raise HTTPException(status_code=404, detail="Tool not found")


# ─── Templates (TemplateInfo[]) ───

@app.get("/api/v1/templates")
async def list_templates():
    return [
        {{
            "name": "chatml", "display_name": "ChatML",
            "supports_tool_calls": True,
            "special_tokens": ["<|im_start|>", "<|im_end|>"],
        }},
        {{
            "name": "llama3", "display_name": "Llama 3",
            "supports_tool_calls": True,
            "special_tokens": ["<|begin_of_text|>", "<|eot_id|>"],
        }},
        {{
            "name": "mistral", "display_name": "Mistral",
            "supports_tool_calls": False,
            "special_tokens": ["[INST]", "[/INST]"],
        }},
    ]

@app.get("/api/v1/templates/config")
async def get_template_config():
    return {{
        "id": "demo-config",
        "organization_id": None,
        "default_template": "chatml",
        "default_tool_call_mode": "none",
        "default_system_prompt": None,
        "preferred_templates": ["chatml", "llama3"],
        "export_format": "jsonl",
        "created_at": NOW,
        "updated_at": NOW,
    }}


# ─── Evaluations (EvaluationReportListResponse) ───

@app.get("/api/v1/evaluations/reports")
async def list_evaluations(page: int = 1, page_size: int = 100):
    start = (page - 1) * page_size
    items = EVALUATION_REPORTS[start:start + page_size]
    return {{"items": items, "total": len(EVALUATION_REPORTS), "page": page, "page_size": page_size}}

@app.get("/api/v1/evaluations/thresholds")
async def get_thresholds():
    return {{
        "rouge_l_min": 0.65,
        "fidelidad_min": 0.90,
        "diversidad_lexica_min": 0.55,
        "coherencia_dialogica_min": 0.85,
        "tool_call_validity_min": 0.90,
        "privacy_score_max": 0.0,
        "memorizacion_max": 0.01,
        "formula": "Q = min(ROUGE, Fidelity, TTR, Coherence) if privacy=0 AND memo<0.01 else 0",
    }}


# ─── Jobs (JobResponse[]) ───

@app.get("/api/v1/jobs")
async def list_jobs():
    return []

@app.get("/api/v1/pipeline/jobs")
async def list_pipeline_jobs():
    return {{"items": [], "total": 0}}


# ─── Providers (ProviderListResponse) ───

@app.get("/api/v1/providers")
async def list_providers():
    return {{
        "items": [{{
            "id": "demo-provider-1",
            "name": "Demo LLM (mock)",
            "provider_type": "custom",
            "api_base": None,
            "has_api_key": False,
            "default_model": "demo-mock",
            "max_tokens": 4096,
            "temperature_default": 0.7,
            "is_active": True,
            "is_default": True,
            "organization_id": None,
            "created_at": NOW,
            "updated_at": NOW,
        }}],
        "total": 1,
    }}


# ─── Costs (CostSummary / DailyCost[]) ───

@app.get("/api/v1/costs/summary")
async def costs_summary(period_days: int = 30):
    return {{
        "organization_id": "demo",
        "period_days": period_days,
        "total_cost_usd": 0.0,
        "total_tokens": 0,
        "event_count": 0,
        "cost_by_provider": {{}},
        "cost_by_event_type": {{}},
    }}

@app.get("/api/v1/costs/daily")
async def daily_costs(days: int = 30):
    return []


# ─── Plugins (PluginManifest[] / InstalledPluginListResponse) ───

@app.get("/api/v1/plugins/catalog")
async def plugin_catalog():
    return []

@app.get("/api/v1/plugins/installed")
async def installed_plugins():
    return {{"items": [], "total": 0}}

@app.get("/api/v1/plugins")
async def list_plugins():
    return []


# ─── Knowledge Base ───

@app.get("/api/v1/knowledge/documents")
async def list_knowledge():
    return {{"items": [], "total": 0, "page": 1, "page_size": 25}}


# ─── Connectors ───

@app.get("/api/v1/connectors")
async def list_connectors():
    return []


# ─── Audit Logs ───

@app.get("/api/v1/audit/logs")
async def list_audit_logs(page: int = 1, page_size: int = 50):
    return {{"items": [], "total": 0, "page": page, "page_size": page_size}}


# ─── Blockchain ───

@app.get("/api/v1/blockchain/stats")
async def blockchain_stats():
    return {{
        "total_hashed": 0,
        "total_batched": 0,
        "total_unbatched": 0,
        "total_batches": 0,
        "total_anchored": 0,
        "total_pending_anchor": 0,
        "total_failed_anchor": 0,
    }}

@app.get("/api/v1/blockchain/batches")
async def blockchain_batches():
    return []

@app.get("/api/v1/blockchain/verify/{{report_id}}")
async def blockchain_verify(report_id: str):
    raise HTTPException(status_code=404, detail="Report not found in blockchain ledger")


# ─── Organizations ───

@app.get("/api/v1/organizations/{{org_id}}")
async def get_organization(org_id: str):
    return {{
        "id": org_id,
        "name": "Demo Organization",
        "slug": "demo-org",
        "description": "Demo sandbox organization",
        "is_active": True,
        "created_at": NOW,
        "updated_at": NOW,
    }}


# ─── Webhooks ───

@app.get("/api/v1/webhooks")
async def list_webhooks():
    return {{"items": [], "total": 0, "page": 1, "page_size": 25}}


# ─── Scenario Packs ───

@app.get("/api/v1/scenarios/packs")
async def list_scenario_packs():
    return {{"packs": [], "total": 0}}


# ─── Usage ───

@app.get("/api/v1/usage")
async def usage_summary():
    return {{"total_requests": 0, "period": "current"}}


# ─── Sandbox Info ───

@app.get("/api/v1/sandbox/info")
async def sandbox_info():
    return {{
        "mode": "demo",
        "domain": "{domain}",
        "total_seeds": len(DEMO_SEEDS),
        "features": ["seeds", "generation", "evaluation", "blockchain", "plugins", "knowledge"],
        "note": "This is a short-lived demo sandbox. Data will be lost when it expires.",
    }}

@app.get("/api/v1/sandbox/status")
async def sandbox_status():
    return {{"enabled": True, "max_parallel": 5, "template_id": "demo"}}


# ─── Catch-all: return empty JSON for any unhandled /api/v1/ endpoint ───

@app.api_route("/api/v1/{{path:path}}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def catch_all(request: Request, path: str):
    """Return empty data for any unrecognized endpoint to prevent 404 errors."""
    return JSONResponse(content={{"items": [], "total": 0, "detail": "demo endpoint not implemented"}})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

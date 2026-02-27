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
        # response.api_url -> "https://<sandbox>.e2b.dev:8000"
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

            # Start the bootstrap in the background so we don't block
            # on the E2B SDK's HTTP request timeout during pip install.
            logger.info("demo_sandbox_installing", job_id=job.job_id)
            await sandbox.commands.run(
                "chmod +x /home/user/bootstrap.sh && nohup /home/user/bootstrap.sh &",
                timeout=10,
            )

            # Wait for the API to be ready (poll health endpoint)
            import asyncio

            api_ready = False
            for _ in range(30):
                check = await sandbox.commands.run(
                    "curl -sf http://localhost:8000/health || true",
                    timeout=5,
                )
                if check.stdout and "ok" in check.stdout:
                    api_ready = True
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
                msg = f"Demo API did not start within 90s. Log: {log_tail[:300]}"
                raise SandboxError(msg)

            # Build URLs
            sandbox_host = getattr(sandbox, "get_host", None)
            host = sandbox_host(8000) if callable(sandbox_host) else f"https://{sandbox.sandbox_id}.e2b.dev:8000"

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
    """Build a minimal FastAPI script for the demo sandbox.

    This creates a lightweight API with pre-loaded seeds that
    demonstrates the UNCASE generation flow.
    """
    return f'''"""UNCASE Demo API — {domain}"""
import json
import random
import uuid
import uvicorn
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

DEMO_SEEDS = json.loads("""{json.dumps(seeds, ensure_ascii=False)}""")


class GenerateRequest(BaseModel):
    seed_id: str | None = None
    count: int = Field(default=1, ge=1, le=5)


@app.get("/health")
async def health():
    return {{"status": "ok", "domain": "{domain}", "mode": "demo"}}

@app.get("/api/v1/seeds")
async def list_seeds():
    return {{"seeds": DEMO_SEEDS, "total": len(DEMO_SEEDS)}}

@app.get("/api/v1/seeds/{{seed_id}}")
async def get_seed(seed_id: str):
    for seed in DEMO_SEEDS:
        if seed.get("seed_id") == seed_id:
            return seed
    raise HTTPException(status_code=404, detail="Seed not found")

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
        conversations.append({{
            "conversation_id": uuid.uuid4().hex[:16],
            "seed_id": seed.get("seed_id", "unknown"),
            "dominio": seed.get("dominio", "{domain}"),
            "idioma": seed.get("idioma", "es"),
            "turnos": turns,
            "es_sintetica": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {{"mode": "demo"}},
        }})
    return {{
        "conversations": conversations,
        "generation_summary": {{
            "total_generated": len(conversations),
            "model_used": "demo-mock",
            "temperature": 0.7,
            "duration_seconds": 0.1,
        }},
    }}

@app.get("/api/v1/sandbox/info")
async def sandbox_info():
    return {{
        "mode": "demo",
        "domain": "{domain}",
        "total_seeds": len(DEMO_SEEDS),
        "features": ["seeds", "generation", "evaluation"],
        "note": "This is a short-lived demo sandbox. Data will be lost when it expires.",
    }}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

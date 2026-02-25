#!/usr/bin/env python3
"""Generate the UNCASE Business Proposal PDF in Spanish.

Usage:
    /tmp/pdfenv/bin/python scripts/generate_business_proposal.py
"""

from __future__ import annotations

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Color Palette — Deep teal / navy professional
# ---------------------------------------------------------------------------
PRIMARY = colors.HexColor("#0F2B3C")       # Dark navy for cover & headings
ACCENT = colors.HexColor("#0D7377")        # Deep teal — section titles, KPIs
ACCENT_DARK = colors.HexColor("#094B4E")   # Darker teal for hover/emphasis
ACCENT_LIGHT = colors.HexColor("#E0F2F1")  # Very light teal tint
DARK_TEXT = colors.HexColor("#1C1C1C")     # Near-black body text
MID_TEXT = colors.HexColor("#3D4F5F")      # Muted slate for subtitles
LIGHT_TEXT = colors.HexColor("#6B7D8D")    # Grey-blue for captions/footer
WHITE = colors.white
TABLE_HEADER_BG = colors.HexColor("#0F2B3C")  # Dark navy header
TABLE_ALT_ROW = colors.HexColor("#F5FAFA")    # Subtle teal-tinted row
TABLE_BORDER = colors.HexColor("#D1DBE3")      # Soft grey-blue borders
GOLD = colors.HexColor("#B8860B")              # Dark gold for callouts

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs",
    "UNCASE-Propuesta-de-Negocio-2026.pdf",
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
_base = getSampleStyleSheet()


def _style(name: str, **kw) -> ParagraphStyle:
    return ParagraphStyle(name, **kw)


STYLES = {
    "cover_title": _style(
        "cover_title",
        fontName="Helvetica-Bold",
        fontSize=36,
        leading=44,
        textColor=WHITE,
        alignment=TA_CENTER,
    ),
    "cover_subtitle": _style(
        "cover_subtitle",
        fontName="Helvetica",
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#8CB8B8"),
        alignment=TA_CENTER,
    ),
    "cover_date": _style(
        "cover_date",
        fontName="Helvetica",
        fontSize=11,
        textColor=colors.HexColor("#7A9E9E"),
        alignment=TA_CENTER,
    ),
    "section_title": _style(
        "section_title",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=4,
        spaceBefore=20,
    ),
    "subsection": _style(
        "subsection",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=ACCENT_DARK,
        spaceAfter=6,
        spaceBefore=14,
    ),
    "subsubsection": _style(
        "subsubsection",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=MID_TEXT,
        spaceAfter=4,
        spaceBefore=8,
    ),
    "body": _style(
        "body",
        fontName="Helvetica",
        fontSize=10,
        leading=14.5,
        textColor=DARK_TEXT,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    ),
    "body_bold": _style(
        "body_bold",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14.5,
        textColor=DARK_TEXT,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    ),
    "bullet": _style(
        "bullet",
        fontName="Helvetica",
        fontSize=10,
        leading=14.5,
        textColor=DARK_TEXT,
        leftIndent=20,
        bulletIndent=8,
        spaceAfter=4,
    ),
    "small": _style(
        "small",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=LIGHT_TEXT,
    ),
    "footer": _style(
        "footer",
        fontName="Helvetica",
        fontSize=8,
        textColor=LIGHT_TEXT,
        alignment=TA_CENTER,
    ),
    "toc_entry": _style(
        "toc_entry",
        fontName="Helvetica",
        fontSize=11,
        leading=22,
        textColor=DARK_TEXT,
        leftIndent=12,
    ),
    "toc_title": _style(
        "toc_title",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=18,
        alignment=TA_CENTER,
    ),
    "callout": _style(
        "callout",
        fontName="Helvetica-Oblique",
        fontSize=10.5,
        leading=15,
        textColor=GOLD,
        leftIndent=24,
        rightIndent=24,
        spaceAfter=12,
        spaceBefore=12,
        alignment=TA_CENTER,
    ),
    "table_header": _style(
        "table_header",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=WHITE,
    ),
    "table_cell": _style(
        "table_cell",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=DARK_TEXT,
    ),
    "table_cell_bold": _style(
        "table_cell_bold",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=DARK_TEXT,
    ),
    "kpi_number": _style(
        "kpi_number",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=32,
        textColor=ACCENT,
        alignment=TA_CENTER,
    ),
    "kpi_label": _style(
        "kpi_label",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=MID_TEXT,
        alignment=TA_CENTER,
    ),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def S(name: str) -> ParagraphStyle:
    return STYLES[name]


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S(style))


def Bullet(text: str) -> Paragraph:
    return Paragraph(f"\u2022  {text}", S("bullet"))


def HR() -> HRFlowable:
    return HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=10, spaceBefore=2)


def make_table(headers: list[str], rows: list[list[str]], col_widths: list[float] | None = None) -> Table:
    """Create a styled table with header row."""
    header_cells = [Paragraph(h, S("table_header")) for h in headers]
    data_rows = []
    for row in rows:
        data_rows.append([Paragraph(cell, S("table_cell")) for cell in row])
    all_data = [header_cells] + data_rows

    tbl = Table(all_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, TABLE_ALT_ROW]),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def kpi_box(value: str, label: str) -> Table:
    """Small KPI card."""
    data = [
        [Paragraph(value, S("kpi_number"))],
        [Paragraph(label, S("kpi_label"))],
    ]
    t = Table(data, colWidths=[3.2 * cm])
    t.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 1.2, ACCENT),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FCFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    return t


def section_number(num: int, title: str) -> Paragraph:
    return Paragraph(f"{num}. {title}", S("section_title"))


# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------

def _cover_bg(canvas, doc):
    """Draw formal cover background with navy + teal accent."""
    canvas.saveState()
    # Main dark navy background
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, 0, letter[0], letter[1], fill=1)
    # Thin teal accent line at top
    canvas.setFillColor(ACCENT)
    canvas.rect(0, letter[1] - 4, letter[0], 4, fill=1)
    # Subtle darker band at bottom
    canvas.setFillColor(colors.HexColor("#091E2A"))
    canvas.rect(0, 0, letter[0], 90, fill=1)
    # Thin teal line separating bottom band
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(0.5)
    canvas.line(inch * 1.5, 90, letter[0] - inch * 1.5, 90)
    canvas.restoreState()


def _normal_header_footer(canvas, doc):
    """Header/footer for normal pages."""
    canvas.saveState()
    # Top line — thin teal
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(1.5)
    canvas.line(inch, letter[1] - 0.6 * inch, letter[0] - inch, letter[1] - 0.6 * inch)
    # Header text
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(MID_TEXT)
    canvas.drawString(inch, letter[1] - 0.5 * inch, "UNCASE  \u2014  Propuesta de Negocio")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(LIGHT_TEXT)
    canvas.drawRightString(letter[0] - inch, letter[1] - 0.5 * inch, "Febrero 2026  \u2014  Confidencial")
    # Footer — thin line + page number
    canvas.setStrokeColor(TABLE_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(inch, 0.75 * inch, letter[0] - inch, 0.75 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(LIGHT_TEXT)
    canvas.drawCentredString(letter[0] / 2, 0.5 * inch, f"\u2014  {doc.page}  \u2014")
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Main document builder
# ---------------------------------------------------------------------------

def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    doc = BaseDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        title="UNCASE - Propuesta de Negocio",
        author="UNCASE AI",
    )

    frame_cover = Frame(
        inch,
        inch,
        letter[0] - 2 * inch,
        letter[1] - 2 * inch,
        id="cover",
    )
    frame_normal = Frame(
        inch,
        0.9 * inch,
        letter[0] - 2 * inch,
        letter[1] - 1.8 * inch,
        id="normal",
    )

    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=frame_cover, onPage=_cover_bg),
        PageTemplate(id="Normal", frames=frame_normal, onPage=_normal_header_footer),
    ])

    story = []

    # ==================== COVER ====================
    story.append(Spacer(1, 2.5 * inch))
    story.append(P("UNCASE", "cover_title"))
    story.append(Spacer(1, 0.2 * inch))
    story.append(P("Propuesta de Negocio", "cover_title"))
    story.append(Spacer(1, 0.4 * inch))
    story.append(
        P(
            "Infraestructura de IA para Datos Sintéticos Conversacionales<br/>"
            "en Industrias Reguladas",
            "cover_subtitle",
        )
    )
    story.append(Spacer(1, 0.6 * inch))
    story.append(P("Febrero 2026  |  Versión 1.0  |  Confidencial", "cover_date"))
    story.append(Spacer(1, 1.2 * inch))
    story.append(
        P(
            "Preparado por: Mariano Morales<br/>Fundador &amp; CTO",
            "cover_date",
        )
    )
    story.append(NextPageTemplate("Normal"))
    story.append(PageBreak())

    # ==================== TABLE OF CONTENTS ====================
    story.append(P("Índice", "toc_title"))
    story.append(Spacer(1, 0.2 * inch))
    toc_items = [
        ("1", "Resumen Ejecutivo"),
        ("2", "El Problema"),
        ("3", "La Solución: UNCASE"),
        ("4", "Producto y Tecnología"),
        ("5", "Modelo de Negocio y Monetización"),
        ("6", "Mercado y Demanda"),
        ("7", "Competencia y Diferenciación"),
        ("8", "Mercados Objetivo y Expansión Geográfica"),
        ("9", "Regulaciones y Certificaciones"),
        ("10", "Equipo y Estructura Organizacional"),
        ("11", "Infraestructura Técnica"),
        ("12", "Plan de Marketing"),
        ("13", "Proyección Financiera y Camino al ROI"),
        ("14", "Plan de Ejecución"),
        ("15", "Riesgos y Mitigación"),
        ("16", "Solicitud de Inversión"),
    ]
    for num, title in toc_items:
        story.append(P(f"<b>{num}.</b>  {title}", "toc_entry"))
    story.append(PageBreak())

    # ==================== 1. RESUMEN EJECUTIVO ====================
    story.append(section_number(1, "Resumen Ejecutivo"))
    story.append(HR())

    story.append(
        P(
            "<b>UNCASE</b> (Unbiased Neutral Convention for Agnostic Seed Engineering) es un framework "
            "open-source que permite a organizaciones en industrias reguladas (salud, finanzas, legal, "
            "manufactura) generar datos conversacionales sintéticos de alta calidad para fine-tuning de "
            "modelos de lenguaje (LLMs), <b>sin exponer datos reales ni información personal</b>.",
        )
    )
    story.append(
        P(
            "El producto resuelve un problema crítico: las empresas necesitan LLMs especializados, "
            "pero no pueden usar sus datos reales para entrenarlos por restricciones regulatorias "
            "(HIPAA, GDPR, Ley 1581). UNCASE ofrece un pipeline completo de 5 capas — desde la "
            "ingestion anonimizada hasta el adaptador LoRA entrenado — con <b>cero tolerancia a PII</b> "
            "y trazabilidad completa.",
        )
    )

    # KPI row
    kpis = Table(
        [[
            kpi_box("75+", "Endpoints API"),
            kpi_box("970", "Tests"),
            kpi_box("5", "Capas Pipeline"),
            kpi_box("6", "Industrias"),
            kpi_box("0%", "PII en Output"),
        ]],
        colWidths=[3.6 * cm] * 5,
    )
    kpis.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(kpis)
    story.append(Spacer(1, 0.15 * inch))

    story.append(
        P(
            "<i>\"El mercado global de datos sintéticos alcanza USD 584M en 2025, con un CAGR proyectado "
            "de 38.2% hasta 2034 (USD 5,515M). Gartner predice que el 75% de las empresas usará IA "
            "generativa para crear datos sintéticos de clientes en 2026.\"</i>",
            "callout",
        )
    )

    story.append(PageBreak())

    # ==================== 2. EL PROBLEMA ====================
    story.append(section_number(2, "El Problema"))
    story.append(HR())

    story.append(P("<b>Las organizaciones reguladas enfrentan un dilema imposible:</b>"))
    story.append(Spacer(1, 4))

    story.append(Bullet(
        "<b>Necesitan LLMs especializados</b> — Un chatbot genérico no puede asesorar sobre créditos "
        "hipotecarios, diagnósticos médicos o procedimientos legales con la precisión que requiere la industria."
    ))
    story.append(Bullet(
        "<b>Fine-tuning requiere datos reales</b> — Conversaciones de call centers, historiales clínicos, "
        "expedientes legales. Datos que contienen PII, PHI, datos financieros y privilegio legal."
    ))
    story.append(Bullet(
        "<b>Los datos no pueden salir de la organización</b> — HIPAA (multas hasta USD 1.5M/violación), "
        "GDPR (multas hasta 4% de facturación global), Ley 1581 en Colombia, LGPD en Brasil, LFPDPPP en México."
    ))
    story.append(Bullet(
        "<b>La anonimización simple destruye valor</b> — Enmascarar nombres y teléfonos con [REDACTED] "
        "elimina los patrones de dominio específico que hacen valioso el fine-tuning."
    ))
    story.append(Bullet(
        "<b>No existe un pipeline unificado</b> — Las empresas ensamblan 6-10 herramientas diferentes "
        "(parsers, anonimizadores, generadores, evaluadores, scripts de entrenamiento) con código ad-hoc."
    ))

    story.append(Spacer(1, 10))
    story.append(
        P(
            "<b>Resultado:</b> La mayoría de organizaciones renuncian a la especialización de LLMs, "
            "o arriesgan violaciones de compliance enviando datos reales a APIs en la nube.",
        )
    )

    story.append(Spacer(1, 8))
    story.append(P("Impacto económico del problema:", "subsection"))

    problem_data = [
        ["Sector", "Costo de Compliance de Datos", "Costo de NO cumplir"],
        ["Salud (HIPAA)", "USD 1.27M promedio anual", "USD 1.5M por violación (max)"],
        ["Finanzas (GDPR)", "EUR 1.3M promedio anual", "4% facturación global"],
        ["Legal", "USD 800K promedio anual", "Demandas + pérdida de licencia"],
        ["Manufactura", "USD 500K promedio anual", "Multas regulatorias + retirada"],
    ]
    story.append(
        make_table(
            problem_data[0],
            problem_data[1:],
            col_widths=[2.5 * cm, 5.5 * cm, 5.5 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 3. LA SOLUCION ====================
    story.append(section_number(3, "La Solución: UNCASE"))
    story.append(HR())

    story.append(
        P(
            "UNCASE transforma conversaciones reales en datos sintéticos certificados a través de un "
            "pipeline de 5 capas donde <b>ningún dato real sale de la infraestructura del cliente</b>."
        )
    )
    story.append(Spacer(1, 6))

    pipeline_data = [
        ["Capa", "Nombre", "Función", "Tecnología"],
        [
            "0", "Seed Engine",
            "Ingestion de conversaciones reales, eliminación de PII, extracción de semillas estructuradas",
            "Presidio + SpaCy NER, 9 patrones regex"
        ],
        [
            "1", "Parser/Validador",
            "Parsing multi-formato y validación contra SeedSchema v1",
            "CSV, JSONL, WhatsApp, OpenAI, ShareGPT"
        ],
        [
            "2", "Evaluador",
            "6 métricas de calidad con umbrales obligatorios",
            "ROUGE-L, Fidelidad, TTR, Coherencia, Privacidad, Memorización"
        ],
        [
            "3", "Generador",
            "Generación sintética multi-proveedor con herramientas",
            "LiteLLM (Claude, GPT-4, Gemini, Ollama, vLLM)"
        ],
        [
            "4", "Pipeline LoRA",
            "Fine-tuning con garantías de privacidad diferencial",
            "HuggingFace transformers + peft + DP-SGD"
        ],
    ]
    story.append(
        make_table(
            pipeline_data[0],
            pipeline_data[1:],
            col_widths=[1.1 * cm, 2.5 * cm, 5.2 * cm, 4.7 * cm],
        )
    )
    story.append(Spacer(1, 10))

    story.append(P("Paradigma de Semillas (Seed Schema)", "subsection"))
    story.append(
        P(
            "A diferencia de generadores sintéticos convencionales que parten de prompts, UNCASE utiliza "
            "un <b>Seed Schema</b> — un modelo estructurado que captura el ADN de una conversación "
            "(dominio, roles, tono, pasos, parámetros factuales) sin contener ningún dato real. Las "
            "semillas son <b>trazables</b> (cada conversación sintética mapea a su semilla), "
            "<b>reproducibles</b> (misma semilla + misma config = output consistente) y "
            "<b>auditables</b> (reguladores pueden inspeccionar semillas sin ver datos reales)."
        )
    )

    story.append(Spacer(1, 8))
    story.append(P("Propuesta de valor clave:", "subsection"))
    story.append(Bullet("<b>Un solo pipeline</b> — De conversación real a modelo entrenado en un flujo."))
    story.append(Bullet("<b>Cero PII</b> — Tolerancia 0 verificada por evaluador automático en cada etapa."))
    story.append(Bullet("<b>Multi-proveedor</b> — Cualquier LLM via gateway unificado con intercepción de privacidad."))
    story.append(Bullet("<b>Multi-industria</b> — 6 dominios con herramientas y templates especializados."))
    story.append(Bullet("<b>Open source</b> — Transparencia total, auditabilidad de código, comunidad."))
    story.append(Bullet("<b>Trazabilidad completa</b> — Audit trail desde dato original hasta modelo final."))
    story.append(PageBreak())

    # ==================== 4. PRODUCTO Y TECNOLOGIA ====================
    story.append(section_number(4, "Producto y Tecnología"))
    story.append(HR())

    story.append(P("Estado actual (febrero 2026):", "subsection"))
    story.append(Spacer(1, 4))

    tech_data = [
        ["Componente", "Detalle", "Estado"],
        ["API REST", "75+ endpoints, 22 routers, versionado /api/v1/", "Producción"],
        ["Dashboard", "28+ páginas, 137 componentes React, tema claro/oscuro", "Producción"],
        ["Pipeline 5 capas", "Seed Engine, Parser, Evaluator, Generator, LoRA Pipeline", "Completo"],
        ["LLM Gateway", "Proxy universal con intercepción de privacidad (audit/warn/block)", "Producción"],
        ["Conectores", "WhatsApp, Webhook, CSV, JSONL con anonimización automática", "Producción"],
        ["Plugins", "6 plugins oficiales, 30 herramientas de dominio", "Producción"],
        ["Knowledge Base", "Carga de documentos con chunking y búsqueda full-text", "Producción"],
        ["Proveedores LLM", "Anthropic, OpenAI, Google, Groq, Ollama, vLLM, Custom", "Producción"],
        ["Audit Logging", "Trail inmutable para compliance con retención configurable", "Producción"],
        ["Cost Tracking", "Seguimiento de costos LLM por org, job y proveedor", "Producción"],
        ["Observabilidad", "Prometheus + Grafana con dashboards pre-construidos", "Producción"],
        ["E2B Sandboxes", "Ejecución paralela en MicroVMs, 20 concurrentes", "Producción"],
        ["Tests", "970+ tests, 73% cobertura, suite de privacidad obligatoria", "CI/CD"],
        ["Distribución", "Docker Compose, pip install, Git + uv", "Disponible"],
    ]
    story.append(
        make_table(
            tech_data[0],
            tech_data[1:],
            col_widths=[3 * cm, 7 * cm, 2.5 * cm],
        )
    )
    story.append(Spacer(1, 10))

    story.append(P("Stack tecnológico:", "subsection"))

    stack_data = [
        ["Capa", "Tecnologías"],
        ["Backend", "Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy async, PostgreSQL, structlog, Typer CLI"],
        ["ML/AI", "LiteLLM, HuggingFace transformers, peft, trl, MLflow, Opacus (DP-SGD)"],
        ["Privacidad", "Microsoft Presidio, SpaCy NER, Fernet encryption, argon2 hashing"],
        ["Frontend", "Next.js 16, React 19, TypeScript 5.9, Tailwind CSS 4, shadcn/ui, Recharts"],
        ["Infra", "Docker Compose (multi-profile), Prometheus, Grafana, E2B sandboxes"],
        ["CI/CD", "GitHub Actions, Ruff, mypy strict, pytest, Alembic migrations"],
    ]
    story.append(
        make_table(
            stack_data[0],
            stack_data[1:],
            col_widths=[2.5 * cm, 11 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 5. MODELO DE NEGOCIO ====================
    story.append(section_number(5, "Modelo de Negocio y Monetización"))
    story.append(HR())

    story.append(P("Estrategia open-core: código abierto + capas enterprise de pago", "subsection"))
    story.append(Spacer(1, 4))

    story.append(
        P(
            "El core del framework es <b>Apache 2.0</b> (completamente open-source). Esto no es un "
            "sacrificio sino una ventaja competitiva deliberada:"
        )
    )
    story.append(Bullet(
        "<b>Confianza regulatoria</b> — Los departamentos de compliance de salud, finanzas y legal "
        "exigen poder auditar el código que maneja sus datos. Código abierto = auditabilidad total."
    ))
    story.append(Bullet(
        "<b>Adopción bottom-up</b> — Los ingenieros de ML descubren la herramienta, la prueban gratis, "
        "y escalan a plan enterprise cuando necesitan soporte, SSO, SLAs. Modelo validado por "
        "Hugging Face (USD 4.5B valuación), LangChain (USD 200M+ funding), Weights & Biases."
    ))
    story.append(Bullet(
        "<b>Efecto comunidad</b> — Contribuciones de terceros mejoran el producto sin costo de desarrollo. "
        "Plugins de dominio y conectores creados por la comunidad expanden el ecosistema."
    ))
    story.append(Bullet(
        "<b>Reducción de CAC</b> — Repositorio GitHub como canal de adquisición. Developers que usan "
        "el framework gratuito se convierten en champions internos para la venta enterprise."
    ))

    story.append(Spacer(1, 8))
    story.append(P("Tiers de monetización:", "subsection"))

    tiers_data = [
        ["Tier", "Precio", "Incluye"],
        [
            "Community (OSS)",
            "Gratis",
            "Framework completo, 5 capas, CLI, API, 6 dominios, 30 herramientas, "
            "soporte comunidad (GitHub Issues)"
        ],
        [
            "Pro",
            "USD 499/mes",
            "Cloud dashboard, hasta 10K generaciones/mes, 5 proveedores LLM, "
            "knowledge base 1GB, soporte email (48h SLA), 3 usuarios"
        ],
        [
            "Team",
            "USD 1,499/mes",
            "Todo Pro + 100K generaciones/mes, SSO/SAML, audit logs exportables, "
            "cost tracking avanzado, 10 usuarios, soporte prioritario (24h SLA)"
        ],
        [
            "Enterprise",
            "Custom (desde USD 5,000/mes)",
            "Todo Team + ilimitado, deployment on-premise o VPC dedicada, "
            "DP-SGD garantizado, compliance packs (HIPAA, GDPR, SOC 2), "
            "SLA 99.9%, soporte dedicado, usuarios ilimitados, integraciones custom"
        ],
    ]
    story.append(
        make_table(
            tiers_data[0],
            tiers_data[1:],
            col_widths=[2.5 * cm, 3 * cm, 8 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Flujos de revenue adicionales:", "subsection"))
    story.append(Bullet(
        "<b>Consultoría de implementación</b> — USD 15,000-50,000 por proyecto. Configuración de pipeline "
        "específico para el dominio del cliente, integración con sus sistemas (CRM, EHR, DMS), creación "
        "de semillas iniciales y entrenamiento del equipo."
    ))
    story.append(Bullet(
        "<b>Domain packs premium</b> — USD 2,000-10,000/pack. Paquetes de semillas curadas (50-200) para "
        "industrias específicas con templates, herramientas y umbrales de calidad pre-configurados."
    ))
    story.append(Bullet(
        "<b>Marketplace de adaptadores</b> — Comisión del 20% sobre venta de adaptadores LoRA entrenados "
        "en el marketplace (los datos nunca salen, solo el modelo entrenado se comparte)."
    ))
    story.append(Bullet(
        "<b>Capacitación y certificación</b> — USD 500-2,000/persona. Programas de certificación "
        "\"UNCASE Certified Engineer\" para equipos de ML en industrias reguladas."
    ))
    story.append(PageBreak())

    # ==================== 6. MERCADO Y DEMANDA ====================
    story.append(section_number(6, "Mercado y Demanda"))
    story.append(HR())

    story.append(P("Mercado de datos sintéticos:", "subsection"))
    story.append(
        P(
            "El mercado global de datos sintéticos fue valuado en <b>USD 584M en 2025</b> y se proyecta "
            "alcanzar <b>USD 5,515M para 2034</b>, con un CAGR de 38.2%. El margen bruto promedio de "
            "plataformas de datos sintéticos es ~70%."
        )
    )
    story.append(Spacer(1, 4))

    market_data = [
        ["Métrica", "Valor", "Fuente"],
        ["Mercado datos sintéticos 2025", "USD 584M", "IntelMarketResearch 2025"],
        ["Proyección 2034", "USD 5,515M (CAGR 38.2%)", "IntelMarketResearch 2025"],
        ["IA en salud 2025", "USD 22.5B", "Grand View Research"],
        ["IA en servicios financieros", "USD 42.8B (2026 proj.)", "MarketsandMarkets"],
        ["Legal tech AI", "USD 1.2B (CAGR 28%)", "Allied Market Research"],
        ["Gasto en compliance de datos", "USD 5.47M promedio/empresa", "Ponemon Institute"],
        ["Empresas usando synth data (2026)", "75% (predicción Gartner)", "Gartner 2024"],
    ]
    story.append(
        make_table(
            market_data[0],
            market_data[1:],
            col_widths=[4.5 * cm, 4.5 * cm, 4.5 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("TAM / SAM / SOM:", "subsection"))

    tam_data = [
        ["Nivel", "Definición", "Estimación"],
        [
            "TAM", "Mercado total de datos sintéticos + MLOps regulado",
            "USD 5.5B (2034)"
        ],
        [
            "SAM", "Datos sintéticos conversacionales para industrias reguladas (salud, finanzas, legal) en Americas + Europa",
            "USD 800M (2028)"
        ],
        [
            "SOM", "Clientes enterprise y consultoría en LATAM + US Hispanic market en primeros 3 años",
            "USD 8-15M ARR (Año 3)"
        ],
    ]
    story.append(
        make_table(
            tam_data[0],
            tam_data[1:],
            col_widths=[1.5 * cm, 7 * cm, 5 * cm],
        )
    )

    story.append(Spacer(1, 8))
    story.append(P("Drivers de demanda:", "subsection"))
    story.append(Bullet(
        "<b>Regulación creciente</b> — EU AI Act (vigente 2025), HIPAA enforcement acelerado, "
        "GDPR multas record (Meta EUR 1.2B, 2023). Las empresas <i>necesitan</i> datos sintéticos."
    ))
    story.append(Bullet(
        "<b>Explosión de fine-tuning</b> — El costo de fine-tuning bajo 90% desde 2023. "
        "QLoRA permite entrenar modelos 70B en una GPU de consumo. Pero los datos siguen siendo el cuello de botella."
    ))
    story.append(Bullet(
        "<b>Escasez de datos de calidad en español</b> — El 95% de datasets públicos son en inglés. "
        "LATAM representa un mercado desatendido con enorme demanda de LLMs en español para "
        "salud, banca, legal y retail."
    ))
    story.append(Bullet(
        "<b>Adopción enterprise de IA generativa</b> — McKinsey estima que la IA generativa puede "
        "agregar USD 2.6-4.4T en valor global anual. Pero el 67% de ejecutivos citan la privacidad "
        "de datos como la barrera principal."
    ))
    story.append(PageBreak())

    # ==================== 7. COMPETENCIA ====================
    story.append(section_number(7, "Competencia y Diferenciación"))
    story.append(HR())

    comp_data = [
        ["Competidor", "Funding", "Enfoque", "Limitación vs UNCASE"],
        [
            "Mostly AI",
            "USD 31M (Series B)",
            "Datos sintéticos tabulares, banca y seguros",
            "No genera conversaciones. No produce modelos. Sin pipeline end-to-end."
        ],
        [
            "Gretel.ai",
            "USD 67M (NVIDIA-backed)",
            "Synth data general, tabular + texto",
            "No enfocado en reguladas. Sin seed-based generation. Sin DP-SGD en fine-tuning."
        ],
        [
            "Tonic.ai",
            "USD 45M (Series B)",
            "Test data para DevOps",
            "Orientado a QA/testing, no a LLM training. Sin pipeline conversacional."
        ],
        [
            "Hazy (SAS)",
            "Adquirida por SAS",
            "Synth data con DP para finanzas",
            "Propietario (SAS). Sin gateway LLM. Sin herramientas de dominio."
        ],
        [
            "Scale AI",
            "USD 1.3B+",
            "Data labeling general",
            "Enfoque en labeling humano, no generación. Caro. No privacy-first."
        ],
    ]
    story.append(
        make_table(
            comp_data[0],
            comp_data[1:],
            col_widths=[2.3 * cm, 2.5 * cm, 3.5 * cm, 5.2 * cm],
        )
    )
    story.append(Spacer(1, 10))

    story.append(P("Ventajas competitivas de UNCASE:", "subsection"))

    diff_data = [
        ["Feature", "Mostly AI", "Gretel", "Tonic", "UNCASE"],
        ["Pipeline seed-to-model", "No", "No", "No", "Si (5 capas)"],
        ["Privacy-first architecture", "Parcial", "Básica", "Básica", "Zero PII + DP-SGD"],
        ["Open source", "No", "Parcial", "No", "Apache 2.0"],
        ["LLM Gateway con PII scan", "No", "No", "No", "Si (3 modos)"],
        ["Multi-industria regulada", "Solo finanzas", "General", "DevOps", "6 dominios"],
        ["Tool-augmented generation", "No", "No", "No", "30 herramientas"],
        ["Datos en español", "Limitado", "No", "No", "Nativo bilingüe"],
        ["On-premise deployment", "No", "No", "No", "Docker + GPU"],
    ]
    story.append(
        make_table(
            diff_data[0],
            diff_data[1:],
            col_widths=[3.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 3.2 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 8. MERCADOS OBJETIVO ====================
    story.append(section_number(8, "Mercados Objetivo y Expansión Geográfica"))
    story.append(HR())

    story.append(P("Fase 1 — LATAM (Meses 1-12):", "subsection"))
    story.append(
        P(
            "El mercado inicial es <b>Colombia y México</b>, seguido de Brasil y Chile. "
            "La ventaja de UNCASE en español y su comprensión de regulaciones locales "
            "(Ley 1581, LFPDPPP) crea un moat regional que competidores US/EU no tienen."
        )
    )
    geo_latam = [
        ["País", "Sectores objetivo", "Regulación clave", "Tamaño oportunidad"],
        ["Colombia", "Banca, salud, BPO", "Ley 1581 (datos personales)", "USD 890M en IA (2025)"],
        ["México", "Finanzas, manufactura, retail", "LFPDPPP", "USD 1.5B en IA (2025)"],
        ["Brasil", "Salud, fintechs, legal", "LGPD", "USD 3.2B en IA (2025)"],
        ["Chile", "Minería, banca, salud", "Ley 19.628 (en reforma)", "USD 450M en IA (2025)"],
    ]
    story.append(
        make_table(
            geo_latam[0],
            geo_latam[1:],
            col_widths=[2 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Fase 2 — US Hispanic Market + EU (Meses 12-24):", "subsection"))
    story.append(Bullet(
        "<b>US</b> — Healthcare (HIPAA), financial services, legal tech. Foco en empresas con "
        "operaciones bilingües (US Hispanic market = 62M personas, USD 3.4T en poder adquisitivo)."
    ))
    story.append(Bullet(
        "<b>Europa</b> — GDPR crea demanda masiva de datos sintéticos. España como puerta de entrada. "
        "Alemania y Francia como mercados secundarios."
    ))

    story.append(Spacer(1, 8))
    story.append(P("Fase 3 — Global (Meses 24-36):", "subsection"))
    story.append(Bullet("Expansión a Asia-Pacific (regulaciones estrictas de privacidad en Japón, Corea, Australia)."))
    story.append(Bullet("Partnerships con consultoras Big 4 (Deloitte, PwC, EY, KPMG) para deployment enterprise."))
    story.append(Bullet("Modelo marketplace con comisiones sobre adaptadores LoRA compartidos."))
    story.append(PageBreak())

    # ==================== 9. REGULACIONES ====================
    story.append(section_number(9, "Regulaciones y Certificaciones"))
    story.append(HR())

    story.append(P("Regulaciones en scope (ya compatibles):", "subsection"))

    reg_current = [
        ["Regulación", "Jurisdicción", "Relevancia para UNCASE", "Estado"],
        ["GDPR", "Unión Europea", "Datos sintéticos como alternativa a procesamiento de datos reales", "Cumple"],
        ["HIPAA", "Estados Unidos", "PHI nunca expuesta; synthetic data no es PHI", "Cumple (pre-cert)"],
        ["Ley 1581", "Colombia", "Tratamiento de datos personales; semillas anonimizadas", "Cumple"],
        ["LFPDPPP", "México", "Protección de datos personales en posesión de particulares", "Cumple"],
        ["LGPD", "Brasil", "Ley General de Protección de Datos, similar a GDPR", "Cumple"],
        ["EU AI Act", "Unión Europea", "Clasificación de sistemas IA de alto riesgo", "Compatible"],
    ]
    story.append(
        make_table(
            reg_current[0],
            reg_current[1:],
            col_widths=[2 * cm, 2.5 * cm, 6 * cm, 2 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Certificaciones que requieren inversión:", "subsection"))

    cert_data = [
        ["Certificación", "Costo estimado", "Timeline", "Prioridad", "Impacto en ventas"],
        [
            "SOC 2 Type I",
            "USD 20,000-50,000",
            "3-6 meses",
            "Alta",
            "Requerido por el 89% de enterprise prospects en US"
        ],
        [
            "SOC 2 Type II",
            "USD 30,000-80,000",
            "12 meses post Type I",
            "Alta",
            "Demuestra cumplimiento sostenido"
        ],
        [
            "ISO 27001",
            "USD 15,000-40,000",
            "6-12 meses",
            "Media",
            "Estándar en EU y LATAM enterprise"
        ],
        [
            "HIPAA BAA",
            "USD 5,000-15,000 (legal)",
            "1-3 meses",
            "Alta",
            "Obligatorio para vender a healthcare US"
        ],
        [
            "Verificación DP formal",
            "USD 30,000-60,000",
            "4-8 meses",
            "Diferenciador",
            "Partnership académico para validar epsilon"
        ],
    ]
    story.append(
        make_table(
            cert_data[0],
            cert_data[1:],
            col_widths=[2.3 * cm, 2.5 * cm, 2.5 * cm, 1.8 * cm, 4.4 * cm],
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "<b>Inversión total en certificaciones:</b> USD 100,000-245,000 en los primeros 18 meses. "
            "Esta inversión es esencial para vender a enterprise en US y EU.",
        )
    )
    story.append(PageBreak())

    # ==================== 10. EQUIPO ====================
    story.append(section_number(10, "Equipo y Estructura Organizacional"))
    story.append(HR())

    story.append(P("Modalidad de trabajo:", "subsection"))
    story.append(
        P(
            "<b>100% remoto</b> en la fase inicial (0-18 meses). No se requiere oficina física. "
            "Las herramientas de desarrollo, CI/CD y comunicación son todas cloud-based. "
            "Cuando el equipo supere 10 personas (fase de escala), evaluar un espacio de coworking "
            "en Bogotá o CDMX para reuniones de equipo y eventos con clientes (USD 300-600/mes)."
        )
    )
    story.append(Spacer(1, 6))

    story.append(P("Equipo fundador (Meses 1-6):", "subsection"))

    team_core = [
        ["Rol", "Ubicación", "Salario mensual (USD)", "Responsabilidad"],
        [
            "CEO/CTO (Fundador)",
            "LATAM (remoto)",
            "3,000-4,000",
            "Arquitectura, estrategia de producto, primeros clientes, visión técnica"
        ],
        [
            "ML Engineer Sr.",
            "LATAM (remoto)",
            "3,500-5,000",
            "Pipeline LoRA, DP-SGD, optimización de modelos, benchmarks"
        ],
        [
            "Full-Stack Developer",
            "LATAM (remoto)",
            "2,500-3,500",
            "Dashboard, API, integraciones, frontend features"
        ],
    ]
    story.append(
        make_table(
            team_core[0],
            team_core[1:],
            col_widths=[3 * cm, 2.5 * cm, 3 * cm, 5 * cm],
        )
    )
    story.append(Spacer(1, 4))
    story.append(P("<b>Costo mensual equipo fundador: USD 9,000-12,500</b>", "body_bold"))

    story.append(Spacer(1, 8))
    story.append(P("Equipo de crecimiento (Meses 7-12):", "subsection"))

    team_growth = [
        ["Rol", "Ubicación", "Salario mensual (USD)", "Responsabilidad"],
        [
            "DevOps / Platform Engineer",
            "LATAM (remoto)",
            "3,000-4,000",
            "Kubernetes, CI/CD, observabilidad, deployments on-premise para clientes"
        ],
        [
            "Sales / BD Lead",
            "LATAM (remoto)",
            "2,500-3,500 + comisión",
            "Pipeline de ventas, demos, relaciones con enterprise, partnerships"
        ],
        [
            "Content / Growth Marketer",
            "LATAM (remoto)",
            "2,000-3,000",
            "Blog técnico, SEO, GitHub presence, developer community"
        ],
    ]
    story.append(
        make_table(
            team_growth[0],
            team_growth[1:],
            col_widths=[3 * cm, 2.5 * cm, 3 * cm, 5 * cm],
        )
    )
    story.append(Spacer(1, 4))
    story.append(P("<b>Costo mensual equipo completo (Año 1): USD 16,500-26,500</b>", "body_bold"))

    story.append(Spacer(1, 8))
    story.append(P("Equipo de escala (Año 2):", "subsection"))

    team_scale = [
        ["Rol", "Salario mensual (USD)", "Motivo de contratación"],
        ["ML Engineer Jr.", "2,000-3,000", "Soporte al pipeline, testing, seed curation"],
        ["Customer Success", "2,000-2,500", "Onboarding clientes, soporte técnico, retención"],
        ["Legal / Compliance (part-time)", "1,500-2,500", "Certificaciones, contratos enterprise, BAAs"],
        ["Data Scientist", "3,000-4,000", "Benchmarks, métricas de calidad, investigación"],
    ]
    story.append(
        make_table(
            team_scale[0],
            team_scale[1:],
            col_widths=[3.5 * cm, 3.5 * cm, 6.5 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 11. INFRAESTRUCTURA ====================
    story.append(section_number(11, "Infraestructura Técnica"))
    story.append(HR())

    story.append(P("Opciones de cómputo GPU:", "subsection"))
    story.append(Spacer(1, 4))

    gpu_data = [
        ["Opción", "Costo/hora", "Costo/mes (uso parcial)", "Cuándo usarla"],
        ["NVIDIA A100 80GB (cloud)", "USD 1.50-2.50/hr", "USD 200-400", "Fine-tuning modelos hasta 13B"],
        ["NVIDIA H100 (cloud)", "USD 2.50-4.00/hr", "USD 400-700", "Fine-tuning modelos 70B+"],
        ["Lambda Labs (A100)", "USD 1.10/hr", "USD 150-300", "Mejor precio/rendimiento para batch"],
        ["RunPod (A100/H100)", "USD 0.75-2.50/hr", "USD 100-400", "Spot instances para demos"],
        ["Ollama local (Mac/Linux)", "Gratis", "USD 0", "Desarrollo y testing local"],
        ["A100 on-premise (compra)", "N/A", "USD 10,000-15,000 (única vez)", "Solo con 10+ clientes enterprise"],
    ]
    story.append(
        make_table(
            gpu_data[0],
            gpu_data[1:],
            col_widths=[3.2 * cm, 2.3 * cm, 3 * cm, 5 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Infraestructura cloud mínima:", "subsection"))

    infra_data = [
        ["Servicio", "Proveedor", "Costo mensual", "Propósito"],
        ["VPS (API + DB)", "Hetzner / DigitalOcean", "USD 50-100", "FastAPI + PostgreSQL producción"],
        ["GPU on-demand", "Lambda Labs / RunPod", "USD 200-500", "Fine-tuning bajo demanda"],
        ["Frontend hosting", "Vercel (pro)", "USD 20", "Next.js dashboard"],
        ["CI/CD", "GitHub Actions", "Gratis (2,000 min/mes)", "Tests, linting, deploys"],
        ["Email / Comms", "Resend + Slack", "USD 20-50", "Emails transaccionales, team comms"],
        ["Monitoring", "Grafana Cloud free tier", "Gratis", "Métricas y alertas"],
        ["LLM APIs", "Anthropic / OpenAI", "USD 100-500", "Generación sintética y demos"],
    ]
    story.append(
        make_table(
            infra_data[0],
            infra_data[1:],
            col_widths=[3 * cm, 3.5 * cm, 2.5 * cm, 4.5 * cm],
        )
    )
    story.append(Spacer(1, 4))
    story.append(P("<b>Costo total infraestructura mínima: USD 390-1,170/mes</b>", "body_bold"))

    story.append(PageBreak())

    # ==================== 12. PLAN DE MARKETING ====================
    story.append(section_number(12, "Plan de Marketing"))
    story.append(HR())

    story.append(P("Estrategia: Developer-first + Enterprise outbound", "subsection"))
    story.append(Spacer(1, 4))

    mkt_data = [
        ["Canal", "Actividad", "Costo mensual", "KPI objetivo"],
        [
            "GitHub + Open Source",
            "Repositorio público, releases, README impecable, contributing guide",
            "USD 0 (tiempo)",
            "500 stars (6 meses), 50 contributors (12 meses)"
        ],
        [
            "Contenido técnico",
            "Blog semanal (ML, privacidad, regulación), tutorials, benchmarks",
            "USD 500-1,000",
            "10K visitantes/mes, 500 signups"
        ],
        [
            "LinkedIn B2B",
            "Posts del fundador, case studies, thought leadership en privacidad + IA",
            "USD 300-500 (ads)",
            "50 leads calificados/mes"
        ],
        [
            "Developer community",
            "Discord/Slack, Stack Overflow, Reddit (r/MachineLearning, r/LocalLLaMA)",
            "USD 0 (tiempo)",
            "200 miembros activos"
        ],
        [
            "Eventos y conferencias",
            "PyCon, LATAM AI Summit, compliance conferences, webinars mensuales",
            "USD 500-1,500",
            "5 leads enterprise/evento"
        ],
        [
            "Partnerships",
            "Consultoras, firmas legales, hospitales, aceleradoras",
            "USD 0-500",
            "3 partnerships estratégicas/trimestre"
        ],
        [
            "Email marketing",
            "Newsletter quincenal, drip campaigns para leads",
            "USD 50-100",
            "25% open rate, 5% conversion"
        ],
        [
            "SEO técnico",
            "Docs site optimizado, landing pages por industria y regulación",
            "USD 200-500",
            "Top 5 en 'synthetic data regulated industries'"
        ],
    ]
    story.append(
        make_table(
            mkt_data[0],
            mkt_data[1:],
            col_widths=[2.5 * cm, 4 * cm, 2.5 * cm, 4.5 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Presupuesto de marketing consolidado:", "subsection"))

    mkt_budget = [
        ["Escenario", "Mensual", "Anual", "Descripción"],
        [
            "Mínimo viable",
            "USD 2,000",
            "USD 24,000",
            "Contenido + SEO + LinkedIn básico. Sin eventos."
        ],
        [
            "Recomendado",
            "USD 5,000",
            "USD 60,000",
            "Todo lo anterior + eventos + ads + email automation."
        ],
        [
            "Agresivo (con funding)",
            "USD 15,000",
            "USD 180,000",
            "Todo + sponsorships, producción video, PR, paid dev relations."
        ],
    ]
    story.append(
        make_table(
            mkt_budget[0],
            mkt_budget[1:],
            col_widths=[3 * cm, 2.3 * cm, 2.3 * cm, 6 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 13. PROYECCION FINANCIERA ====================
    story.append(section_number(13, "Proyección Financiera y Camino al ROI"))
    story.append(HR())

    story.append(P("Escenario conservador (sin funding externo):", "subsection"))

    fin_bootstrap = [
        ["Mes", "Revenue", "Gastos", "Balance", "Hitos"],
        ["1-3", "USD 0", "USD 35,000", "-USD 35,000", "Producto terminado, primeros beta users"],
        ["4-6", "USD 3,000", "USD 40,000", "-USD 72,000", "3 clientes Pro, 1 consultoría"],
        ["7-9", "USD 12,000", "USD 50,000", "-USD 110,000", "10 clientes Pro, 2 Team, 2 consultorías"],
        ["10-12", "USD 30,000", "USD 55,000", "-USD 135,000", "20 clientes Pro, 5 Team, 1 Enterprise"],
        ["13-18", "USD 60,000/mes", "USD 65,000/mes", "-USD 165,000", "Break-even en mes ~18"],
        ["19-24", "USD 100,000/mes", "USD 75,000/mes", "+USD 325,000", "Cash flow positivo, ARR USD 1.2M"],
    ]
    story.append(
        make_table(
            fin_bootstrap[0],
            fin_bootstrap[1:],
            col_widths=[1.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 4.5 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Escenario con seed funding (USD 500K):", "subsection"))

    fin_funded = [
        ["Mes", "Revenue", "Gastos", "Cash restante", "Hitos"],
        ["1-3", "USD 0", "USD 50,000", "USD 350,000", "Equipo de 5, producto maduro, SOC 2 inicio"],
        ["4-6", "USD 8,000", "USD 60,000", "USD 194,000", "10 Pro, 3 Team, 2 consultorías, SOC 2 Type I"],
        ["7-9", "USD 25,000", "USD 70,000", "USD 79,000", "30 Pro, 8 Team, 2 Enterprise, HIPAA BAA"],
        ["10-12", "USD 55,000", "USD 80,000", "+USD 4,000", "Break-even en mes 12, ARR USD 660K"],
        ["13-18", "USD 100,000/mes", "USD 90,000/mes", "+USD 64,000/mes", "ARR USD 1.2M, equipo de 10"],
        ["19-24", "USD 180,000/mes", "USD 120,000/mes", "+USD 60,000/mes", "ARR USD 2.16M, Series A ready"],
    ]
    story.append(
        make_table(
            fin_funded[0],
            fin_funded[1:],
            col_widths=[1.5 * cm, 2.5 * cm, 2.5 * cm, 2.8 * cm, 4.2 * cm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Unit economics:", "subsection"))

    unit_data = [
        ["Métrica", "Valor", "Notas"],
        ["Margen bruto", "75-85%", "Software + LLM API pass-through con markup"],
        ["CAC (Cost of Acquisition)", "USD 2,000-5,000", "Marketing + sales time per enterprise deal"],
        ["LTV (Lifetime Value)", "USD 25,000-120,000", "18-36 meses retention, upsell Pro→Enterprise"],
        ["LTV/CAC ratio", "5-24x", "Saludable (benchmark B2B SaaS: >3x)"],
        ["Net Revenue Retention", "120%+", "Expansión via más usuarios, más generaciones, enterprise upgrade"],
        ["Payback period", "4-8 meses", "Tiempo para recuperar CAC"],
    ]
    story.append(
        make_table(
            unit_data[0],
            unit_data[1:],
            col_widths=[3.5 * cm, 3 * cm, 7 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 14. PLAN DE EJECUCION ====================
    story.append(section_number(14, "Plan de Ejecución"))
    story.append(HR())

    exec_data = [
        ["Trimestre", "Objetivos", "Entregables", "KPIs"],
        [
            "Q1 2026 (actual)",
            "Completar producto, validar con beta users",
            "Pipeline 5 capas completo, 75+ endpoints, 970 tests, "
            "observabilidad, audit logging, cost tracking",
            "5 beta users, 100 GitHub stars"
        ],
        [
            "Q2 2026",
            "Primeros clientes de pago, SDK, certificaciones",
            "Python SDK en PyPI, MCP server, SOC 2 Type I inicio, "
            "3 domain packs, benchmarks publicados",
            "10 clientes Pro, USD 5K MRR, 300 stars"
        ],
        [
            "Q3 2026",
            "Escalar ventas, equipo completo",
            "SOC 2 Type I obtenido, HIPAA BAA, 6 domain packs, "
            "marketplace v1, partnerships con 3 consultoras",
            "30 clientes, USD 25K MRR, 500 stars"
        ],
        [
            "Q4 2026",
            "Enterprise push, expansión regional",
            "5 Enterprise clients, ISO 27001 inicio, "
            "Kubernetes deployment, multi-tenant hard isolation",
            "50 clientes, USD 55K MRR, 1K stars"
        ],
        [
            "Q1-Q2 2027",
            "Escala internacional, Series A prep",
            "US market entry, EU GDPR compliance pack, "
            "partner program, DP verification academic paper",
            "100 clientes, USD 100K MRR, Series A"
        ],
    ]
    story.append(
        make_table(
            exec_data[0],
            exec_data[1:],
            col_widths=[2.2 * cm, 3.5 * cm, 4 * cm, 3.8 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 15. RIESGOS ====================
    story.append(section_number(15, "Riesgos y Mitigación"))
    story.append(HR())

    risk_data = [
        ["Riesgo", "Probabilidad", "Impacto", "Mitigación"],
        [
            "Competidor con más funding lanza producto similar",
            "Media",
            "Alto",
            "Diferenciación en español, regulaciones LATAM, open-source trust. "
            "Los competidores actuales no hacen conversacional + regulado + LoRA."
        ],
        [
            "Cambio regulatorio inesperado",
            "Baja",
            "Alto",
            "Compliance profiles son modulares y pluggables. "
            "Adaptación rápida a nuevas regulaciones sin cambiar el core."
        ],
        [
            "Costos de LLM API se disparan",
            "Baja",
            "Medio",
            "Soporte nativo para modelos locales (Ollama, vLLM). "
            "El gateway permite cambiar proveedor sin modificar el pipeline."
        ],
        [
            "Adopción lenta de enterprise",
            "Media",
            "Alto",
            "Modelo freemium reduce barrera. Consultorías generan revenue "
            "mientras se construye pipeline de ventas enterprise."
        ],
        [
            "Concentración en pocos clientes",
            "Media",
            "Medio",
            "Diversificar entre industrias y geografías. "
            "Self-serve Pro tier como base de revenue distribuida."
        ],
        [
            "La IA cambia radicalmente (AGI, nuevos paradigmas)",
            "Baja",
            "Alto",
            "La infraestructura de UNCASE (gateway, plugins, observabilidad) "
            "es útil para CUALQUIER aplicación LLM, no solo fine-tuning. "
            "Capacidad de pivotar rápidamente."
        ],
        [
            "Falla de seguridad / data breach",
            "Baja",
            "Crítico",
            "Zero PII architecture. Datos reales nunca persisten en UNCASE. "
            "Audit logging + Fernet encryption. SOC 2 + pen testing."
        ],
    ]
    story.append(
        make_table(
            risk_data[0],
            risk_data[1:],
            col_widths=[3.2 * cm, 1.8 * cm, 1.5 * cm, 7 * cm],
        )
    )
    story.append(PageBreak())

    # ==================== 16. SOLICITUD DE INVERSION ====================
    story.append(section_number(16, "Solicitud de Inversión"))
    story.append(HR())

    story.append(P("Escenario mínimo (bootstrapping + angel):", "subsection"))

    inv_min = [
        ["Concepto", "Monto (USD)", "Uso"],
        ["Salarios equipo fundador (6 meses)", "75,000", "CEO/CTO + ML Engineer + Full-Stack"],
        ["Infraestructura cloud (6 meses)", "7,000", "VPS, GPUs on-demand, LLM APIs"],
        ["Marketing (6 meses)", "12,000", "Contenido, SEO, LinkedIn, primeros eventos"],
        ["Legal y certificaciones", "25,000", "Constitución, HIPAA BAA, SOC 2 inicio"],
        ["Contingencia (15%)", "18,000", "Imprevistos"],
        ["<b>TOTAL MÍNIMO</b>", "<b>137,000</b>", "<b>Runway de 6 meses hasta primeros ingresos</b>"],
    ]
    story.append(
        make_table(
            inv_min[0],
            inv_min[1:],
            col_widths=[4.5 * cm, 2.5 * cm, 6.5 * cm],
        )
    )
    story.append(Spacer(1, 10))

    story.append(P("Escenario ideal (seed round):", "subsection"))

    inv_ideal = [
        ["Concepto", "Monto (USD)", "Uso"],
        ["Salarios equipo completo (12 meses)", "250,000", "6 personas: tech + sales + marketing"],
        ["Infraestructura (12 meses)", "20,000", "Cloud, GPUs, monitoring, dominios"],
        ["Marketing (12 meses)", "60,000", "Contenido, ads, eventos, PR, partnerships"],
        ["Certificaciones", "100,000", "SOC 2 Type I+II, ISO 27001, HIPAA BAA, DP verification"],
        ["Legal y operaciones", "30,000", "Constitución, contratos, propiedad intelectual, seguros"],
        ["Contingencia (15%)", "70,000", "Imprevistos y oportunidades"],
        ["<b>TOTAL SEED ROUND</b>", "<b>530,000</b>", "<b>Runway de 12 meses, break-even al mes 12</b>"],
    ]
    story.append(
        make_table(
            inv_ideal[0],
            inv_ideal[1:],
            col_widths=[4.5 * cm, 2.5 * cm, 6.5 * cm],
        )
    )
    story.append(Spacer(1, 12))

    story.append(P("Retorno esperado:", "subsection"))
    story.append(Bullet(
        "<b>Con USD 530K seed</b> → ARR USD 1.2M al mes 18, USD 2.16M al mes 24. "
        "Valuación estimada para Series A: USD 10-20M (5-10x ARR)."
    ))
    story.append(Bullet(
        "<b>Return on investment:</b> 4-8x en 24-36 meses basado en valuación de Series A."
    ))
    story.append(Bullet(
        "<b>Comparable:</b> Mostly AI (USD 31M Series B, datos sintéticos regulados), "
        "Gretel (USD 67M, datos sintéticos general), Tonic (USD 45M, test data)."
    ))

    story.append(Spacer(1, 16))
    story.append(HR())
    story.append(Spacer(1, 8))
    story.append(
        P(
            "<b>Contacto</b><br/><br/>"
            "Mariano Morales — Fundador &amp; CTO<br/>"
            "UNCASE AI<br/><br/>"
            "GitHub: github.com/uncase-ai/UNCASE<br/>"
            "Web: uncase.dev<br/><br/>"
            "<i>Febrero 2026 — Documento confidencial</i>",
            "body",
        )
    )

    # ==================== BUILD ====================
    doc.build(story)
    print(f"\nPDF generado: {OUTPUT_PATH}")
    print(f"Tamaño: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == "__main__":
    build_pdf()

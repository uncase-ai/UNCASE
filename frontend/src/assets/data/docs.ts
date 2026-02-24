import type { LucideIcon } from 'lucide-react'
import {
  Rocket,
  Layers,
  Globe,
  Terminal,
  Shield,
  Cloud,
  Settings,
  GitPullRequest,
  Clock,
} from 'lucide-react'

export type Locale = 'en' | 'es'

export type BilingualText = {
  en: string
  es: string
}

export type DocCategory = {
  id: string
  label: BilingualText
  description: BilingualText
  icon: LucideIcon
  order: number
}

export type DocArticle = {
  id: string
  title: BilingualText
  description: BilingualText
  content: BilingualText
  category: string
  keywords: string[]
  lastUpdated: string
  order: number
}

export const CATEGORIES: DocCategory[] = [
  {
    id: 'getting-started',
    label: { en: 'Getting Started', es: 'Primeros Pasos' },
    description: {
      en: 'Installation, quick start, and initial configuration.',
      es: 'Instalación, inicio rápido y configuración inicial.',
    },
    icon: Rocket,
    order: 0,
  },
  {
    id: 'architecture',
    label: { en: 'Architecture', es: 'Arquitectura' },
    description: {
      en: 'The 5-layer SCSF pipeline and data flow.',
      es: 'El pipeline SCSF de 5 capas y flujo de datos.',
    },
    icon: Layers,
    order: 1,
  },
  {
    id: 'api',
    label: { en: 'API Reference', es: 'Referencia API' },
    description: {
      en: 'REST endpoints, authentication, and responses.',
      es: 'Endpoints REST, autenticación y respuestas.',
    },
    icon: Globe,
    order: 2,
  },
  {
    id: 'cli',
    label: { en: 'CLI Reference', es: 'Referencia CLI' },
    description: {
      en: 'Command-line interface and available commands.',
      es: 'Interfaz de línea de comandos y comandos disponibles.',
    },
    icon: Terminal,
    order: 3,
  },
  {
    id: 'privacy',
    label: { en: 'Privacy & Security', es: 'Privacidad y Seguridad' },
    description: {
      en: 'PII handling, DP-SGD, and quality thresholds.',
      es: 'Manejo de PII, DP-SGD y umbrales de calidad.',
    },
    icon: Shield,
    order: 4,
  },
  {
    id: 'deployment',
    label: { en: 'Deployment', es: 'Despliegue' },
    description: {
      en: 'Docker, Vercel, and production deployment.',
      es: 'Docker, Vercel y despliegue a producción.',
    },
    icon: Cloud,
    order: 5,
  },
  {
    id: 'configuration',
    label: { en: 'Configuration', es: 'Configuración' },
    description: {
      en: 'Environment variables and settings.',
      es: 'Variables de entorno y ajustes.',
    },
    icon: Settings,
    order: 6,
  },
  {
    id: 'contributing',
    label: { en: 'Contributing', es: 'Contribuir' },
    description: {
      en: 'Development workflow, PR checklist, and conventions.',
      es: 'Flujo de desarrollo, checklist de PR y convenciones.',
    },
    icon: GitPullRequest,
    order: 7,
  },
  {
    id: 'changelog',
    label: { en: 'Changelog', es: 'Registro de Cambios' },
    description: {
      en: 'Version history and release notes.',
      es: 'Historial de versiones y notas de release.',
    },
    icon: Clock,
    order: 8,
  },
]

export const ARTICLES: DocArticle[] = [
  // ── Technology Stack ────────────────────────────────────
  {
    id: 'technology-stack',
    title: { en: 'Technology Stack', es: 'Stack Tecnológico' },
    description: {
      en: 'Backend (Python), Frontend (Next.js), and all dependencies.',
      es: 'Backend (Python), Frontend (Next.js) y todas las dependencias.',
    },
    category: 'getting-started',
    keywords: ['tech', 'stack', 'python', 'fastapi', 'nextjs', 'postgres'],
    lastUpdated: '2026-02-24',
    order: 2,
    content: {
      en: `<h2>Backend Stack (Python)</h2>
<table>
<thead><tr><th>Component</th><th>Technology</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td>Language</td><td>Python ≥ 3.11</td><td>Core implementation</td></tr>
<tr><td>Package manager</td><td>uv + lockfile</td><td>Fast dependency resolution</td></tr>
<tr><td>Web framework</td><td>FastAPI + Uvicorn</td><td>REST API and async support</td></tr>
<tr><td>Data validation</td><td>Pydantic v2</td><td>Schemas, field validation, OpenAPI</td></tr>
<tr><td>LLM integrations</td><td>LiteLLM</td><td>Unified interface to Claude, Gemini, Qwen, LLaMA</td></tr>
<tr><td>CLI</td><td>Typer</td><td>Command-line interface</td></tr>
<tr><td>Database</td><td>PostgreSQL 16</td><td>Primary datastore</td></tr>
<tr><td>ORM</td><td>SQLAlchemy 2.0 (async)</td><td>Database abstraction</td></tr>
<tr><td>Async driver</td><td>asyncpg</td><td>PostgreSQL async driver</td></tr>
<tr><td>Logging</td><td>structlog</td><td>Structured JSON logging</td></tr>
<tr><td>Testing</td><td>pytest + pytest-asyncio</td><td>Unit, integration, privacy tests</td></tr>
<tr><td>Linting</td><td>Ruff</td><td>Fast Python linter & formatter</td></tr>
<tr><td>Type checking</td><td>mypy (strict)</td><td>Static type verification</td></tr>
<tr><td>Privacy</td><td>SpaCy + Presidio</td><td>PII detection and redaction</td></tr>
<tr><td>Fine-tuning</td><td>transformers + peft + trl</td><td>LoRA/QLoRA training</td></tr>
<tr><td>ML tracking</td><td>MLflow</td><td>Experiment tracking and models</td></tr>
</tbody>
</table>

<h2>Frontend Stack (Next.js)</h2>
<table>
<thead><tr><th>Component</th><th>Technology</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td>Framework</td><td>Next.js 16 (App Router)</td><td>Server and client rendering</td></tr>
<tr><td>Runtime</td><td>React 19</td><td>UI components</td></tr>
<tr><td>Language</td><td>TypeScript 5.9 (strict)</td><td>Type safety</td></tr>
<tr><td>Styling</td><td>Tailwind CSS v4</td><td>Utility-first CSS</td></tr>
<tr><td>UI Components</td><td>shadcn/ui (new-york)</td><td>Composable component library</td></tr>
<tr><td>Primitives</td><td>Radix UI</td><td>Accessible UI primitives</td></tr>
<tr><td>Icons</td><td>Lucide Icons</td><td>SVG icon library</td></tr>
<tr><td>Animation</td><td>Framer Motion</td><td>React animation library</td></tr>
<tr><td>Themes</td><td>next-themes</td><td>Dark mode support</td></tr>
<tr><td>Markdown</td><td>next-mdx-remote-client</td><td>MDX content processing</td></tr>
<tr><td>Code linting</td><td>ESLint</td><td>Code quality</td></tr>
<tr><td>Formatting</td><td>Prettier</td><td>Code formatting</td></tr>
<tr><td>Deployment</td><td>Vercel</td><td>Edge functions and CDN</td></tr>
</tbody>
</table>

<h2>Extras & Optional Dependencies</h2>
<table>
<thead><tr><th>Extra</th><th>Includes</th><th>Use Case</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, Typer, SQLAlchemy</td><td>Minimal installation</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td><td>Development and testing</td></tr>
<tr><td><code>[ml]</code></td><td>torch, transformers, peft, trl, accelerate, bitsandbytes</td><td>LoRA fine-tuning</td></tr>
<tr><td><code>[privacy]</code></td><td>spacy, presidio-analyzer, presidio-anonymizer</td><td>PII detection/redaction</td></tr>
<tr><td><code>[all]</code></td><td>dev + ml + privacy</td><td>Full featured</td></tr>
</tbody>
</table>

<h2>Supported Python Version</h2>
<p><strong>Python 3.11+</strong> is required for:</p>
<ul>
<li>Async context managers and error handling</li>
<li>Type union syntax (<code>X | Y</code>)</li>
<li>Performance improvements in asyncio</li>
<li>Pydantic v2 optimizations</li>
</ul>`,
      es: `<h2>Stack Backend (Python)</h2>
<table>
<thead><tr><th>Componente</th><th>Tecnología</th><th>Propósito</th></tr></thead>
<tbody>
<tr><td>Lenguaje</td><td>Python ≥ 3.11</td><td>Implementación principal</td></tr>
<tr><td>Gestor de paquetes</td><td>uv + lockfile</td><td>Resolución rápida de dependencias</td></tr>
<tr><td>Framework web</td><td>FastAPI + Uvicorn</td><td>API REST y soporte async</td></tr>
<tr><td>Validación datos</td><td>Pydantic v2</td><td>Esquemas, validación, OpenAPI</td></tr>
<tr><td>Integraciones LLM</td><td>LiteLLM</td><td>Interfaz unificada a Claude, Gemini, Qwen, LLaMA</td></tr>
<tr><td>CLI</td><td>Typer</td><td>Interfaz de línea de comandos</td></tr>
<tr><td>Base de datos</td><td>PostgreSQL 16</td><td>Almacenamiento principal</td></tr>
<tr><td>ORM</td><td>SQLAlchemy 2.0 (async)</td><td>Abstracción de base de datos</td></tr>
<tr><td>Driver async</td><td>asyncpg</td><td>Driver PostgreSQL async</td></tr>
<tr><td>Logging</td><td>structlog</td><td>Logging estructurado JSON</td></tr>
<tr><td>Testing</td><td>pytest + pytest-asyncio</td><td>Tests unitarios, integración, privacidad</td></tr>
<tr><td>Linting</td><td>Ruff</td><td>Linter y formateador rápido</td></tr>
<tr><td>Type checking</td><td>mypy (strict)</td><td>Verificación estática de tipos</td></tr>
<tr><td>Privacidad</td><td>SpaCy + Presidio</td><td>Detección y redacción de PII</td></tr>
<tr><td>Fine-tuning</td><td>transformers + peft + trl</td><td>Entrenamiento LoRA/QLoRA</td></tr>
<tr><td>ML tracking</td><td>MLflow</td><td>Tracking de experimentos y modelos</td></tr>
</tbody>
</table>

<h2>Stack Frontend (Next.js)</h2>
<table>
<thead><tr><th>Componente</th><th>Tecnología</th><th>Propósito</th></tr></thead>
<tbody>
<tr><td>Framework</td><td>Next.js 16 (App Router)</td><td>Renderizado servidor y cliente</td></tr>
<tr><td>Runtime</td><td>React 19</td><td>Componentes UI</td></tr>
<tr><td>Lenguaje</td><td>TypeScript 5.9 (strict)</td><td>Seguridad de tipos</td></tr>
<tr><td>Styling</td><td>Tailwind CSS v4</td><td>CSS utility-first</td></tr>
<tr><td>Componentes UI</td><td>shadcn/ui (new-york)</td><td>Librería de componentes composables</td></tr>
<tr><td>Primitivas</td><td>Radix UI</td><td>Primitivas UI accesibles</td></tr>
<tr><td>Iconos</td><td>Lucide Icons</td><td>Librería de iconos SVG</td></tr>
<tr><td>Animaciones</td><td>Framer Motion</td><td>Librería de animaciones React</td></tr>
<tr><td>Temas</td><td>next-themes</td><td>Soporte de modo oscuro</td></tr>
<tr><td>Markdown</td><td>next-mdx-remote-client</td><td>Procesamiento de contenido MDX</td></tr>
<tr><td>Linting código</td><td>ESLint</td><td>Calidad de código</td></tr>
<tr><td>Formateo</td><td>Prettier</td><td>Formateo de código</td></tr>
<tr><td>Despliegue</td><td>Vercel</td><td>Edge functions y CDN</td></tr>
</tbody>
</table>

<h2>Extras y Dependencias Opcionales</h2>
<table>
<thead><tr><th>Extra</th><th>Incluye</th><th>Caso de Uso</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, Typer, SQLAlchemy</td><td>Instalación mínima</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td><td>Desarrollo y testing</td></tr>
<tr><td><code>[ml]</code></td><td>torch, transformers, peft, trl, accelerate, bitsandbytes</td><td>Fine-tuning LoRA</td></tr>
<tr><td><code>[privacy]</code></td><td>spacy, presidio-analyzer, presidio-anonymizer</td><td>Detección/redacción de PII</td></tr>
<tr><td><code>[all]</code></td><td>dev + ml + privacy</td><td>Completo</td></tr>
</tbody>
</table>

<h2>Versión de Python Soportada</h2>
<p><strong>Python 3.11+</strong> es requerido para:</p>
<ul>
<li>Gestores de contexto async mejorados</li>
<li>Sintaxis de unión de tipos (<code>X | Y</code>)</li>
<li>Mejoras de rendimiento en asyncio</li>
<li>Optimizaciones de Pydantic v2</li>
</ul>`,
    },
  },

  // ── Getting Started ─────────────────────────────────────
  {
    id: 'installation',
    title: { en: 'Installation', es: 'Instalación' },
    description: {
      en: 'Three ways to install UNCASE: Git, pip, or Docker.',
      es: 'Tres formas de instalar UNCASE: Git, pip o Docker.',
    },
    category: 'getting-started',
    keywords: ['install', 'setup', 'git', 'pip', 'docker', 'uv'],
    lastUpdated: '2026-02-23',
    order: 0,
    content: {
      en: `<h2>Option 1: Git + uv (recommended for development)</h2>
<pre><code>git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync                    # core dependencies
uv sync --extra dev        # + development tools
uv sync --extra all        # everything (dev + ml + privacy)</code></pre>

<h2>Option 2: pip</h2>
<pre><code>pip install uncase                      # core
pip install "uncase[dev]"               # + development
pip install "uncase[ml]"                # + machine learning
pip install "uncase[privacy]"           # + privacy (SpaCy + Presidio)
pip install "uncase[all]"               # everything</code></pre>

<h2>Option 3: Docker</h2>
<pre><code># API + PostgreSQL
docker compose up -d

# With MLflow tracking
docker compose --profile ml up -d

# With GPU support (NVIDIA)
docker compose --profile gpu up -d</code></pre>

<h2>Available extras</h2>
<table>
<thead><tr><th>Extra</th><th>Includes</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td></tr>
<tr><td><code>[ml]</code></td><td>transformers, peft, trl, torch, mlflow, accelerate</td></tr>
<tr><td><code>[privacy]</code></td><td>spacy, presidio-analyzer, presidio-anonymizer</td></tr>
<tr><td><code>[all]</code></td><td>dev + ml + privacy</td></tr>
</tbody>
</table>`,
      es: `<h2>Opción 1: Git + uv (recomendado para desarrollo)</h2>
<pre><code>git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync                    # dependencias core
uv sync --extra dev        # + herramientas de desarrollo
uv sync --extra all        # todo (dev + ml + privacy)</code></pre>

<h2>Opción 2: pip</h2>
<pre><code>pip install uncase                      # core
pip install "uncase[dev]"               # + desarrollo
pip install "uncase[ml]"                # + machine learning
pip install "uncase[privacy]"           # + privacidad (SpaCy + Presidio)
pip install "uncase[all]"               # todo</code></pre>

<h2>Opción 3: Docker</h2>
<pre><code># API + PostgreSQL
docker compose up -d

# Con MLflow tracking
docker compose --profile ml up -d

# Con soporte GPU (NVIDIA)
docker compose --profile gpu up -d</code></pre>

<h2>Extras disponibles</h2>
<table>
<thead><tr><th>Extra</th><th>Incluye</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td></tr>
<tr><td><code>[ml]</code></td><td>transformers, peft, trl, torch, mlflow, accelerate</td></tr>
<tr><td><code>[privacy]</code></td><td>spacy, presidio-analyzer, presidio-anonymizer</td></tr>
<tr><td><code>[all]</code></td><td>dev + ml + privacy</td></tr>
</tbody>
</table>`,
    },
  },
  {
    id: 'roadmap-status',
    title: { en: 'Roadmap & Status', es: 'Hoja de Ruta y Estado' },
    description: {
      en: 'Current implementation phase and planned features.',
      es: 'Fase actual de implementación y características planificadas.',
    },
    category: 'getting-started',
    keywords: ['roadmap', 'phases', 'status', 'progress', 'planning'],
    lastUpdated: '2026-02-24',
    order: 1,
    content: {
      en: `<h2>Current Status: Phase 0-1 Complete (v0.0.0.dev0)</h2>

<h3>Phase 0: Infrastructure & Foundation ✓ Complete</h3>
<ul>
<li>✓ Distribution infrastructure (Git, pip, Docker)</li>
<li>✓ Database and ORM setup (PostgreSQL, SQLAlchemy async)</li>
<li>✓ API scaffolding (FastAPI, Uvicorn, OpenAPI)</li>
<li>✓ CLI scaffolding (Typer)</li>
<li>✓ Organization and user management</li>
<li>✓ Exception handling hierarchy</li>
<li>✓ Structured logging (structlog)</li>
<li>✓ CI/CD and pre-commit hooks</li>
<li>✓ Documentation infrastructure (bilingual EN/ES)</li>
</ul>

<h3>Phase 1: Templates, Tools & Import ✓ Complete</h3>
<ul>
<li>✓ 10 chat templates (ChatML, Alpaca, Llama, Mistral, Qwen, etc.)</li>
<li>✓ Template rendering engine</li>
<li>✓ Tools framework with 5 automotive.sales domain tools</li>
<li>✓ CSV/JSONL import with format auto-detection</li>
<li>✓ Seed validation (SeedSchema v1)</li>
<li>✓ 5 API routers with 23 endpoints</li>
<li>✓ MCP server integration</li>
<li>✓ Landing page and documentation site</li>
<li>✓ 228 passing tests, 86% coverage</li>
</ul>

<h3>Phase 2: Privacy & Quality Evaluation ◌ In Progress</h3>
<p><strong>Target: March 2026</strong></p>
<ul>
<li>PII detection and elimination (Layer 0 — Seed Engine)</li>
<li>Parser for multi-format inputs (Layer 1 — WhatsApp, JSON, CRM)</li>
<li>Quality evaluation metrics (Layer 2 — ROUGE, fidelity, coherence)</li>
<li>Re-evaluation loop for generated synthetics</li>
<li>Privacy test suite (mandatory before PR)</li>
<li>DP-SGD integration foundation</li>
</ul>

<h3>Phase 3: Synthetic Generation ◌ Planned</h3>
<p><strong>Target: April 2026</strong></p>
<ul>
<li>Synthetic conversation generator (Layer 3)</li>
<li>LiteLLM provider integration (Claude, Gemini, Qwen, LLaMA)</li>
<li>Generation strategies (persona variation, flow variation, tool injection)</li>
<li>Expansion ratio: 1 seed → 200-500 synthetics</li>
<li>CLI: <code>uncase generate</code></li>
<li>API endpoints for generation</li>
</ul>

<h3>Phase 4: LoRA Fine-tuning Pipeline ◌ Planned</h3>
<p><strong>Target: May 2026</strong></p>
<ul>
<li>LoRA/QLoRA pipeline (Layer 4)</li>
<li>Dataset preparation from certified synthetics</li>
<li>Integration with transformers + peft + trl</li>
<li>DP-SGD training with epsilon ≤ 8.0</li>
<li>MLflow tracking and model evaluation</li>
<li>Extraction attack testing</li>
<li>CLI: <code>uncase train</code></li>
</ul>

<h3>Phase 5+: Multi-Domain Expansion ◌ Planned</h3>
<p><strong>Target: June-August 2026</strong></p>
<ul>
<li>Domain-specific tools and templates (medical, legal, finance, industrial, education)</li>
<li>Advanced parsers (CRM, transcriptions, Whisper output)</li>
<li>Production hardening (auth, rate limiting, queues)</li>
<li>Public repository launch</li>
<li>Community contributions</li>
</ul>

<h2>Quality Metrics Overview</h2>
<table>
<thead><tr><th>Metric</th><th>Threshold</th><th>Gate</th></tr></thead>
<tbody>
<tr><td>Code coverage</td><td>≥ 80% core, ≥ 90% schemas</td><td>PR blocking</td></tr>
<tr><td>ROUGE-L</td><td>≥ 0.65</td><td>Synthetic quality</td></tr>
<tr><td>Factual Fidelity</td><td>≥ 0.90</td><td>Synthetic quality</td></tr>
<tr><td>Lexical Diversity (TTR)</td><td>≥ 0.55</td><td>Synthetic quality</td></tr>
<tr><td>Dialogic Coherence</td><td>≥ 0.85</td><td>Synthetic quality</td></tr>
<tr><td>Privacy Score (PII)</td><td>= 0.00</td><td>Hard gate (NO EXCEPTIONS)</td></tr>
<tr><td>Memorization</td><td>< 0.01</td><td>Extraction attack resistance</td></tr>
</tbody>
</table>

<h2>Development Guidelines</h2>
<ul>
<li>All commits in English, all PRs require privacy tests</li>
<li>Code style: Ruff (line-length 120), Type hints required</li>
<li>Database: Always read schema before modification</li>
<li>Never commit .env files or real data</li>
<li>Deployment: Use <code>./deploy.sh</code> script only</li>
</ul>`,
      es: `<h2>Estado Actual: Fases 0-1 Completas (v0.0.0.dev0)</h2>

<h3>Fase 0: Infraestructura y Fundación ✓ Completa</h3>
<ul>
<li>✓ Infraestructura de distribución (Git, pip, Docker)</li>
<li>✓ Base de datos y ORM (PostgreSQL, SQLAlchemy async)</li>
<li>✓ Scaffolding API (FastAPI, Uvicorn, OpenAPI)</li>
<li>✓ Scaffolding CLI (Typer)</li>
<li>✓ Gestión de organizaciones y usuarios</li>
<li>✓ Jerarquía de manejo de excepciones</li>
<li>✓ Logging estructurado (structlog)</li>
<li>✓ CI/CD y pre-commit hooks</li>
<li>✓ Infraestructura de documentación (bilingüe EN/ES)</li>
</ul>

<h3>Fase 1: Templates, Herramientas e Importación ✓ Completa</h3>
<ul>
<li>✓ 10 chat templates (ChatML, Alpaca, Llama, Mistral, Qwen, etc.)</li>
<li>✓ Motor de renderizado de templates</li>
<li>✓ Framework de herramientas con 5 tools automotive.sales</li>
<li>✓ Importación CSV/JSONL con auto-detección de formato</li>
<li>✓ Validación de semillas (SeedSchema v1)</li>
<li>✓ 5 routers API con 23 endpoints</li>
<li>✓ Integración servidor MCP</li>
<li>✓ Landing page y sitio de documentación</li>
<li>✓ 228 tests pasando, 86% de cobertura</li>
</ul>

<h3>Fase 2: Privacidad y Evaluación de Calidad ◌ En Progreso</h3>
<p><strong>Objetivo: Marzo 2026</strong></p>
<ul>
<li>Detección y eliminación de PII (Capa 0 — Motor de Semillas)</li>
<li>Parser para entradas multi-formato (Capa 1 — WhatsApp, JSON, CRM)</li>
<li>Métricas de evaluación de calidad (Capa 2 — ROUGE, fidelidad, coherencia)</li>
<li>Loop de re-evaluación para sintéticos generados</li>
<li>Suite de tests de privacidad (obligatoria antes de PR)</li>
<li>Fundación de integración DP-SGD</li>
</ul>

<h3>Fase 3: Generación Sintética ◌ Planificada</h3>
<p><strong>Objetivo: Abril 2026</strong></p>
<ul>
<li>Generador de conversaciones sintéticas (Capa 3)</li>
<li>Integración de proveedores LiteLLM (Claude, Gemini, Qwen, LLaMA)</li>
<li>Estrategias de generación (variación de persona, flujo, herramientas)</li>
<li>Ratio de expansión: 1 semilla → 200-500 sintéticos</li>
<li>CLI: <code>uncase generate</code></li>
<li>Endpoints API para generación</li>
</ul>

<h3>Fase 4: Pipeline LoRA Fine-tuning ◌ Planificada</h3>
<p><strong>Objetivo: Mayo 2026</strong></p>
<ul>
<li>Pipeline LoRA/QLoRA (Capa 4)</li>
<li>Preparación de datasets desde sintéticos certificados</li>
<li>Integración con transformers + peft + trl</li>
<li>Entrenamiento DP-SGD con epsilon ≤ 8.0</li>
<li>Tracking con MLflow y evaluación de modelos</li>
<li>Testing de ataques de extracción</li>
<li>CLI: <code>uncase train</code></li>
</ul>

<h3>Fase 5+: Expansión Multi-Dominio ◌ Planificada</h3>
<p><strong>Objetivo: Junio-Agosto 2026</strong></p>
<ul>
<li>Herramientas y templates específicos de dominio (médico, legal, finanzas, industrial, educación)</li>
<li>Parsers avanzados (CRM, transcripciones, salida de Whisper)</li>
<li>Hardening para producción (auth, rate limiting, colas)</li>
<li>Lanzamiento de repositorio público</li>
<li>Contribuciones comunitarias</li>
</ul>

<h2>Resumen de Métricas de Calidad</h2>
<table>
<thead><tr><th>Métrica</th><th>Umbral</th><th>Gate</th></tr></thead>
<tbody>
<tr><td>Cobertura de código</td><td>≥ 80% core, ≥ 90% schemas</td><td>Bloqueo de PR</td></tr>
<tr><td>ROUGE-L</td><td>≥ 0.65</td><td>Calidad sintética</td></tr>
<tr><td>Fidelidad Factual</td><td>≥ 0.90</td><td>Calidad sintética</td></tr>
<tr><td>Diversidad Léxica (TTR)</td><td>≥ 0.55</td><td>Calidad sintética</td></tr>
<tr><td>Coherencia Dialógica</td><td>≥ 0.85</td><td>Calidad sintética</td></tr>
<tr><td>Privacy Score (PII)</td><td>= 0.00</td><td>Gate duro (SIN EXCEPCIONES)</td></tr>
<tr><td>Memorización</td><td>< 0.01</td><td>Resistencia a ataques de extracción</td></tr>
</tbody>
</table>

<h2>Directrices de Desarrollo</h2>
<ul>
<li>Todos los commits en inglés, todo PR requiere tests de privacidad</li>
<li>Estilo de código: Ruff (line-length 120), type hints obligatorios</li>
<li>Base de datos: Siempre leer schema antes de modificar</li>
<li>Nunca commitear archivos .env o datos reales</li>
<li>Despliegue: Usar solo script <code>./deploy.sh</code></li>
</ul>`,
    },
  },
  {
    id: 'quick-start',
    title: { en: 'Quick Start', es: 'Inicio Rápido' },
    description: {
      en: 'Get UNCASE running in under 5 minutes.',
      es: 'Pon UNCASE en marcha en menos de 5 minutos.',
    },
    category: 'getting-started',
    keywords: ['quickstart', 'first-steps', 'hello-world'],
    lastUpdated: '2026-02-24',
    order: 3,
    content: {
      en: `<h2>1. Clone and install</h2>
<pre><code>git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync --extra dev</code></pre>

<h2>2. Configure environment</h2>
<pre><code>cp .env.example .env
# Edit .env with your API keys and database URL</code></pre>

<h2>3. Start the API server</h2>
<pre><code>make api
# or: uv run uvicorn uncase.api.main:app --reload --port 8000</code></pre>

<h2>4. Verify it works</h2>
<pre><code>curl http://localhost:8000/health
# {"status":"ok","version":"0.0.0.dev0"}</code></pre>

<h2>5. Explore the CLI</h2>
<pre><code>uv run uncase --help
uv run uncase --version</code></pre>

<h2>Using Make</h2>
<p>The project includes a Makefile with all common commands:</p>
<pre><code>make help       # see all available commands
make test       # run tests
make lint       # run linter
make check      # lint + typecheck + tests</code></pre>`,
      es: `<h2>1. Clonar e instalar</h2>
<pre><code>git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync --extra dev</code></pre>

<h2>2. Configurar entorno</h2>
<pre><code>cp .env.example .env
# Edita .env con tus API keys y URL de base de datos</code></pre>

<h2>3. Iniciar el servidor API</h2>
<pre><code>make api
# o: uv run uvicorn uncase.api.main:app --reload --port 8000</code></pre>

<h2>4. Verificar que funciona</h2>
<pre><code>curl http://localhost:8000/health
# {"status":"ok","version":"0.0.0.dev0"}</code></pre>

<h2>5. Explorar el CLI</h2>
<pre><code>uv run uncase --help
uv run uncase --version</code></pre>

<h2>Usando Make</h2>
<p>El proyecto incluye un Makefile con todos los comandos comunes:</p>
<pre><code>make help       # ver todos los comandos disponibles
make test       # ejecutar tests
make lint       # ejecutar linter
make check      # lint + typecheck + tests</code></pre>`,
    },
  },

  // ── Architecture ────────────────────────────────────────
  {
    id: 'scsf-overview',
    title: { en: 'SCSF Architecture', es: 'Arquitectura SCSF' },
    description: {
      en: 'The 5-layer Synthetic Conversational Seed Framework.',
      es: 'El framework SCSF de 5 capas para semillas conversacionales sintéticas.',
    },
    category: 'architecture',
    keywords: ['scsf', 'layers', 'pipeline', 'architecture', 'seed'],
    lastUpdated: '2026-02-23',
    order: 0,
    content: {
      en: `<h2>Overview</h2>
<p>UNCASE implements the <strong>Synthetic Conversational Seed Framework (SCSF)</strong>, a 5-layer pipeline that transforms real conversations into privacy-safe synthetic training data for LoRA/QLoRA fine-tuning.</p>

<h2>The 5 Layers</h2>
<ul>
<li><strong>Layer 0 — Seed Engine:</strong> Ingests real conversations and strips all PII (Personally Identifiable Information) to produce abstract SeedSchema v1 objects.</li>
<li><strong>Layer 1 — Parser &amp; Validator:</strong> Parses multi-format inputs (WhatsApp, JSON, CRM, transcriptions) and validates them against the internal SCSF schema.</li>
<li><strong>Layer 2 — Quality Evaluator:</strong> Scores seeds across ROUGE-L, factual fidelity, lexical diversity, and dialogic coherence. Also re-evaluates generated synthetics.</li>
<li><strong>Layer 3 — Synthetic Generator:</strong> Produces high-quality synthetic conversations from validated seeds using LLM providers via LiteLLM.</li>
<li><strong>Layer 4 — LoRA Pipeline:</strong> Automated fine-tuning pipeline supporting ShareGPT, Alpaca, and ChatML formats with DP-SGD privacy guarantees.</li>
</ul>

<h2>Data Flow</h2>
<pre><code>Real Conversation → [Layer 0: PII Removal] → SeedSchema v1
    → [Layer 1: Parsing + Validation] → Internal SCSF Schema
    → [Layer 2: Quality Evaluation] → Validated Seeds
    → [Layer 3: Synthetic Generation] → Synthetic Conversations
    → [Layer 2: Re-evaluation] → Certified Data
    → [Layer 4: LoRA Pipeline] → LoRA Adapter
    → Production → Feedback → [Layer 0] (flywheel cycle)</code></pre>

<h2>Supported Domains</h2>
<ul>
<li><code>automotive.sales</code> — Pilot domain</li>
<li><code>medical.consultation</code></li>
<li><code>legal.advisory</code></li>
<li><code>finance.advisory</code></li>
<li><code>industrial.support</code></li>
<li><code>education.tutoring</code></li>
</ul>`,
      es: `<h2>Descripción general</h2>
<p>UNCASE implementa el <strong>Synthetic Conversational Seed Framework (SCSF)</strong>, un pipeline de 5 capas que transforma conversaciones reales en datos sintéticos de entrenamiento seguros en privacidad para fine-tuning de LoRA/QLoRA.</p>

<h2>Las 5 Capas</h2>
<ul>
<li><strong>Capa 0 — Motor de Semillas:</strong> Ingesta conversaciones reales y elimina toda PII (Información Personal Identificable) para producir objetos abstractos SeedSchema v1.</li>
<li><strong>Capa 1 — Parser y Validador:</strong> Parsea entradas multi-formato (WhatsApp, JSON, CRM, transcripciones) y las valida contra el esquema interno SCSF.</li>
<li><strong>Capa 2 — Evaluador de Calidad:</strong> Puntúa semillas en ROUGE-L, fidelidad factual, diversidad léxica y coherencia dialógica. También re-evalúa los sintéticos generados.</li>
<li><strong>Capa 3 — Generador Sintético:</strong> Produce conversaciones sintéticas de alta calidad a partir de semillas validadas usando proveedores LLM vía LiteLLM.</li>
<li><strong>Capa 4 — Pipeline LoRA:</strong> Pipeline automatizado de fine-tuning que soporta formatos ShareGPT, Alpaca y ChatML con garantías de privacidad DP-SGD.</li>
</ul>

<h2>Flujo de Datos</h2>
<pre><code>Conversación Real → [Capa 0: Eliminación PII] → SeedSchema v1
    → [Capa 1: Parsing + Validación] → Esquema Interno SCSF
    → [Capa 2: Evaluación de Calidad] → Semillas Validadas
    → [Capa 3: Generación Sintética] → Conversaciones Sintéticas
    → [Capa 2: Re-evaluación] → Datos Certificados
    → [Capa 4: Pipeline LoRA] → Adaptador LoRA
    → Producción → Feedback → [Capa 0] (ciclo flywheel)</code></pre>

<h2>Dominios Soportados</h2>
<ul>
<li><code>automotive.sales</code> — Dominio piloto</li>
<li><code>medical.consultation</code></li>
<li><code>legal.advisory</code></li>
<li><code>finance.advisory</code></li>
<li><code>industrial.support</code></li>
<li><code>education.tutoring</code></li>
</ul>`,
    },
  },

  // ── API Reference ───────────────────────────────────────
  {
    id: 'api-overview',
    title: { en: 'API Overview', es: 'Visión General de la API' },
    description: {
      en: 'REST API structure, versioning, and available endpoints (Phase 0-1 complete).',
      es: 'Estructura de la API REST, versionado y endpoints disponibles (Fases 0-1 completas).',
    },
    category: 'api',
    keywords: ['api', 'rest', 'endpoints', 'fastapi', 'openapi'],
    lastUpdated: '2026-02-24',
    order: 0,
    content: {
      en: `<h2>Base URL</h2>
<pre><code>http://localhost:8000</code></pre>

<h2>Core Endpoints (Phase 0-1)</h2>
<table>
<thead><tr><th>Method</th><th>Path</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>GET</code></td><td><code>/health</code></td><td>Health check — returns status and version</td></tr>
<tr><td><code>GET</code></td><td><code>/docs</code></td><td>Interactive Swagger UI documentation</td></tr>
<tr><td><code>GET</code></td><td><code>/redoc</code></td><td>ReDoc API documentation</td></tr>
<tr><td><code>GET</code></td><td><code>/api/v1/templates</code></td><td>List all 10 chat templates</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/templates/render</code></td><td>Render conversation to template format</td></tr>
<tr><td><code>GET</code></td><td><code>/api/v1/tools</code></td><td>List registered tools</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/tools/{tool_id}/simulate</code></td><td>Simulate tool execution</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/import/csv</code></td><td>Import CSV conversations</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/import/jsonl</code></td><td>Import JSONL conversations with format detection</td></tr>
</tbody>
</table>

<h2>Health Check</h2>
<pre><code>GET /health

Response:
{
  "status": "ok",
  "version": "0.0.0.dev0"
}</code></pre>

<h2>Example: List Templates</h2>
<pre><code>curl http://localhost:8000/api/v1/templates

Response: [
  { "id": "chatml", "name": "ChatML", "supports_tools": true },
  { "id": "alpaca", "name": "Alpaca", "supports_tools": false },
  ...
]</code></pre>

<h2>API Versioning</h2>
<p>Current version: <code>/api/v1/</code>. Endpoints are organized by layer/domain with one router per component. Full OpenAPI/Swagger documentation available at <code>/docs</code>.</p>

<h2>Interactive Docs</h2>
<p>Once the server is running, visit <code>http://localhost:8000/docs</code> for the full Swagger UI with all available endpoints, request/response schemas, and the ability to test directly from the browser.</p>`,
      es: `<h2>URL Base</h2>
<pre><code>http://localhost:8000</code></pre>

<h2>Endpoints Principales (Fases 0-1)</h2>
<table>
<thead><tr><th>Método</th><th>Ruta</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>GET</code></td><td><code>/health</code></td><td>Health check — retorna estado y versión</td></tr>
<tr><td><code>GET</code></td><td><code>/docs</code></td><td>Documentación interactiva Swagger UI</td></tr>
<tr><td><code>GET</code></td><td><code>/redoc</code></td><td>Documentación API ReDoc</td></tr>
<tr><td><code>GET</code></td><td><code>/api/v1/templates</code></td><td>Listar 10 chat templates</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/templates/render</code></td><td>Renderizar conversación a formato de template</td></tr>
<tr><td><code>GET</code></td><td><code>/api/v1/tools</code></td><td>Listar herramientas registradas</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/tools/{tool_id}/simulate</code></td><td>Simular ejecución de herramientas</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/import/csv</code></td><td>Importar conversaciones CSV</td></tr>
<tr><td><code>POST</code></td><td><code>/api/v1/import/jsonl</code></td><td>Importar conversaciones JSONL con auto-detección</td></tr>
</tbody>
</table>

<h2>Health Check</h2>
<pre><code>GET /health

Respuesta:
{
  "status": "ok",
  "version": "0.0.0.dev0"
}</code></pre>

<h2>Ejemplo: Listar Templates</h2>
<pre><code>curl http://localhost:8000/api/v1/templates

Respuesta: [
  { "id": "chatml", "name": "ChatML", "supports_tools": true },
  { "id": "alpaca", "name": "Alpaca", "supports_tools": false },
  ...
]</code></pre>

<h2>Versionado de API</h2>
<p>Versión actual: <code>/api/v1/</code>. Los endpoints están organizados por capa/dominio con un router por componente. Documentación completa OpenAPI/Swagger disponible en <code>/docs</code>.</p>

<h2>Documentación Interactiva</h2>
<p>Una vez que el servidor esté corriendo, visita <code>http://localhost:8000/docs</code> para el Swagger UI completo con todos los endpoints disponibles, esquemas de request/response, y la posibilidad de probar directamente desde el navegador.</p>`,
    },
  },

  // ── CLI Reference ───────────────────────────────────────
  {
    id: 'cli-commands',
    title: { en: 'CLI Commands', es: 'Comandos CLI' },
    description: {
      en: 'All available UNCASE CLI commands and their usage.',
      es: 'Todos los comandos CLI de UNCASE disponibles y su uso.',
    },
    category: 'cli',
    keywords: ['cli', 'terminal', 'commands', 'typer'],
    lastUpdated: '2026-02-24',
    order: 0,
    content: {
      en: `<h2>Global Options</h2>
<pre><code>uncase --help              # show available commands
uncase --version           # show version</code></pre>

<h2>Available Commands (Phase 0-1 Complete)</h2>
<table>
<thead><tr><th>Command</th><th>Layer</th><th>Status</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>uncase seed --help</code></td><td>0</td><td><strong>✓ Available</strong></td><td>Seed management and validation</td></tr>
<tr><td><code>uncase import csv|jsonl</code></td><td>1</td><td><strong>✓ Available</strong></td><td>Import conversational data with format auto-detection</td></tr>
<tr><td><code>uncase template list</code></td><td>-</td><td><strong>✓ Available</strong></td><td>List available chat templates (10 formats)</td></tr>
<tr><td><code>uncase template export</code></td><td>-</td><td><strong>✓ Available</strong></td><td>Export conversations to fine-tuning format</td></tr>
<tr><td><code>uncase tool list</code></td><td>-</td><td><strong>✓ Available</strong></td><td>List registered tools by domain</td></tr>
<tr><td><code>uncase tool show</code></td><td>-</td><td><strong>✓ Available</strong></td><td>Display tool details and schemas</td></tr>
</tbody>
</table>

<h2>Planned Commands (Phase 2+)</h2>
<p>The following commands will be available as each layer is implemented:</p>
<table>
<thead><tr><th>Command</th><th>Layer</th><th>Phase</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>uncase evaluate</code></td><td>2</td><td>Phase 2</td><td>Evaluate seed/synthetic quality with ROUGE, fidelity, coherence metrics</td></tr>
<tr><td><code>uncase generate</code></td><td>3</td><td>Phase 2</td><td>Generate synthetic conversations from validated seeds</td></tr>
<tr><td><code>uncase train</code></td><td>4</td><td>Phase 2</td><td>Run the LoRA fine-tuning pipeline with DP-SGD</td></tr>
</tbody>
</table>`,
      es: `<h2>Opciones Globales</h2>
<pre><code>uncase --help              # mostrar comandos disponibles
uncase --version           # mostrar versión</code></pre>

<h2>Comandos Disponibles (Fases 0-1 Completas)</h2>
<table>
<thead><tr><th>Comando</th><th>Capa</th><th>Estado</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>uncase seed --help</code></td><td>0</td><td><strong>✓ Disponible</strong></td><td>Gestión y validación de semillas</td></tr>
<tr><td><code>uncase import csv|jsonl</code></td><td>1</td><td><strong>✓ Disponible</strong></td><td>Importar datos conversacionales con auto-detección de formato</td></tr>
<tr><td><code>uncase template list</code></td><td>-</td><td><strong>✓ Disponible</strong></td><td>Listar 10 templates de chat disponibles</td></tr>
<tr><td><code>uncase template export</code></td><td>-</td><td><strong>✓ Disponible</strong></td><td>Exportar conversaciones a formato de fine-tuning</td></tr>
<tr><td><code>uncase tool list</code></td><td>-</td><td><strong>✓ Disponible</strong></td><td>Listar herramientas registradas por dominio</td></tr>
<tr><td><code>uncase tool show</code></td><td>-</td><td><strong>✓ Disponible</strong></td><td>Mostrar detalles y esquemas de herramientas</td></tr>
</tbody>
</table>

<h2>Comandos Planificados (Fase 2+)</h2>
<p>Los siguientes comandos estarán disponibles conforme se implemente cada capa:</p>
<table>
<thead><tr><th>Comando</th><th>Capa</th><th>Fase</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>uncase evaluate</code></td><td>2</td><td>Fase 2</td><td>Evaluar calidad con métricas ROUGE, fidelidad, coherencia</td></tr>
<tr><td><code>uncase generate</code></td><td>3</td><td>Fase 2</td><td>Generar conversaciones sintéticas a partir de semillas validadas</td></tr>
<tr><td><code>uncase train</code></td><td>4</td><td>Fase 2</td><td>Ejecutar pipeline de fine-tuning LoRA con DP-SGD</td></tr>
</tbody>
</table>`,
    },
  },

  // ── Privacy & Security ──────────────────────────────────
  {
    id: 'privacy-guarantees',
    title: { en: 'Privacy Guarantees', es: 'Garantías de Privacidad' },
    description: {
      en: 'Zero-PII policy, DP-SGD, and mandatory quality thresholds.',
      es: 'Política de cero PII, DP-SGD y umbrales de calidad obligatorios.',
    },
    category: 'privacy',
    keywords: ['pii', 'privacy', 'dp-sgd', 'presidio', 'security'],
    lastUpdated: '2026-02-23',
    order: 0,
    content: {
      en: `<h2>Non-Negotiable Principles</h2>
<ul>
<li><strong>PII tolerance = 0</strong> in all final data outputs</li>
<li>Every generated conversation traces back to its source seed</li>
<li>DP-SGD with <strong>epsilon &le; 8.0</strong> during fine-tuning</li>
<li>Extraction attack success rate <strong>&lt; 1%</strong></li>
<li>Real conversation content is <strong>never logged</strong></li>
<li>Tests use <strong>only synthetic/fictional data</strong></li>
</ul>

<h2>Quality Thresholds</h2>
<table>
<thead><tr><th>Metric</th><th>Threshold</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td>ROUGE-L</td><td>&ge; 0.65</td><td>Structural coherence with seed</td></tr>
<tr><td>Factual Fidelity</td><td>&ge; 0.90</td><td>Domain fact accuracy</td></tr>
<tr><td>Lexical Diversity (TTR)</td><td>&ge; 0.55</td><td>Type-Token Ratio</td></tr>
<tr><td>Dialogic Coherence</td><td>&ge; 0.85</td><td>Cross-turn role consistency</td></tr>
<tr><td>Privacy Score</td><td>= 0.00</td><td>Zero residual PII (Presidio)</td></tr>
<tr><td>Memorization</td><td>&lt; 0.01</td><td>Extraction attack success rate</td></tr>
</tbody>
</table>

<h2>Composite Formula</h2>
<p><code>Q = min(ROUGE, Fidelity, TTR, Coherence)</code> if privacy=0 AND memorization&lt;0.01, otherwise Q=0.</p>

<h2>Technology</h2>
<ul>
<li><strong>PII Detection:</strong> SpaCy + Microsoft Presidio</li>
<li><strong>Privacy Training:</strong> DP-SGD via Opacus/custom implementation</li>
<li><strong>Verification:</strong> Mandatory privacy test suite before every PR</li>
</ul>`,
      es: `<h2>Principios No Negociables</h2>
<ul>
<li><strong>Tolerancia PII = 0</strong> en todos los datos de salida finales</li>
<li>Toda conversación generada traza su semilla de origen</li>
<li>DP-SGD con <strong>epsilon &le; 8.0</strong> durante el fine-tuning</li>
<li>Tasa de éxito de ataques de extracción <strong>&lt; 1%</strong></li>
<li>El contenido de conversaciones reales <strong>nunca se loguea</strong></li>
<li>Los tests usan <strong>solo datos sintéticos/ficticios</strong></li>
</ul>

<h2>Umbrales de Calidad</h2>
<table>
<thead><tr><th>Métrica</th><th>Umbral</th><th>Propósito</th></tr></thead>
<tbody>
<tr><td>ROUGE-L</td><td>&ge; 0.65</td><td>Coherencia estructural con semilla</td></tr>
<tr><td>Fidelidad Factual</td><td>&ge; 0.90</td><td>Precisión de hechos del dominio</td></tr>
<tr><td>Diversidad Léxica (TTR)</td><td>&ge; 0.55</td><td>Type-Token Ratio</td></tr>
<tr><td>Coherencia Dialógica</td><td>&ge; 0.85</td><td>Consistencia de roles inter-turno</td></tr>
<tr><td>Privacy Score</td><td>= 0.00</td><td>Cero PII residual (Presidio)</td></tr>
<tr><td>Memorización</td><td>&lt; 0.01</td><td>Tasa de éxito de ataques de extracción</td></tr>
</tbody>
</table>

<h2>Fórmula Compuesta</h2>
<p><code>Q = min(ROUGE, Fidelidad, TTR, Coherencia)</code> si privacy=0 Y memorización&lt;0.01, sino Q=0.</p>

<h2>Tecnología</h2>
<ul>
<li><strong>Detección PII:</strong> SpaCy + Microsoft Presidio</li>
<li><strong>Entrenamiento Privado:</strong> DP-SGD vía Opacus/implementación custom</li>
<li><strong>Verificación:</strong> Suite de tests de privacidad obligatoria antes de cada PR</li>
</ul>`,
    },
  },

  // ── Deployment ──────────────────────────────────────────
  {
    id: 'docker-deployment',
    title: { en: 'Docker Deployment', es: 'Despliegue con Docker' },
    description: {
      en: 'Running UNCASE with Docker Compose.',
      es: 'Ejecutar UNCASE con Docker Compose.',
    },
    category: 'deployment',
    keywords: ['docker', 'compose', 'container', 'postgresql', 'gpu'],
    lastUpdated: '2026-02-23',
    order: 0,
    content: {
      en: `<h2>Services</h2>
<table>
<thead><tr><th>Service</th><th>Description</th><th>Port</th><th>Profile</th></tr></thead>
<tbody>
<tr><td><code>api</code></td><td>FastAPI (UNCASE API)</td><td>8000</td><td>default</td></tr>
<tr><td><code>postgres</code></td><td>PostgreSQL 16 Alpine</td><td>5432</td><td>default</td></tr>
<tr><td><code>mlflow</code></td><td>MLflow tracking server</td><td>5000</td><td>ml</td></tr>
<tr><td><code>api-gpu</code></td><td>API with NVIDIA GPU</td><td>8001</td><td>gpu</td></tr>
</tbody>
</table>

<h2>Usage</h2>
<pre><code># Start API + PostgreSQL
docker compose up -d

# Start with MLflow
docker compose --profile ml up -d

# Start with GPU support
docker compose --profile gpu up -d

# View logs
docker compose logs -f api

# Stop everything
docker compose down</code></pre>

<h2>Custom Builds</h2>
<pre><code># Build with all extras
docker build --build-arg INSTALL_EXTRAS=all -t uncase:full .

# Build for GPU
docker build \\
  --build-arg BASE_IMAGE=nvidia/cuda:12.4.1-runtime-ubuntu22.04 \\
  --build-arg INSTALL_EXTRAS=all \\
  -t uncase:gpu .</code></pre>`,
      es: `<h2>Servicios</h2>
<table>
<thead><tr><th>Servicio</th><th>Descripción</th><th>Puerto</th><th>Perfil</th></tr></thead>
<tbody>
<tr><td><code>api</code></td><td>FastAPI (UNCASE API)</td><td>8000</td><td>default</td></tr>
<tr><td><code>postgres</code></td><td>PostgreSQL 16 Alpine</td><td>5432</td><td>default</td></tr>
<tr><td><code>mlflow</code></td><td>MLflow tracking server</td><td>5000</td><td>ml</td></tr>
<tr><td><code>api-gpu</code></td><td>API con GPU NVIDIA</td><td>8001</td><td>gpu</td></tr>
</tbody>
</table>

<h2>Uso</h2>
<pre><code># Iniciar API + PostgreSQL
docker compose up -d

# Iniciar con MLflow
docker compose --profile ml up -d

# Iniciar con soporte GPU
docker compose --profile gpu up -d

# Ver logs
docker compose logs -f api

# Detener todo
docker compose down</code></pre>

<h2>Builds Personalizados</h2>
<pre><code># Build con todos los extras
docker build --build-arg INSTALL_EXTRAS=all -t uncase:full .

# Build para GPU
docker build \\
  --build-arg BASE_IMAGE=nvidia/cuda:12.4.1-runtime-ubuntu22.04 \\
  --build-arg INSTALL_EXTRAS=all \\
  -t uncase:gpu .</code></pre>`,
    },
  },

  // ── Configuration ───────────────────────────────────────
  {
    id: 'environment-variables',
    title: { en: 'Environment Variables', es: 'Variables de Entorno' },
    description: {
      en: 'All configuration options via .env file.',
      es: 'Todas las opciones de configuración vía archivo .env.',
    },
    category: 'configuration',
    keywords: ['env', 'config', 'environment', 'settings'],
    lastUpdated: '2026-02-23',
    order: 0,
    content: {
      en: `<h2>Setup</h2>
<pre><code>cp .env.example .env
# Edit .env with your values</code></pre>

<h2>Core Variables</h2>
<table>
<thead><tr><th>Variable</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>UNCASE_ENV</code></td><td><code>development</code></td><td>Environment: development, staging, production</td></tr>
<tr><td><code>UNCASE_LOG_LEVEL</code></td><td><code>DEBUG</code></td><td>Logging level: DEBUG, INFO, WARNING, ERROR</td></tr>
<tr><td><code>UNCASE_DEFAULT_LOCALE</code></td><td><code>es</code></td><td>Default language: es, en</td></tr>
<tr><td><code>DATABASE_URL</code></td><td>&mdash;</td><td>PostgreSQL async connection string</td></tr>
<tr><td><code>API_PORT</code></td><td><code>8000</code></td><td>API server port</td></tr>
<tr><td><code>API_SECRET_KEY</code></td><td>&mdash;</td><td>Secret key for signing (change in production)</td></tr>
</tbody>
</table>

<h2>LLM Providers</h2>
<table>
<thead><tr><th>Variable</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>LITELLM_API_KEY</code></td><td>API key for active LLM provider</td></tr>
<tr><td><code>ANTHROPIC_API_KEY</code></td><td>Claude API key (optional, LiteLLM manages it)</td></tr>
<tr><td><code>OPENAI_API_KEY</code></td><td>OpenAI API key</td></tr>
<tr><td><code>GOOGLE_API_KEY</code></td><td>Google AI (Gemini) API key</td></tr>
</tbody>
</table>

<h2>Privacy</h2>
<table>
<thead><tr><th>Variable</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>UNCASE_PII_CONFIDENCE_THRESHOLD</code></td><td><code>0.85</code></td><td>Minimum confidence for PII detection</td></tr>
<tr><td><code>UNCASE_DP_EPSILON</code></td><td><code>8.0</code></td><td>Differential privacy epsilon bound</td></tr>
</tbody>
</table>`,
      es: `<h2>Configuración</h2>
<pre><code>cp .env.example .env
# Edita .env con tus valores</code></pre>

<h2>Variables Principales</h2>
<table>
<thead><tr><th>Variable</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>UNCASE_ENV</code></td><td><code>development</code></td><td>Entorno: development, staging, production</td></tr>
<tr><td><code>UNCASE_LOG_LEVEL</code></td><td><code>DEBUG</code></td><td>Nivel de logging: DEBUG, INFO, WARNING, ERROR</td></tr>
<tr><td><code>UNCASE_DEFAULT_LOCALE</code></td><td><code>es</code></td><td>Idioma por defecto: es, en</td></tr>
<tr><td><code>DATABASE_URL</code></td><td>&mdash;</td><td>Cadena de conexión PostgreSQL async</td></tr>
<tr><td><code>API_PORT</code></td><td><code>8000</code></td><td>Puerto del servidor API</td></tr>
<tr><td><code>API_SECRET_KEY</code></td><td>&mdash;</td><td>Clave secreta para firma (cambiar en producción)</td></tr>
</tbody>
</table>

<h2>Proveedores LLM</h2>
<table>
<thead><tr><th>Variable</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>LITELLM_API_KEY</code></td><td>API key del proveedor LLM activo</td></tr>
<tr><td><code>ANTHROPIC_API_KEY</code></td><td>API key de Claude (opcional, LiteLLM la gestiona)</td></tr>
<tr><td><code>OPENAI_API_KEY</code></td><td>API key de OpenAI</td></tr>
<tr><td><code>GOOGLE_API_KEY</code></td><td>API key de Google AI (Gemini)</td></tr>
</tbody>
</table>

<h2>Privacidad</h2>
<table>
<thead><tr><th>Variable</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>UNCASE_PII_CONFIDENCE_THRESHOLD</code></td><td><code>0.85</code></td><td>Confianza mínima para detección de PII</td></tr>
<tr><td><code>UNCASE_DP_EPSILON</code></td><td><code>8.0</code></td><td>Epsilon de privacidad diferencial</td></tr>
</tbody>
</table>`,
    },
  },

  // ── Contributing ────────────────────────────────────────
  {
    id: 'pr-checklist',
    title: { en: 'PR Checklist', es: 'Checklist de PR' },
    description: {
      en: 'Required checks before every pull request.',
      es: 'Verificaciones requeridas antes de cada pull request.',
    },
    category: 'contributing',
    keywords: ['pr', 'contributing', 'checklist', 'workflow'],
    lastUpdated: '2026-02-23',
    order: 0,
    content: {
      en: `<h2>Before Every PR</h2>
<ol>
<li><code>uv run ruff check .</code> — no linting errors</li>
<li><code>uv run ruff format --check .</code> — code is formatted</li>
<li><code>uv run mypy uncase/</code> — no type errors</li>
<li><code>uv run pytest</code> — all tests pass</li>
<li><code>uv run pytest tests/privacy/</code> — privacy suite passes</li>
<li>No real data in code or tests</li>
</ol>
<p>Or use the shortcut:</p>
<pre><code>make check    # runs lint + typecheck + tests</code></pre>

<h2>Code Conventions</h2>
<ul>
<li>Ruff for linting and formatting (line-length: 120)</li>
<li>Google-style docstrings</li>
<li>Type hints required on all public functions</li>
<li>Structured logging with <code>structlog</code> (never <code>print()</code>)</li>
<li>Custom exceptions inheriting from <code>UNCASEError</code></li>
<li>Pydantic v2 for all data models</li>
</ul>

<h2>Test Requirements</h2>
<ul>
<li>Minimum coverage: 80% for <code>core/</code>, 90% for <code>schemas/</code></li>
<li>Privacy tests are <strong>mandatory</strong> before merge</li>
<li>Use <code>factory_boy</code> for test data — never real data</li>
<li>Parametrized tests for SeedSchema validations</li>
</ul>`,
      es: `<h2>Antes de Cada PR</h2>
<ol>
<li><code>uv run ruff check .</code> — sin errores de linting</li>
<li><code>uv run ruff format --check .</code> — código formateado</li>
<li><code>uv run mypy uncase/</code> — sin errores de tipos</li>
<li><code>uv run pytest</code> — todos los tests pasan</li>
<li><code>uv run pytest tests/privacy/</code> — suite de privacidad pasa</li>
<li>Ningún dato real en código o tests</li>
</ol>
<p>O usa el atajo:</p>
<pre><code>make check    # ejecuta lint + typecheck + tests</code></pre>

<h2>Convenciones de Código</h2>
<ul>
<li>Ruff para linting y formateo (line-length: 120)</li>
<li>Docstrings estilo Google</li>
<li>Type hints obligatorios en todas las funciones públicas</li>
<li>Logging estructurado con <code>structlog</code> (nunca <code>print()</code>)</li>
<li>Excepciones custom heredando de <code>UNCASEError</code></li>
<li>Pydantic v2 para todos los modelos de datos</li>
</ul>

<h2>Requisitos de Tests</h2>
<ul>
<li>Cobertura mínima: 80% para <code>core/</code>, 90% para <code>schemas/</code></li>
<li>Tests de privacidad son <strong>obligatorios</strong> antes de merge</li>
<li>Usar <code>factory_boy</code> para datos de prueba — nunca datos reales</li>
<li>Tests parametrizados para validaciones de SeedSchema</li>
</ul>`,
    },
  },

  // ── Changelog ───────────────────────────────────────────
  {
    id: 'v0-0-0-dev0',
    title: { en: 'v0.0.0.dev0 — Phase 0-1 Complete', es: 'v0.0.0.dev0 — Fases 0-1 Completas' },
    description: {
      en: 'Full distribution, CLI, API, templates, tools, and imports implemented.',
      es: 'Distribución completa, CLI, API, templates, herramientas e importación implementados.',
    },
    category: 'changelog',
    keywords: ['release', 'changelog', 'v0', 'phase0', 'phase1'],
    lastUpdated: '2026-02-24',
    order: 0,
    content: {
      en: `<h2>2026-02-24 — v0.0.0.dev0 (Phase 0-1 Complete)</h2>

<h3>Phase 0: Infrastructure & Foundation</h3>
<ul>
<li>✓ Distribution via Git (<code>uv sync</code>), pip (<code>pip install uncase</code>), and Docker</li>
<li>✓ <code>pyproject.toml</code> with hatchling build, 4 extras groups (dev, ml, privacy, all)</li>
<li>✓ PostgreSQL async database with SQLAlchemy ORM</li>
<li>✓ Multi-stage Dockerfile with CPU/GPU support</li>
<li>✓ Docker Compose with API, PostgreSQL, MLflow, and GPU services</li>
<li>✓ Makefile with 18 development targets</li>
<li>✓ Pre-commit hooks and CI/CD pipeline</li>
<li>✓ Structured logging with structlog (JSON)</li>
<li>✓ Exception handling with custom UNCASEError hierarchy</li>
</ul>

<h3>Phase 1: Templates, Tools & Import</h3>
<ul>
<li>✓ 10 chat templates (ChatML, Alpaca, Llama, Mistral, Qwen, Nemotron, Moonshot, MiniMax, OpenAI, Harmony)</li>
<li>✓ Template rendering engine with format auto-detection</li>
<li>✓ Framework of tools with 5 automotive.sales domain tools</li>
<li>✓ CSV/JSONL import with automatic format detection (OpenAI, ShareGPT, UNCASE native)</li>
<li>✓ Seed validation against SeedSchema v1</li>
<li>✓ CLI commands: seed, import, template, tool</li>
<li>✓ FastAPI REST API with 5 routers and 23 endpoints</li>
<li>✓ MCP server integration (9 tools)</li>
<li>✓ Bilingual documentation system (EN/ES with auto-translation)</li>
<li>✓ Landing page with architecture, benefits, and use cases</li>
<li>✓ 228 passing tests, 86% code coverage</li>
<li>✓ Pydantic v2 schemas with full validation</li>
<li>✓ Organization and user management</li>
</ul>

<h3>Technology Stack Confirmed</h3>
<ul>
<li>Python 3.11+, FastAPI, Pydantic v2, LiteLLM, structlog</li>
<li>Typer CLI, pytest, ruff, mypy</li>
<li>PostgreSQL 16, SQLAlchemy async, asyncpg</li>
<li>spaCy + Presidio (privacy layer foundation)</li>
<li>Transformers, peft, trl (LoRA layer foundation)</li>
</ul>

<h3>Domains Supported</h3>
<ul>
<li>automotive.sales — Pilot domain with 5 tools</li>
<li>medical.consultation — Configuration ready</li>
<li>legal.advisory — Configuration ready</li>
<li>finance.advisory — Configuration ready</li>
<li>industrial.support — Configuration ready</li>
<li>education.tutoring — Configuration ready</li>
</ul>

<h3>Quality Metrics & Thresholds</h3>
<ul>
<li>ROUGE-L ≥ 0.65 (structural coherence)</li>
<li>Factual Fidelity ≥ 0.90 (domain accuracy)</li>
<li>Lexical Diversity (TTR) ≥ 0.55</li>
<li>Dialogic Coherence ≥ 0.85</li>
<li>Privacy Score = 0.00 (zero PII tolerance)</li>
<li>Memorization < 0.01 (extraction attack resistance)</li>
</ul>`,
      es: `<h2>2026-02-24 — v0.0.0.dev0 (Fases 0-1 Completas)</h2>

<h3>Fase 0: Infraestructura y Fundación</h3>
<ul>
<li>✓ Distribución vía Git (<code>uv sync</code>), pip (<code>pip install uncase</code>) y Docker</li>
<li>✓ <code>pyproject.toml</code> con build hatchling, 4 grupos de extras (dev, ml, privacy, all)</li>
<li>✓ Base de datos PostgreSQL async con SQLAlchemy ORM</li>
<li>✓ Dockerfile multi-stage con soporte CPU/GPU</li>
<li>✓ Docker Compose con API, PostgreSQL, MLflow y servicios GPU</li>
<li>✓ Makefile con 18 targets de desarrollo</li>
<li>✓ Pre-commit hooks y pipeline CI/CD</li>
<li>✓ Logging estructurado con structlog (JSON)</li>
<li>✓ Manejo de excepciones con jerarquía custom UNCASEError</li>
</ul>

<h3>Fase 1: Templates, Herramientas e Importación</h3>
<ul>
<li>✓ 10 templates de chat (ChatML, Alpaca, Llama, Mistral, Qwen, Nemotron, Moonshot, MiniMax, OpenAI, Harmony)</li>
<li>✓ Motor de renderizado de templates con auto-detección de formato</li>
<li>✓ Framework de herramientas con 5 tools del dominio automotive.sales</li>
<li>✓ Importación CSV/JSONL con detección automática de formato (OpenAI, ShareGPT, UNCASE nativo)</li>
<li>✓ Validación de semillas contra SeedSchema v1</li>
<li>✓ Comandos CLI: seed, import, template, tool</li>
<li>✓ API REST FastAPI con 5 routers y 23 endpoints</li>
<li>✓ Integración servidor MCP (9 herramientas)</li>
<li>✓ Sistema de documentación bilingüe (EN/ES con auto-traducción)</li>
<li>✓ Landing page con arquitectura, beneficios y casos de uso</li>
<li>✓ 228 tests pasando, 86% de cobertura de código</li>
<li>✓ Esquemas Pydantic v2 con validación completa</li>
<li>✓ Gestión de organizaciones y usuarios</li>
</ul>

<h3>Stack Tecnológico Confirmado</h3>
<ul>
<li>Python 3.11+, FastAPI, Pydantic v2, LiteLLM, structlog</li>
<li>Typer CLI, pytest, ruff, mypy</li>
<li>PostgreSQL 16, SQLAlchemy async, asyncpg</li>
<li>spaCy + Presidio (fundación capa de privacidad)</li>
<li>Transformers, peft, trl (fundación capa LoRA)</li>
</ul>

<h3>Dominios Soportados</h3>
<ul>
<li>automotive.sales — Dominio piloto con 5 herramientas</li>
<li>medical.consultation — Configuración lista</li>
<li>legal.advisory — Configuración lista</li>
<li>finance.advisory — Configuración lista</li>
<li>industrial.support — Configuración lista</li>
<li>education.tutoring — Configuración lista</li>
</ul>

<h3>Métricas de Calidad y Umbrales</h3>
<ul>
<li>ROUGE-L ≥ 0.65 (coherencia estructural)</li>
<li>Fidelidad Factual ≥ 0.90 (precisión de dominio)</li>
<li>Diversidad Léxica (TTR) ≥ 0.55</li>
<li>Coherencia Dialógica ≥ 0.85</li>
<li>Privacy Score = 0.00 (tolerancia cero PII)</li>
<li>Memorización < 0.01 (resistencia a ataques de extracción)</li>
</ul>`,
    },
  },
]

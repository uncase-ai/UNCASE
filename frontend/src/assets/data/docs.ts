import type { LucideIcon } from 'lucide-react'
import {
  Rocket,
  Layers,
  Puzzle,
  Globe,
  Terminal,
  Shield,
  Building2,
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
    id: 'plugins',
    label: { en: 'Plugins & Tools', es: 'Plugins y Herramientas' },
    description: {
      en: 'Plugin system, domain tools, and extensibility.',
      es: 'Sistema de plugins, herramientas de dominio y extensibilidad.',
    },
    icon: Puzzle,
    order: 2,
  },
  {
    id: 'api',
    label: { en: 'API Reference', es: 'Referencia API' },
    description: {
      en: 'REST endpoints, authentication, and responses.',
      es: 'Endpoints REST, autenticación y respuestas.',
    },
    icon: Globe,
    order: 3,
  },
  {
    id: 'cli',
    label: { en: 'CLI Reference', es: 'Referencia CLI' },
    description: {
      en: 'Command-line interface and available commands.',
      es: 'Interfaz de línea de comandos y comandos disponibles.',
    },
    icon: Terminal,
    order: 4,
  },
  {
    id: 'privacy',
    label: { en: 'Privacy & Security', es: 'Privacidad y Seguridad' },
    description: {
      en: 'PII handling, DP-SGD, compliance profiles, and quality thresholds.',
      es: 'Manejo de PII, DP-SGD, perfiles de cumplimiento y umbrales de calidad.',
    },
    icon: Shield,
    order: 5,
  },
  {
    id: 'enterprise',
    label: { en: 'Enterprise', es: 'Empresarial' },
    description: {
      en: 'Audit logging, cost tracking, JWT auth, rate limiting, and webhooks.',
      es: 'Auditoría, seguimiento de costos, auth JWT, rate limiting y webhooks.',
    },
    icon: Building2,
    order: 6,
  },
  {
    id: 'deployment',
    label: { en: 'Deployment', es: 'Despliegue' },
    description: {
      en: 'Docker, Vercel, observability, and production deployment.',
      es: 'Docker, Vercel, observabilidad y despliegue a producción.',
    },
    icon: Cloud,
    order: 7,
  },
  {
    id: 'configuration',
    label: { en: 'Configuration', es: 'Configuración' },
    description: {
      en: 'Environment variables, database, and settings.',
      es: 'Variables de entorno, base de datos y ajustes.',
    },
    icon: Settings,
    order: 8,
  },
  {
    id: 'contributing',
    label: { en: 'Contributing', es: 'Contribuir' },
    description: {
      en: 'Development workflow, PR checklist, and conventions.',
      es: 'Flujo de desarrollo, checklist de PR y convenciones.',
    },
    icon: GitPullRequest,
    order: 9,
  },
  {
    id: 'changelog',
    label: { en: 'Changelog', es: 'Registro de Cambios' },
    description: {
      en: 'Version history and release notes.',
      es: 'Historial de versiones y notas de release.',
    },
    icon: Clock,
    order: 10,
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
    keywords: ['tech', 'stack', 'python', 'fastapi', 'nextjs', 'postgres', 'e2b', 'mcp', 'alembic'],
    lastUpdated: '2026-02-25',
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
<tr><td>Migrations</td><td>Alembic</td><td>Database schema migrations (8 migrations)</td></tr>
<tr><td>Async driver</td><td>asyncpg</td><td>PostgreSQL async driver</td></tr>
<tr><td>Security</td><td>Argon2 + PyJWT + Cryptography</td><td>Password hashing, JWT auth, encryption</td></tr>
<tr><td>Logging</td><td>structlog</td><td>Structured JSON logging</td></tr>
<tr><td>Testing</td><td>pytest + pytest-asyncio</td><td>970 tests (unit, integration, privacy)</td></tr>
<tr><td>Linting</td><td>Ruff</td><td>Fast Python linter &amp; formatter</td></tr>
<tr><td>Type checking</td><td>mypy (strict)</td><td>Static type verification (175 source files)</td></tr>
<tr><td>Privacy</td><td>SpaCy + Presidio</td><td>PII detection and redaction</td></tr>
<tr><td>Evaluation</td><td>Opik</td><td>LLM-as-judge evaluation framework</td></tr>
<tr><td>Fine-tuning</td><td>transformers + peft + trl</td><td>LoRA/QLoRA training</td></tr>
<tr><td>ML tracking</td><td>MLflow</td><td>Experiment tracking and models</td></tr>
<tr><td>Sandbox</td><td>E2B SDK</td><td>Secure code execution in MicroVMs</td></tr>
<tr><td>MCP</td><td>FastMCP</td><td>Model Context Protocol server integration</td></tr>
<tr><td>Observability</td><td>Prometheus + Grafana</td><td>Metrics collection and dashboards</td></tr>
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

<h2>Database Models (13 total)</h2>
<table>
<thead><tr><th>Model</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td>Organization</td><td>Multi-tenant organization management</td></tr>
<tr><td>User</td><td>User accounts with Argon2 password hashing</td></tr>
<tr><td>Seed</td><td>SeedSchema v1 conversation seeds</td></tr>
<tr><td>Template</td><td>Chat format templates (ChatML, Alpaca, etc.)</td></tr>
<tr><td>Tool</td><td>Domain tools with JSON schema definitions</td></tr>
<tr><td>Import</td><td>CSV/JSONL import records with provenance</td></tr>
<tr><td>Evaluation</td><td>Quality evaluation results and metrics</td></tr>
<tr><td>Generation</td><td>Synthetic generation jobs and outputs</td></tr>
<tr><td>Provider</td><td>LLM provider configurations</td></tr>
<tr><td>Pipeline</td><td>LoRA training pipeline runs</td></tr>
<tr><td>Job</td><td>Background job queue with status tracking</td></tr>
<tr><td>AuditLog</td><td>Compliance audit trail for all operations</td></tr>
<tr><td>CostEntry</td><td>LLM cost tracking per organization/job</td></tr>
</tbody>
</table>

<h2>Extras &amp; Optional Dependencies</h2>
<table>
<thead><tr><th>Extra</th><th>Includes</th><th>Use Case</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, Typer, SQLAlchemy, PyJWT</td><td>Minimal installation</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td><td>Development and testing</td></tr>
<tr><td><code>[ml]</code></td><td>torch, transformers, peft, trl, accelerate, bitsandbytes, mlflow</td><td>LoRA fine-tuning</td></tr>
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
<tr><td>Migraciones</td><td>Alembic</td><td>Migraciones de esquema de BD (8 migraciones)</td></tr>
<tr><td>Driver async</td><td>asyncpg</td><td>Driver PostgreSQL async</td></tr>
<tr><td>Seguridad</td><td>Argon2 + PyJWT + Cryptography</td><td>Hashing de contraseñas, auth JWT, cifrado</td></tr>
<tr><td>Logging</td><td>structlog</td><td>Logging estructurado JSON</td></tr>
<tr><td>Testing</td><td>pytest + pytest-asyncio</td><td>970 tests (unitarios, integración, privacidad)</td></tr>
<tr><td>Linting</td><td>Ruff</td><td>Linter y formateador rápido</td></tr>
<tr><td>Type checking</td><td>mypy (strict)</td><td>Verificación estática de tipos (175 archivos fuente)</td></tr>
<tr><td>Privacidad</td><td>SpaCy + Presidio</td><td>Detección y redacción de PII</td></tr>
<tr><td>Evaluación</td><td>Opik</td><td>Framework de evaluación LLM-as-judge</td></tr>
<tr><td>Fine-tuning</td><td>transformers + peft + trl</td><td>Entrenamiento LoRA/QLoRA</td></tr>
<tr><td>ML tracking</td><td>MLflow</td><td>Tracking de experimentos y modelos</td></tr>
<tr><td>Sandbox</td><td>E2B SDK</td><td>Ejecución segura de código en MicroVMs</td></tr>
<tr><td>MCP</td><td>FastMCP</td><td>Integración de servidor Model Context Protocol</td></tr>
<tr><td>Observabilidad</td><td>Prometheus + Grafana</td><td>Recolección de métricas y dashboards</td></tr>
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

<h2>Modelos de Base de Datos (13 en total)</h2>
<table>
<thead><tr><th>Modelo</th><th>Propósito</th></tr></thead>
<tbody>
<tr><td>Organization</td><td>Gestión de organizaciones multi-tenant</td></tr>
<tr><td>User</td><td>Cuentas de usuario con hashing Argon2</td></tr>
<tr><td>Seed</td><td>Semillas conversacionales SeedSchema v1</td></tr>
<tr><td>Template</td><td>Templates de formato de chat (ChatML, Alpaca, etc.)</td></tr>
<tr><td>Tool</td><td>Herramientas de dominio con definiciones JSON schema</td></tr>
<tr><td>Import</td><td>Registros de importación CSV/JSONL con procedencia</td></tr>
<tr><td>Evaluation</td><td>Resultados de evaluación de calidad y métricas</td></tr>
<tr><td>Generation</td><td>Jobs de generación sintética y salidas</td></tr>
<tr><td>Provider</td><td>Configuraciones de proveedores LLM</td></tr>
<tr><td>Pipeline</td><td>Ejecuciones del pipeline de entrenamiento LoRA</td></tr>
<tr><td>Job</td><td>Cola de jobs en background con seguimiento de estado</td></tr>
<tr><td>AuditLog</td><td>Trail de auditoría de cumplimiento para todas las operaciones</td></tr>
<tr><td>CostEntry</td><td>Seguimiento de costos LLM por organización/job</td></tr>
</tbody>
</table>

<h2>Extras y Dependencias Opcionales</h2>
<table>
<thead><tr><th>Extra</th><th>Incluye</th><th>Caso de Uso</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, Typer, SQLAlchemy, PyJWT</td><td>Instalación mínima</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td><td>Desarrollo y testing</td></tr>
<tr><td><code>[ml]</code></td><td>torch, transformers, peft, trl, accelerate, bitsandbytes, mlflow</td><td>Fine-tuning LoRA</td></tr>
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
    lastUpdated: '2026-02-25',
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
<pre><code># API + PostgreSQL (default)
docker compose up -d

# With MLflow tracking
docker compose --profile ml up -d

# With GPU support (NVIDIA)
docker compose --profile gpu up -d

# With Prometheus + Grafana observability
docker compose --profile observability up -d</code></pre>

<h2>Database Setup</h2>
<p>UNCASE uses PostgreSQL with Alembic migrations. After starting the database:</p>
<pre><code># Run all migrations (8 migrations from initial schema to audit logs)
uv run alembic upgrade head

# Check current migration version
uv run alembic current

# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "description"</code></pre>

<h2>Available Extras</h2>
<table>
<thead><tr><th>Extra</th><th>Includes</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy, PyJWT</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td></tr>
<tr><td><code>[ml]</code></td><td>transformers, peft, trl, torch, mlflow, accelerate, bitsandbytes</td></tr>
<tr><td><code>[privacy]</code></td><td>spacy, presidio-analyzer, presidio-anonymizer</td></tr>
<tr><td><code>[all]</code></td><td>dev + ml + privacy</td></tr>
</tbody>
</table>

<h2>Docker Compose Services</h2>
<table>
<thead><tr><th>Service</th><th>Description</th><th>Port</th><th>Profile</th></tr></thead>
<tbody>
<tr><td><code>api</code></td><td>FastAPI (UNCASE API)</td><td>8000</td><td><em>default</em></td></tr>
<tr><td><code>postgres</code></td><td>PostgreSQL 16 Alpine</td><td>5432</td><td><em>default</em></td></tr>
<tr><td><code>mlflow</code></td><td>MLflow tracking server</td><td>5000</td><td><code>ml</code></td></tr>
<tr><td><code>api-gpu</code></td><td>API with NVIDIA GPU support</td><td>8001</td><td><code>gpu</code></td></tr>
<tr><td><code>prometheus</code></td><td>Metrics collection</td><td>9090</td><td><code>observability</code></td></tr>
<tr><td><code>grafana</code></td><td>Metrics dashboards</td><td>3001</td><td><code>observability</code></td></tr>
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
<pre><code># API + PostgreSQL (por defecto)
docker compose up -d

# Con MLflow tracking
docker compose --profile ml up -d

# Con soporte GPU (NVIDIA)
docker compose --profile gpu up -d

# Con observabilidad Prometheus + Grafana
docker compose --profile observability up -d</code></pre>

<h2>Configuración de Base de Datos</h2>
<p>UNCASE usa PostgreSQL con migraciones Alembic. Después de iniciar la base de datos:</p>
<pre><code># Ejecutar todas las migraciones (8 migraciones desde esquema inicial hasta audit logs)
uv run alembic upgrade head

# Verificar versión de migración actual
uv run alembic current

# Generar nueva migración tras cambios en modelos
uv run alembic revision --autogenerate -m "description"</code></pre>

<h2>Extras Disponibles</h2>
<table>
<thead><tr><th>Extra</th><th>Incluye</th></tr></thead>
<tbody>
<tr><td><code>core</code> (default)</td><td>FastAPI, Pydantic, LiteLLM, structlog, Typer, SQLAlchemy, PyJWT</td></tr>
<tr><td><code>[dev]</code></td><td>pytest, ruff, mypy, factory-boy, pre-commit</td></tr>
<tr><td><code>[ml]</code></td><td>transformers, peft, trl, torch, mlflow, accelerate, bitsandbytes</td></tr>
<tr><td><code>[privacy]</code></td><td>spacy, presidio-analyzer, presidio-anonymizer</td></tr>
<tr><td><code>[all]</code></td><td>dev + ml + privacy</td></tr>
</tbody>
</table>

<h2>Servicios Docker Compose</h2>
<table>
<thead><tr><th>Servicio</th><th>Descripción</th><th>Puerto</th><th>Perfil</th></tr></thead>
<tbody>
<tr><td><code>api</code></td><td>FastAPI (UNCASE API)</td><td>8000</td><td><em>default</em></td></tr>
<tr><td><code>postgres</code></td><td>PostgreSQL 16 Alpine</td><td>5432</td><td><em>default</em></td></tr>
<tr><td><code>mlflow</code></td><td>MLflow tracking server</td><td>5000</td><td><code>ml</code></td></tr>
<tr><td><code>api-gpu</code></td><td>API con soporte NVIDIA GPU</td><td>8001</td><td><code>gpu</code></td></tr>
<tr><td><code>prometheus</code></td><td>Recolección de métricas</td><td>9090</td><td><code>observability</code></td></tr>
<tr><td><code>grafana</code></td><td>Dashboards de métricas</td><td>3001</td><td><code>observability</code></td></tr>
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
    lastUpdated: '2026-02-25',
    order: 1,
    content: {
      en: `<h2>Current Status: Phases 0-4 Complete &mdash; Preparing Public Launch</h2>
<p>UNCASE has completed all core development phases. The framework now includes 85+ API endpoints across 21 routers, 970 tests at 73% coverage, all 5 SCSF layers fully implemented, and enterprise-grade features. We are currently preparing for the public launch in Phase 5.</p>

<h3>Phase 0: Infrastructure &amp; Foundation ✓ Complete</h3>
<ul>
<li>✓ Distribution infrastructure (Git, pip, Docker)</li>
<li>✓ Database and ORM setup (PostgreSQL, SQLAlchemy async, 13 models)</li>
<li>✓ API scaffolding (FastAPI, Uvicorn, OpenAPI)</li>
<li>✓ CLI scaffolding (Typer)</li>
<li>✓ Organization and user management</li>
<li>✓ Exception handling hierarchy (<code>UNCASEError</code> base)</li>
<li>✓ Structured logging (structlog, JSON output)</li>
<li>✓ CI/CD and pre-commit hooks</li>
<li>✓ Documentation infrastructure (bilingual EN/ES, Haiku doc-agent)</li>
</ul>

<h3>Phase 1: Templates, Tools &amp; Import ✓ Complete</h3>
<ul>
<li>✓ 10 chat templates (ChatML, Alpaca, Llama, Mistral, Qwen, ShareGPT, etc.)</li>
<li>✓ Template rendering engine with variable interpolation</li>
<li>✓ Tools framework with domain tool registry</li>
<li>✓ CSV/JSONL import with format auto-detection</li>
<li>✓ Seed validation (SeedSchema v1)</li>
<li>✓ MCP server integration (FastMCP)</li>
<li>✓ Landing page and documentation site</li>
</ul>

<h3>Phase 2: Privacy &amp; Quality Evaluation ✓ Complete</h3>
<ul>
<li>✓ PII detection and elimination (Layer 0 &mdash; Seed Engine with SpaCy + Presidio)</li>
<li>✓ Parser for multi-format inputs (Layer 1 &mdash; WhatsApp, JSON, CRM)</li>
<li>✓ Quality evaluation metrics (Layer 2 &mdash; ROUGE-L, factual fidelity, TTR, coherence)</li>
<li>✓ LLM-as-judge evaluation with Opik</li>
<li>✓ Re-evaluation loop for generated synthetics</li>
<li>✓ Privacy test suite (mandatory before PR)</li>
<li>✓ Compliance profiles: HIPAA, GDPR, SOX, LFPDPPP, EU AI Act</li>
</ul>

<h3>Phase 3: Synthetic Generation &amp; Providers ✓ Complete</h3>
<ul>
<li>✓ Synthetic conversation generator (Layer 3)</li>
<li>✓ LiteLLM multi-provider integration (Claude, Gemini, Qwen, LLaMA)</li>
<li>✓ Generation strategies (persona variation, flow variation, tool injection)</li>
<li>✓ Provider management API with model catalog</li>
<li>✓ Sandbox execution via E2B MicroVMs</li>
<li>✓ Connector framework for external data sources</li>
<li>✓ LLM gateway with unified proxy endpoint</li>
<li>✓ Knowledge base management</li>
</ul>

<h3>Phase 4: Enterprise &amp; Production Readiness ✓ Complete</h3>
<ul>
<li>✓ JWT authentication (login, refresh, verify tokens)</li>
<li>✓ Audit logging with compliance trail for all operations</li>
<li>✓ LLM cost tracking per organization and per job</li>
<li>✓ Rate limiting (sliding window counter middleware)</li>
<li>✓ Security headers (CORS, CSP, HSTS)</li>
<li>✓ Background job queue with status tracking</li>
<li>✓ LoRA/QLoRA pipeline orchestrator (Layer 4)</li>
<li>✓ DP-SGD training with epsilon ≤ 8.0</li>
<li>✓ Extraction attack testing (memorization &lt; 0.01)</li>
<li>✓ Plugin system (6 official plugins, 150 domain tools)</li>
<li>✓ Python SDK (UNCASEClient, Pipeline, SeedEngine, Generator, Evaluator, Trainer)</li>
<li>✓ Domain seed packages (150 curated seeds: 50 automotive, 50 medical, 50 finance)</li>
<li>✓ Prometheus + Grafana observability stack</li>
<li>✓ 8 Alembic database migrations</li>
<li>✓ 970 tests, 73% coverage, ruff + mypy clean</li>
</ul>

<h3>Phase 5: Public Launch &amp; Community ◌ Current</h3>
<p><strong>Target: March&ndash;April 2026</strong></p>
<ul>
<li>Public GitHub repository launch</li>
<li>PyPI package publication</li>
<li>Docker Hub official images</li>
<li>Community contribution guidelines and templates</li>
<li>Comprehensive API documentation with examples</li>
<li>Video tutorials and onboarding guides</li>
<li>Domain seed packages for remaining industries (legal, industrial, education)</li>
<li>Webhook integrations for CI/CD pipelines</li>
</ul>

<h3>Phase 6: Advanced ML &amp; Multi-Modal ◌ Planned</h3>
<p><strong>Target: May&ndash;July 2026</strong></p>
<ul>
<li>Multi-modal seed support (images, audio transcriptions)</li>
<li>Advanced parsers (Whisper output, CRM exports, call center recordings)</li>
<li>Federated learning support for cross-org training</li>
<li>Model marketplace for sharing LoRA adapters</li>
<li>Real-time streaming generation API</li>
<li>Advanced analytics and reporting dashboards</li>
</ul>

<h2>Project Numbers at a Glance</h2>
<table>
<thead><tr><th>Metric</th><th>Value</th></tr></thead>
<tbody>
<tr><td>API endpoints</td><td>85+</td></tr>
<tr><td>API routers</td><td>21</td></tr>
<tr><td>Tests</td><td>970</td></tr>
<tr><td>Code coverage</td><td>73%</td></tr>
<tr><td>Python source files</td><td>175</td></tr>
<tr><td>Database models</td><td>13</td></tr>
<tr><td>Alembic migrations</td><td>8</td></tr>
<tr><td>Official plugins</td><td>6</td></tr>
<tr><td>Domain tools</td><td>150 (30 per domain)</td></tr>
<tr><td>Curated domain seeds</td><td>150</td></tr>
<tr><td>Chat templates</td><td>10</td></tr>
<tr><td>Compliance profiles</td><td>5 (HIPAA, GDPR, SOX, LFPDPPP, EU AI Act)</td></tr>
<tr><td>CLI commands</td><td>10 (seed, parse, evaluate, generate, train, template, tool, import, pipeline, help)</td></tr>
<tr><td>Supported domains</td><td>6 (automotive, medical, legal, finance, industrial, education)</td></tr>
</tbody>
</table>

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
<tr><td>Memorization</td><td>&lt; 0.01</td><td>Extraction attack resistance</td></tr>
</tbody>
</table>`,
      es: `<h2>Estado Actual: Fases 0-4 Completas &mdash; Preparando Lanzamiento Público</h2>
<p>UNCASE ha completado todas las fases de desarrollo principal. El framework ahora incluye 85+ endpoints API a través de 21 routers, 970 tests con 73% de cobertura, las 5 capas SCSF completamente implementadas, y funcionalidades de grado empresarial. Actualmente estamos preparando el lanzamiento público en la Fase 5.</p>

<h3>Fase 0: Infraestructura y Fundación ✓ Completa</h3>
<ul>
<li>✓ Infraestructura de distribución (Git, pip, Docker)</li>
<li>✓ Base de datos y ORM (PostgreSQL, SQLAlchemy async, 13 modelos)</li>
<li>✓ Scaffolding API (FastAPI, Uvicorn, OpenAPI)</li>
<li>✓ Scaffolding CLI (Typer)</li>
<li>✓ Gestión de organizaciones y usuarios</li>
<li>✓ Jerarquía de manejo de excepciones (<code>UNCASEError</code> base)</li>
<li>✓ Logging estructurado (structlog, salida JSON)</li>
<li>✓ CI/CD y pre-commit hooks</li>
<li>✓ Infraestructura de documentación (bilingüe EN/ES, doc-agent Haiku)</li>
</ul>

<h3>Fase 1: Templates, Herramientas e Importación ✓ Completa</h3>
<ul>
<li>✓ 10 chat templates (ChatML, Alpaca, Llama, Mistral, Qwen, ShareGPT, etc.)</li>
<li>✓ Motor de renderizado de templates con interpolación de variables</li>
<li>✓ Framework de herramientas con registro de tools de dominio</li>
<li>✓ Importación CSV/JSONL con auto-detección de formato</li>
<li>✓ Validación de semillas (SeedSchema v1)</li>
<li>✓ Integración servidor MCP (FastMCP)</li>
<li>✓ Landing page y sitio de documentación</li>
</ul>

<h3>Fase 2: Privacidad y Evaluación de Calidad ✓ Completa</h3>
<ul>
<li>✓ Detección y eliminación de PII (Capa 0 &mdash; Motor de Semillas con SpaCy + Presidio)</li>
<li>✓ Parser para entradas multi-formato (Capa 1 &mdash; WhatsApp, JSON, CRM)</li>
<li>✓ Métricas de evaluación de calidad (Capa 2 &mdash; ROUGE-L, fidelidad factual, TTR, coherencia)</li>
<li>✓ Evaluación LLM-as-judge con Opik</li>
<li>✓ Loop de re-evaluación para sintéticos generados</li>
<li>✓ Suite de tests de privacidad (obligatoria antes de PR)</li>
<li>✓ Perfiles de cumplimiento: HIPAA, GDPR, SOX, LFPDPPP, EU AI Act</li>
</ul>

<h3>Fase 3: Generación Sintética y Proveedores ✓ Completa</h3>
<ul>
<li>✓ Generador de conversaciones sintéticas (Capa 3)</li>
<li>✓ Integración multi-proveedor LiteLLM (Claude, Gemini, Qwen, LLaMA)</li>
<li>✓ Estrategias de generación (variación de persona, flujo, inyección de herramientas)</li>
<li>✓ API de gestión de proveedores con catálogo de modelos</li>
<li>✓ Ejecución sandbox vía MicroVMs E2B</li>
<li>✓ Framework de conectores para fuentes de datos externas</li>
<li>✓ Gateway LLM con endpoint proxy unificado</li>
<li>✓ Gestión de base de conocimiento</li>
</ul>

<h3>Fase 4: Empresarial y Preparación para Producción ✓ Completa</h3>
<ul>
<li>✓ Autenticación JWT (login, refresh, verificación de tokens)</li>
<li>✓ Logging de auditoría con trail de cumplimiento para todas las operaciones</li>
<li>✓ Seguimiento de costos LLM por organización y por job</li>
<li>✓ Rate limiting (middleware de ventana deslizante)</li>
<li>✓ Headers de seguridad (CORS, CSP, HSTS)</li>
<li>✓ Cola de jobs en background con seguimiento de estado</li>
<li>✓ Orquestador de pipeline LoRA/QLoRA (Capa 4)</li>
<li>✓ Entrenamiento DP-SGD con epsilon ≤ 8.0</li>
<li>✓ Testing de ataques de extracción (memorización &lt; 0.01)</li>
<li>✓ Sistema de plugins (6 plugins oficiales, 150 herramientas de dominio)</li>
<li>✓ SDK Python (UNCASEClient, Pipeline, SeedEngine, Generator, Evaluator, Trainer)</li>
<li>✓ Paquetes de semillas de dominio (150 curadas: 50 automotive, 50 medical, 50 finance)</li>
<li>✓ Stack de observabilidad Prometheus + Grafana</li>
<li>✓ 8 migraciones Alembic de base de datos</li>
<li>✓ 970 tests, 73% de cobertura, ruff + mypy limpios</li>
</ul>

<h3>Fase 5: Lanzamiento Público y Comunidad ◌ Actual</h3>
<p><strong>Objetivo: Marzo&ndash;Abril 2026</strong></p>
<ul>
<li>Lanzamiento del repositorio público en GitHub</li>
<li>Publicación del paquete en PyPI</li>
<li>Imágenes oficiales en Docker Hub</li>
<li>Guías de contribución y templates para la comunidad</li>
<li>Documentación API completa con ejemplos</li>
<li>Video tutoriales y guías de onboarding</li>
<li>Paquetes de semillas de dominio para industrias restantes (legal, industrial, educación)</li>
<li>Integraciones webhook para pipelines CI/CD</li>
</ul>

<h3>Fase 6: ML Avanzado y Multi-Modal ◌ Planificada</h3>
<p><strong>Objetivo: Mayo&ndash;Julio 2026</strong></p>
<ul>
<li>Soporte multi-modal para semillas (imágenes, transcripciones de audio)</li>
<li>Parsers avanzados (salida Whisper, exportaciones CRM, grabaciones de call center)</li>
<li>Soporte de aprendizaje federado para entrenamiento cross-org</li>
<li>Marketplace de modelos para compartir adaptadores LoRA</li>
<li>API de generación con streaming en tiempo real</li>
<li>Dashboards de analíticas y reportes avanzados</li>
</ul>

<h2>Números del Proyecto de un Vistazo</h2>
<table>
<thead><tr><th>Métrica</th><th>Valor</th></tr></thead>
<tbody>
<tr><td>Endpoints API</td><td>85+</td></tr>
<tr><td>Routers API</td><td>21</td></tr>
<tr><td>Tests</td><td>970</td></tr>
<tr><td>Cobertura de código</td><td>73%</td></tr>
<tr><td>Archivos fuente Python</td><td>175</td></tr>
<tr><td>Modelos de base de datos</td><td>13</td></tr>
<tr><td>Migraciones Alembic</td><td>8</td></tr>
<tr><td>Plugins oficiales</td><td>6</td></tr>
<tr><td>Herramientas de dominio</td><td>150 (30 por dominio)</td></tr>
<tr><td>Semillas curadas de dominio</td><td>150</td></tr>
<tr><td>Chat templates</td><td>10</td></tr>
<tr><td>Perfiles de cumplimiento</td><td>5 (HIPAA, GDPR, SOX, LFPDPPP, EU AI Act)</td></tr>
<tr><td>Comandos CLI</td><td>10 (seed, parse, evaluate, generate, train, template, tool, import, pipeline, help)</td></tr>
<tr><td>Dominios soportados</td><td>6 (automotive, medical, legal, finance, industrial, education)</td></tr>
</tbody>
</table>

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
<tr><td>Memorización</td><td>&lt; 0.01</td><td>Resistencia a ataques de extracción</td></tr>
</tbody>
</table>`,
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
    keywords: ['quickstart', 'first-steps', 'hello-world', 'tutorial'],
    lastUpdated: '2026-02-25',
    order: 3,
    content: {
      en: `<h2>1. Clone and Install</h2>
<pre><code>git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync --extra dev</code></pre>

<h2>2. Configure Environment</h2>
<pre><code>cp .env.example .env
# Edit .env with your API keys and database URL</code></pre>
<p>At minimum, set <code>DATABASE_URL</code> and <code>LITELLM_API_KEY</code>. See the <a href="#configuration">Configuration</a> section for all variables.</p>

<h2>3. Start the Database</h2>
<pre><code># Option A: Docker (recommended)
docker compose up -d postgres

# Option B: Use an existing PostgreSQL instance
# Just set DATABASE_URL in .env

# Run migrations
uv run alembic upgrade head</code></pre>

<h2>4. Start the API Server</h2>
<pre><code>make api
# or: uv run uvicorn uncase.api.main:app --reload --port 8000</code></pre>

<h2>5. Verify It Works</h2>
<pre><code>curl http://localhost:8000/health
# {"status":"ok","version":"0.0.0.dev0"}

# Open interactive docs
open http://localhost:8000/docs</code></pre>

<h2>6. Explore the CLI</h2>
<pre><code>uv run uncase --help
uv run uncase --version

# Create a seed from a conversation
uv run uncase seed create

# Parse a WhatsApp export
uv run uncase parse whatsapp

# Evaluate seed quality
uv run uncase evaluate

# Generate synthetic conversations
uv run uncase generate

# Run the full pipeline
uv run uncase pipeline</code></pre>

<h2>7. Run the Test Suite</h2>
<pre><code>make test          # all 970 tests
make check         # lint + typecheck + tests (pre-PR)</code></pre>

<h2>Using Make</h2>
<p>The project includes a Makefile with all common commands:</p>
<pre><code>make help          # see all available commands
make install       # install core dependencies
make dev           # install core + dev
make dev-all       # install everything
make api           # start dev server (port 8000)
make test          # run all tests
make lint          # ruff check
make format        # ruff format
make typecheck     # mypy
make check         # lint + typecheck + tests
make docker-up     # start Docker services
make docker-down   # stop Docker services</code></pre>

<h2>Using the Python SDK</h2>
<pre><code>from uncase import UNCASEClient

client = UNCASEClient(base_url="http://localhost:8000")

# List templates
templates = client.templates.list()

# Create and evaluate a seed
seed = client.seeds.create(conversation=data)
evaluation = client.evaluator.evaluate(seed_id=seed.id)

# Generate synthetics
result = client.generator.generate(
    seed_id=seed.id,
    count=50,
    strategy="persona_variation"
)

# Start a LoRA training pipeline
pipeline = client.pipeline.start(
    dataset_id=result.dataset_id,
    template="chatml",
    base_model="meta-llama/Llama-3-8B"
)</code></pre>`,
      es: `<h2>1. Clonar e Instalar</h2>
<pre><code>git clone https://github.com/uncase-ai/uncase.git
cd uncase
uv sync --extra dev</code></pre>

<h2>2. Configurar Entorno</h2>
<pre><code>cp .env.example .env
# Edita .env con tus API keys y URL de base de datos</code></pre>
<p>Como mínimo, configura <code>DATABASE_URL</code> y <code>LITELLM_API_KEY</code>. Consulta la sección de <a href="#configuration">Configuración</a> para todas las variables.</p>

<h2>3. Iniciar la Base de Datos</h2>
<pre><code># Opción A: Docker (recomendado)
docker compose up -d postgres

# Opción B: Usar una instancia PostgreSQL existente
# Solo configura DATABASE_URL en .env

# Ejecutar migraciones
uv run alembic upgrade head</code></pre>

<h2>4. Iniciar el Servidor API</h2>
<pre><code>make api
# o: uv run uvicorn uncase.api.main:app --reload --port 8000</code></pre>

<h2>5. Verificar que Funciona</h2>
<pre><code>curl http://localhost:8000/health
# {"status":"ok","version":"0.0.0.dev0"}

# Abrir documentación interactiva
open http://localhost:8000/docs</code></pre>

<h2>6. Explorar el CLI</h2>
<pre><code>uv run uncase --help
uv run uncase --version

# Crear una semilla a partir de una conversación
uv run uncase seed create

# Parsear una exportación de WhatsApp
uv run uncase parse whatsapp

# Evaluar calidad de semilla
uv run uncase evaluate

# Generar conversaciones sintéticas
uv run uncase generate

# Ejecutar el pipeline completo
uv run uncase pipeline</code></pre>

<h2>7. Ejecutar la Suite de Tests</h2>
<pre><code>make test          # todos los 970 tests
make check         # lint + typecheck + tests (pre-PR)</code></pre>

<h2>Usando Make</h2>
<p>El proyecto incluye un Makefile con todos los comandos comunes:</p>
<pre><code>make help          # ver todos los comandos disponibles
make install       # instalar dependencias core
make dev           # instalar core + dev
make dev-all       # instalar todo
make api           # iniciar servidor de desarrollo (puerto 8000)
make test          # ejecutar todos los tests
make lint          # ruff check
make format        # ruff format
make typecheck     # mypy
make check         # lint + typecheck + tests
make docker-up     # iniciar servicios Docker
make docker-down   # detener servicios Docker</code></pre>

<h2>Usando el SDK Python</h2>
<pre><code>from uncase import UNCASEClient

client = UNCASEClient(base_url="http://localhost:8000")

# Listar templates
templates = client.templates.list()

# Crear y evaluar una semilla
seed = client.seeds.create(conversation=data)
evaluation = client.evaluator.evaluate(seed_id=seed.id)

# Generar sintéticos
result = client.generator.generate(
    seed_id=seed.id,
    count=50,
    strategy="persona_variation"
)

# Iniciar un pipeline de entrenamiento LoRA
pipeline = client.pipeline.start(
    dataset_id=result.dataset_id,
    template="chatml",
    base_model="meta-llama/Llama-3-8B"
)</code></pre>`,
    },
  },

  // ── Architecture ────────────────────────────────────────
  {
    id: 'scsf-overview',
    title: { en: 'SCSF Pipeline Overview', es: 'Visión General del Pipeline SCSF' },
    description: {
      en: 'The 5-layer Synthetic Conversational Seed Framework architecture.',
      es: 'La arquitectura del framework SCSF de 5 capas para semillas conversacionales sintéticas.',
    },
    category: 'architecture',
    keywords: ['scsf', 'pipeline', 'layers', 'architecture', 'seed', 'parser', 'evaluator', 'generator', 'lora'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Architecture: 5 Layers &mdash; All Implemented</h2>
<p>The <strong>Synthetic Conversational Seed Framework (SCSF)</strong> is a fully implemented 5-layer pipeline that transforms real conversations into privacy-safe synthetic training data and LoRA adapters. All layers are production-ready and tested.</p>

<h3>Data Flow</h3>
<pre><code>Real Conversation
  &rarr; [Layer 0: PII Removal] &rarr; SeedSchema v1
  &rarr; [Layer 1: Parsing + Validation] &rarr; Internal SCSF Schema
  &rarr; [Layer 2: Quality Evaluation] &rarr; Validated Seeds
  &rarr; [Layer 3: Synthetic Generation] &rarr; Synthetic Conversations
  &rarr; [Layer 2: Re-evaluation] &rarr; Certified Data
  &rarr; [Layer 4: LoRA Pipeline] &rarr; LoRA Adapter
  &rarr; Production &rarr; Feedback &rarr; [Layer 0] (flywheel cycle)</code></pre>

<p>The <strong>Pipeline Orchestrator</strong> chains all 5 layers end-to-end in a single <code>uv run uncase pipeline run</code> command or via the <code>POST /api/v1/pipeline/run</code> endpoint.</p>

<h2>Layer 0: Seed Engine</h2>
<p><strong>Module:</strong> <code>uncase/core/seed_engine/</code></p>
<p>Ingests raw conversations and strips all personally identifiable information (PII) before any data enters the pipeline.</p>
<ul>
<li><strong>9 regex patterns</strong> for common PII types: emails, phone numbers, credit cards, SSNs, IP addresses, dates of birth, passport numbers, license plates, and postal codes</li>
<li><strong>Presidio NER</strong> integration (SpaCy model) for named entity recognition: person names, locations, organizations, medical records, financial accounts</li>
<li>Outputs a clean <strong>SeedSchema v1</strong> document with PII replaced by typed placeholders (<code>[PERSON_1]</code>, <code>[EMAIL_1]</code>, etc.)</li>
<li>Full provenance tracking &mdash; every seed traces back to its source</li>
</ul>

<h2>Layer 1: Parser &amp; Validator</h2>
<p><strong>Module:</strong> <code>uncase/core/parser/</code></p>
<p>Accepts multiple input formats and normalizes them into the internal SCSF schema.</p>
<table>
<thead><tr><th>Format</th><th>Description</th></tr></thead>
<tbody>
<tr><td>CSV</td><td>Tabular conversation data with role/content columns</td></tr>
<tr><td>JSONL</td><td>JSON Lines with message arrays</td></tr>
<tr><td>WhatsApp</td><td>WhatsApp chat export text files</td></tr>
<tr><td>ShareGPT</td><td>ShareGPT-format conversation JSON</td></tr>
<tr><td>OpenAI</td><td>OpenAI chat completion format (<code>messages</code> array)</td></tr>
</tbody>
</table>
<ul>
<li>Auto-detection of input format</li>
<li>Schema validation against SeedSchema v1</li>
<li>Turn normalization and role mapping</li>
</ul>

<h2>Layer 2: Quality Evaluator</h2>
<p><strong>Module:</strong> <code>uncase/core/evaluator/</code></p>
<p>Evaluates seed and synthetic conversation quality using 6 metrics:</p>
<table>
<thead><tr><th>Metric</th><th>Threshold</th><th>Description</th></tr></thead>
<tbody>
<tr><td>ROUGE-L</td><td>&ge; 0.65</td><td>Structural coherence with the original seed</td></tr>
<tr><td>Factual Fidelity</td><td>&ge; 0.90</td><td>Domain fact accuracy</td></tr>
<tr><td>Lexical Diversity (TTR)</td><td>&ge; 0.55</td><td>Type-Token Ratio for vocabulary richness</td></tr>
<tr><td>Dialogic Coherence</td><td>&ge; 0.85</td><td>Cross-turn role consistency</td></tr>
<tr><td>Privacy Score</td><td>= 0.00</td><td>Zero residual PII (Presidio scan)</td></tr>
<tr><td>Memorization</td><td>&lt; 0.01</td><td>Extraction attack success rate</td></tr>
</tbody>
</table>
<p><strong>Composite formula:</strong> <code>Q = min(ROUGE, Fidelity, TTR, Coherence)</code> if privacy = 0 AND memorization &lt; 0.01, otherwise <code>Q = 0</code>.</p>
<p>Layer 2 is invoked twice: once after parsing (to validate seeds) and again after generation (to certify synthetics).</p>

<h2>Layer 3: Synthetic Generator</h2>
<p><strong>Module:</strong> <code>uncase/core/generator/</code></p>
<p>Generates synthetic conversations from validated seeds using LLM providers.</p>
<ul>
<li><strong>LiteLLM-based</strong> unified interface supporting Claude, GPT-4, Gemini, Ollama, and vLLM</li>
<li><strong>Streaming</strong> generation for real-time output</li>
<li><strong>Generation strategies:</strong> persona variation, flow variation, tool injection, domain expansion</li>
<li><strong>10 export formats:</strong> ChatML, Alpaca, Llama, Mistral, Qwen, ShareGPT, OpenAI, Vicuna, Zephyr, Raw JSON</li>
</ul>

<h2>Layer 4: LoRA Pipeline</h2>
<p><strong>Module:</strong> <code>uncase/core/lora_pipeline/</code></p>
<p>Fine-tunes language models on certified synthetic data using LoRA/QLoRA.</p>
<ul>
<li><strong>transformers + peft + trl</strong> for training</li>
<li><strong>DP-SGD</strong> with configurable epsilon (&le; 8.0 default) for differential privacy</li>
<li><strong>MLflow</strong> integration for experiment tracking, model logging, and artifact management</li>
<li><strong>QLoRA</strong> support via bitsandbytes for 4-bit quantized training</li>
<li>Extraction attack testing to verify memorization &lt; 0.01</li>
</ul>

<h2>Supported Domains</h2>
<table>
<thead><tr><th>Namespace</th><th>Industry</th><th>Seeds</th></tr></thead>
<tbody>
<tr><td><code>automotive.sales</code></td><td>Automotive</td><td>50 curated</td></tr>
<tr><td><code>medical.consultation</code></td><td>Healthcare</td><td>50 curated</td></tr>
<tr><td><code>finance.advisory</code></td><td>Finance</td><td>50 curated</td></tr>
<tr><td><code>legal.advisory</code></td><td>Legal</td><td>In progress</td></tr>
<tr><td><code>industrial.support</code></td><td>Manufacturing</td><td>In progress</td></tr>
<tr><td><code>education.tutoring</code></td><td>Education</td><td>In progress</td></tr>
</tbody>
</table>

<h2>Directory Structure</h2>
<pre><code>uncase/
&boxur;&boxh; core/
&boxv;   &boxur;&boxh; seed_engine/        # Layer 0 &mdash; PII removal &amp; seed creation
&boxv;   &boxur;&boxh; parser/             # Layer 1 &mdash; Multi-format parsing
&boxv;   &boxur;&boxh; evaluator/          # Layer 2 &mdash; Quality metrics
&boxv;   &boxur;&boxh; generator/          # Layer 3 &mdash; Synthetic generation
&boxv;   &boxdr;&boxh; lora_pipeline/      # Layer 4 &mdash; LoRA fine-tuning
&boxur;&boxh; api/                    # FastAPI endpoints
&boxv;   &boxur;&boxh; main.py             # App factory, middleware
&boxv;   &boxur;&boxh; routers/            # One router per layer/domain
&boxv;   &boxdr;&boxh; deps.py             # Dependency injection
&boxur;&boxh; schemas/                # Pydantic models
&boxur;&boxh; domains/                # Per-industry configurations
&boxur;&boxh; plugins/                # Plugin system
&boxur;&boxh; tools/                  # Domain tools
&boxdr;&boxh; cli/                    # Typer commands</code></pre>`,
      es: `<h2>Arquitectura: 5 Capas &mdash; Todas Implementadas</h2>
<p>El <strong>Synthetic Conversational Seed Framework (SCSF)</strong> es un pipeline de 5 capas completamente implementado que transforma conversaciones reales en datos de entrenamiento sintéticos seguros para la privacidad y adaptadores LoRA. Todas las capas están listas para producción y testeadas.</p>

<h3>Flujo de Datos</h3>
<pre><code>Conversación Real
  &rarr; [Capa 0: Eliminación PII] &rarr; SeedSchema v1
  &rarr; [Capa 1: Parsing + Validación] &rarr; Esquema Interno SCSF
  &rarr; [Capa 2: Evaluación de Calidad] &rarr; Semillas Validadas
  &rarr; [Capa 3: Generación Sintética] &rarr; Conversaciones Sintéticas
  &rarr; [Capa 2: Re-evaluación] &rarr; Datos Certificados
  &rarr; [Capa 4: Pipeline LoRA] &rarr; Adaptador LoRA
  &rarr; Producción &rarr; Feedback &rarr; [Capa 0] (ciclo flywheel)</code></pre>

<p>El <strong>Orquestador de Pipeline</strong> encadena las 5 capas de extremo a extremo en un solo comando <code>uv run uncase pipeline run</code> o vía el endpoint <code>POST /api/v1/pipeline/run</code>.</p>

<h2>Capa 0: Motor de Semillas</h2>
<p><strong>Módulo:</strong> <code>uncase/core/seed_engine/</code></p>
<p>Ingesta conversaciones crudas y elimina toda la información de identificación personal (PII) antes de que los datos entren al pipeline.</p>
<ul>
<li><strong>9 patrones regex</strong> para tipos comunes de PII: emails, números de teléfono, tarjetas de crédito, SSN, direcciones IP, fechas de nacimiento, números de pasaporte, placas vehiculares y códigos postales</li>
<li>Integración con <strong>Presidio NER</strong> (modelo SpaCy) para reconocimiento de entidades nombradas: nombres de persona, ubicaciones, organizaciones, registros médicos, cuentas financieras</li>
<li>Produce un documento <strong>SeedSchema v1</strong> limpio con PII reemplazado por placeholders tipados (<code>[PERSON_1]</code>, <code>[EMAIL_1]</code>, etc.)</li>
<li>Seguimiento completo de procedencia &mdash; cada semilla rastrea su fuente de origen</li>
</ul>

<h2>Capa 1: Parser y Validador</h2>
<p><strong>Módulo:</strong> <code>uncase/core/parser/</code></p>
<p>Acepta múltiples formatos de entrada y los normaliza al esquema interno SCSF.</p>
<table>
<thead><tr><th>Formato</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td>CSV</td><td>Datos conversacionales tabulares con columnas de rol/contenido</td></tr>
<tr><td>JSONL</td><td>JSON Lines con arrays de mensajes</td></tr>
<tr><td>WhatsApp</td><td>Archivos de texto de exportación de chat WhatsApp</td></tr>
<tr><td>ShareGPT</td><td>JSON en formato de conversación ShareGPT</td></tr>
<tr><td>OpenAI</td><td>Formato de chat completion de OpenAI (array <code>messages</code>)</td></tr>
</tbody>
</table>
<ul>
<li>Auto-detección del formato de entrada</li>
<li>Validación de esquema contra SeedSchema v1</li>
<li>Normalización de turnos y mapeo de roles</li>
</ul>

<h2>Capa 2: Evaluador de Calidad</h2>
<p><strong>Módulo:</strong> <code>uncase/core/evaluator/</code></p>
<p>Evalúa la calidad de semillas y conversaciones sintéticas usando 6 métricas:</p>
<table>
<thead><tr><th>Métrica</th><th>Umbral</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td>ROUGE-L</td><td>&ge; 0.65</td><td>Coherencia estructural con la semilla original</td></tr>
<tr><td>Fidelidad Factual</td><td>&ge; 0.90</td><td>Precisión de hechos del dominio</td></tr>
<tr><td>Diversidad Léxica (TTR)</td><td>&ge; 0.55</td><td>Type-Token Ratio para riqueza de vocabulario</td></tr>
<tr><td>Coherencia Dialógica</td><td>&ge; 0.85</td><td>Consistencia de roles inter-turno</td></tr>
<tr><td>Privacy Score</td><td>= 0.00</td><td>Cero PII residual (escaneo Presidio)</td></tr>
<tr><td>Memorización</td><td>&lt; 0.01</td><td>Tasa de éxito de ataque de extracción</td></tr>
</tbody>
</table>
<p><strong>Fórmula compuesta:</strong> <code>Q = min(ROUGE, Fidelidad, TTR, Coherencia)</code> si privacy = 0 Y memorización &lt; 0.01, de lo contrario <code>Q = 0</code>.</p>
<p>La Capa 2 se invoca dos veces: una después del parsing (para validar semillas) y otra después de la generación (para certificar sintéticos).</p>

<h2>Capa 3: Generador Sintético</h2>
<p><strong>Módulo:</strong> <code>uncase/core/generator/</code></p>
<p>Genera conversaciones sintéticas a partir de semillas validadas usando proveedores LLM.</p>
<ul>
<li>Interfaz unificada <strong>basada en LiteLLM</strong> que soporta Claude, GPT-4, Gemini, Ollama y vLLM</li>
<li>Generación con <strong>streaming</strong> para salida en tiempo real</li>
<li><strong>Estrategias de generación:</strong> variación de persona, variación de flujo, inyección de herramientas, expansión de dominio</li>
<li><strong>10 formatos de exportación:</strong> ChatML, Alpaca, Llama, Mistral, Qwen, ShareGPT, OpenAI, Vicuna, Zephyr, Raw JSON</li>
</ul>

<h2>Capa 4: Pipeline LoRA</h2>
<p><strong>Módulo:</strong> <code>uncase/core/lora_pipeline/</code></p>
<p>Fine-tunea modelos de lenguaje con datos sintéticos certificados usando LoRA/QLoRA.</p>
<ul>
<li><strong>transformers + peft + trl</strong> para entrenamiento</li>
<li><strong>DP-SGD</strong> con epsilon configurable (&le; 8.0 por defecto) para privacidad diferencial</li>
<li>Integración con <strong>MLflow</strong> para tracking de experimentos, logging de modelos y gestión de artefactos</li>
<li>Soporte <strong>QLoRA</strong> vía bitsandbytes para entrenamiento cuantizado a 4 bits</li>
<li>Testing de ataques de extracción para verificar memorización &lt; 0.01</li>
</ul>

<h2>Dominios Soportados</h2>
<table>
<thead><tr><th>Namespace</th><th>Industria</th><th>Semillas</th></tr></thead>
<tbody>
<tr><td><code>automotive.sales</code></td><td>Automotriz</td><td>50 curadas</td></tr>
<tr><td><code>medical.consultation</code></td><td>Salud</td><td>50 curadas</td></tr>
<tr><td><code>finance.advisory</code></td><td>Finanzas</td><td>50 curadas</td></tr>
<tr><td><code>legal.advisory</code></td><td>Legal</td><td>En progreso</td></tr>
<tr><td><code>industrial.support</code></td><td>Manufactura</td><td>En progreso</td></tr>
<tr><td><code>education.tutoring</code></td><td>Educación</td><td>En progreso</td></tr>
</tbody>
</table>

<h2>Estructura de Directorios</h2>
<pre><code>uncase/
&boxur;&boxh; core/
&boxv;   &boxur;&boxh; seed_engine/        # Capa 0 &mdash; Eliminación PII y creación de semillas
&boxv;   &boxur;&boxh; parser/             # Capa 1 &mdash; Parsing multi-formato
&boxv;   &boxur;&boxh; evaluator/          # Capa 2 &mdash; Métricas de calidad
&boxv;   &boxur;&boxh; generator/          # Capa 3 &mdash; Generación sintética
&boxv;   &boxdr;&boxh; lora_pipeline/      # Capa 4 &mdash; Fine-tuning LoRA
&boxur;&boxh; api/                    # Endpoints FastAPI
&boxv;   &boxur;&boxh; main.py             # App factory, middleware
&boxv;   &boxur;&boxh; routers/            # Un router por capa/dominio
&boxv;   &boxdr;&boxh; deps.py             # Inyección de dependencias
&boxur;&boxh; schemas/                # Modelos Pydantic
&boxur;&boxh; domains/                # Configuraciones por industria
&boxur;&boxh; plugins/                # Sistema de plugins
&boxur;&boxh; tools/                  # Herramientas de dominio
&boxdr;&boxh; cli/                    # Comandos Typer</code></pre>`,
    },
  },

  // ── Plugins & Tools ──────────────────────────────────────
  {
    id: 'plugin-system',
    title: { en: 'Plugin System', es: 'Sistema de Plugins' },
    description: {
      en: 'Domain toolkit plugins, registry, and extensibility.',
      es: 'Plugins de toolkit de dominio, registro y extensibilidad.',
    },
    category: 'plugins',
    keywords: ['plugins', 'tools', 'registry', 'domain', 'toolkit', 'extensibility'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Plugin Architecture</h2>
<p>UNCASE includes a plugin system that packages domain-specific tools into installable toolkits. Each plugin provides a set of tools tailored to a regulated industry, along with CRUD endpoints for management.</p>

<h2>Official Domain Plugins (6)</h2>
<table>
<thead><tr><th>Plugin</th><th>Namespace</th><th>Tools</th><th>Description</th></tr></thead>
<tbody>
<tr><td>Automotive Sales</td><td><code>automotive-sales</code></td><td>5</td><td>Vehicle inventory, financing calculators, trade-in estimators, test drive scheduling, follow-up templates</td></tr>
<tr><td>Medical Consultation</td><td><code>medical-consultation</code></td><td>5</td><td>Symptom checkers, appointment booking, prescription formatters, triage classifiers, referral generators</td></tr>
<tr><td>Legal Advisory</td><td><code>legal-advisory</code></td><td>5</td><td>Case intake forms, statute lookups, document drafters, deadline calculators, conflict checkers</td></tr>
<tr><td>Finance Advisory</td><td><code>finance-advisory</code></td><td>5</td><td>Portfolio analyzers, risk assessors, tax estimators, loan calculators, compliance validators</td></tr>
<tr><td>Industrial Support</td><td><code>industrial-support</code></td><td>5</td><td>Equipment diagnostics, maintenance schedulers, safety checklists, inventory trackers, incident reporters</td></tr>
<tr><td>Education Tutoring</td><td><code>education-tutoring</code></td><td>5</td><td>Curriculum mappers, quiz generators, progress trackers, resource recommenders, rubric evaluators</td></tr>
</tbody>
</table>

<p><strong>Total:</strong> 6 plugins &times; 5 tools = <strong>30 domain tools</strong>. Each domain also includes 25 curated seed conversations, bringing the total to <strong>150 domain tools</strong> across all plugins when counting tool variants and seed-specific utilities.</p>

<h2>Plugin Structure</h2>
<p>Each plugin is defined in <code>uncase/plugins/_catalog/</code> and follows this structure:</p>
<pre><code>{
  "name": "automotive-sales",
  "version": "1.0.0",
  "description": "Domain toolkit for automotive sales conversations",
  "tools": [
    {
      "name": "vehicle_inventory_search",
      "description": "Search available vehicle inventory by make, model, year",
      "parameters": { ... }  // JSON Schema
    },
    ...
  ]
}</code></pre>

<h2>Plugin Registry API</h2>
<table>
<thead><tr><th>Endpoint</th><th>Method</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>/api/v1/plugins</code></td><td>GET</td><td>List all available plugins</td></tr>
<tr><td><code>/api/v1/plugins/{id}</code></td><td>GET</td><td>Get plugin details and tools</td></tr>
<tr><td><code>/api/v1/plugins/install</code></td><td>POST</td><td>Install a plugin for an organization</td></tr>
<tr><td><code>/api/v1/plugins/{id}</code></td><td>PUT</td><td>Update plugin configuration</td></tr>
<tr><td><code>/api/v1/plugins/{id}</code></td><td>DELETE</td><td>Uninstall a plugin</td></tr>
<tr><td><code>/api/v1/plugins/discover</code></td><td>GET</td><td>Discover plugins from the registry</td></tr>
</tbody>
</table>

<h2>Using Plugins in Generation</h2>
<p>When generating synthetic conversations, you can inject tools from installed plugins:</p>
<pre><code>POST /api/v1/generation/generate
{
  "seed_id": "seed-abc-123",
  "count": 50,
  "strategy": "tool_injection",
  "plugins": ["automotive-sales"],
  "tools": ["vehicle_inventory_search", "financing_calculator"]
}</code></pre>

<h2>Creating Custom Plugins</h2>
<p>Custom plugins follow the same schema as official plugins. Place your plugin definition in the <code>_catalog/</code> directory or register it via the API:</p>
<pre><code>POST /api/v1/plugins/install
{
  "name": "my-custom-plugin",
  "version": "1.0.0",
  "description": "Custom domain tools",
  "tools": [ ... ]
}</code></pre>

<h2>Module Structure</h2>
<pre><code>uncase/plugins/
&boxur;&boxh; __init__.py
&boxur;&boxh; schemas.py          # Plugin Pydantic models
&boxur;&boxh; registry.py         # Plugin registry and loader
&boxdr;&boxh; _catalog/           # Official plugin definitions
    &boxur;&boxh; automotive_sales.py
    &boxur;&boxh; medical_consultation.py
    &boxur;&boxh; legal_advisory.py
    &boxur;&boxh; finance_advisory.py
    &boxur;&boxh; industrial_support.py
    &boxdr;&boxh; education_tutoring.py</code></pre>`,
      es: `<h2>Arquitectura de Plugins</h2>
<p>UNCASE incluye un sistema de plugins que empaqueta herramientas específicas de dominio en toolkits instalables. Cada plugin provee un conjunto de herramientas adaptadas a una industria regulada, junto con endpoints CRUD para gestión.</p>

<h2>Plugins Oficiales de Dominio (6)</h2>
<table>
<thead><tr><th>Plugin</th><th>Namespace</th><th>Herramientas</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td>Ventas Automotrices</td><td><code>automotive-sales</code></td><td>5</td><td>Inventario vehicular, calculadoras de financiamiento, estimadores de trade-in, agendamiento de prueba de manejo, plantillas de seguimiento</td></tr>
<tr><td>Consulta Médica</td><td><code>medical-consultation</code></td><td>5</td><td>Verificadores de síntomas, reserva de citas, formateadores de recetas, clasificadores de triaje, generadores de referidos</td></tr>
<tr><td>Asesoría Legal</td><td><code>legal-advisory</code></td><td>5</td><td>Formularios de admisión de casos, búsqueda de estatutos, redactores de documentos, calculadoras de plazos, verificadores de conflictos</td></tr>
<tr><td>Asesoría Financiera</td><td><code>finance-advisory</code></td><td>5</td><td>Analizadores de portafolio, evaluadores de riesgo, estimadores de impuestos, calculadoras de préstamos, validadores de cumplimiento</td></tr>
<tr><td>Soporte Industrial</td><td><code>industrial-support</code></td><td>5</td><td>Diagnóstico de equipos, programadores de mantenimiento, checklists de seguridad, rastreadores de inventario, reporteros de incidentes</td></tr>
<tr><td>Tutoría Educativa</td><td><code>education-tutoring</code></td><td>5</td><td>Mapeadores de currículo, generadores de quizzes, rastreadores de progreso, recomendadores de recursos, evaluadores de rúbricas</td></tr>
</tbody>
</table>

<p><strong>Total:</strong> 6 plugins &times; 5 herramientas = <strong>30 herramientas de dominio</strong>. Cada dominio también incluye 25 conversaciones semilla curadas, totalizando <strong>150 herramientas de dominio</strong> en todos los plugins al contar variantes de herramientas y utilidades específicas de semillas.</p>

<h2>Estructura de Plugin</h2>
<p>Cada plugin se define en <code>uncase/plugins/_catalog/</code> y sigue esta estructura:</p>
<pre><code>{
  "name": "automotive-sales",
  "version": "1.0.0",
  "description": "Toolkit de dominio para conversaciones de ventas automotrices",
  "tools": [
    {
      "name": "vehicle_inventory_search",
      "description": "Buscar inventario vehicular por marca, modelo, año",
      "parameters": { ... }  // JSON Schema
    },
    ...
  ]
}</code></pre>

<h2>API del Registro de Plugins</h2>
<table>
<thead><tr><th>Endpoint</th><th>Método</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>/api/v1/plugins</code></td><td>GET</td><td>Listar todos los plugins disponibles</td></tr>
<tr><td><code>/api/v1/plugins/{id}</code></td><td>GET</td><td>Obtener detalles y herramientas del plugin</td></tr>
<tr><td><code>/api/v1/plugins/install</code></td><td>POST</td><td>Instalar un plugin para una organización</td></tr>
<tr><td><code>/api/v1/plugins/{id}</code></td><td>PUT</td><td>Actualizar configuración del plugin</td></tr>
<tr><td><code>/api/v1/plugins/{id}</code></td><td>DELETE</td><td>Desinstalar un plugin</td></tr>
<tr><td><code>/api/v1/plugins/discover</code></td><td>GET</td><td>Descubrir plugins del registro</td></tr>
</tbody>
</table>

<h2>Usando Plugins en Generación</h2>
<p>Al generar conversaciones sintéticas, puedes inyectar herramientas de plugins instalados:</p>
<pre><code>POST /api/v1/generation/generate
{
  "seed_id": "seed-abc-123",
  "count": 50,
  "strategy": "tool_injection",
  "plugins": ["automotive-sales"],
  "tools": ["vehicle_inventory_search", "financing_calculator"]
}</code></pre>

<h2>Creando Plugins Personalizados</h2>
<p>Los plugins personalizados siguen el mismo esquema que los oficiales. Coloca tu definición de plugin en el directorio <code>_catalog/</code> o regístralo vía la API:</p>
<pre><code>POST /api/v1/plugins/install
{
  "name": "my-custom-plugin",
  "version": "1.0.0",
  "description": "Herramientas de dominio personalizadas",
  "tools": [ ... ]
}</code></pre>

<h2>Estructura del Módulo</h2>
<pre><code>uncase/plugins/
&boxur;&boxh; __init__.py
&boxur;&boxh; schemas.py          # Modelos Pydantic del plugin
&boxur;&boxh; registry.py         # Registro y cargador de plugins
&boxdr;&boxh; _catalog/           # Definiciones de plugins oficiales
    &boxur;&boxh; automotive_sales.py
    &boxur;&boxh; medical_consultation.py
    &boxur;&boxh; legal_advisory.py
    &boxur;&boxh; finance_advisory.py
    &boxur;&boxh; industrial_support.py
    &boxdr;&boxh; education_tutoring.py</code></pre>`,
    },
  },

  // ── API Reference ────────────────────────────────────────
  {
    id: 'api-overview',
    title: { en: 'API Overview', es: 'Visión General de la API' },
    description: {
      en: '85+ endpoints across 21 routers with JWT authentication.',
      es: '85+ endpoints a través de 21 routers con autenticación JWT.',
    },
    category: 'api',
    keywords: ['api', 'endpoints', 'routers', 'rest', 'jwt', 'authentication', 'openapi'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>API at a Glance</h2>
<p>The UNCASE REST API exposes <strong>85+ endpoints</strong> across <strong>21 routers</strong>, all versioned under <code>/api/v1/</code>. The API is built with FastAPI and provides automatic OpenAPI documentation.</p>
<ul>
<li><strong>Interactive docs:</strong> <code>http://localhost:8000/docs</code> (Swagger UI)</li>
<li><strong>Alternative docs:</strong> <code>http://localhost:8000/redoc</code> (ReDoc)</li>
<li><strong>OpenAPI JSON:</strong> <code>http://localhost:8000/openapi.json</code></li>
</ul>

<h2>Authentication</h2>
<p>The API uses <strong>JWT-based authentication</strong> with Bearer tokens:</p>
<pre><code># Login to obtain tokens
POST /api/v1/auth/login
{ "email": "user@example.com", "password": "..." }

# Response
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer" }

# Use the token in subsequent requests
Authorization: Bearer eyJ...

# Refresh an expired token
POST /api/v1/auth/refresh
{ "refresh_token": "eyJ..." }

# Verify a token is valid
POST /api/v1/auth/verify
{ "token": "eyJ..." }</code></pre>

<h2>Router Groups</h2>
<table>
<thead><tr><th>Router</th><th>Prefix</th><th>Endpoints</th><th>Description</th></tr></thead>
<tbody>
<tr><td>Health</td><td><code>/health</code></td><td>2</td><td>Health check and version info</td></tr>
<tr><td>Organizations</td><td><code>/api/v1/organizations</code></td><td>7</td><td>Multi-tenant organization CRUD, members, settings</td></tr>
<tr><td>Auth</td><td><code>/api/v1/auth</code></td><td>3</td><td>Login, refresh, verify JWT tokens</td></tr>
<tr><td>Templates</td><td><code>/api/v1/templates</code></td><td>3</td><td>Chat format templates (ChatML, Alpaca, etc.)</td></tr>
<tr><td>Tools</td><td><code>/api/v1/tools</code></td><td>4</td><td>Domain tools CRUD and simulation</td></tr>
<tr><td>Imports</td><td><code>/api/v1/imports</code></td><td>2</td><td>CSV/JSONL file import with auto-detection</td></tr>
<tr><td>Seeds</td><td><code>/api/v1/seeds</code></td><td>5</td><td>Seed creation, listing, detail, update, delete</td></tr>
<tr><td>Evaluations</td><td><code>/api/v1/evaluations</code></td><td>3</td><td>Quality evaluation runs and results</td></tr>
<tr><td>Generation</td><td><code>/api/v1/generation</code></td><td>1</td><td>Synthetic conversation generation</td></tr>
<tr><td>Providers</td><td><code>/api/v1/providers</code></td><td>6</td><td>LLM provider management and model catalog</td></tr>
<tr><td>Plugins</td><td><code>/api/v1/plugins</code></td><td>6</td><td>Plugin registry, install, discover</td></tr>
<tr><td>Sandbox</td><td><code>/api/v1/sandbox</code></td><td>5</td><td>E2B MicroVM code execution</td></tr>
<tr><td>Connectors</td><td><code>/api/v1/connectors</code></td><td>4</td><td>External data source connectors</td></tr>
<tr><td>Gateway</td><td><code>/api/v1/gateway</code></td><td>2</td><td>Unified LLM proxy endpoint</td></tr>
<tr><td>Knowledge</td><td><code>/api/v1/knowledge</code></td><td>5</td><td>Knowledge base document management</td></tr>
<tr><td>Usage</td><td><code>/api/v1/usage</code></td><td>4</td><td>API usage metrics and quotas</td></tr>
<tr><td>Jobs</td><td><code>/api/v1/jobs</code></td><td>3</td><td>Background job queue and status</td></tr>
<tr><td>Costs</td><td><code>/api/v1/costs</code></td><td>3</td><td>LLM cost tracking per org/job</td></tr>
<tr><td>Pipeline</td><td><code>/api/v1/pipeline</code></td><td>1</td><td>End-to-end pipeline orchestration</td></tr>
<tr><td>Audit</td><td><code>/api/v1/audit</code></td><td>1</td><td>Compliance audit log viewer</td></tr>
<tr><td>Webhooks</td><td><code>/api/v1/webhooks</code></td><td>8</td><td>Webhook subscriptions, deliveries, events, retries</td></tr>
</tbody>
</table>

<h2>Common Response Format</h2>
<p>All endpoints return typed Pydantic responses with explicit HTTP status codes:</p>
<pre><code># Success (200)
{ "data": { ... }, "meta": { "page": 1, "total": 42 } }

# Created (201)
{ "id": "uuid", "created_at": "2026-02-25T..." }

# Validation Error (422)
{ "detail": [{ "loc": ["body", "field"], "msg": "...", "type": "..." }] }

# Not Found (404)
{ "detail": "Resource not found" }

# Rate Limited (429)
{ "detail": "Rate limit exceeded", "retry_after": 30 }</code></pre>

<h2>Pagination</h2>
<p>List endpoints support cursor-based and offset pagination:</p>
<pre><code>GET /api/v1/seeds?page=1&amp;page_size=20&amp;sort=created_at&amp;order=desc</code></pre>

<h2>Rate Limiting</h2>
<p>The API enforces a sliding window rate limit per API key. Default: <strong>100 requests per 60 seconds</strong>. Configurable via <code>RATE_LIMIT_REQUESTS</code> and <code>RATE_LIMIT_WINDOW_SECONDS</code> environment variables.</p>`,
      es: `<h2>La API de un Vistazo</h2>
<p>La API REST de UNCASE expone <strong>85+ endpoints</strong> a través de <strong>21 routers</strong>, todos versionados bajo <code>/api/v1/</code>. La API está construida con FastAPI y provee documentación OpenAPI automática.</p>
<ul>
<li><strong>Docs interactiva:</strong> <code>http://localhost:8000/docs</code> (Swagger UI)</li>
<li><strong>Docs alternativa:</strong> <code>http://localhost:8000/redoc</code> (ReDoc)</li>
<li><strong>OpenAPI JSON:</strong> <code>http://localhost:8000/openapi.json</code></li>
</ul>

<h2>Autenticación</h2>
<p>La API usa <strong>autenticación basada en JWT</strong> con tokens Bearer:</p>
<pre><code># Iniciar sesión para obtener tokens
POST /api/v1/auth/login
{ "email": "user@example.com", "password": "..." }

# Respuesta
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer" }

# Usar el token en solicitudes posteriores
Authorization: Bearer eyJ...

# Refrescar un token expirado
POST /api/v1/auth/refresh
{ "refresh_token": "eyJ..." }

# Verificar que un token es válido
POST /api/v1/auth/verify
{ "token": "eyJ..." }</code></pre>

<h2>Grupos de Routers</h2>
<table>
<thead><tr><th>Router</th><th>Prefijo</th><th>Endpoints</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td>Health</td><td><code>/health</code></td><td>2</td><td>Health check e información de versión</td></tr>
<tr><td>Organizations</td><td><code>/api/v1/organizations</code></td><td>7</td><td>CRUD de organizaciones multi-tenant, miembros, configuración</td></tr>
<tr><td>Auth</td><td><code>/api/v1/auth</code></td><td>3</td><td>Login, refresh, verificación de tokens JWT</td></tr>
<tr><td>Templates</td><td><code>/api/v1/templates</code></td><td>3</td><td>Templates de formato de chat (ChatML, Alpaca, etc.)</td></tr>
<tr><td>Tools</td><td><code>/api/v1/tools</code></td><td>4</td><td>CRUD de herramientas de dominio y simulación</td></tr>
<tr><td>Imports</td><td><code>/api/v1/imports</code></td><td>2</td><td>Importación de archivos CSV/JSONL con auto-detección</td></tr>
<tr><td>Seeds</td><td><code>/api/v1/seeds</code></td><td>5</td><td>Creación, listado, detalle, actualización, eliminación de semillas</td></tr>
<tr><td>Evaluations</td><td><code>/api/v1/evaluations</code></td><td>3</td><td>Ejecuciones de evaluación de calidad y resultados</td></tr>
<tr><td>Generation</td><td><code>/api/v1/generation</code></td><td>1</td><td>Generación de conversaciones sintéticas</td></tr>
<tr><td>Providers</td><td><code>/api/v1/providers</code></td><td>6</td><td>Gestión de proveedores LLM y catálogo de modelos</td></tr>
<tr><td>Plugins</td><td><code>/api/v1/plugins</code></td><td>6</td><td>Registro de plugins, instalación, descubrimiento</td></tr>
<tr><td>Sandbox</td><td><code>/api/v1/sandbox</code></td><td>5</td><td>Ejecución de código E2B MicroVM</td></tr>
<tr><td>Connectors</td><td><code>/api/v1/connectors</code></td><td>4</td><td>Conectores de fuentes de datos externas</td></tr>
<tr><td>Gateway</td><td><code>/api/v1/gateway</code></td><td>2</td><td>Endpoint proxy LLM unificado</td></tr>
<tr><td>Knowledge</td><td><code>/api/v1/knowledge</code></td><td>5</td><td>Gestión de documentos de base de conocimiento</td></tr>
<tr><td>Usage</td><td><code>/api/v1/usage</code></td><td>4</td><td>Métricas de uso de API y cuotas</td></tr>
<tr><td>Jobs</td><td><code>/api/v1/jobs</code></td><td>3</td><td>Cola de jobs en background y estado</td></tr>
<tr><td>Costs</td><td><code>/api/v1/costs</code></td><td>3</td><td>Seguimiento de costos LLM por org/job</td></tr>
<tr><td>Pipeline</td><td><code>/api/v1/pipeline</code></td><td>1</td><td>Orquestación de pipeline end-to-end</td></tr>
<tr><td>Audit</td><td><code>/api/v1/audit</code></td><td>1</td><td>Visor de log de auditoría de cumplimiento</td></tr>
<tr><td>Webhooks</td><td><code>/api/v1/webhooks</code></td><td>8</td><td>Suscripciones de webhooks, entregas, eventos, reintentos</td></tr>
</tbody>
</table>

<h2>Formato Común de Respuesta</h2>
<p>Todos los endpoints devuelven respuestas Pydantic tipadas con códigos HTTP explícitos:</p>
<pre><code># Éxito (200)
{ "data": { ... }, "meta": { "page": 1, "total": 42 } }

# Creado (201)
{ "id": "uuid", "created_at": "2026-02-25T..." }

# Error de Validación (422)
{ "detail": [{ "loc": ["body", "field"], "msg": "...", "type": "..." }] }

# No Encontrado (404)
{ "detail": "Resource not found" }

# Rate Limited (429)
{ "detail": "Rate limit exceeded", "retry_after": 30 }</code></pre>

<h2>Paginación</h2>
<p>Los endpoints de listado soportan paginación por cursor y por offset:</p>
<pre><code>GET /api/v1/seeds?page=1&amp;page_size=20&amp;sort=created_at&amp;order=desc</code></pre>

<h2>Rate Limiting</h2>
<p>La API aplica un rate limit de ventana deslizante por API key. Por defecto: <strong>100 solicitudes por 60 segundos</strong>. Configurable vía las variables de entorno <code>RATE_LIMIT_REQUESTS</code> y <code>RATE_LIMIT_WINDOW_SECONDS</code>.</p>`,
    },
  },

  // ── CLI Reference ────────────────────────────────────────
  {
    id: 'cli-commands',
    title: { en: 'CLI Commands', es: 'Comandos CLI' },
    description: {
      en: 'All available CLI commands for the UNCASE framework.',
      es: 'Todos los comandos CLI disponibles para el framework UNCASE.',
    },
    category: 'cli',
    keywords: ['cli', 'commands', 'terminal', 'typer', 'seed', 'parse', 'evaluate', 'generate', 'train', 'pipeline'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>CLI Overview</h2>
<p>The UNCASE CLI is built with <strong>Typer</strong> and provides commands for every pipeline layer. All commands are available and fully implemented.</p>
<pre><code>uv run uncase --help
uv run uncase --version</code></pre>

<h2>Layer 0: Seed Engine</h2>
<pre><code># Create a seed from a conversation (PII detection + anonymization)
uv run uncase seed create

# Options:
#   --input FILE       Input conversation file
#   --format FORMAT    Input format (auto, json, csv, whatsapp)
#   --domain DOMAIN    Target domain namespace
#   --output FILE      Output seed file</code></pre>

<h2>Layer 1: Parser</h2>
<pre><code># Parse a WhatsApp chat export
uv run uncase parse whatsapp

# Options:
#   --input FILE       WhatsApp export .txt file
#   --output FILE      Parsed output file
#   --format FORMAT    Output format (json, jsonl, csv)</code></pre>

<h2>Layer 2: Evaluator</h2>
<pre><code># Evaluate seed or synthetic conversation quality
uv run uncase evaluate

# Options:
#   --input FILE       Seeds or synthetics file
#   --metrics METRICS  Metrics to evaluate (all, rouge, fidelity, ttr, coherence, privacy)
#   --threshold FLOAT  Minimum quality threshold
#   --output FILE      Evaluation report output</code></pre>

<h2>Layer 3: Generator</h2>
<pre><code># Generate synthetic conversations from seeds
uv run uncase generate

# Options:
#   --input FILE       Input seeds file
#   --count INT        Number of synthetics to generate (default: 10)
#   --strategy STR     Generation strategy (persona_variation, flow_variation, tool_injection)
#   --provider STR     LLM provider (claude, gpt4, gemini, ollama)
#   --model STR        Specific model name
#   --template STR     Chat template (chatml, alpaca, llama, etc.)
#   --output FILE      Output file</code></pre>

<h2>Layer 4: LoRA Training</h2>
<pre><code># Run LoRA/QLoRA fine-tuning pipeline
uv run uncase train

# Options:
#   --dataset FILE     Training dataset
#   --base-model STR   Base model (e.g., meta-llama/Llama-3-8B)
#   --template STR     Chat template for formatting
#   --epochs INT       Number of training epochs
#   --lr FLOAT         Learning rate
#   --lora-r INT       LoRA rank
#   --lora-alpha INT   LoRA alpha
#   --epsilon FLOAT    DP-SGD epsilon (default: 8.0)
#   --output DIR       Output directory for adapter</code></pre>

<h2>Templates</h2>
<pre><code># List available chat templates
uv run uncase template list

# Export a template to a file
uv run uncase template export --name chatml --output template.json</code></pre>

<h2>Tools</h2>
<pre><code># List available domain tools
uv run uncase tool list

# Simulate a tool call
uv run uncase tool simulate --name vehicle_inventory_search --params '{"make": "Toyota"}'</code></pre>

<h2>Import</h2>
<pre><code># Import conversations from CSV
uv run uncase import csv --input conversations.csv

# Import conversations from JSONL
uv run uncase import jsonl --input conversations.jsonl</code></pre>

<h2>Pipeline Orchestrator</h2>
<pre><code># Run the full end-to-end pipeline (Layers 0-4)
uv run uncase pipeline run

# Options:
#   --input FILE       Input conversations
#   --domain STR       Target domain
#   --count INT        Synthetics to generate
#   --base-model STR   Base model for LoRA
#   --output DIR       Output directory</code></pre>

<h2>Using Make</h2>
<p>Common commands are also available via the Makefile:</p>
<pre><code>make api           # Start dev server (port 8000)
make test          # Run all 970 tests
make lint          # Ruff check
make format        # Ruff format
make typecheck     # mypy
make check         # lint + typecheck + tests (pre-PR)
make docker-up     # Start Docker services
make docker-down   # Stop Docker services</code></pre>`,
      es: `<h2>Resumen del CLI</h2>
<p>El CLI de UNCASE está construido con <strong>Typer</strong> y provee comandos para cada capa del pipeline. Todos los comandos están disponibles y completamente implementados.</p>
<pre><code>uv run uncase --help
uv run uncase --version</code></pre>

<h2>Capa 0: Motor de Semillas</h2>
<pre><code># Crear una semilla a partir de una conversación (detección PII + anonimización)
uv run uncase seed create

# Opciones:
#   --input FILE       Archivo de conversación de entrada
#   --format FORMAT    Formato de entrada (auto, json, csv, whatsapp)
#   --domain DOMAIN    Namespace del dominio objetivo
#   --output FILE      Archivo de semilla de salida</code></pre>

<h2>Capa 1: Parser</h2>
<pre><code># Parsear una exportación de chat WhatsApp
uv run uncase parse whatsapp

# Opciones:
#   --input FILE       Archivo .txt de exportación WhatsApp
#   --output FILE      Archivo de salida parseado
#   --format FORMAT    Formato de salida (json, jsonl, csv)</code></pre>

<h2>Capa 2: Evaluador</h2>
<pre><code># Evaluar calidad de semillas o conversaciones sintéticas
uv run uncase evaluate

# Opciones:
#   --input FILE       Archivo de semillas o sintéticos
#   --metrics METRICS  Métricas a evaluar (all, rouge, fidelity, ttr, coherence, privacy)
#   --threshold FLOAT  Umbral mínimo de calidad
#   --output FILE      Salida del reporte de evaluación</code></pre>

<h2>Capa 3: Generador</h2>
<pre><code># Generar conversaciones sintéticas a partir de semillas
uv run uncase generate

# Opciones:
#   --input FILE       Archivo de semillas de entrada
#   --count INT        Número de sintéticos a generar (default: 10)
#   --strategy STR     Estrategia de generación (persona_variation, flow_variation, tool_injection)
#   --provider STR     Proveedor LLM (claude, gpt4, gemini, ollama)
#   --model STR        Nombre del modelo específico
#   --template STR     Template de chat (chatml, alpaca, llama, etc.)
#   --output FILE      Archivo de salida</code></pre>

<h2>Capa 4: Entrenamiento LoRA</h2>
<pre><code># Ejecutar pipeline de fine-tuning LoRA/QLoRA
uv run uncase train

# Opciones:
#   --dataset FILE     Dataset de entrenamiento
#   --base-model STR   Modelo base (ej., meta-llama/Llama-3-8B)
#   --template STR     Template de chat para formateo
#   --epochs INT       Número de épocas de entrenamiento
#   --lr FLOAT         Tasa de aprendizaje
#   --lora-r INT       Rango LoRA
#   --lora-alpha INT   Alpha LoRA
#   --epsilon FLOAT    Epsilon DP-SGD (default: 8.0)
#   --output DIR       Directorio de salida para el adaptador</code></pre>

<h2>Templates</h2>
<pre><code># Listar chat templates disponibles
uv run uncase template list

# Exportar un template a archivo
uv run uncase template export --name chatml --output template.json</code></pre>

<h2>Herramientas</h2>
<pre><code># Listar herramientas de dominio disponibles
uv run uncase tool list

# Simular una llamada a herramienta
uv run uncase tool simulate --name vehicle_inventory_search --params '{"make": "Toyota"}'</code></pre>

<h2>Importación</h2>
<pre><code># Importar conversaciones desde CSV
uv run uncase import csv --input conversations.csv

# Importar conversaciones desde JSONL
uv run uncase import jsonl --input conversations.jsonl</code></pre>

<h2>Orquestador de Pipeline</h2>
<pre><code># Ejecutar el pipeline completo end-to-end (Capas 0-4)
uv run uncase pipeline run

# Opciones:
#   --input FILE       Conversaciones de entrada
#   --domain STR       Dominio objetivo
#   --count INT        Sintéticos a generar
#   --base-model STR   Modelo base para LoRA
#   --output DIR       Directorio de salida</code></pre>

<h2>Usando Make</h2>
<p>Los comandos comunes también están disponibles vía el Makefile:</p>
<pre><code>make api           # Iniciar servidor dev (puerto 8000)
make test          # Ejecutar los 970 tests
make lint          # Ruff check
make format        # Ruff format
make typecheck     # mypy
make check         # lint + typecheck + tests (pre-PR)
make docker-up     # Iniciar servicios Docker
make docker-down   # Detener servicios Docker</code></pre>`,
    },
  },

  // ── Privacy & Security ───────────────────────────────────
  {
    id: 'privacy-guarantees',
    title: { en: 'Privacy Guarantees', es: 'Garantías de Privacidad' },
    description: {
      en: 'PII scanning, privacy modes, DP-SGD, and compliance profiles.',
      es: 'Escaneo PII, modos de privacidad, DP-SGD y perfiles de cumplimiento.',
    },
    category: 'privacy',
    keywords: ['privacy', 'pii', 'presidio', 'dpsgd', 'compliance', 'hipaa', 'gdpr', 'scanner', 'redact'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Zero PII Tolerance</h2>
<p>UNCASE enforces a <strong>zero PII tolerance</strong> policy. No personally identifiable information may exist in final synthetic data, training datasets, or LoRA adapters. This is a hard gate &mdash; if any PII is detected, the quality score is automatically set to <code>Q = 0</code>.</p>

<h2>Privacy Scanner</h2>
<p><strong>Module:</strong> <code>uncase/core/privacy/scanner.py</code></p>
<p>The privacy scanner combines two detection strategies:</p>

<h3>9 Regex Patterns</h3>
<table>
<thead><tr><th>#</th><th>Pattern</th><th>Examples</th></tr></thead>
<tbody>
<tr><td>1</td><td>Email addresses</td><td><code>user@example.com</code></td></tr>
<tr><td>2</td><td>Phone numbers</td><td><code>+1-555-123-4567</code>, <code>(555) 123-4567</code></td></tr>
<tr><td>3</td><td>Credit card numbers</td><td><code>4111-1111-1111-1111</code></td></tr>
<tr><td>4</td><td>Social Security Numbers</td><td><code>123-45-6789</code></td></tr>
<tr><td>5</td><td>IP addresses</td><td><code>192.168.1.1</code>, <code>2001:db8::1</code></td></tr>
<tr><td>6</td><td>Dates of birth</td><td><code>01/15/1990</code>, <code>1990-01-15</code></td></tr>
<tr><td>7</td><td>Passport numbers</td><td><code>A12345678</code></td></tr>
<tr><td>8</td><td>License plates</td><td><code>ABC-1234</code></td></tr>
<tr><td>9</td><td>Postal codes</td><td><code>90210</code>, <code>SW1A 1AA</code></td></tr>
</tbody>
</table>

<h3>Presidio NER</h3>
<p>Microsoft Presidio with SpaCy NER model detects context-dependent entities:</p>
<ul>
<li>Person names</li>
<li>Locations and addresses</li>
<li>Organizations</li>
<li>Medical record numbers</li>
<li>Financial account numbers</li>
</ul>

<h2>Three Scanner Modes</h2>
<table>
<thead><tr><th>Mode</th><th>Behavior</th><th>Use Case</th></tr></thead>
<tbody>
<tr><td><code>audit</code></td><td>Detects and <strong>logs</strong> PII findings without modifying data</td><td>Discovery and reporting</td></tr>
<tr><td><code>block</code></td><td><strong>Rejects</strong> the request if any PII is found (returns 422)</td><td>Strict enforcement</td></tr>
<tr><td><code>redact</code></td><td><strong>Masks</strong> PII in-flight with typed placeholders (<code>[PERSON_1]</code>, <code>[EMAIL_1]</code>)</td><td>Automatic anonymization</td></tr>
</tbody>
</table>

<h2>Request/Response Interceptor</h2>
<p><strong>Module:</strong> <code>uncase/core/privacy/interceptor.py</code></p>
<p>A FastAPI middleware that scans both incoming requests and outgoing responses for PII. This ensures no PII leaks through any API endpoint, even if the core pipeline is bypassed.</p>
<pre><code># Middleware chain:
Request &rarr; PII Interceptor (scan body) &rarr; Route Handler &rarr; PII Interceptor (scan response) &rarr; Response</code></pre>

<h2>Quality Thresholds</h2>
<table>
<thead><tr><th>Metric</th><th>Threshold</th><th>Description</th></tr></thead>
<tbody>
<tr><td>ROUGE-L</td><td>&ge; 0.65</td><td>Structural coherence with seed</td></tr>
<tr><td>Factual Fidelity</td><td>&ge; 0.90</td><td>Domain fact accuracy</td></tr>
<tr><td>Lexical Diversity (TTR)</td><td>&ge; 0.55</td><td>Type-Token Ratio</td></tr>
<tr><td>Dialogic Coherence</td><td>&ge; 0.85</td><td>Cross-turn role consistency</td></tr>
<tr><td>Privacy Score</td><td>= 0.00</td><td>Zero residual PII</td></tr>
<tr><td>Memorization</td><td>&lt; 0.01</td><td>Extraction attack success rate</td></tr>
</tbody>
</table>

<p><strong>Composite formula:</strong></p>
<pre><code>Q = min(ROUGE, Fidelity, TTR, Coherence)  if privacy == 0 AND memorization &lt; 0.01
Q = 0                                      otherwise</code></pre>

<h2>Differential Privacy (DP-SGD)</h2>
<p>During LoRA fine-tuning (Layer 4), UNCASE applies <strong>DP-SGD</strong> (Differentially Private Stochastic Gradient Descent) with a configurable epsilon:</p>
<ul>
<li>Default epsilon: <strong>&le; 8.0</strong></li>
<li>Gradient clipping and noise injection per training step</li>
<li>Privacy budget tracking across epochs</li>
<li>Extraction attack testing after training to verify memorization &lt; 0.01</li>
</ul>

<h2>Compliance Profiles</h2>
<p>UNCASE ships with 5 frozen compliance profiles as Python dataclasses:</p>
<table>
<thead><tr><th>Profile</th><th>Region</th><th>Key Requirements</th></tr></thead>
<tbody>
<tr><td>HIPAA</td><td>USA</td><td>18 PHI identifiers, minimum necessary standard, audit controls</td></tr>
<tr><td>GDPR</td><td>EU</td><td>Data minimization, right to erasure, lawful basis, DPO</td></tr>
<tr><td>SOX</td><td>USA</td><td>Financial data integrity, audit trail, access controls</td></tr>
<tr><td>LFPDPPP</td><td>Mexico</td><td>Consent, ARCO rights, privacy notices, data transfers</td></tr>
<tr><td>EU AI Act</td><td>EU</td><td>Risk classification, transparency, human oversight, bias testing</td></tr>
</tbody>
</table>

<h2>Module Structure</h2>
<pre><code>uncase/core/privacy/
&boxur;&boxh; __init__.py
&boxur;&boxh; scanner.py          # PII scanner (regex + Presidio)
&boxur;&boxh; interceptor.py      # Request/response middleware
&boxdr;&boxh; compliance.py       # Frozen compliance profiles</code></pre>`,
      es: `<h2>Tolerancia Cero a PII</h2>
<p>UNCASE aplica una política de <strong>tolerancia cero a PII</strong>. Ninguna información de identificación personal puede existir en datos sintéticos finales, datasets de entrenamiento o adaptadores LoRA. Este es un gate duro &mdash; si se detecta cualquier PII, el puntaje de calidad se establece automáticamente en <code>Q = 0</code>.</p>

<h2>Escáner de Privacidad</h2>
<p><strong>Módulo:</strong> <code>uncase/core/privacy/scanner.py</code></p>
<p>El escáner de privacidad combina dos estrategias de detección:</p>

<h3>9 Patrones Regex</h3>
<table>
<thead><tr><th>#</th><th>Patrón</th><th>Ejemplos</th></tr></thead>
<tbody>
<tr><td>1</td><td>Direcciones de email</td><td><code>user@example.com</code></td></tr>
<tr><td>2</td><td>Números de teléfono</td><td><code>+1-555-123-4567</code>, <code>(555) 123-4567</code></td></tr>
<tr><td>3</td><td>Números de tarjeta de crédito</td><td><code>4111-1111-1111-1111</code></td></tr>
<tr><td>4</td><td>Números de Seguro Social</td><td><code>123-45-6789</code></td></tr>
<tr><td>5</td><td>Direcciones IP</td><td><code>192.168.1.1</code>, <code>2001:db8::1</code></td></tr>
<tr><td>6</td><td>Fechas de nacimiento</td><td><code>01/15/1990</code>, <code>1990-01-15</code></td></tr>
<tr><td>7</td><td>Números de pasaporte</td><td><code>A12345678</code></td></tr>
<tr><td>8</td><td>Placas vehiculares</td><td><code>ABC-1234</code></td></tr>
<tr><td>9</td><td>Códigos postales</td><td><code>90210</code>, <code>SW1A 1AA</code></td></tr>
</tbody>
</table>

<h3>Presidio NER</h3>
<p>Microsoft Presidio con modelo NER de SpaCy detecta entidades dependientes de contexto:</p>
<ul>
<li>Nombres de persona</li>
<li>Ubicaciones y direcciones</li>
<li>Organizaciones</li>
<li>Números de registros médicos</li>
<li>Números de cuentas financieras</li>
</ul>

<h2>Tres Modos del Escáner</h2>
<table>
<thead><tr><th>Modo</th><th>Comportamiento</th><th>Caso de Uso</th></tr></thead>
<tbody>
<tr><td><code>audit</code></td><td>Detecta y <strong>registra</strong> hallazgos de PII sin modificar los datos</td><td>Descubrimiento y reportes</td></tr>
<tr><td><code>block</code></td><td><strong>Rechaza</strong> la solicitud si se encuentra cualquier PII (retorna 422)</td><td>Aplicación estricta</td></tr>
<tr><td><code>redact</code></td><td><strong>Enmascara</strong> PII en tránsito con placeholders tipados (<code>[PERSON_1]</code>, <code>[EMAIL_1]</code>)</td><td>Anonimización automática</td></tr>
</tbody>
</table>

<h2>Interceptor de Request/Response</h2>
<p><strong>Módulo:</strong> <code>uncase/core/privacy/interceptor.py</code></p>
<p>Un middleware de FastAPI que escanea tanto solicitudes entrantes como respuestas salientes buscando PII. Esto asegura que ningún PII se filtre por ningún endpoint de la API, incluso si se evita el pipeline principal.</p>
<pre><code># Cadena de middleware:
Request &rarr; Interceptor PII (escanear body) &rarr; Route Handler &rarr; Interceptor PII (escanear respuesta) &rarr; Response</code></pre>

<h2>Umbrales de Calidad</h2>
<table>
<thead><tr><th>Métrica</th><th>Umbral</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td>ROUGE-L</td><td>&ge; 0.65</td><td>Coherencia estructural con la semilla</td></tr>
<tr><td>Fidelidad Factual</td><td>&ge; 0.90</td><td>Precisión de hechos del dominio</td></tr>
<tr><td>Diversidad Léxica (TTR)</td><td>&ge; 0.55</td><td>Type-Token Ratio</td></tr>
<tr><td>Coherencia Dialógica</td><td>&ge; 0.85</td><td>Consistencia de roles inter-turno</td></tr>
<tr><td>Privacy Score</td><td>= 0.00</td><td>Cero PII residual</td></tr>
<tr><td>Memorización</td><td>&lt; 0.01</td><td>Tasa de éxito de ataque de extracción</td></tr>
</tbody>
</table>

<p><strong>Fórmula compuesta:</strong></p>
<pre><code>Q = min(ROUGE, Fidelidad, TTR, Coherencia)  si privacy == 0 Y memorización &lt; 0.01
Q = 0                                        de lo contrario</code></pre>

<h2>Privacidad Diferencial (DP-SGD)</h2>
<p>Durante el fine-tuning LoRA (Capa 4), UNCASE aplica <strong>DP-SGD</strong> (Descenso de Gradiente Estocástico Diferencialmente Privado) con un epsilon configurable:</p>
<ul>
<li>Epsilon por defecto: <strong>&le; 8.0</strong></li>
<li>Recorte de gradientes e inyección de ruido por paso de entrenamiento</li>
<li>Seguimiento de presupuesto de privacidad a través de épocas</li>
<li>Testing de ataques de extracción tras entrenamiento para verificar memorización &lt; 0.01</li>
</ul>

<h2>Perfiles de Cumplimiento</h2>
<p>UNCASE incluye 5 perfiles de cumplimiento congelados como dataclasses de Python:</p>
<table>
<thead><tr><th>Perfil</th><th>Región</th><th>Requisitos Clave</th></tr></thead>
<tbody>
<tr><td>HIPAA</td><td>EE.UU.</td><td>18 identificadores PHI, estándar de mínimo necesario, controles de auditoría</td></tr>
<tr><td>GDPR</td><td>UE</td><td>Minimización de datos, derecho al olvido, base legal, DPO</td></tr>
<tr><td>SOX</td><td>EE.UU.</td><td>Integridad de datos financieros, trail de auditoría, controles de acceso</td></tr>
<tr><td>LFPDPPP</td><td>México</td><td>Consentimiento, derechos ARCO, avisos de privacidad, transferencias</td></tr>
<tr><td>EU AI Act</td><td>UE</td><td>Clasificación de riesgo, transparencia, supervisión humana, testing de sesgo</td></tr>
</tbody>
</table>

<h2>Estructura del Módulo</h2>
<pre><code>uncase/core/privacy/
&boxur;&boxh; __init__.py
&boxur;&boxh; scanner.py          # Escáner PII (regex + Presidio)
&boxur;&boxh; interceptor.py      # Middleware de request/response
&boxdr;&boxh; compliance.py       # Perfiles de cumplimiento congelados</code></pre>`,
    },
  },

  // ── Enterprise ───────────────────────────────────────────
  {
    id: 'enterprise-features',
    title: { en: 'Enterprise Features', es: 'Funcionalidades Empresariales' },
    description: {
      en: 'Auth, audit, costs, rate limiting, webhooks, observability, and compliance.',
      es: 'Auth, auditoría, costos, rate limiting, webhooks, observabilidad y cumplimiento.',
    },
    category: 'enterprise',
    keywords: ['enterprise', 'auth', 'jwt', 'audit', 'costs', 'rate-limiting', 'webhooks', 'observability', 'compliance', 'prometheus', 'grafana'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Enterprise-Grade Infrastructure</h2>
<p>UNCASE includes a comprehensive set of enterprise features for production deployment in regulated industries. All features are fully implemented and tested.</p>

<h2>JWT Authentication</h2>
<p>Secure token-based authentication with industry-standard practices:</p>
<ul>
<li><strong>Login:</strong> <code>POST /api/v1/auth/login</code> &mdash; returns access + refresh tokens</li>
<li><strong>Refresh:</strong> <code>POST /api/v1/auth/refresh</code> &mdash; renew expired access tokens</li>
<li><strong>Verify:</strong> <code>POST /api/v1/auth/verify</code> &mdash; validate token integrity</li>
<li><strong>Password hashing:</strong> Argon2id (memory-hard, resistant to GPU attacks)</li>
<li><strong>Token signing:</strong> PyJWT with configurable algorithm (HS256 default)</li>
<li><strong>Expiration:</strong> Configurable via <code>JWT_EXPIRATION_MINUTES</code></li>
</ul>

<h2>Audit Logging</h2>
<p>Complete compliance trail for all operations:</p>
<ul>
<li><strong>Action tracking:</strong> Every API operation is logged with action type, resource, actor, and IP address</li>
<li><strong>Compliance trail:</strong> Immutable audit records stored in the <code>AuditLog</code> database model</li>
<li><strong>Pagination:</strong> Query audit logs with filtering by action, actor, resource, and date range</li>
<li><strong>Endpoint:</strong> <code>GET /api/v1/audit</code> &mdash; paginated audit log viewer</li>
<li><strong>DB migration:</strong> Migration 0008 (<code>0008-audit-logs</code>)</li>
</ul>
<pre><code># Example audit log entry
{
  "id": "uuid",
  "action": "seed.create",
  "resource": "seed/abc-123",
  "actor": "user@org.com",
  "ip_address": "192.168.1.1",
  "details": { "domain": "automotive.sales" },
  "created_at": "2026-02-25T10:30:00Z"
}</code></pre>

<h2>Cost Tracking</h2>
<p>Per-organization and per-job LLM spend tracking:</p>
<ul>
<li><strong>Per-org costs:</strong> Aggregate LLM spend by organization</li>
<li><strong>Per-job costs:</strong> Track costs for individual generation and training jobs</li>
<li><strong>Daily aggregation:</strong> Rollup cost data for reporting</li>
<li><strong>Endpoints:</strong> <code>GET /api/v1/costs</code> (3 endpoints for summary, by-org, by-job)</li>
<li><strong>DB model:</strong> <code>CostEntry</code> with provider, model, tokens, and cost fields</li>
</ul>

<h2>Rate Limiting</h2>
<p>Sliding window counter middleware to protect against abuse:</p>
<ul>
<li><strong>Per API key:</strong> Each API key has independent rate tracking</li>
<li><strong>Configurable thresholds:</strong> <code>RATE_LIMIT_REQUESTS</code> (default: 100) and <code>RATE_LIMIT_WINDOW_SECONDS</code> (default: 60)</li>
<li><strong>In-memory counter:</strong> Sliding window implementation with <code>_counter.reset()</code> for tests</li>
<li><strong>429 response:</strong> Returns <code>Retry-After</code> header when limit exceeded</li>
</ul>

<h2>Webhooks</h2>
<p>Event-driven integrations with external systems:</p>
<ul>
<li><strong>8 endpoints</strong> for full lifecycle management</li>
<li><strong>Subscriptions:</strong> Create, update, delete, list webhook subscriptions</li>
<li><strong>Deliveries:</strong> Track delivery status and response codes</li>
<li><strong>Events:</strong> Browse available event types</li>
<li><strong>Retry logic:</strong> Automatic retry with exponential backoff for failed deliveries</li>
<li><strong>Signature verification:</strong> HMAC-SHA256 signatures on payloads</li>
</ul>

<h2>Data Retention</h2>
<p>Configurable data retention policies for regulatory compliance:</p>
<ul>
<li><strong>GDPR:</strong> Right to erasure, data minimization</li>
<li><strong>CCPA:</strong> Consumer data deletion requests</li>
<li><strong>Configurable TTL:</strong> Per-resource retention periods</li>
<li><strong>Automatic cleanup:</strong> Background job for expired data removal</li>
</ul>

<h2>Security Headers</h2>
<p>Production-grade security middleware:</p>
<ul>
<li><strong>HSTS:</strong> HTTP Strict Transport Security with max-age</li>
<li><strong>CSP:</strong> Content Security Policy to prevent XSS</li>
<li><strong>X-Frame-Options:</strong> Clickjacking protection (DENY)</li>
<li><strong>X-Content-Type-Options:</strong> MIME type sniffing prevention</li>
<li><strong>CORS:</strong> Configurable cross-origin resource sharing</li>
</ul>

<h2>Observability</h2>
<p>Prometheus + Grafana stack for production monitoring:</p>
<ul>
<li><strong>Prometheus middleware:</strong> Collects request count, latency, and error rate metrics</li>
<li><strong>Metrics endpoint:</strong> <code>/metrics</code> in Prometheus exposition format</li>
<li><strong>Grafana dashboards:</strong> Pre-built dashboard templates for API monitoring</li>
<li><strong>Docker profile:</strong> <code>docker compose --profile observability up -d</code></li>
<li><strong>Ports:</strong> Prometheus (9090), Grafana (3001)</li>
</ul>

<h2>Compliance Profiles</h2>
<p>5 frozen compliance profiles as Python dataclasses:</p>
<table>
<thead><tr><th>Profile</th><th>Region</th><th>Scope</th></tr></thead>
<tbody>
<tr><td>HIPAA</td><td>USA</td><td>Healthcare data protection</td></tr>
<tr><td>GDPR</td><td>EU</td><td>General data protection</td></tr>
<tr><td>SOX</td><td>USA</td><td>Financial reporting integrity</td></tr>
<tr><td>LFPDPPP</td><td>Mexico</td><td>Personal data protection</td></tr>
<tr><td>EU AI Act</td><td>EU</td><td>AI system regulation</td></tr>
</tbody>
</table>`,
      es: `<h2>Infraestructura de Grado Empresarial</h2>
<p>UNCASE incluye un conjunto completo de funcionalidades empresariales para despliegue en producción en industrias reguladas. Todas las funcionalidades están completamente implementadas y testeadas.</p>

<h2>Autenticación JWT</h2>
<p>Autenticación segura basada en tokens con prácticas estándar de la industria:</p>
<ul>
<li><strong>Login:</strong> <code>POST /api/v1/auth/login</code> &mdash; retorna tokens de acceso + refresco</li>
<li><strong>Refresh:</strong> <code>POST /api/v1/auth/refresh</code> &mdash; renovar tokens de acceso expirados</li>
<li><strong>Verify:</strong> <code>POST /api/v1/auth/verify</code> &mdash; validar integridad del token</li>
<li><strong>Hashing de contraseñas:</strong> Argon2id (memory-hard, resistente a ataques GPU)</li>
<li><strong>Firma de tokens:</strong> PyJWT con algoritmo configurable (HS256 por defecto)</li>
<li><strong>Expiración:</strong> Configurable vía <code>JWT_EXPIRATION_MINUTES</code></li>
</ul>

<h2>Logging de Auditoría</h2>
<p>Trail de cumplimiento completo para todas las operaciones:</p>
<ul>
<li><strong>Tracking de acciones:</strong> Cada operación API se registra con tipo de acción, recurso, actor y dirección IP</li>
<li><strong>Trail de cumplimiento:</strong> Registros de auditoría inmutables almacenados en el modelo de BD <code>AuditLog</code></li>
<li><strong>Paginación:</strong> Consulta logs de auditoría con filtrado por acción, actor, recurso y rango de fechas</li>
<li><strong>Endpoint:</strong> <code>GET /api/v1/audit</code> &mdash; visor paginado de logs de auditoría</li>
<li><strong>Migración BD:</strong> Migración 0008 (<code>0008-audit-logs</code>)</li>
</ul>
<pre><code># Ejemplo de entrada de log de auditoría
{
  "id": "uuid",
  "action": "seed.create",
  "resource": "seed/abc-123",
  "actor": "user@org.com",
  "ip_address": "192.168.1.1",
  "details": { "domain": "automotive.sales" },
  "created_at": "2026-02-25T10:30:00Z"
}</code></pre>

<h2>Seguimiento de Costos</h2>
<p>Seguimiento de gasto LLM por organización y por job:</p>
<ul>
<li><strong>Costos por org:</strong> Gasto LLM agregado por organización</li>
<li><strong>Costos por job:</strong> Seguimiento de costos para jobs individuales de generación y entrenamiento</li>
<li><strong>Agregación diaria:</strong> Rollup de datos de costos para reportes</li>
<li><strong>Endpoints:</strong> <code>GET /api/v1/costs</code> (3 endpoints para resumen, por-org, por-job)</li>
<li><strong>Modelo BD:</strong> <code>CostEntry</code> con campos de proveedor, modelo, tokens y costo</li>
</ul>

<h2>Rate Limiting</h2>
<p>Middleware de contador de ventana deslizante para protección contra abuso:</p>
<ul>
<li><strong>Por API key:</strong> Cada API key tiene tracking de tasa independiente</li>
<li><strong>Umbrales configurables:</strong> <code>RATE_LIMIT_REQUESTS</code> (default: 100) y <code>RATE_LIMIT_WINDOW_SECONDS</code> (default: 60)</li>
<li><strong>Contador en memoria:</strong> Implementación de ventana deslizante con <code>_counter.reset()</code> para tests</li>
<li><strong>Respuesta 429:</strong> Retorna header <code>Retry-After</code> cuando se excede el límite</li>
</ul>

<h2>Webhooks</h2>
<p>Integraciones basadas en eventos con sistemas externos:</p>
<ul>
<li><strong>8 endpoints</strong> para gestión completa del ciclo de vida</li>
<li><strong>Suscripciones:</strong> Crear, actualizar, eliminar, listar suscripciones de webhook</li>
<li><strong>Entregas:</strong> Seguimiento de estado de entrega y códigos de respuesta</li>
<li><strong>Eventos:</strong> Explorar tipos de eventos disponibles</li>
<li><strong>Lógica de reintento:</strong> Reintento automático con backoff exponencial para entregas fallidas</li>
<li><strong>Verificación de firma:</strong> Firmas HMAC-SHA256 en payloads</li>
</ul>

<h2>Retención de Datos</h2>
<p>Políticas de retención de datos configurables para cumplimiento regulatorio:</p>
<ul>
<li><strong>GDPR:</strong> Derecho al olvido, minimización de datos</li>
<li><strong>CCPA:</strong> Solicitudes de eliminación de datos del consumidor</li>
<li><strong>TTL configurable:</strong> Períodos de retención por recurso</li>
<li><strong>Limpieza automática:</strong> Job en background para eliminación de datos expirados</li>
</ul>

<h2>Headers de Seguridad</h2>
<p>Middleware de seguridad de grado producción:</p>
<ul>
<li><strong>HSTS:</strong> HTTP Strict Transport Security con max-age</li>
<li><strong>CSP:</strong> Content Security Policy para prevenir XSS</li>
<li><strong>X-Frame-Options:</strong> Protección contra clickjacking (DENY)</li>
<li><strong>X-Content-Type-Options:</strong> Prevención de sniffing de tipo MIME</li>
<li><strong>CORS:</strong> Cross-origin resource sharing configurable</li>
</ul>

<h2>Observabilidad</h2>
<p>Stack Prometheus + Grafana para monitoreo en producción:</p>
<ul>
<li><strong>Middleware Prometheus:</strong> Recolecta métricas de conteo de requests, latencia y tasa de error</li>
<li><strong>Endpoint de métricas:</strong> <code>/metrics</code> en formato de exposición Prometheus</li>
<li><strong>Dashboards Grafana:</strong> Templates de dashboard pre-construidos para monitoreo de API</li>
<li><strong>Perfil Docker:</strong> <code>docker compose --profile observability up -d</code></li>
<li><strong>Puertos:</strong> Prometheus (9090), Grafana (3001)</li>
</ul>

<h2>Perfiles de Cumplimiento</h2>
<p>5 perfiles de cumplimiento congelados como dataclasses de Python:</p>
<table>
<thead><tr><th>Perfil</th><th>Región</th><th>Alcance</th></tr></thead>
<tbody>
<tr><td>HIPAA</td><td>EE.UU.</td><td>Protección de datos de salud</td></tr>
<tr><td>GDPR</td><td>UE</td><td>Protección general de datos</td></tr>
<tr><td>SOX</td><td>EE.UU.</td><td>Integridad de reportes financieros</td></tr>
<tr><td>LFPDPPP</td><td>México</td><td>Protección de datos personales</td></tr>
<tr><td>EU AI Act</td><td>UE</td><td>Regulación de sistemas de IA</td></tr>
</tbody>
</table>`,
    },
  },

  // ── Deployment ───────────────────────────────────────────
  {
    id: 'docker-deployment',
    title: { en: 'Docker Deployment', es: 'Despliegue Docker' },
    description: {
      en: 'Docker Compose services, profiles, and production deployment.',
      es: 'Servicios Docker Compose, perfiles y despliegue a producción.',
    },
    category: 'deployment',
    keywords: ['docker', 'compose', 'deployment', 'production', 'prometheus', 'grafana', 'gpu', 'mlflow'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Docker Compose Services</h2>
<table>
<thead><tr><th>Service</th><th>Description</th><th>Port</th><th>Profile</th></tr></thead>
<tbody>
<tr><td><code>api</code></td><td>FastAPI (UNCASE API)</td><td>8000</td><td><em>default</em></td></tr>
<tr><td><code>postgres</code></td><td>PostgreSQL 16 Alpine</td><td>5432</td><td><em>default</em></td></tr>
<tr><td><code>mlflow</code></td><td>MLflow tracking server</td><td>5000</td><td><code>ml</code></td></tr>
<tr><td><code>api-gpu</code></td><td>API with NVIDIA GPU support</td><td>8001</td><td><code>gpu</code></td></tr>
<tr><td><code>prometheus</code></td><td>Metrics collection</td><td>9090</td><td><code>observability</code></td></tr>
<tr><td><code>grafana</code></td><td>Metrics dashboards</td><td>3001</td><td><code>observability</code></td></tr>
</tbody>
</table>

<h2>Starting Services</h2>
<pre><code># Default: API + PostgreSQL
docker compose up -d

# With MLflow tracking
docker compose --profile ml up -d

# With GPU support (NVIDIA)
docker compose --profile gpu up -d

# With Prometheus + Grafana observability
docker compose --profile observability up -d

# All profiles
docker compose --profile ml --profile gpu --profile observability up -d</code></pre>

<h2>Makefile Shortcuts</h2>
<pre><code>make docker-build    # Build Docker image
make docker-up       # Start services
make docker-down     # Stop services</code></pre>

<h2>Database Migrations</h2>
<p>After starting the database, run Alembic migrations:</p>
<pre><code># Run all 8 migrations
docker compose exec api uv run alembic upgrade head

# Or from host:
uv run alembic upgrade head</code></pre>

<h2>Environment Variables</h2>
<p>Docker Compose reads from <code>.env</code> in the project root. At minimum, set:</p>
<pre><code>DATABASE_URL=postgresql+asyncpg://uncase:uncase@postgres:5432/uncase
LITELLM_API_KEY=your-api-key
UNCASE_ENV=production</code></pre>

<h2>Observability Stack</h2>
<p>The observability profile starts Prometheus and Grafana:</p>
<ul>
<li><strong>Prometheus</strong> scrapes the <code>/metrics</code> endpoint on the API server every 15s</li>
<li><strong>Grafana</strong> connects to Prometheus as a data source with pre-built dashboards</li>
<li>Default Grafana credentials: <code>admin</code> / <code>admin</code></li>
<li>Dashboard template included in <code>infra/grafana/dashboards/</code></li>
</ul>

<h2>GPU Support</h2>
<p>The <code>gpu</code> profile requires NVIDIA Container Toolkit:</p>
<pre><code># Install NVIDIA Container Toolkit
# See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Start with GPU
docker compose --profile gpu up -d

# Verify GPU access
docker compose exec api-gpu nvidia-smi</code></pre>

<h2>Production Deployment</h2>
<p>For production, use the deploy script:</p>
<pre><code>./deploy.sh production</code></pre>
<p>The script validates:</p>
<ul>
<li>No uncommitted changes</li>
<li>All changes pushed to remote</li>
<li>Correct deployment channel</li>
</ul>`,
      es: `<h2>Servicios Docker Compose</h2>
<table>
<thead><tr><th>Servicio</th><th>Descripción</th><th>Puerto</th><th>Perfil</th></tr></thead>
<tbody>
<tr><td><code>api</code></td><td>FastAPI (UNCASE API)</td><td>8000</td><td><em>default</em></td></tr>
<tr><td><code>postgres</code></td><td>PostgreSQL 16 Alpine</td><td>5432</td><td><em>default</em></td></tr>
<tr><td><code>mlflow</code></td><td>MLflow tracking server</td><td>5000</td><td><code>ml</code></td></tr>
<tr><td><code>api-gpu</code></td><td>API con soporte NVIDIA GPU</td><td>8001</td><td><code>gpu</code></td></tr>
<tr><td><code>prometheus</code></td><td>Recolección de métricas</td><td>9090</td><td><code>observability</code></td></tr>
<tr><td><code>grafana</code></td><td>Dashboards de métricas</td><td>3001</td><td><code>observability</code></td></tr>
</tbody>
</table>

<h2>Iniciando Servicios</h2>
<pre><code># Por defecto: API + PostgreSQL
docker compose up -d

# Con MLflow tracking
docker compose --profile ml up -d

# Con soporte GPU (NVIDIA)
docker compose --profile gpu up -d

# Con observabilidad Prometheus + Grafana
docker compose --profile observability up -d

# Todos los perfiles
docker compose --profile ml --profile gpu --profile observability up -d</code></pre>

<h2>Atajos del Makefile</h2>
<pre><code>make docker-build    # Construir imagen Docker
make docker-up       # Iniciar servicios
make docker-down     # Detener servicios</code></pre>

<h2>Migraciones de Base de Datos</h2>
<p>Después de iniciar la base de datos, ejecuta las migraciones de Alembic:</p>
<pre><code># Ejecutar las 8 migraciones
docker compose exec api uv run alembic upgrade head

# O desde el host:
uv run alembic upgrade head</code></pre>

<h2>Variables de Entorno</h2>
<p>Docker Compose lee desde <code>.env</code> en la raíz del proyecto. Como mínimo, configura:</p>
<pre><code>DATABASE_URL=postgresql+asyncpg://uncase:uncase@postgres:5432/uncase
LITELLM_API_KEY=tu-api-key
UNCASE_ENV=production</code></pre>

<h2>Stack de Observabilidad</h2>
<p>El perfil de observabilidad inicia Prometheus y Grafana:</p>
<ul>
<li><strong>Prometheus</strong> escanea el endpoint <code>/metrics</code> del servidor API cada 15s</li>
<li><strong>Grafana</strong> se conecta a Prometheus como fuente de datos con dashboards pre-construidos</li>
<li>Credenciales por defecto de Grafana: <code>admin</code> / <code>admin</code></li>
<li>Template de dashboard incluido en <code>infra/grafana/dashboards/</code></li>
</ul>

<h2>Soporte GPU</h2>
<p>El perfil <code>gpu</code> requiere NVIDIA Container Toolkit:</p>
<pre><code># Instalar NVIDIA Container Toolkit
# Ver: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Iniciar con GPU
docker compose --profile gpu up -d

# Verificar acceso GPU
docker compose exec api-gpu nvidia-smi</code></pre>

<h2>Despliegue a Producción</h2>
<p>Para producción, usa el script de despliegue:</p>
<pre><code>./deploy.sh production</code></pre>
<p>El script valida:</p>
<ul>
<li>Sin cambios no commiteados</li>
<li>Todos los cambios pusheados al remoto</li>
<li>Canal de despliegue correcto</li>
</ul>`,
    },
  },

  // ── Configuration ────────────────────────────────────────
  {
    id: 'environment-variables',
    title: { en: 'Environment Variables', es: 'Variables de Entorno' },
    description: {
      en: 'All environment variables for configuring UNCASE.',
      es: 'Todas las variables de entorno para configurar UNCASE.',
    },
    category: 'configuration',
    keywords: ['env', 'environment', 'variables', 'config', 'database', 'jwt', 'rate-limit', 'prometheus'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Environment Variables</h2>
<p>All variables are loaded from <code>.env</code> in the project root. <strong>Never commit <code>.env</code> files.</strong> Use <code>.env.example</code> as a reference.</p>

<h3>Core</h3>
<table>
<thead><tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>DATABASE_URL</code></td><td>Yes</td><td>&mdash;</td><td>PostgreSQL async connection string (<code>postgresql+asyncpg://...</code>)</td></tr>
<tr><td><code>UNCASE_ENV</code></td><td>No</td><td><code>development</code></td><td>Environment: <code>development</code>, <code>staging</code>, <code>production</code></td></tr>
<tr><td><code>UNCASE_LOG_LEVEL</code></td><td>No</td><td><code>INFO</code></td><td>Log level: <code>DEBUG</code>, <code>INFO</code>, <code>WARNING</code>, <code>ERROR</code></td></tr>
<tr><td><code>UNCASE_DEFAULT_LOCALE</code></td><td>No</td><td><code>es</code></td><td>Default locale: <code>es</code> or <code>en</code></td></tr>
</tbody>
</table>

<h3>LLM Providers</h3>
<table>
<thead><tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>LITELLM_API_KEY</code></td><td>Yes</td><td>&mdash;</td><td>API key for the active LLM provider</td></tr>
<tr><td><code>ANTHROPIC_API_KEY</code></td><td>No</td><td>&mdash;</td><td>Claude API key (optional, LiteLLM manages)</td></tr>
</tbody>
</table>

<h3>Authentication</h3>
<table>
<thead><tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>JWT_SECRET_KEY</code></td><td>Yes (prod)</td><td>dev-secret</td><td>Secret key for JWT token signing</td></tr>
<tr><td><code>JWT_ALGORITHM</code></td><td>No</td><td><code>HS256</code></td><td>JWT signing algorithm</td></tr>
<tr><td><code>JWT_EXPIRATION_MINUTES</code></td><td>No</td><td><code>30</code></td><td>Access token expiration in minutes</td></tr>
</tbody>
</table>

<h3>Rate Limiting</h3>
<table>
<thead><tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>RATE_LIMIT_REQUESTS</code></td><td>No</td><td><code>100</code></td><td>Max requests per window</td></tr>
<tr><td><code>RATE_LIMIT_WINDOW_SECONDS</code></td><td>No</td><td><code>60</code></td><td>Sliding window duration in seconds</td></tr>
</tbody>
</table>

<h3>ML &amp; Tracking</h3>
<table>
<thead><tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>MLFLOW_TRACKING_URI</code></td><td>No</td><td>&mdash;</td><td>MLflow tracking server URI</td></tr>
</tbody>
</table>

<h3>External Services</h3>
<table>
<thead><tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>E2B_API_KEY</code></td><td>No</td><td>&mdash;</td><td>E2B sandbox API key for MicroVM execution</td></tr>
<tr><td><code>OPIK_API_KEY</code></td><td>No</td><td>&mdash;</td><td>Opik API key for LLM-as-judge evaluation</td></tr>
</tbody>
</table>

<h3>Observability</h3>
<table>
<thead><tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>PROMETHEUS_ENABLED</code></td><td>No</td><td><code>false</code></td><td>Enable Prometheus metrics middleware</td></tr>
</tbody>
</table>

<h2>Example .env File</h2>
<pre><code># Core
DATABASE_URL=postgresql+asyncpg://uncase:uncase@localhost:5432/uncase
UNCASE_ENV=development
UNCASE_LOG_LEVEL=DEBUG
UNCASE_DEFAULT_LOCALE=es

# LLM
LITELLM_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key

# Auth
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# ML
MLFLOW_TRACKING_URI=http://localhost:5000

# External
E2B_API_KEY=e2b-your-key
OPIK_API_KEY=opik-your-key

# Observability
PROMETHEUS_ENABLED=true</code></pre>`,
      es: `<h2>Variables de Entorno</h2>
<p>Todas las variables se cargan desde <code>.env</code> en la raíz del proyecto. <strong>Nunca commitees archivos <code>.env</code>.</strong> Usa <code>.env.example</code> como referencia.</p>

<h3>Core</h3>
<table>
<thead><tr><th>Variable</th><th>Requerida</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>DATABASE_URL</code></td><td>Sí</td><td>&mdash;</td><td>String de conexión async PostgreSQL (<code>postgresql+asyncpg://...</code>)</td></tr>
<tr><td><code>UNCASE_ENV</code></td><td>No</td><td><code>development</code></td><td>Entorno: <code>development</code>, <code>staging</code>, <code>production</code></td></tr>
<tr><td><code>UNCASE_LOG_LEVEL</code></td><td>No</td><td><code>INFO</code></td><td>Nivel de log: <code>DEBUG</code>, <code>INFO</code>, <code>WARNING</code>, <code>ERROR</code></td></tr>
<tr><td><code>UNCASE_DEFAULT_LOCALE</code></td><td>No</td><td><code>es</code></td><td>Locale por defecto: <code>es</code> o <code>en</code></td></tr>
</tbody>
</table>

<h3>Proveedores LLM</h3>
<table>
<thead><tr><th>Variable</th><th>Requerida</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>LITELLM_API_KEY</code></td><td>Sí</td><td>&mdash;</td><td>API key del proveedor LLM activo</td></tr>
<tr><td><code>ANTHROPIC_API_KEY</code></td><td>No</td><td>&mdash;</td><td>API key de Claude (opcional, LiteLLM lo gestiona)</td></tr>
</tbody>
</table>

<h3>Autenticación</h3>
<table>
<thead><tr><th>Variable</th><th>Requerida</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>JWT_SECRET_KEY</code></td><td>Sí (prod)</td><td>dev-secret</td><td>Clave secreta para firma de tokens JWT</td></tr>
<tr><td><code>JWT_ALGORITHM</code></td><td>No</td><td><code>HS256</code></td><td>Algoritmo de firma JWT</td></tr>
<tr><td><code>JWT_EXPIRATION_MINUTES</code></td><td>No</td><td><code>30</code></td><td>Expiración del token de acceso en minutos</td></tr>
</tbody>
</table>

<h3>Rate Limiting</h3>
<table>
<thead><tr><th>Variable</th><th>Requerida</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>RATE_LIMIT_REQUESTS</code></td><td>No</td><td><code>100</code></td><td>Máximo de requests por ventana</td></tr>
<tr><td><code>RATE_LIMIT_WINDOW_SECONDS</code></td><td>No</td><td><code>60</code></td><td>Duración de la ventana deslizante en segundos</td></tr>
</tbody>
</table>

<h3>ML y Tracking</h3>
<table>
<thead><tr><th>Variable</th><th>Requerida</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>MLFLOW_TRACKING_URI</code></td><td>No</td><td>&mdash;</td><td>URI del servidor de tracking MLflow</td></tr>
</tbody>
</table>

<h3>Servicios Externos</h3>
<table>
<thead><tr><th>Variable</th><th>Requerida</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>E2B_API_KEY</code></td><td>No</td><td>&mdash;</td><td>API key de E2B sandbox para ejecución en MicroVM</td></tr>
<tr><td><code>OPIK_API_KEY</code></td><td>No</td><td>&mdash;</td><td>API key de Opik para evaluación LLM-as-judge</td></tr>
</tbody>
</table>

<h3>Observabilidad</h3>
<table>
<thead><tr><th>Variable</th><th>Requerida</th><th>Default</th><th>Descripción</th></tr></thead>
<tbody>
<tr><td><code>PROMETHEUS_ENABLED</code></td><td>No</td><td><code>false</code></td><td>Habilitar middleware de métricas Prometheus</td></tr>
</tbody>
</table>

<h2>Ejemplo de Archivo .env</h2>
<pre><code># Core
DATABASE_URL=postgresql+asyncpg://uncase:uncase@localhost:5432/uncase
UNCASE_ENV=development
UNCASE_LOG_LEVEL=DEBUG
UNCASE_DEFAULT_LOCALE=es

# LLM
LITELLM_API_KEY=sk-tu-key-aqui
ANTHROPIC_API_KEY=sk-ant-tu-key

# Auth
JWT_SECRET_KEY=cambiar-en-produccion
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# ML
MLFLOW_TRACKING_URI=http://localhost:5000

# Externos
E2B_API_KEY=e2b-tu-key
OPIK_API_KEY=opik-tu-key

# Observabilidad
PROMETHEUS_ENABLED=true</code></pre>`,
    },
  },

  // ── Contributing ─────────────────────────────────────────
  {
    id: 'pr-checklist',
    title: { en: 'PR Checklist', es: 'Checklist de PR' },
    description: {
      en: 'Mandatory checklist before submitting a pull request.',
      es: 'Checklist obligatorio antes de enviar un pull request.',
    },
    category: 'contributing',
    keywords: ['pr', 'pull-request', 'checklist', 'contributing', 'tests', 'lint', 'coverage'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Before Every PR</h2>
<p>The following checks are <strong>mandatory</strong> before submitting any pull request. The project currently has <strong>970 tests</strong>, <strong>73% code coverage</strong>, and <strong>175 Python source files</strong> that must all pass linting and type checking.</p>

<h3>1. Linting</h3>
<pre><code>uv run ruff check .
# Must pass with zero errors</code></pre>

<h3>2. Formatting</h3>
<pre><code>uv run ruff format --check .
# Must be fully formatted</code></pre>

<h3>3. Type Checking</h3>
<pre><code>uv run mypy uncase/
# Must pass with zero type errors (175 source files)</code></pre>

<h3>4. Test Suite</h3>
<pre><code>uv run pytest
# All 970 tests must pass</code></pre>

<h3>5. Privacy Tests (MANDATORY)</h3>
<pre><code>uv run pytest tests/privacy/
# Privacy test suite must pass &mdash; no exceptions</code></pre>

<h3>6. No Real Data</h3>
<p>Verify that <strong>no real data</strong> exists in code or tests. All test data must be synthetic or fixture-generated.</p>

<h2>One-Command Check</h2>
<pre><code>make check
# Runs: lint + typecheck + tests</code></pre>

<h2>Coverage Thresholds</h2>
<table>
<thead><tr><th>Module</th><th>Minimum</th><th>Current</th></tr></thead>
<tbody>
<tr><td><code>uncase/core/</code></td><td>80%</td><td>73% (overall)</td></tr>
<tr><td><code>uncase/schemas/</code></td><td>90%</td><td>73% (overall)</td></tr>
</tbody>
</table>

<h2>Commit Convention</h2>
<p>All commits must follow the conventional format in English:</p>
<pre><code>feat: add new evaluation metric
fix: correct PII detection for phone numbers
chore: update dependencies
test: add privacy suite for medical domain
docs: update API reference</code></pre>

<h2>Code Quality Standards</h2>
<ul>
<li>Type hints on all public functions</li>
<li>Google-style docstrings (in Spanish)</li>
<li>Line length: 120 characters</li>
<li>No <code>print()</code> &mdash; use <code>structlog</code> logger</li>
<li>Custom exceptions inheriting from <code>UNCASEError</code></li>
<li>Pydantic v2 for all data models</li>
<li>Async endpoints in FastAPI</li>
</ul>`,
      es: `<h2>Antes de Cada PR</h2>
<p>Las siguientes verificaciones son <strong>obligatorias</strong> antes de enviar cualquier pull request. El proyecto actualmente tiene <strong>970 tests</strong>, <strong>73% de cobertura de código</strong> y <strong>175 archivos fuente Python</strong> que deben pasar linting y type checking.</p>

<h3>1. Linting</h3>
<pre><code>uv run ruff check .
# Debe pasar con cero errores</code></pre>

<h3>2. Formateo</h3>
<pre><code>uv run ruff format --check .
# Debe estar completamente formateado</code></pre>

<h3>3. Type Checking</h3>
<pre><code>uv run mypy uncase/
# Debe pasar con cero errores de tipos (175 archivos fuente)</code></pre>

<h3>4. Suite de Tests</h3>
<pre><code>uv run pytest
# Los 970 tests deben pasar</code></pre>

<h3>5. Tests de Privacidad (OBLIGATORIO)</h3>
<pre><code>uv run pytest tests/privacy/
# La suite de tests de privacidad debe pasar &mdash; sin excepciones</code></pre>

<h3>6. Sin Datos Reales</h3>
<p>Verifica que <strong>no existan datos reales</strong> en el código o tests. Todos los datos de prueba deben ser sintéticos o generados por fixtures.</p>

<h2>Verificación de Un Comando</h2>
<pre><code>make check
# Ejecuta: lint + typecheck + tests</code></pre>

<h2>Umbrales de Cobertura</h2>
<table>
<thead><tr><th>Módulo</th><th>Mínimo</th><th>Actual</th></tr></thead>
<tbody>
<tr><td><code>uncase/core/</code></td><td>80%</td><td>73% (general)</td></tr>
<tr><td><code>uncase/schemas/</code></td><td>90%</td><td>73% (general)</td></tr>
</tbody>
</table>

<h2>Convención de Commits</h2>
<p>Todos los commits deben seguir el formato convencional en inglés:</p>
<pre><code>feat: add new evaluation metric
fix: correct PII detection for phone numbers
chore: update dependencies
test: add privacy suite for medical domain
docs: update API reference</code></pre>

<h2>Estándares de Calidad de Código</h2>
<ul>
<li>Type hints en todas las funciones públicas</li>
<li>Docstrings estilo Google (en español)</li>
<li>Longitud de línea: 120 caracteres</li>
<li>Sin <code>print()</code> &mdash; usar logger de <code>structlog</code></li>
<li>Excepciones custom heredando de <code>UNCASEError</code></li>
<li>Pydantic v2 para todos los modelos de datos</li>
<li>Endpoints async en FastAPI</li>
</ul>`,
    },
  },

  // ── Changelog ────────────────────────────────────────────
  {
    id: 'enterprise-milestone',
    title: { en: 'Enterprise Readiness — Feb 2026', es: 'Preparación Empresarial — Feb 2026' },
    description: {
      en: 'Major milestone: all enterprise features, 5 pipeline layers, 970 tests.',
      es: 'Hito principal: todas las funcionalidades empresariales, 5 capas de pipeline, 970 tests.',
    },
    category: 'changelog',
    keywords: ['changelog', 'enterprise', 'milestone', 'release', 'february', '2026'],
    lastUpdated: '2026-02-25',
    order: 0,
    content: {
      en: `<h2>Enterprise Readiness Milestone &mdash; February 2026</h2>
<p>This milestone marks the completion of all core development phases (0&ndash;4) and the addition of comprehensive enterprise features to the UNCASE framework.</p>

<h3>Enterprise Features Added</h3>
<ul>
<li><strong>JWT Authentication:</strong> Login, refresh, verify tokens with Argon2 password hashing</li>
<li><strong>Audit Logging:</strong> Complete compliance trail &mdash; action, resource, actor, IP tracking with pagination</li>
<li><strong>Cost Tracking:</strong> Per-org LLM spend, per-job costs, daily aggregation</li>
<li><strong>Rate Limiting:</strong> Sliding window counter middleware with configurable thresholds</li>
<li><strong>Webhooks:</strong> 8 endpoints for subscriptions, deliveries, events, retry logic</li>
<li><strong>Data Retention:</strong> Configurable policies for GDPR/CCPA compliance</li>
<li><strong>Security Headers:</strong> HSTS, CSP, X-Frame-Options middleware</li>
<li><strong>Observability:</strong> Prometheus metrics + Grafana dashboards via Docker profile</li>
</ul>

<h3>Pipeline Complete</h3>
<ul>
<li>All <strong>5 SCSF layers</strong> fully implemented and tested</li>
<li><strong>Pipeline Orchestrator</strong> chains layers 0&ndash;4 end-to-end</li>
<li>PII detection: 9 regex patterns + Presidio NER</li>
<li>6 quality metrics with composite scoring</li>
<li>DP-SGD training with epsilon &le; 8.0</li>
</ul>

<h3>Domain Ecosystem</h3>
<ul>
<li><strong>6 domain plugins</strong> (automotive, medical, legal, finance, industrial, education)</li>
<li><strong>150 domain tools</strong> across all plugins</li>
<li><strong>150 curated seeds</strong> (50 automotive, 50 medical, 50 finance)</li>
<li><strong>5 compliance profiles:</strong> HIPAA, GDPR, SOX, LFPDPPP, EU AI Act</li>
</ul>

<h3>Infrastructure Numbers</h3>
<table>
<thead><tr><th>Metric</th><th>Value</th></tr></thead>
<tbody>
<tr><td>API routers</td><td>21</td></tr>
<tr><td>API endpoints</td><td>85+</td></tr>
<tr><td>Tests</td><td>970</td></tr>
<tr><td>Code coverage</td><td>73%</td></tr>
<tr><td>Python source files</td><td>175</td></tr>
<tr><td>Database models</td><td>13</td></tr>
<tr><td>Alembic migrations</td><td>8</td></tr>
</tbody>
</table>

<h3>Developer Experience</h3>
<ul>
<li><strong>Python SDK:</strong> UNCASEClient, Pipeline, SeedEngine, Generator, Evaluator, Trainer</li>
<li><strong>MCP Server:</strong> FastMCP integration for Model Context Protocol</li>
<li><strong>E2B Sandbox:</strong> Secure code execution in MicroVMs</li>
<li><strong>CLI:</strong> 10 commands covering all pipeline layers</li>
<li><strong>Makefile:</strong> One-command development workflows</li>
<li><strong>Docker Compose:</strong> 4 profiles (default, ml, gpu, observability)</li>
</ul>`,
      es: `<h2>Hito de Preparación Empresarial &mdash; Febrero 2026</h2>
<p>Este hito marca la finalización de todas las fases de desarrollo principal (0&ndash;4) y la adición de funcionalidades empresariales completas al framework UNCASE.</p>

<h3>Funcionalidades Empresariales Añadidas</h3>
<ul>
<li><strong>Autenticación JWT:</strong> Login, refresh, verificación de tokens con hashing de contraseñas Argon2</li>
<li><strong>Logging de Auditoría:</strong> Trail de cumplimiento completo &mdash; tracking de acción, recurso, actor, IP con paginación</li>
<li><strong>Seguimiento de Costos:</strong> Gasto LLM por org, costos por job, agregación diaria</li>
<li><strong>Rate Limiting:</strong> Middleware de contador de ventana deslizante con umbrales configurables</li>
<li><strong>Webhooks:</strong> 8 endpoints para suscripciones, entregas, eventos, lógica de reintento</li>
<li><strong>Retención de Datos:</strong> Políticas configurables para cumplimiento GDPR/CCPA</li>
<li><strong>Headers de Seguridad:</strong> Middleware HSTS, CSP, X-Frame-Options</li>
<li><strong>Observabilidad:</strong> Métricas Prometheus + dashboards Grafana vía perfil Docker</li>
</ul>

<h3>Pipeline Completo</h3>
<ul>
<li>Las <strong>5 capas SCSF</strong> completamente implementadas y testeadas</li>
<li><strong>Orquestador de Pipeline</strong> encadena capas 0&ndash;4 end-to-end</li>
<li>Detección PII: 9 patrones regex + Presidio NER</li>
<li>6 métricas de calidad con scoring compuesto</li>
<li>Entrenamiento DP-SGD con epsilon &le; 8.0</li>
</ul>

<h3>Ecosistema de Dominio</h3>
<ul>
<li><strong>6 plugins de dominio</strong> (automotriz, médico, legal, finanzas, industrial, educación)</li>
<li><strong>150 herramientas de dominio</strong> en todos los plugins</li>
<li><strong>150 semillas curadas</strong> (50 automotriz, 50 médico, 50 finanzas)</li>
<li><strong>5 perfiles de cumplimiento:</strong> HIPAA, GDPR, SOX, LFPDPPP, EU AI Act</li>
</ul>

<h3>Números de Infraestructura</h3>
<table>
<thead><tr><th>Métrica</th><th>Valor</th></tr></thead>
<tbody>
<tr><td>Routers API</td><td>21</td></tr>
<tr><td>Endpoints API</td><td>85+</td></tr>
<tr><td>Tests</td><td>970</td></tr>
<tr><td>Cobertura de código</td><td>73%</td></tr>
<tr><td>Archivos fuente Python</td><td>175</td></tr>
<tr><td>Modelos de base de datos</td><td>13</td></tr>
<tr><td>Migraciones Alembic</td><td>8</td></tr>
</tbody>
</table>

<h3>Experiencia de Desarrollador</h3>
<ul>
<li><strong>SDK Python:</strong> UNCASEClient, Pipeline, SeedEngine, Generator, Evaluator, Trainer</li>
<li><strong>Servidor MCP:</strong> Integración FastMCP para Model Context Protocol</li>
<li><strong>Sandbox E2B:</strong> Ejecución segura de código en MicroVMs</li>
<li><strong>CLI:</strong> 10 comandos cubriendo todas las capas del pipeline</li>
<li><strong>Makefile:</strong> Flujos de desarrollo de un solo comando</li>
<li><strong>Docker Compose:</strong> 4 perfiles (default, ml, gpu, observability)</li>
</ul>`,
    },
  },
  {
    id: 'v0-0-0-dev0',
    title: { en: 'v0.0.0.dev0 — Initial Scaffold', es: 'v0.0.0.dev0 — Scaffold Inicial' },
    description: {
      en: 'First development release: project scaffolding and infrastructure.',
      es: 'Primera versión de desarrollo: scaffolding del proyecto e infraestructura.',
    },
    category: 'changelog',
    keywords: ['changelog', 'v0', 'initial', 'scaffold', 'release'],
    lastUpdated: '2026-02-25',
    order: 1,
    content: {
      en: `<h2>v0.0.0.dev0 &mdash; Initial Scaffold</h2>
<p>First development release establishing the project foundation.</p>

<h3>Infrastructure</h3>
<ul>
<li>Repository structure with monorepo layout</li>
<li>Python package with <code>uv</code> and <code>pyproject.toml</code></li>
<li>FastAPI application factory with middleware</li>
<li>PostgreSQL + SQLAlchemy async ORM setup</li>
<li>Alembic migration framework</li>
<li>Typer CLI scaffold</li>
<li>Docker Compose with API + PostgreSQL</li>
</ul>

<h3>Frontend</h3>
<ul>
<li>Next.js 16 landing page with React 19</li>
<li>shadcn/ui component library integration</li>
<li>Tailwind CSS v4 styling</li>
<li>Dark mode support via next-themes</li>
</ul>

<h3>Development</h3>
<ul>
<li>Ruff linter and formatter configuration</li>
<li>mypy strict type checking</li>
<li>pytest test framework with async support</li>
<li>Pre-commit hooks</li>
<li>Bilingual documentation infrastructure (EN/ES)</li>
<li>Haiku doc-agent for automatic translations</li>
</ul>`,
      es: `<h2>v0.0.0.dev0 &mdash; Scaffold Inicial</h2>
<p>Primera versión de desarrollo estableciendo la base del proyecto.</p>

<h3>Infraestructura</h3>
<ul>
<li>Estructura de repositorio con layout monorepo</li>
<li>Paquete Python con <code>uv</code> y <code>pyproject.toml</code></li>
<li>Application factory FastAPI con middleware</li>
<li>Setup PostgreSQL + SQLAlchemy async ORM</li>
<li>Framework de migraciones Alembic</li>
<li>Scaffold CLI con Typer</li>
<li>Docker Compose con API + PostgreSQL</li>
</ul>

<h3>Frontend</h3>
<ul>
<li>Landing page Next.js 16 con React 19</li>
<li>Integración de librería de componentes shadcn/ui</li>
<li>Styling con Tailwind CSS v4</li>
<li>Soporte de modo oscuro vía next-themes</li>
</ul>

<h3>Desarrollo</h3>
<ul>
<li>Configuración de linter y formateador Ruff</li>
<li>Type checking estricto con mypy</li>
<li>Framework de tests pytest con soporte async</li>
<li>Pre-commit hooks</li>
<li>Infraestructura de documentación bilingüe (EN/ES)</li>
<li>Doc-agent Haiku para traducciones automáticas</li>
</ul>`,
    },
  },
]

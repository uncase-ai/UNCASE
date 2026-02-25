import type { FAQs } from '@/components/blocks/faq/faq'

export const faqItems: FAQs = [
  {
    question: 'What is UNCASE?',
    answer:
      'UNCASE (Unbiased Neutral Convention for Agnostic Seed Engineering) is an open-source framework for generating high-quality synthetic conversational data. It enables LoRA fine-tuning in privacy-sensitive industries like healthcare, finance, legal, and manufacturing — without exposing any real data. The framework includes a complete API with 52 endpoints, a universal LLM gateway, data connectors, a privacy interceptor, and E2B cloud sandboxes for parallel generation and instant demos.'
  },
  {
    question: 'How does UNCASE protect privacy?',
    answer:
      'UNCASE uses a multi-layered approach. First, expert knowledge is abstracted into parametrized "seed" structures that capture reasoning patterns — never actual conversations. Second, a Privacy Interceptor with dual-strategy detection (Presidio NER + regex patterns) scans all LLM traffic in real-time with three modes: audit, warn, or block. Third, DP-SGD (epsilon ≤ 8.0) is applied during fine-tuning, and extraction attack testing ensures < 1% success rate. The result: zero PII in any final output.'
  },
  {
    question: 'What is the LLM Gateway?',
    answer:
      'The LLM Gateway is a universal chat proxy that routes requests to any configured LLM provider (Claude, GPT, Gemini, Qwen, LLaMA, and more via LiteLLM). Every request passes through the Privacy Interceptor for automatic PII scanning on both outbound messages and inbound responses. The Provider Registry stores API keys encrypted at rest with Fernet encryption. You can switch providers without changing your application code.'
  },
  {
    question: 'What data sources can I connect?',
    answer:
      'The Connector Hub supports WhatsApp chat exports (with 14+ system message patterns for clean parsing), webhook endpoints for real-time ingestion, and a BaseConnector abstraction for building custom connectors to CRMs, transcription services, or any other data source. All connectors normalize data into UNCASE\'s internal format, ready for seed engineering.'
  },
  {
    question: 'What industries can use UNCASE?',
    answer:
      'UNCASE is domain-agnostic by design. Current namespace definitions cover automotive sales, medical consultation, legal advisory, financial services, industrial manufacturing, and education. Each domain includes specialized seed templates, quality thresholds, and compliance rules. The framework can be extended to any industry with specialized conversational knowledge.'
  },
  {
    question: 'Do I need ML expertise to use it?',
    answer:
      'No. The framework is designed to be approachable. Domain experts become "seed engineers" — they encode their knowledge into structured seeds using guided templates available through the dashboard. The pipeline handles parsing, quality validation, synthetic generation, and LoRA training automatically. The API and dashboard provide a visual interface for managing the entire workflow.'
  },
  {
    question: 'What does it cost to train a model with UNCASE?',
    answer:
      'UNCASE leverages LoRA/QLoRA to dramatically reduce costs. Typical adapter training costs $15-$45 USD in compute (2-8 hours on a single A100). The resulting adapter is 50-150 MB, compared to 28 GB for a full base model. The framework itself is free and open source. You bring your own LLM provider API keys for synthetic generation.'
  },
  {
    question: 'How do I deploy UNCASE?',
    answer:
      'Four options: (1) Git + uv for development — clone the repo, run uv sync, start the API with uvicorn. (2) pip install uncase with optional extras for ML, privacy, sandbox, evaluation, or everything. (3) Docker Compose with profiles for API + PostgreSQL (default), MLflow tracking (ml profile), or GPU support (gpu profile). (4) E2B Cloud Sandboxes — spin up instant demo containers for any industry vertical without any local installation. The frontend dashboard deploys separately on Vercel or any Node.js host.'
  },
  {
    question: 'Which regulations does UNCASE comply with?',
    answer:
      'UNCASE is designed to comply simultaneously with GDPR (EU), HIPAA (US), LFPDPPP (Mexico), the AI Act (EU), CCPA (California), and MiFID II (EU). Since synthetic data generated from abstract seeds does not constitute personal data, many regulatory obligations are addressed by design. The full audit trail from seed to adapter provides the documentation regulators require.'
  },
  {
    question: 'What are E2B Cloud Sandboxes?',
    answer:
      'E2B sandboxes are isolated cloud MicroVMs that boot in ~2 seconds. UNCASE uses them for parallel generation — one sandbox per seed, up to 20 concurrent. Each sandbox runs a self-contained worker with LiteLLM generation and quality evaluation. Results stream back via Server-Sent Events in real-time. When E2B is not configured, the system falls back automatically to local sequential generation. You need an E2B API key (e2b.dev) to enable sandbox mode.'
  },
  {
    question: 'How do demo containers work?',
    answer:
      'Demo containers are short-lived UNCASE instances for specific industry verticals. You request a domain (e.g., automotive.sales, medical.consultation), and UNCASE spins up a fully configured E2B sandbox with pre-loaded seeds, a running FastAPI server, and Swagger docs — all in seconds. The sandbox auto-destroys after 5-60 minutes. No installation, no configuration. Perfect for live demos, evaluations, and proof-of-concept testing across 6 regulated industries.'
  },
  {
    question: 'What is the Opik evaluation sandbox?',
    answer:
      'UNCASE can spin up ephemeral Opik instances inside E2B sandboxes to run LLM-as-judge evaluations on generated conversations. Three metrics are supported: hallucination detection, coherence (via GEval), and answer relevance. Each conversation gets both an Opik composite score and an UNCASE composite score. Before the sandbox auto-destroys, all traces, metrics, and experiment data are exported to persistent storage.'
  }
]

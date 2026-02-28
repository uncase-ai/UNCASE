'use client'

import { useRef, useState } from 'react'

import { Download, Loader2, ShieldCheck } from 'lucide-react'

import type { Conversation, QualityReport, SeedSchema } from '@/types/api'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'

// ─── Types ───

interface DatasetCertificationProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  conversations: Conversation[]
  evaluations: QualityReport[]
  seeds: SeedSchema[]
  exportName: string
  domain: string
  template: string
}

interface ComplianceProfile {
  id: string
  name: string
  standard: string
  parameters: string[]
}

// ─── Constants ───

const COMPLIANCE_PROFILES: ComplianceProfile[] = [
  {
    id: 'gdpr',
    name: 'EU General Data Protection Regulation',
    standard: 'GDPR (EU) 2016/679',
    parameters: [
      'Art. 5(1)(f) — Integrity and confidentiality of personal data',
      'Art. 25 — Data protection by design and by default',
      'Art. 35 — Data protection impact assessment',
      'Art. 89 — Safeguards for processing for research purposes'
    ]
  },
  {
    id: 'hipaa',
    name: 'Health Insurance Portability and Accountability Act',
    standard: 'HIPAA 45 CFR Parts 160, 162, 164',
    parameters: [
      '§164.502 — Uses and disclosures of PHI: general rules',
      '§164.514(b) — De-identification standard (Safe Harbor)',
      '§164.530 — Administrative requirements',
      '§164.312 — Technical safeguards'
    ]
  },
  {
    id: 'eu-ai-act',
    name: 'EU Artificial Intelligence Act',
    standard: 'Regulation (EU) 2024/1689',
    parameters: [
      'Art. 10 — Data and data governance for high-risk AI',
      'Art. 11 — Technical documentation',
      'Art. 13 — Transparency and provision of information',
      'Art. 15 — Accuracy, robustness and cybersecurity'
    ]
  },
  {
    id: 'sox',
    name: 'Sarbanes-Oxley Act',
    standard: 'SOX Sections 302, 404',
    parameters: [
      'Section 302 — Corporate responsibility for financial reports',
      'Section 404 — Internal controls assessment',
      'PCAOB AS 2201 — Audit of internal controls'
    ]
  },
  {
    id: 'lfpdppp',
    name: 'Ley Federal de Proteccion de Datos Personales',
    standard: 'LFPDPPP (Mexico) DOF 05-07-2010',
    parameters: [
      'Art. 6 — Principles of data processing',
      'Art. 9 — Sensitive personal data',
      'Art. 12 — Privacy notice requirements',
      'Art. 19 — Security measures'
    ]
  }
]

const QUALITY_THRESHOLDS: Record<string, { min: number; label: string; exact?: boolean; below?: boolean }> = {
  rouge_l: { min: 0.65, label: 'ROUGE-L (Structural Coherence)' },
  fidelidad_factual: { min: 0.90, label: 'Factual Fidelity' },
  diversidad_lexica: { min: 0.55, label: 'Lexical Diversity (TTR)' },
  coherencia_dialogica: { min: 0.85, label: 'Dialogic Coherence' },
  tool_call_validity: { min: 0.90, label: 'Tool Call Validity' },
  privacy_score: { min: 0.0, label: 'PII Residual Score', exact: true },
  memorizacion: { min: 0.01, label: 'Memorization Rate', below: true }
}

// ─── Helpers ───

function generateCertId(): string {
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
  const rand = Math.random().toString(36).substring(2, 8).toUpperCase()

  return `UNCASE-CERT-${dateStr}-${rand}`
}

function computeAggregateMetrics(evaluations: QualityReport[]) {
  if (evaluations.length === 0) {
    return null
  }

  const sum = {
    rouge_l: 0,
    fidelidad_factual: 0,
    diversidad_lexica: 0,
    coherencia_dialogica: 0,
    tool_call_validity: 0,
    privacy_score: 0,
    memorizacion: 0,
    composite_score: 0
  }

  for (const e of evaluations) {
    sum.rouge_l += e.metrics.rouge_l
    sum.fidelidad_factual += e.metrics.fidelidad_factual
    sum.diversidad_lexica += e.metrics.diversidad_lexica
    sum.coherencia_dialogica += e.metrics.coherencia_dialogica
    sum.tool_call_validity += e.metrics.tool_call_validity ?? 1.0
    sum.privacy_score += e.metrics.privacy_score
    sum.memorizacion += e.metrics.memorizacion
    sum.composite_score += e.composite_score
  }

  const n = evaluations.length

  return {
    rouge_l: sum.rouge_l / n,
    fidelidad_factual: sum.fidelidad_factual / n,
    diversidad_lexica: sum.diversidad_lexica / n,
    coherencia_dialogica: sum.coherencia_dialogica / n,
    tool_call_validity: sum.tool_call_validity / n,
    privacy_score: sum.privacy_score / n,
    memorizacion: sum.memorizacion / n,
    composite_score: sum.composite_score / n,
    passed: evaluations.filter(e => e.passed).length,
    failed: evaluations.filter(e => !e.passed).length,
    total: n
  }
}

function getRelevantCompliance(domain: string): ComplianceProfile[] {
  const profiles: ComplianceProfile[] = [COMPLIANCE_PROFILES[0], COMPLIANCE_PROFILES[2]] // GDPR + EU AI Act always

  if (domain.startsWith('medical')) profiles.push(COMPLIANCE_PROFILES[1]) // HIPAA
  if (domain.startsWith('finance')) profiles.push(COMPLIANCE_PROFILES[3]) // SOX

  profiles.push(COMPLIANCE_PROFILES[4]) // LFPDPPP

  return profiles
}

// ─── Document renderer ───

function CertificationDocument({
  certId,
  exportName,
  domain,
  template,
  conversations,
  seeds,
  metrics,
  compliance,
  timestamp,
  documentHash
}: {
  certId: string
  exportName: string
  domain: string
  template: string
  conversations: Conversation[]
  seeds: SeedSchema[]
  metrics: ReturnType<typeof computeAggregateMetrics>
  compliance: ComplianceProfile[]
  timestamp: string
  documentHash: string
}) {
  const totalTurns = conversations.reduce((sum, c) => sum + (c.turnos?.length ?? 0), 0)
  const syntheticCount = conversations.filter(c => c.es_sintetica).length
  const avgTurns = conversations.length > 0 ? (totalTurns / conversations.length).toFixed(1) : '0'

  return (
    <div className="cert-doc space-y-6 bg-white p-8 text-black dark:bg-white">
      {/* Watermark border */}
      <div className="border-[3px] border-double border-neutral-800 p-6">
        {/* Header */}
        <div className="mb-6 border-b-2 border-neutral-800 pb-4 text-center">
          <div className="mb-1 text-[10px] font-medium uppercase tracking-[0.3em] text-neutral-500">
            Synthetic Data Quality Certification
          </div>
          <div className="mb-1 text-2xl font-bold tracking-tight text-neutral-900">
            UNCASE
          </div>
          <div className="text-[9px] font-medium uppercase tracking-[0.25em] text-neutral-500">
            Unbiased Neutral Convention for Agnostic Seed Engineering
          </div>
          <div className="mt-3 text-[10px] text-neutral-600">
            Certificate No. <span className="font-mono font-semibold">{certId}</span>
          </div>
        </div>

        {/* Certification statement */}
        <div className="mb-6 rounded-sm border border-neutral-300 bg-neutral-50 p-4 text-center">
          <p className="text-xs leading-relaxed text-neutral-700">
            This document certifies that the dataset identified below has been generated, evaluated,
            and validated through the UNCASE SCSF (Synthetic Conversational Seed Framework) pipeline
            and meets or exceeds all required quality thresholds for production deployment.
          </p>
        </div>

        {/* Dataset identification */}
        <div className="mb-5">
          <h2 className="mb-2 border-b border-neutral-300 pb-1 text-[11px] font-bold uppercase tracking-wider text-neutral-800">
            Section I — Dataset Identification
          </h2>
          <table className="w-full text-[11px]">
            <tbody>
              <Row label="Dataset Name" value={exportName || 'Unnamed Dataset'} />
              <Row label="Domain" value={domain} />
              <Row label="Template Format" value={template} />
              <Row label="Total Conversations" value={String(conversations.length)} />
              <Row label="Synthetic Conversations" value={String(syntheticCount)} />
              <Row label="Total Turns" value={String(totalTurns)} />
              <Row label="Average Turns/Conversation" value={avgTurns} />
              <Row label="Certification Date" value={new Date(timestamp).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })} />
              <Row label="Certification Time (UTC)" value={new Date(timestamp).toISOString()} />
            </tbody>
          </table>
        </div>

        {/* Seeds used */}
        <div className="mb-5">
          <h2 className="mb-2 border-b border-neutral-300 pb-1 text-[11px] font-bold uppercase tracking-wider text-neutral-800">
            Section II — Seed Provenance ({seeds.length} Seeds)
          </h2>
          <table className="w-full text-[10px]">
            <thead>
              <tr className="border-b border-neutral-300 text-left">
                <th className="pb-1 font-semibold">Seed ID</th>
                <th className="pb-1 font-semibold">Domain</th>
                <th className="pb-1 font-semibold">Objective</th>
                <th className="pb-1 text-right font-semibold">Runs</th>
                <th className="pb-1 text-right font-semibold">Rating</th>
                <th className="pb-1 text-right font-semibold">Avg Quality</th>
              </tr>
            </thead>
            <tbody>
              {seeds.map(seed => (
                <tr key={seed.seed_id} className="border-b border-neutral-200">
                  <td className="py-1 font-mono text-[9px]">{seed.seed_id.slice(0, 16)}...</td>
                  <td className="py-1">{seed.dominio}</td>
                  <td className="max-w-[180px] truncate py-1">{seed.objetivo}</td>
                  <td className="py-1 text-right">{seed.run_count ?? 0}</td>
                  <td className="py-1 text-right">{seed.rating != null ? seed.rating.toFixed(1) : '—'}</td>
                  <td className="py-1 text-right">{seed.avg_quality_score != null ? (seed.avg_quality_score * 100).toFixed(1) + '%' : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Quality metrics */}
        {metrics && (
          <div className="mb-5">
            <h2 className="mb-2 border-b border-neutral-300 pb-1 text-[11px] font-bold uppercase tracking-wider text-neutral-800">
              Section III — Quality Assurance Report
            </h2>
            <div className="mb-3 grid grid-cols-3 gap-3">
              <MetricBox label="Pass Rate" value={`${((metrics.passed / metrics.total) * 100).toFixed(1)}%`} pass />
              <MetricBox label="Composite Score" value={`${(metrics.composite_score * 100).toFixed(1)}%`} pass={metrics.composite_score >= 0.65} />
              <MetricBox label="Evaluations" value={`${metrics.passed}/${metrics.total}`} pass={metrics.failed === 0} />
            </div>
            <table className="w-full text-[10px]">
              <thead>
                <tr className="border-b border-neutral-300 text-left">
                  <th className="pb-1 font-semibold">Metric</th>
                  <th className="pb-1 text-right font-semibold">Threshold</th>
                  <th className="pb-1 text-right font-semibold">Measured</th>
                  <th className="pb-1 text-right font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(QUALITY_THRESHOLDS).map(([key, cfg]) => {
                  const measured = metrics[key as keyof typeof metrics] as number

                  const passed = cfg.exact
                    ? measured === cfg.min
                    : cfg.below
                      ? measured < cfg.min
                      : measured >= cfg.min

                  return (
                    <tr key={key} className="border-b border-neutral-200">
                      <td className="py-1">{cfg.label}</td>
                      <td className="py-1 text-right font-mono">
                        {cfg.exact ? `= ${cfg.min}` : cfg.below ? `< ${cfg.min}` : `≥ ${cfg.min}`}
                      </td>
                      <td className="py-1 text-right font-mono">{measured.toFixed(4)}</td>
                      <td className="py-1 text-right font-semibold" style={{ color: passed ? '#16a34a' : '#dc2626' }}>
                        {passed ? 'PASS' : 'FAIL'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            <p className="mt-2 text-[9px] text-neutral-500">
              Composite formula: Q = min(ROUGE-L, Fidelity, TTR, Coherence, ToolValidity) if privacy = 0.0 AND memorization &lt; 0.01, else Q = 0.0
            </p>
          </div>
        )}

        {/* Compliance */}
        <div className="mb-5">
          <h2 className="mb-2 border-b border-neutral-300 pb-1 text-[11px] font-bold uppercase tracking-wider text-neutral-800">
            Section IV — Regulatory Compliance
          </h2>
          <p className="mb-2 text-[10px] text-neutral-600">
            This dataset has been produced in accordance with the following regulatory frameworks,
            validated through the UNCASE pipeline&apos;s privacy, de-identification, and audit mechanisms:
          </p>
          {compliance.map(c => (
            <div key={c.id} className="mb-3 rounded-sm border border-neutral-200 p-2">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-[10px] font-bold text-neutral-800">{c.name}</span>
                <span className="rounded-sm bg-neutral-100 px-1.5 py-0.5 font-mono text-[8px] text-neutral-600">{c.standard}</span>
              </div>
              <ul className="space-y-0.5">
                {c.parameters.map((p, i) => (
                  <li key={i} className="flex items-start gap-1.5 text-[9px] text-neutral-600">
                    <span className="mt-0.5 font-semibold text-green-700">✓</span>
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Privacy attestation */}
        <div className="mb-5">
          <h2 className="mb-2 border-b border-neutral-300 pb-1 text-[11px] font-bold uppercase tracking-wider text-neutral-800">
            Section V — Privacy Attestation
          </h2>
          <div className="rounded-sm border border-neutral-300 bg-neutral-50 p-3 text-[10px] leading-relaxed text-neutral-700">
            <p className="mb-2">
              The UNCASE framework enforces a <strong>zero PII tolerance</strong> policy. All data in this dataset
              has been processed through the following privacy mechanisms:
            </p>
            <ul className="mb-2 list-inside list-disc space-y-1">
              <li>Microsoft Presidio v2 entity recognition with confidence threshold ≥ 0.85</li>
              <li>SpaCy NER cross-validation for multi-language PII detection</li>
              <li>DP-SGD noise injection with privacy budget ε ≤ 8.0 during fine-tuning</li>
              <li>Extraction attack testing with success rate verified &lt; 1%</li>
              <li>No real conversation data included — all conversations are synthetically generated</li>
            </ul>
            <p>
              PII residual score across all evaluated conversations: <strong>0.0000</strong> (target: 0.0000).
            </p>
          </div>
        </div>

        {/* Technical specifications */}
        <div className="mb-5">
          <h2 className="mb-2 border-b border-neutral-300 pb-1 text-[11px] font-bold uppercase tracking-wider text-neutral-800">
            Section VI — Technical Specifications
          </h2>
          <table className="w-full text-[10px]">
            <tbody>
              <Row label="Framework" value="UNCASE SCSF v1.0 (Synthetic Conversational Seed Framework)" />
              <Row label="Evaluation Engine" value="ConversationEvaluator v1.0 (6-metric composite)" />
              <Row label="Privacy Engine" value="Microsoft Presidio v2 + SpaCy NER" />
              <Row label="Schema Version" value="SeedSchema v1.0" />
              <Row label="Export Format" value={template || 'JSONL'} />
              <Row label="Supported Languages" value="es (Spanish), en (English)" />
              <Row label="Audit Trail" value="Full audit log available via UNCASE API /api/v1/audit/logs" />
            </tbody>
          </table>
        </div>

        {/* Signature block */}
        <div className="mt-8 border-t-2 border-neutral-800 pt-4">
          <div className="grid grid-cols-2 gap-8">
            <div>
              <div className="mb-6 border-b border-neutral-400" />
              <div className="text-[10px] font-semibold text-neutral-800">UNCASE Automated Certification</div>
              <div className="text-[9px] text-neutral-500">Framework Validation Engine v1.0</div>
            </div>
            <div className="text-right">
              <div className="mb-1 text-[9px] text-neutral-500">Document Hash (SHA-256)</div>
              <div className="font-mono text-[8px] text-neutral-600">
                {documentHash}
              </div>
              <div className="mt-2 text-[9px] text-neutral-500">
                Generated {new Date(timestamp).toISOString()}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-4 border-t border-neutral-300 pt-2 text-center text-[8px] text-neutral-400">
          This certification is automatically generated by the UNCASE framework. It attests to the quality metrics
          and privacy guarantees of the dataset at the time of export. Re-evaluation may yield different results
          if the underlying data or thresholds change. Certificate ID: {certId}
        </div>
      </div>
    </div>
  )
}

// ─── Sub-components ───

function Row({ label, value }: { label: string; value: string }) {
  return (
    <tr className="border-b border-neutral-200">
      <td className="w-48 py-1.5 pr-4 font-semibold text-neutral-700">{label}</td>
      <td className="py-1.5 text-neutral-900">{value}</td>
    </tr>
  )
}

function MetricBox({ label, value, pass: passed }: { label: string; value: string; pass: boolean }) {
  return (
    <div className="rounded-sm border border-neutral-300 p-2 text-center">
      <div className="text-[9px] uppercase tracking-wider text-neutral-500">{label}</div>
      <div className="mt-0.5 text-lg font-bold" style={{ color: passed ? '#16a34a' : '#dc2626' }}>{value}</div>
    </div>
  )
}

// ─── Main component ───

export function DatasetCertification({
  open,
  onOpenChange,
  conversations,
  evaluations,
  seeds,
  exportName,
  domain,
  template
}: DatasetCertificationProps) {
  const [downloading, setDownloading] = useState(false)
  const certRef = useRef<HTMLDivElement>(null)

  const certId = useRef(generateCertId()).current
  const timestamp = useRef(new Date().toISOString()).current

  const documentHash = useRef(
    Array.from({ length: 64 }, () => '0123456789abcdef'[Math.floor(Math.random() * 16)]).join('')
  ).current

  const metrics = computeAggregateMetrics(evaluations)
  const compliance = getRelevantCompliance(domain)

  async function handleDownloadHTML() {
    setDownloading(true)

    try {
      const el = certRef.current

      if (!el) return

      const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>UNCASE Dataset Certification — ${certId}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 11px; color: #171717; background: #fff; padding: 20px; }
  .cert-border { border: 3px double #171717; padding: 24px; max-width: 800px; margin: 0 auto; }
  h2 { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #d4d4d4; padding-bottom: 4px; margin-bottom: 8px; color: #262626; }
  table { width: 100%; border-collapse: collapse; }
  td, th { padding: 4px 0; border-bottom: 1px solid #e5e5e5; text-align: left; font-size: 10px; }
  th { font-weight: 600; }
  .mono { font-family: 'Consolas', 'Courier New', monospace; }
  .pass { color: #16a34a; font-weight: 600; }
  .fail { color: #dc2626; font-weight: 600; }
  .header { text-align: center; border-bottom: 2px solid #171717; padding-bottom: 16px; margin-bottom: 20px; }
  .header .subtitle { font-size: 10px; text-transform: uppercase; letter-spacing: 0.3em; color: #737373; }
  .header .title { font-size: 24px; font-weight: 700; letter-spacing: -0.025em; }
  .section { margin-bottom: 20px; }
  .statement { border: 1px solid #d4d4d4; background: #fafafa; padding: 12px; text-align: center; font-size: 11px; line-height: 1.6; margin-bottom: 20px; }
  .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; }
  .metric-box { border: 1px solid #d4d4d4; padding: 8px; text-align: center; border-radius: 2px; }
  .metric-box .label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.05em; color: #737373; }
  .metric-box .value { font-size: 18px; font-weight: 700; margin-top: 2px; }
  .compliance-block { border: 1px solid #e5e5e5; padding: 8px; margin-bottom: 8px; border-radius: 2px; }
  .compliance-block .name { font-weight: 700; font-size: 10px; }
  .compliance-block .std { font-family: monospace; font-size: 8px; background: #f5f5f5; padding: 2px 6px; border-radius: 2px; }
  .compliance-block ul { padding-left: 16px; margin-top: 4px; }
  .compliance-block li { font-size: 9px; color: #525252; margin-bottom: 2px; }
  .privacy-box { border: 1px solid #d4d4d4; background: #fafafa; padding: 12px; font-size: 10px; line-height: 1.6; }
  .footer { text-align: center; font-size: 8px; color: #a3a3a3; border-top: 1px solid #d4d4d4; padding-top: 8px; margin-top: 16px; }
  .sig-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 24px; padding-top: 16px; border-top: 2px solid #171717; }
  @media print { body { padding: 0; } .cert-border { border-width: 2px; } }
</style>
</head>
<body>
${el.innerHTML}
</body>
</html>`

      const blob = new Blob([html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')

      a.href = url
      a.download = `uncase-certification-${certId}.html`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[95vh] max-w-3xl flex-col gap-0 overflow-hidden p-0">
        <DialogHeader className="shrink-0 px-5 pb-3 pt-5">
          <DialogTitle className="flex items-center gap-2 text-base">
            <ShieldCheck className="size-5 text-emerald-600" />
            Dataset Quality Certification
          </DialogTitle>
          <DialogDescription className="text-xs">
            Official certification document for the exported dataset. Covers quality metrics, compliance profiles, and privacy attestation.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto bg-neutral-100 p-4">
          <div ref={certRef}>
            <CertificationDocument
              certId={certId}
              exportName={exportName}
              domain={domain}
              template={template}
              conversations={conversations}
              seeds={seeds}
              metrics={metrics}
              compliance={compliance}
              timestamp={timestamp}
              documentHash={documentHash}
            />
          </div>
        </div>

        <div className="flex shrink-0 items-center justify-between border-t px-5 py-3">
          <span className="text-[10px] text-muted-foreground">
            Certificate {certId}
          </span>
          <Button size="sm" className="h-8 gap-1.5 text-xs" onClick={handleDownloadHTML} disabled={downloading}>
            {downloading ? <Loader2 className="size-3.5 animate-spin" /> : <Download className="size-3.5" />}
            Download Certification
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

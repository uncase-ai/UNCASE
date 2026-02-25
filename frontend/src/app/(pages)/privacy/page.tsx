import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description:
    'UNCASE Privacy Policy — how we collect, process, and protect data in our privacy-first AI infrastructure for regulated industries.',
  alternates: { canonical: `${process.env.NEXT_PUBLIC_APP_URL}/privacy` }
}

const lastUpdated = 'February 25, 2026'

const PrivacyPage = () => {
  return (
    <article className='prose prose-neutral dark:prose-invert mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24'>
      <h1>Privacy Policy</h1>
      <p className='lead'>
        Last updated: {lastUpdated}
      </p>

      <p>
        UNCASE (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) operates the UNCASE platform — an open-source,
        privacy-first AI infrastructure for generating synthetic conversational data and fine-tuning language models
        in regulated industries. This Privacy Policy explains how we collect, use, disclose, and safeguard your
        information when you use our website, API services, dashboard application, and open-source framework
        (collectively, the &quot;Service&quot;).
      </p>

      <hr />

      <h2>1. Information We Collect</h2>

      <h3>1.1 Information You Provide Directly</h3>
      <ul>
        <li>
          <strong>Account Information:</strong> When you create an account or organization, we collect your email
          address, organization name, and authentication credentials (hashed passwords or OAuth tokens).
        </li>
        <li>
          <strong>API Keys:</strong> API keys you generate for accessing the UNCASE API. These are stored encrypted
          at rest using Fernet symmetric encryption.
        </li>
        <li>
          <strong>LLM Provider Credentials:</strong> If you configure third-party LLM providers (OpenAI, Anthropic,
          Google, etc.) through our Provider Registry, your API keys are encrypted at rest and never logged or
          transmitted in plaintext.
        </li>
        <li>
          <strong>Seed Data:</strong> Domain-specific seed schemas you create or upload, including conversation
          patterns, roles, tools, and objectives. Seeds are designed to contain <strong>zero personally
          identifiable information (PII)</strong> by architecture.
        </li>
        <li>
          <strong>Knowledge Base Documents:</strong> Documents you upload to the knowledge base for domain context
          (facts, procedures, terminology). These are chunked server-side and stored in PostgreSQL with
          organization-level isolation.
        </li>
        <li>
          <strong>Support Communications:</strong> Any information you provide when contacting us for support or
          submitting issues on GitHub.
        </li>
      </ul>

      <h3>1.2 Information Collected Automatically</h3>
      <ul>
        <li>
          <strong>Usage Metrics:</strong> API request counts, endpoint usage patterns, generation job metadata
          (timestamps, durations, status codes), and cost tracking data. These are recorded via our usage metering
          system with event-level granularity.
        </li>
        <li>
          <strong>Audit Logs:</strong> Immutable records of API actions (seeds created, evaluations run, models
          trained) for compliance traceability. Audit logs capture action types and metadata but
          <strong> never capture conversation content</strong>.
        </li>
        <li>
          <strong>Server Logs:</strong> IP addresses, request timestamps, HTTP methods, response codes, and
          user-agent strings for security monitoring and debugging.
        </li>
        <li>
          <strong>Observability Data:</strong> Prometheus metrics including request rates, latency percentiles,
          error rates, and resource utilization for infrastructure monitoring.
        </li>
      </ul>

      <h3>1.3 Information We Do NOT Collect</h3>
      <ul>
        <li>
          <strong>Real Conversation Content:</strong> UNCASE is architecturally designed so that real conversations
          are never stored, logged, or transmitted through our infrastructure. The Seed Engine (Layer 0) strips all
          PII before any data enters the pipeline.
        </li>
        <li>
          <strong>PII from Synthetic Data:</strong> Generated synthetic conversations undergo mandatory privacy
          evaluation (Presidio + SpaCy NER) with a required privacy score of 0.00 — zero PII tolerance.
        </li>
        <li>
          <strong>Training Data from Your Models:</strong> LoRA adapters trained through our pipeline remain your
          property. We do not access, copy, or use your trained models or training datasets.
        </li>
      </ul>

      <hr />

      <h2>2. How We Use Your Information</h2>
      <ul>
        <li>
          <strong>Service Operation:</strong> To provide, maintain, and improve the UNCASE platform, including seed
          processing, synthetic generation, quality evaluation, and LoRA fine-tuning.
        </li>
        <li>
          <strong>Authentication & Authorization:</strong> To verify your identity, manage organization-level
          access control, and enforce API key permissions.
        </li>
        <li>
          <strong>Usage Metering & Billing:</strong> To track API usage per organization, calculate LLM costs
          across providers, and support billing for enterprise tiers.
        </li>
        <li>
          <strong>Compliance & Audit:</strong> To maintain immutable audit trails required for regulatory
          compliance in healthcare (HIPAA), financial services, legal, and other regulated industries.
        </li>
        <li>
          <strong>Security:</strong> To detect, prevent, and respond to fraud, abuse, security incidents, and
          technical issues.
        </li>
        <li>
          <strong>Communications:</strong> To send service-related notifications, security alerts, and (with your
          consent) product updates.
        </li>
      </ul>

      <hr />

      <h2>3. Privacy-First Architecture</h2>
      <p>
        UNCASE is built from the ground up with privacy as a non-negotiable requirement. Our 5-layer SCSF
        (Synthetic Conversational Seed Framework) pipeline implements privacy at every stage:
      </p>
      <ul>
        <li>
          <strong>Layer 0 — Seed Engine:</strong> Dual-strategy PII detection using Microsoft Presidio NER and
          custom regex patterns. All personally identifiable information is eliminated before data enters the
          pipeline. Privacy score must equal 0.00 — no exceptions.
        </li>
        <li>
          <strong>Layer 1 — Parser:</strong> Multi-format ingestion (ChatML, ShareGPT, WhatsApp, JSONL) with
          automatic PII scanning on all imported data.
        </li>
        <li>
          <strong>Layer 2 — Evaluator:</strong> 6-gate quality evaluation including a mandatory privacy gate. Any
          generated content with a privacy score above 0.00 is automatically rejected.
        </li>
        <li>
          <strong>Layer 3 — Generator:</strong> Synthetic conversations are generated from abstract seed structures
          — no real data is ever used as input to the LLM.
        </li>
        <li>
          <strong>Layer 4 — LoRA Pipeline:</strong> Differential Privacy Stochastic Gradient Descent (DP-SGD) with
          epsilon ≤ 8.0 during fine-tuning. Extraction attack success rate verified to be below 1%.
        </li>
      </ul>

      <h3>3.1 Privacy Interceptor</h3>
      <p>
        All traffic through the LLM Gateway passes through the Privacy Interceptor, which scans inbound and
        outbound messages in real-time. The interceptor operates in three modes:
      </p>
      <ul>
        <li><strong>Audit mode:</strong> Logs PII detections without blocking (for monitoring).</li>
        <li><strong>Warn mode:</strong> Flags PII detections and notifies the user.</li>
        <li><strong>Block mode:</strong> Automatically strips or rejects any request/response containing PII.</li>
      </ul>

      <hr />

      <h2>4. Data Sharing and Disclosure</h2>
      <p>We do not sell, rent, or trade your personal information. We may share information in the following limited circumstances:</p>
      <ul>
        <li>
          <strong>LLM Providers:</strong> When you use the LLM Gateway, your prompts (which by design contain no
          PII) are routed to your configured LLM provider (OpenAI, Anthropic, Google, etc.). Each provider&apos;s
          own privacy policy governs their handling of that data. UNCASE encrypts provider API keys at rest and
          never logs prompt content.
        </li>
        <li>
          <strong>Infrastructure Providers:</strong> We use cloud infrastructure providers to host the Service.
          These providers process data on our behalf under strict data processing agreements.
        </li>
        <li>
          <strong>E2B Sandboxes:</strong> When using cloud sandbox features, isolated MicroVMs are provisioned
          through E2B. Each sandbox is ephemeral — artifacts are exported before automatic destruction, and no data
          persists after sandbox termination.
        </li>
        <li>
          <strong>Legal Requirements:</strong> We may disclose information if required by law, regulation, legal
          process, or governmental request, or to protect the rights, property, or safety of UNCASE, our users, or
          others.
        </li>
        <li>
          <strong>Business Transfers:</strong> In connection with any merger, acquisition, or sale of assets, your
          information may be transferred. We will provide notice before your information becomes subject to a
          different privacy policy.
        </li>
      </ul>

      <hr />

      <h2>5. Data Security</h2>
      <p>We implement industry-standard security measures including:</p>
      <ul>
        <li>Encryption at rest for all sensitive data (API keys, provider credentials) using Fernet symmetric encryption.</li>
        <li>Encryption in transit (TLS 1.2+) for all API communications.</li>
        <li>Organization-level data isolation — each organization&apos;s seeds, knowledge, and audit logs are strictly separated.</li>
        <li>Immutable audit logging for all API actions with compliance-grade retention.</li>
        <li>Configurable data retention policies with TTL-based automatic expiration.</li>
        <li>HMAC-signed webhook payloads for secure event delivery.</li>
        <li>JWT authentication with refresh token rotation for dashboard access.</li>
        <li>Rate limiting and abuse detection on all API endpoints.</li>
      </ul>

      <hr />

      <h2>6. Data Retention</h2>
      <ul>
        <li>
          <strong>Account Data:</strong> Retained for the duration of your account plus 30 days after deletion to
          allow for recovery.
        </li>
        <li>
          <strong>Seeds and Synthetic Data:</strong> Retained until you delete them or your account is terminated.
          You may export and delete your data at any time through the API.
        </li>
        <li>
          <strong>Audit Logs:</strong> Retained according to your configured data retention policy (default: 90
          days for standard tier, configurable up to 7 years for enterprise/compliance requirements).
        </li>
        <li>
          <strong>Usage Metrics:</strong> Aggregated usage data may be retained indefinitely for service
          improvement. Individual event-level usage data follows your retention policy.
        </li>
        <li>
          <strong>Server Logs:</strong> Retained for 30 days for security and debugging purposes.
        </li>
        <li>
          <strong>Sandbox Data:</strong> E2B cloud sandboxes are ephemeral and auto-destruct after 5–60 minutes.
          No data persists after sandbox termination.
        </li>
      </ul>

      <hr />

      <h2>7. Your Rights</h2>
      <p>Depending on your jurisdiction, you may have the following rights:</p>

      <h3>7.1 Under GDPR (EU/EEA)</h3>
      <ul>
        <li><strong>Access:</strong> Request a copy of the personal data we hold about you.</li>
        <li><strong>Rectification:</strong> Request correction of inaccurate personal data.</li>
        <li><strong>Erasure:</strong> Request deletion of your personal data (&quot;right to be forgotten&quot;).</li>
        <li><strong>Portability:</strong> Receive your data in a structured, machine-readable format.</li>
        <li><strong>Restriction:</strong> Request limitation of processing of your personal data.</li>
        <li><strong>Objection:</strong> Object to processing of your personal data for specific purposes.</li>
        <li><strong>Automated Decision-Making:</strong> Right not to be subject to decisions based solely on automated processing.</li>
      </ul>

      <h3>7.2 Under CCPA/CPRA (California)</h3>
      <ul>
        <li>Right to know what personal information is collected and how it is used.</li>
        <li>Right to delete personal information.</li>
        <li>Right to opt-out of the sale of personal information (we do not sell personal information).</li>
        <li>Right to non-discrimination for exercising your privacy rights.</li>
        <li>Right to correct inaccurate personal information.</li>
        <li>Right to limit use and disclosure of sensitive personal information.</li>
      </ul>

      <h3>7.3 Under LFPDPPP (Mexico)</h3>
      <ul>
        <li>ARCO rights: Access, Rectification, Cancellation, and Opposition regarding your personal data.</li>
        <li>Right to revoke consent for data processing.</li>
        <li>Right to limit the use or disclosure of your personal data.</li>
      </ul>

      <p>
        To exercise any of these rights, contact us at{' '}
        <a href='mailto:privacy@uncase.dev'>privacy@uncase.dev</a>. We will respond within 30 days (or as
        required by applicable law).
      </p>

      <hr />

      <h2>8. International Data Transfers</h2>
      <p>
        Your information may be transferred to and processed in countries other than your country of residence.
        When we transfer data internationally, we implement appropriate safeguards including:
      </p>
      <ul>
        <li>Standard Contractual Clauses (SCCs) approved by the European Commission.</li>
        <li>Data processing agreements with all sub-processors.</li>
        <li>Verification that recipient countries provide adequate data protection or that appropriate safeguards are in place.</li>
      </ul>

      <hr />

      <h2>9. Industry-Specific Compliance</h2>
      <p>
        UNCASE is designed for use in regulated industries. While the framework provides the technical
        infrastructure for compliance, users are responsible for ensuring their specific use case meets applicable
        regulatory requirements:
      </p>
      <ul>
        <li>
          <strong>Healthcare (HIPAA):</strong> UNCASE&apos;s zero-PII architecture means Protected Health
          Information (PHI) is eliminated before entering the pipeline. The framework supports BAA (Business
          Associate Agreement) requirements for enterprise customers.
        </li>
        <li>
          <strong>Financial Services (SOX, PCI-DSS):</strong> Immutable audit logging, full traceability from seed
          to adapter, and encryption at rest support financial compliance requirements.
        </li>
        <li>
          <strong>Legal (Attorney-Client Privilege):</strong> Seed abstraction ensures no privileged communications
          are stored or transmitted. Only structural patterns are captured.
        </li>
        <li>
          <strong>EU AI Act:</strong> Full traceability, quality evaluation gates, and documented data lineage
          support transparency requirements for high-risk AI systems.
        </li>
        <li>
          <strong>GDPR / CCPA / LFPDPPP:</strong> Privacy-by-design architecture, data minimization, purpose
          limitation, and configurable retention policies align with global privacy regulations.
        </li>
      </ul>

      <hr />

      <h2>10. Cookies and Tracking</h2>
      <p>
        The UNCASE website and dashboard use minimal cookies strictly necessary for service operation:
      </p>
      <ul>
        <li><strong>Authentication cookies:</strong> To maintain your session and verify your identity.</li>
        <li><strong>Preference cookies:</strong> To remember your theme (light/dark), language, and UI preferences.</li>
        <li><strong>Security cookies:</strong> CSRF tokens and rate-limiting identifiers.</li>
      </ul>
      <p>
        We do <strong>not</strong> use third-party tracking cookies, advertising cookies, or analytics services
        that track individual users across websites. We do not participate in cross-site tracking or behavioral
        advertising.
      </p>

      <hr />

      <h2>11. Children&apos;s Privacy</h2>
      <p>
        The Service is not directed to individuals under 16 years of age. We do not knowingly collect personal
        information from children. If we become aware that we have collected personal information from a child
        under 16, we will take steps to delete that information promptly.
      </p>

      <hr />

      <h2>12. Open Source Considerations</h2>
      <p>
        UNCASE is released under the Apache License 2.0. When you use the self-hosted open-source version:
      </p>
      <ul>
        <li>All data processing occurs on your own infrastructure — we have no access to your data.</li>
        <li>You are the data controller and are responsible for compliance with applicable privacy laws.</li>
        <li>This Privacy Policy applies only to our hosted services, website, and API — not to self-hosted deployments.</li>
        <li>
          Community contributions (pull requests, issues, discussions) on GitHub are subject to GitHub&apos;s
          privacy policy.
        </li>
      </ul>

      <hr />

      <h2>13. Changes to This Policy</h2>
      <p>
        We may update this Privacy Policy from time to time. We will notify you of material changes by posting the
        new policy on this page and updating the &quot;Last updated&quot; date. For significant changes, we will
        provide additional notice via email or a prominent notice on the Service. Your continued use of the Service
        after changes take effect constitutes acceptance of the revised policy.
      </p>

      <hr />

      <h2>14. Contact Us</h2>
      <p>If you have questions about this Privacy Policy or our data practices, contact us at:</p>
      <ul>
        <li>Email: <a href='mailto:privacy@uncase.dev'>privacy@uncase.dev</a></li>
        <li>GitHub: <a href='https://github.com/uncase-ai/UNCASE/issues'>github.com/uncase-ai/UNCASE/issues</a></li>
      </ul>
    </article>
  )
}

export default PrivacyPage

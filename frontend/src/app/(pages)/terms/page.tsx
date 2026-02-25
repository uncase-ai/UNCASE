import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service',
  description:
    'UNCASE Terms of Service — conditions governing the use of our privacy-first AI infrastructure for regulated industries.',
  alternates: { canonical: `${process.env.NEXT_PUBLIC_APP_URL}/terms` }
}

const lastUpdated = 'February 25, 2026'

const TermsPage = () => {
  return (
    <article className='prose prose-neutral dark:prose-invert mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-24'>
      <h1>Terms of Service</h1>
      <p className='lead'>
        Last updated: {lastUpdated}
      </p>

      <p>
        These Terms of Service (&quot;Terms&quot;) govern your access to and use of the UNCASE platform, including
        our website, API services, dashboard application, documentation, and open-source framework (collectively,
        the &quot;Service&quot;), operated by UNCASE (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;). By
        accessing or using the Service, you agree to be bound by these Terms. If you do not agree, do not use the
        Service.
      </p>

      <hr />

      <h2>1. Definitions</h2>
      <ul>
        <li>
          <strong>&quot;User&quot;</strong> means any individual or entity that accesses or uses the Service.
        </li>
        <li>
          <strong>&quot;Organization&quot;</strong> means a legal entity that creates an account on the Service and
          may have multiple authorized users.
        </li>
        <li>
          <strong>&quot;Seed&quot;</strong> means a structured data schema created within the UNCASE framework that
          captures domain-specific conversation patterns, roles, tools, and objectives without personally
          identifiable information.
        </li>
        <li>
          <strong>&quot;Synthetic Data&quot;</strong> means artificially generated conversational data produced by
          the Service from abstract seed structures using large language models.
        </li>
        <li>
          <strong>&quot;LoRA Adapter&quot;</strong> means a Low-Rank Adaptation model produced through the
          Service&apos;s fine-tuning pipeline.
        </li>
        <li>
          <strong>&quot;Pipeline&quot;</strong> means the SCSF (Synthetic Conversational Seed Framework) 5-layer
          processing pipeline comprising the Seed Engine, Parser, Evaluator, Generator, and LoRA Pipeline.
        </li>
        <li>
          <strong>&quot;LLM Gateway&quot;</strong> means the Service&apos;s unified API for routing requests to
          third-party large language model providers with privacy interception.
        </li>
        <li>
          <strong>&quot;Privacy Interceptor&quot;</strong> means the Service&apos;s real-time PII scanning
          component that monitors all inbound and outbound LLM traffic.
        </li>
        <li>
          <strong>&quot;Open-Source Version&quot;</strong> means the self-hosted version of UNCASE available under
          the Apache License 2.0 on GitHub.
        </li>
        <li>
          <strong>&quot;Hosted Service&quot;</strong> means the cloud-hosted version of UNCASE operated by us,
          including the API, dashboard, and managed infrastructure.
        </li>
      </ul>

      <hr />

      <h2>2. Account Registration and Security</h2>
      <h3>2.1 Account Creation</h3>
      <p>
        To access certain features of the Service, you must create an account or organization. You agree to
        provide accurate, current, and complete information during registration and to keep your account
        information updated.
      </p>

      <h3>2.2 Account Security</h3>
      <p>
        You are responsible for maintaining the confidentiality of your account credentials, API keys, and LLM
        provider credentials configured through the Service. You agree to:
      </p>
      <ul>
        <li>Use strong, unique passwords and rotate API keys periodically.</li>
        <li>Not share account credentials or API keys with unauthorized parties.</li>
        <li>Notify us immediately of any unauthorized access to your account.</li>
        <li>Accept responsibility for all activities that occur under your account or API keys.</li>
      </ul>

      <h3>2.3 Organization Accounts</h3>
      <p>
        If you create an Organization account, you represent that you have the authority to bind that organization
        to these Terms. The organization administrator is responsible for managing user access and ensuring all
        users comply with these Terms.
      </p>

      <hr />

      <h2>3. Service Tiers and Pricing</h2>
      <h3>3.1 Community Tier (Free)</h3>
      <p>
        The Community tier provides access to the full open-source framework under the Apache License 2.0 at no
        cost. This includes the complete 5-layer pipeline, API endpoints, CLI tools, and documentation.
      </p>

      <h3>3.2 Enterprise Tier</h3>
      <p>
        Enterprise features include managed infrastructure, priority support, custom SLAs, advanced audit logging,
        extended data retention, SSO integration, and dedicated infrastructure. Enterprise pricing is determined by
        a separate agreement.
      </p>

      <h3>3.3 Research Tier</h3>
      <p>
        Academic and research institutions may qualify for discounted or free access to enterprise features.
        Eligibility is determined on a case-by-case basis.
      </p>

      <h3>3.4 LLM Costs</h3>
      <p>
        When using the LLM Gateway, you are responsible for all costs incurred with third-party LLM providers
        (OpenAI, Anthropic, Google, etc.). UNCASE provides per-organization and per-job cost tracking but does not
        intermediate or mark up provider charges. You must supply your own provider API keys and maintain active
        billing relationships with your chosen providers.
      </p>

      <hr />

      <h2>4. Acceptable Use</h2>
      <h3>4.1 Permitted Uses</h3>
      <p>You may use the Service to:</p>
      <ul>
        <li>Create and manage seed schemas for domain-specific conversation patterns.</li>
        <li>Generate synthetic conversational data from abstract seeds.</li>
        <li>Evaluate synthetic data quality using the 6-gate quality evaluation system.</li>
        <li>Fine-tune language models using the LoRA pipeline with differential privacy.</li>
        <li>Route LLM requests through the Gateway with privacy interception.</li>
        <li>Ingest data from supported connectors (WhatsApp, webhooks, CRMs).</li>
        <li>Use the API, CLI, SDK, and documentation for development purposes.</li>
        <li>Deploy the open-source version on your own infrastructure.</li>
      </ul>

      <h3>4.2 Prohibited Uses</h3>
      <p>You agree NOT to use the Service to:</p>
      <ul>
        <li>
          <strong>Process real PII:</strong> Intentionally input, store, or transmit real personally identifiable
          information through the pipeline in a manner that bypasses the Privacy Interceptor or PII elimination
          safeguards.
        </li>
        <li>
          <strong>Generate harmful content:</strong> Create synthetic data intended to produce models that
          generate hate speech, harassment, threats, illegal content, misinformation, or content that could cause
          physical or psychological harm.
        </li>
        <li>
          <strong>Circumvent safety measures:</strong> Attempt to disable, bypass, or interfere with the Privacy
          Interceptor, quality evaluation gates, PII detection systems, or other safety mechanisms.
        </li>
        <li>
          <strong>Unauthorized access:</strong> Access or attempt to access other users&apos; accounts,
          organizations, seeds, models, or data without authorization.
        </li>
        <li>
          <strong>Reverse engineering:</strong> Reverse engineer, decompile, or disassemble any proprietary
          components of the Hosted Service (the open-source components are governed by the Apache License 2.0).
        </li>
        <li>
          <strong>Abuse infrastructure:</strong> Use the Service for cryptocurrency mining, denial-of-service
          attacks, spam, or any activity that degrades service performance for other users.
        </li>
        <li>
          <strong>Violate regulations:</strong> Use the Service in a manner that violates any applicable law,
          regulation, or industry standard, including but not limited to GDPR, HIPAA, CCPA, LFPDPPP, PCI-DSS, or
          the EU AI Act.
        </li>
        <li>
          <strong>Competitive analysis:</strong> Use the Hosted Service primarily to build a competing product or
          service (the open-source version may be used without this restriction under the Apache License 2.0).
        </li>
        <li>
          <strong>Misrepresent synthetic data:</strong> Present synthetic data generated by UNCASE as real patient
          records, financial data, legal transcripts, or other authentic documents without clear disclosure that
          the data is synthetically generated.
        </li>
      </ul>

      <h3>4.3 Rate Limits and Fair Use</h3>
      <p>
        We may impose rate limits on API usage to ensure fair access for all users. Sustained excessive usage that
        degrades service quality may result in temporary throttling or account suspension with prior notice.
      </p>

      <hr />

      <h2>5. Intellectual Property</h2>
      <h3>5.1 Your Content</h3>
      <p>
        You retain all ownership rights to your Seeds, Synthetic Data, LoRA Adapters, Knowledge Base documents,
        and any other content you create or upload through the Service (&quot;Your Content&quot;). You grant us a
        limited, non-exclusive license to process Your Content solely to provide the Service to you.
      </p>

      <h3>5.2 Generated Outputs</h3>
      <p>
        Synthetic conversations, evaluation reports, and LoRA adapters generated through the Service from your
        Seeds are your property. We claim no ownership over outputs generated from your inputs. You are
        responsible for ensuring that your use of generated outputs complies with applicable laws and regulations.
      </p>

      <h3>5.3 Open-Source License</h3>
      <p>
        The UNCASE framework is released under the Apache License 2.0. Your use of the open-source codebase is
        governed by that license. These Terms supplement but do not replace the Apache License 2.0 for the
        open-source components.
      </p>

      <h3>5.4 Our Intellectual Property</h3>
      <p>
        The UNCASE name, logo, brand identity, website design, and any proprietary components of the Hosted
        Service (excluding open-source code) are our intellectual property. You may not use our trademarks without
        prior written permission, except as permitted by trademark law (e.g., nominative fair use).
      </p>

      <h3>5.5 Feedback</h3>
      <p>
        If you provide suggestions, feature requests, or other feedback about the Service, we may use that
        feedback without obligation to you. Contributions to the open-source repository are governed by the
        project&apos;s Contributor License Agreement.
      </p>

      <hr />

      <h2>6. Data Processing and Privacy</h2>
      <h3>6.1 Privacy Policy</h3>
      <p>
        Our collection and use of personal information is described in our{' '}
        <a href='/privacy'>Privacy Policy</a>, which is incorporated into these Terms by reference.
      </p>

      <h3>6.2 Data Processing Role</h3>
      <p>
        When you use the Hosted Service to process data on behalf of your organization, we act as a data
        processor and you act as the data controller. You are responsible for ensuring you have the appropriate
        legal basis for any data you input into the Service.
      </p>

      <h3>6.3 Data Processing Agreement</h3>
      <p>
        Enterprise customers may request a Data Processing Agreement (DPA) that complies with GDPR Article 28
        requirements. Contact us at{' '}
        <a href='mailto:legal@uncase.dev'>legal@uncase.dev</a> to execute a DPA.
      </p>

      <h3>6.4 Zero-PII Guarantee</h3>
      <p>
        The Service is architecturally designed to eliminate PII at the earliest possible stage (Layer 0 — Seed
        Engine). However, the effectiveness of PII detection depends on correct configuration and the nature of
        input data. You acknowledge that:
      </p>
      <ul>
        <li>
          No PII detection system is 100% infallible. You should review seeds and outputs for your specific
          compliance requirements.
        </li>
        <li>
          The Privacy Interceptor&apos;s effectiveness depends on the languages and PII types configured in your
          deployment.
        </li>
        <li>
          You remain ultimately responsible for ensuring compliance with applicable privacy regulations for your
          specific use case and jurisdiction.
        </li>
      </ul>

      <hr />

      <h2>7. Third-Party Services</h2>
      <h3>7.1 LLM Providers</h3>
      <p>
        The LLM Gateway routes requests to third-party providers based on your configuration. Your use of these
        providers is subject to their respective terms of service and privacy policies. We are not responsible
        for the availability, performance, or data handling practices of third-party LLM providers.
      </p>

      <h3>7.2 E2B Sandboxes</h3>
      <p>
        Cloud sandbox features utilize E2B&apos;s MicroVM infrastructure. Sandbox instances are ephemeral and
        isolated. You acknowledge that sandbox availability depends on E2B&apos;s service and is subject to their
        terms.
      </p>

      <h3>7.3 Connectors</h3>
      <p>
        Data ingested through connectors (WhatsApp, webhooks, CRMs) is subject to the terms and privacy policies
        of those source platforms. You are responsible for ensuring you have the right to import data from
        connected sources.
      </p>

      <hr />

      <h2>8. Service Level and Availability</h2>
      <h3>8.1 Availability</h3>
      <p>
        We aim to maintain high availability of the Hosted Service but do not guarantee uninterrupted access. We
        may perform scheduled maintenance with advance notice. Emergency maintenance may occur without notice to
        address security vulnerabilities or critical issues.
      </p>

      <h3>8.2 SLA</h3>
      <p>
        Enterprise customers may negotiate custom Service Level Agreements (SLAs) with defined uptime
        commitments, response times, and remedies. Community tier users receive best-effort support.
      </p>

      <h3>8.3 Self-Hosted Deployments</h3>
      <p>
        If you deploy the Open-Source Version on your own infrastructure, you are solely responsible for its
        availability, security, performance, and compliance. We do not provide SLAs or operational support for
        self-hosted deployments unless covered by a separate support agreement.
      </p>

      <hr />

      <h2>9. Warranty Disclaimer</h2>
      <p>
        THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND,
        EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR
        A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND ACCURACY.
      </p>
      <p>Without limiting the foregoing, we do not warrant that:</p>
      <ul>
        <li>The Service will meet your specific requirements or expectations.</li>
        <li>The Service will be uninterrupted, timely, secure, or error-free.</li>
        <li>The PII detection and elimination will be 100% complete in all cases and languages.</li>
        <li>
          Synthetic data generated by the Service will be suitable for any particular regulatory or compliance
          purpose without additional review by qualified professionals.
        </li>
        <li>
          LoRA adapters produced by the Service will perform to any specific accuracy, quality, or reliability
          standard.
        </li>
        <li>The quality evaluation gates will catch all potential issues in generated data.</li>
      </ul>
      <p>
        YOU ACKNOWLEDGE THAT AI-GENERATED CONTENT MAY CONTAIN ERRORS, HALLUCINATIONS, OR BIASES. YOU ARE
        RESPONSIBLE FOR REVIEWING AND VALIDATING ALL OUTPUTS BEFORE DEPLOYING THEM IN PRODUCTION, ESPECIALLY IN
        REGULATED INDUSTRIES.
      </p>

      <hr />

      <h2>10. Limitation of Liability</h2>
      <p>
        TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL UNCASE, ITS DIRECTORS, EMPLOYEES,
        PARTNERS, AGENTS, SUPPLIERS, OR AFFILIATES BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL,
        CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO:
      </p>
      <ul>
        <li>Loss of profits, revenue, data, or business opportunities.</li>
        <li>Regulatory fines or penalties resulting from your use of the Service.</li>
        <li>Costs of procurement of substitute services.</li>
        <li>Damages arising from unauthorized access to your account or data.</li>
        <li>Damages arising from errors in synthetic data or trained models.</li>
        <li>Damages arising from third-party LLM provider failures or data handling.</li>
      </ul>
      <p>
        OUR TOTAL AGGREGATE LIABILITY FOR ALL CLAIMS ARISING FROM OR RELATED TO THESE TERMS OR THE SERVICE SHALL
        NOT EXCEED THE GREATER OF (A) THE AMOUNT YOU PAID US IN THE 12 MONTHS PRECEDING THE CLAIM, OR (B)
        USD $100.
      </p>

      <hr />

      <h2>11. Indemnification</h2>
      <p>
        You agree to indemnify, defend, and hold harmless UNCASE and its officers, directors, employees, and
        agents from and against any claims, liabilities, damages, losses, costs, and expenses (including
        reasonable attorneys&apos; fees) arising from:
      </p>
      <ul>
        <li>Your use of the Service in violation of these Terms.</li>
        <li>Your violation of any applicable law, regulation, or third-party rights.</li>
        <li>
          Your failure to comply with applicable privacy regulations (GDPR, HIPAA, CCPA, etc.) in connection
          with data you process through the Service.
        </li>
        <li>Claims by third parties arising from your use of synthetic data or trained models in production.</li>
        <li>Your misrepresentation of synthetic data as authentic data.</li>
        <li>
          Any PII that enters the pipeline due to your failure to properly configure or use the PII elimination
          features.
        </li>
      </ul>

      <hr />

      <h2>12. Termination</h2>
      <h3>12.1 By You</h3>
      <p>
        You may terminate your account at any time by contacting us or using the account deletion feature in the
        dashboard. Upon termination, we will delete your data in accordance with our data retention policy and
        Privacy Policy.
      </p>

      <h3>12.2 By Us</h3>
      <p>We may suspend or terminate your access to the Service if:</p>
      <ul>
        <li>You violate these Terms, including the Acceptable Use provisions.</li>
        <li>You fail to pay applicable fees for 30 or more days.</li>
        <li>Your use poses a security risk to the Service or other users.</li>
        <li>We are required to do so by law or regulation.</li>
        <li>We discontinue the Hosted Service (with at least 90 days&apos; notice).</li>
      </ul>

      <h3>12.3 Effect of Termination</h3>
      <p>Upon termination:</p>
      <ul>
        <li>Your right to access the Hosted Service ceases immediately.</li>
        <li>We will provide a data export window of 30 days before permanent deletion.</li>
        <li>
          Your right to use the Open-Source Version under the Apache License 2.0 is unaffected by account
          termination.
        </li>
        <li>Provisions that by their nature should survive termination (including Sections 5, 9, 10, 11, and 14) will survive.</li>
      </ul>

      <hr />

      <h2>13. Dispute Resolution</h2>
      <h3>13.1 Informal Resolution</h3>
      <p>
        Before filing any formal claim, you agree to contact us at{' '}
        <a href='mailto:legal@uncase.dev'>legal@uncase.dev</a> and attempt to resolve the dispute informally for
        at least 30 days.
      </p>

      <h3>13.2 Governing Law</h3>
      <p>
        These Terms shall be governed by and construed in accordance with the laws of the United Mexican States,
        without regard to its conflict of law provisions. For users in the European Union, this choice of law does
        not deprive you of protections afforded by mandatory consumer protection laws of your country of residence.
      </p>

      <h3>13.3 Jurisdiction</h3>
      <p>
        Any disputes arising from these Terms that cannot be resolved informally shall be submitted to the
        competent courts of Mexico City, Mexico. EU consumers may bring proceedings in the courts of their country
        of residence.
      </p>

      <hr />

      <h2>14. General Provisions</h2>
      <h3>14.1 Entire Agreement</h3>
      <p>
        These Terms, together with the Privacy Policy and any applicable DPA or enterprise agreement, constitute
        the entire agreement between you and UNCASE regarding the Service.
      </p>

      <h3>14.2 Severability</h3>
      <p>
        If any provision of these Terms is found to be unenforceable or invalid, that provision shall be limited
        or eliminated to the minimum extent necessary, and the remaining provisions shall remain in full force
        and effect.
      </p>

      <h3>14.3 Waiver</h3>
      <p>
        Our failure to enforce any right or provision of these Terms shall not constitute a waiver of such right
        or provision.
      </p>

      <h3>14.4 Assignment</h3>
      <p>
        You may not assign or transfer these Terms or your rights under them without our prior written consent. We
        may assign these Terms in connection with a merger, acquisition, or sale of all or substantially all of
        our assets.
      </p>

      <h3>14.5 Force Majeure</h3>
      <p>
        We shall not be liable for any failure or delay in performing our obligations under these Terms due to
        events beyond our reasonable control, including but not limited to natural disasters, pandemics,
        government actions, internet outages, third-party service failures, or acts of war or terrorism.
      </p>

      <h3>14.6 Modifications</h3>
      <p>
        We reserve the right to modify these Terms at any time. We will provide at least 30 days&apos; notice of
        material changes by posting the updated Terms on this page and notifying you via email. Your continued use
        of the Service after the effective date of changes constitutes acceptance of the modified Terms. If you do
        not agree with the changes, you must stop using the Service and terminate your account.
      </p>

      <hr />

      <h2>15. Contact Us</h2>
      <p>If you have questions about these Terms, contact us at:</p>
      <ul>
        <li>Email: <a href='mailto:legal@uncase.dev'>legal@uncase.dev</a></li>
        <li>GitHub: <a href='https://github.com/uncase-ai/UNCASE/issues'>github.com/uncase-ai/UNCASE/issues</a></li>
      </ul>
    </article>
  )
}

export default TermsPage

import type { FAQs } from '@/components/blocks/faq/faq'

export const faqItems: FAQs = [
  {
    question: 'What is UNCASE?',
    answer:
      'UNCASE (Unbiased Neutral Convention for Agnostic Seed Engineering) is an open-source framework for generating high-quality synthetic conversational data. It enables LoRA fine-tuning in privacy-sensitive industries like healthcare, finance, and legal — without exposing any real data.'
  },
  {
    question: 'How does UNCASE protect privacy?',
    answer:
      'UNCASE uses a "seed engineering" approach: expert knowledge is abstracted into parametrized structures (seeds) that capture reasoning patterns and domain logic — never actual conversations or identifiable data. The entire pipeline is privacy-by-design with differential privacy (DP-SGD, ε ≤ 8.0), extraction attack testing, and zero-PII validation.'
  },
  {
    question: 'What industries can use UNCASE?',
    answer:
      'UNCASE is domain-agnostic by design. Current namespace definitions cover automotive sales, medical consultation, legal advisory, financial services, industrial manufacturing, and education. The framework can be extended to any industry with specialized conversational knowledge.'
  },
  {
    question: 'Do I need ML expertise to use it?',
    answer:
      'The framework is designed to be approachable. Domain experts become "seed engineers" — they encode their knowledge into structured seeds using guided templates. The pipeline handles parsing, quality validation, synthetic generation, and LoRA training automatically.'
  },
  {
    question: 'What does it cost to train a model with UNCASE?',
    answer:
      'UNCASE leverages LoRA/QLoRA to dramatically reduce costs. Typical adapter training costs $15–$45 USD in compute (2–8 hours on an A100). The resulting adapter is 50–150 MB, compared to 28 GB for a base model. The framework itself is free and open source.'
  },
  {
    question: 'Which regulations does UNCASE comply with?',
    answer:
      'UNCASE is designed to comply simultaneously with GDPR (EU), HIPAA (US), LFPDPPP (Mexico), the AI Act (EU), CCPA (California), and MiFID II (EU). Since synthetic data generated from abstract seeds does not constitute personal data, many regulatory obligations are addressed by design.'
  }
]

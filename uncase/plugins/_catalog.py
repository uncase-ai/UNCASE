"""Built-in plugin catalog for the UNCASE framework.

Defines official plugin manifests that wrap the domain-specific tool packs
shipped with UNCASE.  Each plugin is a curated collection of tools for a
specific industry vertical.

Community plugins can be registered at runtime via the API.
"""

from __future__ import annotations

import contextlib

from uncase.plugins.schemas import PluginManifest

# ---------------------------------------------------------------------------
# Official domain plugin manifests
# ---------------------------------------------------------------------------

BUILTIN_PLUGINS: list[PluginManifest] = []


# -- Automotive Sales -------------------------------------------------------

with contextlib.suppress(ImportError):
    from uncase.tools._builtin.automotive import AUTOMOTIVE_TOOLS

    BUILTIN_PLUGINS.append(
        PluginManifest(
            id="automotive-sales-toolkit",
            name="Automotive Sales Toolkit",
            description=(
                "Complete tool suite for automotive dealership conversations. "
                "Includes inventory search, price quoting, financing options, "
                "model comparison, and CRM integration. Ideal for training "
                "sales agents that handle vehicle inquiries end-to-end."
            ),
            version="1.0.0",
            author="UNCASE Team",
            domains=["automotive.sales"],
            tags=["automotive", "sales", "dealership", "vehicles", "crm", "financing", "inventory"],
            tools=AUTOMOTIVE_TOOLS,
            icon="car",
            license="MIT",
            homepage="https://github.com/uncase-ai/uncase",
            source="official",
            verified=True,
            downloads=1240,
        )
    )


# -- Medical Consultation ---------------------------------------------------

with contextlib.suppress(ImportError):
    from uncase.tools._builtin.medical import MEDICAL_TOOLS

    BUILTIN_PLUGINS.append(
        PluginManifest(
            id="medical-consultation-toolkit",
            name="Medical Consultation Toolkit",
            description=(
                "Healthcare-focused tools for medical consultation workflows. "
                "Covers patient history lookup, medication databases, appointment "
                "scheduling, lab results, and insurance verification. Designed "
                "for HIPAA-aware synthetic data generation in clinical settings."
            ),
            version="1.0.0",
            author="UNCASE Team",
            domains=["medical.consultation"],
            tags=["medical", "healthcare", "ehr", "appointments", "lab", "insurance", "hipaa"],
            tools=MEDICAL_TOOLS,
            icon="heart-pulse",
            license="MIT",
            homepage="https://github.com/uncase-ai/uncase",
            source="official",
            verified=True,
            downloads=980,
        )
    )


# -- Legal Advisory ----------------------------------------------------------

with contextlib.suppress(ImportError):
    from uncase.tools._builtin.legal import LEGAL_TOOLS

    BUILTIN_PLUGINS.append(
        PluginManifest(
            id="legal-advisory-toolkit",
            name="Legal Advisory Toolkit",
            description=(
                "Comprehensive legal practice tools for advisory conversations. "
                "Includes case law search, case file management, deadline tracking, "
                "legislation lookup, and fee calculation. Built for regulated "
                "legal environments with compliance requirements."
            ),
            version="1.0.0",
            author="UNCASE Team",
            domains=["legal.advisory"],
            tags=["legal", "law", "jurisprudence", "compliance", "contracts", "litigation"],
            tools=LEGAL_TOOLS,
            icon="scale",
            license="MIT",
            homepage="https://github.com/uncase-ai/uncase",
            source="official",
            verified=True,
            downloads=720,
        )
    )


# -- Finance Advisory --------------------------------------------------------

with contextlib.suppress(ImportError):
    from uncase.tools._builtin.finance import FINANCE_TOOLS

    BUILTIN_PLUGINS.append(
        PluginManifest(
            id="finance-advisory-toolkit",
            name="Finance Advisory Toolkit",
            description=(
                "Financial services tools for investment advisory conversations. "
                "Covers portfolio management, risk profiling, market data, "
                "regulatory compliance (KYC/AML), and investment simulation. "
                "Suitable for wealth management and banking use cases."
            ),
            version="1.0.0",
            author="UNCASE Team",
            domains=["finance.advisory"],
            tags=["finance", "investment", "portfolio", "risk", "compliance", "kyc", "banking"],
            tools=FINANCE_TOOLS,
            icon="landmark",
            license="MIT",
            homepage="https://github.com/uncase-ai/uncase",
            source="official",
            verified=True,
            downloads=850,
        )
    )


# -- Industrial Support ------------------------------------------------------

with contextlib.suppress(ImportError):
    from uncase.tools._builtin.industrial import INDUSTRIAL_TOOLS

    BUILTIN_PLUGINS.append(
        PluginManifest(
            id="industrial-support-toolkit",
            name="Industrial Support Toolkit",
            description=(
                "Manufacturing and industrial operations tools for support "
                "conversations. Includes equipment diagnostics, parts inventory, "
                "maintenance scheduling, technical documentation search, and "
                "safety incident reporting. ISO 45001 aligned."
            ),
            version="1.0.0",
            author="UNCASE Team",
            domains=["industrial.support"],
            tags=["industrial", "manufacturing", "maintenance", "safety", "equipment", "iso"],
            tools=INDUSTRIAL_TOOLS,
            icon="factory",
            license="MIT",
            homepage="https://github.com/uncase-ai/uncase",
            source="official",
            verified=True,
            downloads=610,
        )
    )


# -- Education Tutoring ------------------------------------------------------

with contextlib.suppress(ImportError):
    from uncase.tools._builtin.education import EDUCATION_TOOLS

    BUILTIN_PLUGINS.append(
        PluginManifest(
            id="education-tutoring-toolkit",
            name="Education Tutoring Toolkit",
            description=(
                "Educational tools for tutoring and e-learning conversations. "
                "Includes curriculum search, student progress tracking, exercise "
                "generation, resource discovery, and session scheduling. "
                "Supports competency-based learning frameworks."
            ),
            version="1.0.0",
            author="UNCASE Team",
            domains=["education.tutoring"],
            tags=["education", "tutoring", "learning", "curriculum", "assessment", "e-learning"],
            tools=EDUCATION_TOOLS,
            icon="graduation-cap",
            license="MIT",
            homepage="https://github.com/uncase-ai/uncase",
            source="official",
            verified=True,
            downloads=540,
        )
    )

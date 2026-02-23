"""Automotive sales domain configuration — pilot domain for UNCASE."""

from __future__ import annotations

from uncase.domains.base import DomainConfig

AUTOMOTIVE_SALES_CONFIG = DomainConfig(
    namespace="automotive.sales",
    display_name={
        "en": "Automotive Sales",
        "es": "Ventas Automotrices",
    },
    description={
        "en": (
            "Conversations in automotive dealerships covering vehicle sales, "
            "financing, trade-ins, test drives, and after-sales service."
        ),
        "es": (
            "Conversaciones en concesionarias automotrices que cubren venta de "
            "vehículos, financiamiento, intercambios, pruebas de manejo y "
            "servicio postventa."
        ),
    },
    typical_roles=[
        "vendedor",
        "cliente",
        "gerente_financiero",
        "asesor_servicio",
    ],
    typical_tools=[
        "crm",
        "cotizador",
        "inventario",
        "comparador_modelos",
    ],
    turnos_min=6,
    turnos_max=30,
    required_parametros=[
        "marca",
        "modelo",
        "anio",
        "tipo_operacion",
        "presupuesto_cliente",
        "forma_pago",
    ],
)

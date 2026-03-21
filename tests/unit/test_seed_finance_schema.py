"""Tests for the SeedFinance extraction schema."""

from __future__ import annotations

from uncase.core.seed_engine.layer0.schemas.base import FieldMeta
from uncase.core.seed_engine.layer0.schemas.finance import (
    ClienteFinanciero,
    ContextoFinanciero,
    EscenarioFinanciero,
    ObjetivoFinanciero,
    ReglasFinancieras,
    REQUIRED_FIELDS_FINANCE,
    SeedFinance,
)


# ===================================================================
# SeedFinance — instantiation
# ===================================================================


class TestSeedFinanceInstantiation:
    """Test SeedFinance can be created with defaults and custom values."""

    def test_default_creation(self) -> None:
        """SeedFinance can be created with all defaults (empty schema)."""
        seed = SeedFinance()
        assert seed.idioma == "es"
        assert isinstance(seed.cliente_financiero, ClienteFinanciero)
        assert isinstance(seed.objetivo_financiero, ObjetivoFinanciero)
        assert isinstance(seed.contexto_financiero, ContextoFinanciero)
        assert isinstance(seed.escenario_financiero, EscenarioFinanciero)
        assert isinstance(seed.reglas_financieras, ReglasFinancieras)

    def test_nested_fields_default_to_none(self) -> None:
        """Optional nested fields default to None."""
        seed = SeedFinance()
        assert seed.cliente_financiero.tipo_cliente is None
        assert seed.cliente_financiero.perfil_riesgo is None
        assert seed.cliente_financiero.nivel_conocimiento_financiero is None
        assert seed.objetivo_financiero.tipo_servicio is None
        assert seed.objetivo_financiero.objetivo_especifico is None
        assert seed.contexto_financiero.canal is None

    def test_boolean_defaults(self) -> None:
        """EscenarioFinanciero boolean fields have correct defaults."""
        seed = SeedFinance()
        assert seed.escenario_financiero.incluir_divulgacion_riesgo is True
        assert seed.escenario_financiero.incluir_comparacion is False
        assert seed.escenario_financiero.incluir_simulacion is False
        assert seed.escenario_financiero.incluir_divulgacion_regulatoria is True
        assert seed.escenario_financiero.incluir_educacion_financiera is False

    def test_custom_values(self) -> None:
        """SeedFinance accepts custom field values."""
        seed = SeedFinance(
            idioma="en",
            cliente_financiero=ClienteFinanciero(
                tipo_cliente="persona_moral",
                perfil_riesgo="agresivo",
                nivel_conocimiento_financiero="avanzado",
            ),
            objetivo_financiero=ObjetivoFinanciero(
                tipo_servicio="inversion",
                objetivo_especifico="Diversificar portafolio en renta variable",
            ),
        )
        assert seed.idioma == "en"
        assert seed.cliente_financiero.tipo_cliente == "persona_moral"
        assert seed.objetivo_financiero.tipo_servicio == "inversion"


# ===================================================================
# SeedFinance — field registry
# ===================================================================


class TestSeedFinanceRegistry:
    """Test the field registry for finance schema."""

    def test_registry_returns_field_meta_list(self) -> None:
        """get_field_registry returns a list of FieldMeta."""
        registry = SeedFinance.get_field_registry()
        assert isinstance(registry, list)
        assert all(isinstance(fm, FieldMeta) for fm in registry)

    def test_registry_has_all_categories(self) -> None:
        """Registry covers all 5 categories."""
        registry = SeedFinance.get_field_registry()
        categories = {fm.category for fm in registry}
        assert "cliente_financiero" in categories
        assert "objetivo_financiero" in categories
        assert "contexto_financiero" in categories
        assert "escenario_financiero" in categories
        assert "reglas_financieras" in categories

    def test_registry_field_count(self) -> None:
        """Registry has a reasonable field count (>= number of leaf fields)."""
        registry = SeedFinance.get_field_registry()
        # ClienteFinanciero: 9, ObjetivoFinanciero: 8, ContextoFinanciero: 7,
        # EscenarioFinanciero: 8, ReglasFinancieras: 9 = 41 + idioma = 42
        assert len(registry) >= 40

    def test_required_fields_exist_in_registry(self) -> None:
        """All required field names from REQUIRED_FIELDS_FINANCE are in the registry."""
        registry = SeedFinance.get_field_registry()
        registry_names = {fm.field_name for fm in registry}
        for required in REQUIRED_FIELDS_FINANCE:
            assert required in registry_names, f"Required field '{required}' not in registry"

    def test_required_field_names_method(self) -> None:
        """required_field_names returns the expected frozenset."""
        assert SeedFinance.required_field_names() == REQUIRED_FIELDS_FINANCE

    def test_required_field_count(self) -> None:
        """REQUIRED_FIELDS_FINANCE has the expected number of required fields."""
        assert len(REQUIRED_FIELDS_FINANCE) == 10

    def test_field_descriptions_not_empty(self) -> None:
        """All fields should have non-empty descriptions."""
        registry = SeedFinance.get_field_registry()
        for fm in registry:
            assert fm.description, f"Field '{fm.field_name}' has empty description"

    def test_required_vs_optional_classification(self) -> None:
        """Required fields from REQUIRED_FIELDS_FINANCE are a subset of all registry fields."""
        registry = SeedFinance.get_field_registry()
        all_names = {fm.field_name for fm in registry}
        required = REQUIRED_FIELDS_FINANCE

        # Required fields should be a proper subset — there should be optional fields too
        assert required.issubset(all_names)
        optional = all_names - required
        assert len(optional) > 0, "There should be optional fields beyond the required ones"


# ===================================================================
# SeedFinance — industry helpers
# ===================================================================


class TestSeedFinanceIndustry:
    """Test industry identification methods."""

    def test_industry_name(self) -> None:
        assert SeedFinance.industry_name() == "finance"

    def test_industry_display_es(self) -> None:
        assert SeedFinance.industry_display("es") == "Asesoría Financiera"

    def test_industry_display_en(self) -> None:
        assert SeedFinance.industry_display("en") == "Financial Advisory"

    def test_industry_display_fallback(self) -> None:
        """Unknown locale falls back to English."""
        assert SeedFinance.industry_display("fr") == "Financial Advisory"


# ===================================================================
# SeedFinance — to_seed_dict()
# ===================================================================


class TestSeedFinanceToSeedDict:
    """Test to_seed_dict produces a valid SeedSchema-compatible dict."""

    def test_empty_schema_produces_valid_dict(self) -> None:
        """Even an empty SeedFinance produces a well-formed seed dict."""
        seed = SeedFinance()
        d = seed.to_seed_dict()
        assert isinstance(d, dict)

        # Required top-level keys
        assert d["version"] == "1.0"
        assert d["dominio"] == "finance.advisory"
        assert d["idioma"] == "es"
        assert isinstance(d["etiquetas"], list)
        assert isinstance(d["roles"], list)
        assert isinstance(d["descripcion_roles"], dict)
        assert isinstance(d["objetivo"], str)
        assert isinstance(d["tono"], str)
        assert isinstance(d["pasos_turnos"], dict)
        assert isinstance(d["parametros_factuales"], dict)
        assert isinstance(d["privacidad"], dict)
        assert isinstance(d["metricas_calidad"], dict)

    def test_seed_dict_has_all_required_keys(self) -> None:
        """Seed dict has every key expected by SeedSchema v1."""
        seed = SeedFinance()
        d = seed.to_seed_dict()
        expected_keys = {
            "version",
            "dominio",
            "idioma",
            "etiquetas",
            "roles",
            "descripcion_roles",
            "objetivo",
            "tono",
            "pasos_turnos",
            "parametros_factuales",
            "privacidad",
            "metricas_calidad",
        }
        assert expected_keys.issubset(d.keys())

    def test_seed_dict_roles(self) -> None:
        """Roles should be client and financial_advisor."""
        seed = SeedFinance()
        d = seed.to_seed_dict()
        assert d["roles"] == ["client", "financial_advisor"]
        assert "client" in d["descripcion_roles"]
        assert "financial_advisor" in d["descripcion_roles"]

    def test_seed_dict_turnos(self) -> None:
        """Pasos_turnos should have expected structure."""
        seed = SeedFinance()
        d = seed.to_seed_dict()
        turnos = d["pasos_turnos"]
        assert turnos["turnos_min"] == 6
        assert turnos["turnos_max"] == 14
        assert isinstance(turnos["flujo_esperado"], list)
        assert len(turnos["flujo_esperado"]) >= 2

    def test_seed_dict_parametros_factuales(self) -> None:
        """Parametros_factuales has contexto, restricciones, herramientas, metadata."""
        seed = SeedFinance()
        d = seed.to_seed_dict()
        pf = d["parametros_factuales"]
        assert "contexto" in pf
        assert "restricciones" in pf
        assert "herramientas" in pf
        assert "metadata" in pf
        assert isinstance(pf["restricciones"], list)
        assert isinstance(pf["herramientas"], list)
        assert isinstance(pf["metadata"], dict)

    def test_seed_dict_privacidad(self) -> None:
        """Privacidad section has required privacy fields."""
        seed = SeedFinance()
        d = seed.to_seed_dict()
        priv = d["privacidad"]
        assert priv["pii_eliminado"] is True
        assert priv["metodo_anonimizacion"] == "presidio_v2"
        assert priv["nivel_confianza"] == 0.99

    def test_seed_dict_metricas_calidad(self) -> None:
        """Quality metrics have the expected thresholds."""
        seed = SeedFinance()
        d = seed.to_seed_dict()
        metrics = d["metricas_calidad"]
        assert metrics["rouge_l_min"] >= 0.20
        assert metrics["fidelidad_min"] >= 0.80
        assert metrics["diversidad_lexica_min"] >= 0.55
        assert metrics["coherencia_dialogica_min"] >= 0.65

    def test_seed_dict_with_populated_fields(self) -> None:
        """A fully populated SeedFinance produces a richer seed dict."""
        seed = SeedFinance(
            cliente_financiero=ClienteFinanciero(
                tipo_cliente="persona_fisica",
                perfil_riesgo="conservador",
                nivel_conocimiento_financiero="basico",
                rango_ingresos="medio",
                productos_actuales=["tarjeta_credito", "ahorro"],
                situacion_laboral="asalariado",
                historial_crediticio="bueno",
                edad_rango="25-35",
                tiene_dependientes=True,
            ),
            objetivo_financiero=ObjetivoFinanciero(
                tipo_servicio="credito",
                objetivo_especifico="Comprar casa en 2 anios",
                monto_rango="1,000,000-5,000,000",
                horizonte_temporal="largo_plazo",
                prioridad="importante",
                tiene_deuda_existente=False,
                productos_existentes=["inversion_cetes"],
                tasa_referencia_esperada="11% anual",
            ),
            contexto_financiero=ContextoFinanciero(
                canal="sucursal",
                tipo_institucion="banco",
                entorno_regulatorio="cnbv",
                relacion_cliente="existente",
                fuente_referencia="recomendacion",
            ),
            escenario_financiero=EscenarioFinanciero(
                tipo_escenario="solicitud_credito",
                complejidad="moderado",
                tono="consultivo",
                incluir_divulgacion_riesgo=True,
                incluir_comparacion=True,
                incluir_simulacion=True,
                incluir_divulgacion_regulatoria=True,
                incluir_educacion_financiera=True,
            ),
            reglas_financieras=ReglasFinancieras(
                marco_cumplimiento="ley_bancos",
                nivel_kyc="normal",
                requiere_firma=True,
                restricciones_producto=["monto_minimo_apertura", "requiere_garantia"],
                divulgacion_comisiones="obligatoria",
                contexto_tasa_interes="TIIE + 6 puntos",
                politica_cancelacion="Cancelacion sin penalizacion en primeros 10 dias",
                prevencion_lavado_dinero="Operacion sujeta a reporte por monto",
                proteccion_datos="Aviso de privacidad integral entregado",
            ),
        )
        d = seed.to_seed_dict()

        # Verify domain-specific values propagated
        assert "solicitud_credito" in d["objetivo"]
        assert "persona_fisica" in d["objetivo"]
        assert "conservador" in d["objetivo"]
        assert d["tono"] == "consultivo"
        assert "ai-extracted" in d["etiquetas"]
        assert "finance" in d["etiquetas"]
        assert "complexity:moderado" in d["etiquetas"]
        assert "service:credito" in d["etiquetas"]
        assert "risk:conservador" in d["etiquetas"]

        # Verify constraints were built
        restricciones = d["parametros_factuales"]["restricciones"]
        assert any("monto_minimo_apertura" in r for r in restricciones)
        assert any("ley_bancos" in r for r in restricciones)
        assert any("comisiones" in r.lower() for r in restricciones)
        assert any("PLD" in r for r in restricciones)
        assert any("Protección de datos" in r or "Proteccion de datos" in r or "proteccion_datos" in r.lower()
                    for r in restricciones)
        assert any("KYC" in r for r in restricciones)

        # Verify context was built
        contexto = d["parametros_factuales"]["contexto"]
        assert "sucursal" in contexto
        assert "banco" in contexto
        assert "cnbv" in contexto
        assert "existente" in contexto
        assert "bueno" in contexto  # historial crediticio

        # Verify tools were added
        herramientas = d["parametros_factuales"]["herramientas"]
        assert "simulador_financiero" in herramientas
        assert "comparador_productos" in herramientas
        assert "verificador_identidad" in herramientas

        # Verify metadata
        metadata = d["parametros_factuales"]["metadata"]
        assert metadata["extracted_by"] == "ai-interview"
        assert metadata["scenario_type"] == "solicitud_credito"
        assert metadata["complexity"] == "moderado"
        assert metadata["client_type"] == "persona_fisica"
        assert metadata["risk_profile"] == "conservador"
        assert metadata["financial_literacy"] == "basico"
        assert metadata["service_type"] == "credito"
        assert metadata["time_horizon"] == "largo_plazo"
        assert metadata["requires_signature"] is True
        assert metadata["risk_disclosure_included"] is True
        assert metadata["regulatory_disclosure_included"] is True

    def test_seed_dict_flow_with_all_steps(self) -> None:
        """When all scenario flags are enabled, flow includes all optional steps."""
        seed = SeedFinance(
            escenario_financiero=EscenarioFinanciero(
                incluir_divulgacion_riesgo=True,
                incluir_comparacion=True,
                incluir_simulacion=True,
                incluir_divulgacion_regulatoria=True,
                incluir_educacion_financiera=True,
            ),
        )
        d = seed.to_seed_dict()
        flujo = d["pasos_turnos"]["flujo_esperado"]
        flujo_text = " ".join(flujo).lower()
        assert "educación financiera" in flujo_text or "educacion financiera" in flujo_text
        assert "comparación" in flujo_text or "comparacion" in flujo_text
        assert "simulación" in flujo_text or "simulacion" in flujo_text
        assert "riesgos" in flujo_text
        assert "regulatoria" in flujo_text

    def test_seed_dict_flow_minimal(self) -> None:
        """When optional scenario flags are disabled, flow has fewer steps."""
        seed = SeedFinance(
            escenario_financiero=EscenarioFinanciero(
                incluir_divulgacion_riesgo=False,
                incluir_comparacion=False,
                incluir_simulacion=False,
                incluir_divulgacion_regulatoria=False,
                incluir_educacion_financiera=False,
            ),
        )
        d = seed.to_seed_dict()
        flujo = d["pasos_turnos"]["flujo_esperado"]
        # Should still have basic steps
        assert any("Saludo" in step for step in flujo)
        assert any("Cierre" in step or "siguientes pasos" in step.lower() for step in flujo)

    def test_seed_dict_no_comparison_adds_restriction(self) -> None:
        """When incluir_comparacion is False, a no-compare restriction is added."""
        seed = SeedFinance(
            escenario_financiero=EscenarioFinanciero(incluir_comparacion=False),
        )
        d = seed.to_seed_dict()
        restricciones = d["parametros_factuales"]["restricciones"]
        assert any("no comparar" in r.lower() for r in restricciones)

    def test_seed_dict_tools_empty_without_flags(self) -> None:
        """Herramientas list is empty when simulation/comparison/kyc not enabled."""
        seed = SeedFinance(
            escenario_financiero=EscenarioFinanciero(
                incluir_simulacion=False,
                incluir_comparacion=False,
            ),
        )
        d = seed.to_seed_dict()
        herramientas = d["parametros_factuales"]["herramientas"]
        # No simulador or comparador
        assert "simulador_financiero" not in herramientas
        assert "comparador_productos" not in herramientas


# ===================================================================
# SeedFinance — to_extraction_dict()
# ===================================================================


class TestSeedFinanceToExtractionDict:
    """Test to_extraction_dict returns correct structure."""

    def test_empty_schema_extraction_dict(self) -> None:
        """Empty schema produces an extraction dict with only non-None values."""
        seed = SeedFinance()
        d = seed.to_extraction_dict()
        assert isinstance(d, dict)
        # idioma is set by default
        assert "idioma" in d
        assert d["idioma"] == "es"

    def test_populated_extraction_dict(self) -> None:
        """Populated fields appear as dot-path keys in extraction dict."""
        seed = SeedFinance(
            cliente_financiero=ClienteFinanciero(tipo_cliente="persona_fisica"),
            objetivo_financiero=ObjetivoFinanciero(tipo_servicio="credito"),
        )
        d = seed.to_extraction_dict()
        assert d["cliente_financiero.tipo_cliente"] == "persona_fisica"
        assert d["objetivo_financiero.tipo_servicio"] == "credito"

    def test_none_fields_excluded(self) -> None:
        """Fields with None values are excluded from extraction dict."""
        seed = SeedFinance()
        d = seed.to_extraction_dict()
        # Optional fields that are None should not appear
        assert "cliente_financiero.tipo_cliente" not in d
        assert "objetivo_financiero.tipo_servicio" not in d
        assert "reglas_financieras.marco_cumplimiento" not in d

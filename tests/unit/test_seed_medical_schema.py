"""Tests for the SeedMedical extraction schema."""

from __future__ import annotations

from uncase.core.seed_engine.layer0.schemas.base import FieldMeta
from uncase.core.seed_engine.layer0.schemas.medical import (
    ContextoClinico,
    EscenarioMedico,
    MotivoConsulta,
    PacientePerfil,
    ReglasClinicas,
    REQUIRED_FIELDS_MEDICAL,
    SeedMedical,
)


# ===================================================================
# SeedMedical — instantiation
# ===================================================================


class TestSeedMedicalInstantiation:
    """Test SeedMedical can be created with defaults and custom values."""

    def test_default_creation(self) -> None:
        """SeedMedical can be created with all defaults (empty schema)."""
        seed = SeedMedical()
        assert seed.idioma == "es"
        assert isinstance(seed.paciente_perfil, PacientePerfil)
        assert isinstance(seed.motivo_consulta, MotivoConsulta)
        assert isinstance(seed.contexto_clinico, ContextoClinico)
        assert isinstance(seed.escenario_medico, EscenarioMedico)
        assert isinstance(seed.reglas_clinicas, ReglasClinicas)

    def test_nested_fields_default_to_none(self) -> None:
        """Optional nested fields default to None."""
        seed = SeedMedical()
        assert seed.paciente_perfil.tipo_paciente is None
        assert seed.paciente_perfil.severidad_condicion is None
        assert seed.paciente_perfil.cobertura_medica is None
        assert seed.motivo_consulta.especialidad is None
        assert seed.motivo_consulta.motivo_principal is None
        assert seed.contexto_clinico.canal is None

    def test_boolean_defaults(self) -> None:
        """EscenarioMedico boolean fields have correct defaults."""
        seed = SeedMedical()
        assert seed.escenario_medico.incluir_exploracion is True
        assert seed.escenario_medico.incluir_razonamiento_diagnostico is True
        assert seed.escenario_medico.incluir_plan_tratamiento is True
        assert seed.escenario_medico.incluir_educacion_paciente is False

    def test_custom_values(self) -> None:
        """SeedMedical accepts custom field values."""
        seed = SeedMedical(
            idioma="en",
            paciente_perfil=PacientePerfil(
                tipo_paciente="pediatrico",
                severidad_condicion="grave",
                cobertura_medica="seguro_privado",
            ),
            motivo_consulta=MotivoConsulta(
                especialidad="cardiologia",
                motivo_principal="dolor en el pecho",
            ),
        )
        assert seed.idioma == "en"
        assert seed.paciente_perfil.tipo_paciente == "pediatrico"
        assert seed.motivo_consulta.especialidad == "cardiologia"


# ===================================================================
# SeedMedical — field registry
# ===================================================================


class TestSeedMedicalRegistry:
    """Test the field registry for medical schema."""

    def test_registry_returns_field_meta_list(self) -> None:
        """get_field_registry returns a list of FieldMeta."""
        registry = SeedMedical.get_field_registry()
        assert isinstance(registry, list)
        assert all(isinstance(fm, FieldMeta) for fm in registry)

    def test_registry_has_all_categories(self) -> None:
        """Registry covers all 5 categories."""
        registry = SeedMedical.get_field_registry()
        categories = {fm.category for fm in registry}
        assert "paciente_perfil" in categories
        assert "motivo_consulta" in categories
        assert "contexto_clinico" in categories
        assert "escenario_medico" in categories
        assert "reglas_clinicas" in categories

    def test_registry_field_count(self) -> None:
        """Registry has a reasonable field count (>= number of leaf fields)."""
        registry = SeedMedical.get_field_registry()
        # 5 categories with multiple fields each + idioma
        # PacientePerfil: 7, MotivoConsulta: 6, ContextoClinico: 5,
        # EscenarioMedico: 7, ReglasClinicas: 6 = 31 + idioma = 32
        assert len(registry) >= 30

    def test_required_fields_exist_in_registry(self) -> None:
        """All required field names from REQUIRED_FIELDS_MEDICAL are in the registry."""
        registry = SeedMedical.get_field_registry()
        registry_names = {fm.field_name for fm in registry}
        for required in REQUIRED_FIELDS_MEDICAL:
            assert required in registry_names, f"Required field '{required}' not in registry"

    def test_required_field_names_method(self) -> None:
        """required_field_names returns the expected frozenset."""
        assert SeedMedical.required_field_names() == REQUIRED_FIELDS_MEDICAL

    def test_required_field_count(self) -> None:
        """REQUIRED_FIELDS_MEDICAL has the expected number of required fields."""
        assert len(REQUIRED_FIELDS_MEDICAL) == 10

    def test_field_descriptions_not_empty(self) -> None:
        """All fields should have non-empty descriptions."""
        registry = SeedMedical.get_field_registry()
        for fm in registry:
            assert fm.description, f"Field '{fm.field_name}' has empty description"

    def test_required_vs_optional_classification(self) -> None:
        """Required fields from REQUIRED_FIELDS_MEDICAL are a subset of all registry fields."""
        registry = SeedMedical.get_field_registry()
        all_names = {fm.field_name for fm in registry}
        required = REQUIRED_FIELDS_MEDICAL

        # Required fields should be a proper subset — there should be optional fields too
        assert required.issubset(all_names)
        optional = all_names - required
        assert len(optional) > 0, "There should be optional fields beyond the required ones"


# ===================================================================
# SeedMedical — industry helpers
# ===================================================================


class TestSeedMedicalIndustry:
    """Test industry identification methods."""

    def test_industry_name(self) -> None:
        assert SeedMedical.industry_name() == "medical"

    def test_industry_display_es(self) -> None:
        assert SeedMedical.industry_display("es") == "Consulta Médica"

    def test_industry_display_en(self) -> None:
        assert SeedMedical.industry_display("en") == "Medical Consultation"

    def test_industry_display_fallback(self) -> None:
        """Unknown locale falls back to English."""
        assert SeedMedical.industry_display("fr") == "Medical Consultation"


# ===================================================================
# SeedMedical — to_seed_dict()
# ===================================================================


class TestSeedMedicalToSeedDict:
    """Test to_seed_dict produces a valid SeedSchema-compatible dict."""

    def test_empty_schema_produces_valid_dict(self) -> None:
        """Even an empty SeedMedical produces a well-formed seed dict."""
        seed = SeedMedical()
        d = seed.to_seed_dict()
        assert isinstance(d, dict)

        # Required top-level keys
        assert d["version"] == "1.0"
        assert d["dominio"] == "medical.consultation"
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
        seed = SeedMedical()
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
        """Roles should be patient and physician."""
        seed = SeedMedical()
        d = seed.to_seed_dict()
        assert d["roles"] == ["patient", "physician"]
        assert "patient" in d["descripcion_roles"]
        assert "physician" in d["descripcion_roles"]

    def test_seed_dict_turnos(self) -> None:
        """Pasos_turnos should have expected structure."""
        seed = SeedMedical()
        d = seed.to_seed_dict()
        turnos = d["pasos_turnos"]
        assert turnos["turnos_min"] == 6
        assert turnos["turnos_max"] == 14
        assert isinstance(turnos["flujo_esperado"], list)
        assert len(turnos["flujo_esperado"]) >= 2  # at least saludo + cierre

    def test_seed_dict_parametros_factuales(self) -> None:
        """Parametros_factuales has contexto, restricciones, herramientas, metadata."""
        seed = SeedMedical()
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
        seed = SeedMedical()
        d = seed.to_seed_dict()
        priv = d["privacidad"]
        assert priv["pii_eliminado"] is True
        assert priv["metodo_anonimizacion"] == "presidio_v2"
        assert priv["nivel_confianza"] == 0.99

    def test_seed_dict_metricas_calidad(self) -> None:
        """Quality metrics have the expected thresholds."""
        seed = SeedMedical()
        d = seed.to_seed_dict()
        metrics = d["metricas_calidad"]
        assert metrics["rouge_l_min"] >= 0.20
        assert metrics["fidelidad_min"] >= 0.80
        assert metrics["diversidad_lexica_min"] >= 0.55
        assert metrics["coherencia_dialogica_min"] >= 0.65

    def test_seed_dict_with_populated_fields(self) -> None:
        """A fully populated SeedMedical produces a richer seed dict."""
        seed = SeedMedical(
            paciente_perfil=PacientePerfil(
                tipo_paciente="geriatrico",
                severidad_condicion="grave",
                cobertura_medica="seguro_social",
                alergias_conocidas=["penicilina", "sulfas"],
                condiciones_cronicas=["diabetes_tipo_2", "hipertension"],
                medicamentos_actuales=["metformina_850mg"],
                estado_emocional="ansioso",
            ),
            motivo_consulta=MotivoConsulta(
                especialidad="cardiologia",
                motivo_principal="dolor en el pecho al hacer esfuerzo",
                duracion_sintomas="cronico",
                tratamientos_previos=["automedicacion_ibuprofeno"],
                es_seguimiento=True,
                fuente_referencia="referido",
            ),
            contexto_clinico=ContextoClinico(
                canal="telemedicina",
                entorno="hospital",
                restriccion_tiempo="urgente",
                requiere_interprete=True,
                acompanante="familiar",
            ),
            escenario_medico=EscenarioMedico(
                tipo_escenario="seguimiento",
                complejidad="complejo",
                tono="empatico",
                incluir_exploracion=True,
                incluir_razonamiento_diagnostico=True,
                incluir_plan_tratamiento=True,
                incluir_educacion_paciente=True,
            ),
            reglas_clinicas=ReglasClinicas(
                nivel_confidencialidad="alto",
                requiere_consentimiento_informado=True,
                marco_regulatorio="hipaa",
                tipo_documentacion="referencia",
                contraindicaciones=["alergia_penicilina"],
                guias_clinicas=["gpc_diabetes_tipo2"],
            ),
        )
        d = seed.to_seed_dict()

        # Verify domain-specific values propagated
        assert "cardiologia" in d["objetivo"]
        assert "seguimiento" in d["objetivo"]
        assert "geriatrico" in d["objetivo"]
        assert d["tono"] == "empatico"
        assert "ai-extracted" in d["etiquetas"]
        assert "medical" in d["etiquetas"]
        assert "complexity:complejo" in d["etiquetas"]
        assert "specialty:cardiologia" in d["etiquetas"]
        assert "severity:grave" in d["etiquetas"]

        # Verify constraints were built
        restricciones = d["parametros_factuales"]["restricciones"]
        assert any("penicilina" in r.lower() for r in restricciones)
        assert any("consentimiento" in r.lower() for r in restricciones)
        assert any("hipaa" in r.lower() for r in restricciones)
        assert any("confidencialidad" in r.lower() for r in restricciones)
        assert any("gpc_diabetes_tipo2" in r for r in restricciones)

        # Verify context was built
        contexto = d["parametros_factuales"]["contexto"]
        assert "telemedicina" in contexto
        assert "hospital" in contexto
        assert "intérprete" in contexto
        assert "seguimiento" in contexto.lower() or "Consulta de seguimiento" in contexto

        # Verify metadata
        metadata = d["parametros_factuales"]["metadata"]
        assert metadata["extracted_by"] == "ai-interview"
        assert metadata["scenario_type"] == "seguimiento"
        assert metadata["complexity"] == "complejo"
        assert metadata["patient_type"] == "geriatrico"
        assert metadata["severity"] == "grave"
        assert metadata["specialty"] == "cardiologia"
        assert metadata["includes_patient_education"] is True

    def test_seed_dict_flow_includes_education_when_enabled(self) -> None:
        """When incluir_educacion_paciente is True, flow includes education step."""
        seed = SeedMedical(
            escenario_medico=EscenarioMedico(incluir_educacion_paciente=True),
        )
        d = seed.to_seed_dict()
        flujo = d["pasos_turnos"]["flujo_esperado"]
        assert any("educación" in step.lower() or "Educación" in step for step in flujo)

    def test_seed_dict_flow_excludes_steps_when_disabled(self) -> None:
        """When scenario flags are False, optional steps are excluded from flow."""
        seed = SeedMedical(
            escenario_medico=EscenarioMedico(
                incluir_exploracion=False,
                incluir_razonamiento_diagnostico=False,
                incluir_plan_tratamiento=False,
                incluir_educacion_paciente=False,
            ),
        )
        d = seed.to_seed_dict()
        flujo = d["pasos_turnos"]["flujo_esperado"]
        # Should still have at least saludo and cierre
        assert any("Saludo" in step for step in flujo)
        assert any("Cierre" in step for step in flujo)
        # Optional steps should not be present
        assert not any("Exploración" in step for step in flujo)
        assert not any("diagnóstico" in step.lower() for step in flujo)
        assert not any("tratamiento" in step.lower() for step in flujo)


# ===================================================================
# SeedMedical — to_extraction_dict()
# ===================================================================


class TestSeedMedicalToExtractionDict:
    """Test to_extraction_dict returns correct structure."""

    def test_empty_schema_extraction_dict(self) -> None:
        """Empty schema produces an extraction dict with only non-None values."""
        seed = SeedMedical()
        d = seed.to_extraction_dict()
        assert isinstance(d, dict)
        # idioma is set by default, and boolean defaults are non-None
        assert "idioma" in d
        assert d["idioma"] == "es"

    def test_populated_extraction_dict(self) -> None:
        """Populated fields appear as dot-path keys in extraction dict."""
        seed = SeedMedical(
            paciente_perfil=PacientePerfil(tipo_paciente="adulto"),
            motivo_consulta=MotivoConsulta(especialidad="general"),
        )
        d = seed.to_extraction_dict()
        assert d["paciente_perfil.tipo_paciente"] == "adulto"
        assert d["motivo_consulta.especialidad"] == "general"

    def test_none_fields_excluded(self) -> None:
        """Fields with None values are excluded from extraction dict."""
        seed = SeedMedical()
        d = seed.to_extraction_dict()
        # Optional fields that are None should not appear
        assert "paciente_perfil.tipo_paciente" not in d
        assert "motivo_consulta.especialidad" not in d
        assert "reglas_clinicas.nivel_confidencialidad" not in d

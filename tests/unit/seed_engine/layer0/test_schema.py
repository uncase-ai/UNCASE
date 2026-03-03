"""Tests for Layer 0 schemas — base and automotive."""

from __future__ import annotations

import pytest

from uncase.core.seed_engine.layer0.schemas.automotriz import (
    REQUIRED_FIELDS_AUTOMOTRIZ,
    ClientePerfil,
    ContextoConversacion,
    Escenario,
    Intencion,
    ReglasNegocio,
    SeedAutomotriz,
)
from uncase.core.seed_engine.layer0.schemas.base import (
    BaseSeedExtraction,
    FieldMeta,
    FieldStatus,
)


# ===================================================================
# FieldMeta / FieldStatus
# ===================================================================


class TestFieldMeta:
    """Test FieldMeta and FieldStatus enums."""

    def test_field_status_values(self) -> None:
        """FieldStatus enum has the expected members."""
        assert FieldStatus.EMPTY.value == "empty"
        assert FieldStatus.EXTRACTED.value == "extracted"
        assert FieldStatus.CONFIRMED.value == "confirmed"
        assert FieldStatus.AMBIGUOUS.value == "ambiguous"

    def test_field_meta_defaults(self) -> None:
        """FieldMeta has sensible defaults."""
        meta = FieldMeta(field_name="test.field")
        assert meta.status == FieldStatus.EMPTY
        assert meta.confidence == 0.0
        assert meta.is_required is False
        assert meta.category == ""

    def test_field_meta_confidence_bounds(self) -> None:
        """Confidence must be between 0 and 1."""
        meta = FieldMeta(field_name="test", confidence=1.0)
        assert meta.confidence == 1.0

        with pytest.raises(Exception):  # noqa: B017
            FieldMeta(field_name="test", confidence=1.5)

        with pytest.raises(Exception):  # noqa: B017
            FieldMeta(field_name="test", confidence=-0.1)


# ===================================================================
# BaseSeedExtraction
# ===================================================================


class TestBaseSeedExtraction:
    """Test BaseSeedExtraction introspection methods."""

    def test_idioma_default(self) -> None:
        """Default idioma is 'es'."""
        schema = BaseSeedExtraction()
        assert schema.idioma == "es"

    def test_get_field_registry_returns_list(self) -> None:
        """get_field_registry returns a list of FieldMeta."""
        registry = BaseSeedExtraction.get_field_registry()
        assert isinstance(registry, list)
        # BaseSeedExtraction itself has only 'idioma'
        assert any(fm.field_name == "idioma" for fm in registry)


# ===================================================================
# SeedAutomotriz — instantiation
# ===================================================================


class TestSeedAutomotrizInstantiation:
    """Test SeedAutomotriz can be created with defaults and custom values."""

    def test_default_creation(self) -> None:
        """SeedAutomotriz can be created with all defaults."""
        seed = SeedAutomotriz()
        assert seed.idioma == "es"
        assert isinstance(seed.cliente_perfil, ClientePerfil)
        assert isinstance(seed.intencion, Intencion)
        assert isinstance(seed.contexto_conversacion, ContextoConversacion)
        assert isinstance(seed.escenario, Escenario)
        assert isinstance(seed.reglas_negocio, ReglasNegocio)

    def test_custom_values(self) -> None:
        """SeedAutomotriz accepts custom field values."""
        seed = SeedAutomotriz(
            idioma="en",
            cliente_perfil=ClientePerfil(tipo_cliente="particular", urgencia="urgente"),
            intencion=Intencion(uso_principal="familia"),
        )
        assert seed.idioma == "en"
        assert seed.cliente_perfil.tipo_cliente == "particular"
        assert seed.intencion.uso_principal == "familia"

    def test_nested_field_defaults_are_none(self) -> None:
        """Optional nested fields default to None."""
        seed = SeedAutomotriz()
        assert seed.cliente_perfil.tipo_cliente is None
        assert seed.cliente_perfil.presupuesto_rango is None
        assert seed.intencion.marca_preferida is None

    def test_boolean_defaults(self) -> None:
        """Escenario boolean fields have correct defaults."""
        seed = SeedAutomotriz()
        assert seed.escenario.incluir_objeciones is True
        assert seed.escenario.incluir_negociacion is False
        assert seed.escenario.incluir_comparacion_competencia is False


# ===================================================================
# SeedAutomotriz — field registry
# ===================================================================


class TestSeedAutomotrizRegistry:
    """Test the field registry for automotive schema."""

    def test_registry_has_all_categories(self) -> None:
        """Registry covers all 5 categories."""
        registry = SeedAutomotriz.get_field_registry()
        categories = {fm.category for fm in registry}
        # Should include the top-level nested model names
        assert "cliente_perfil" in categories
        assert "intencion" in categories
        assert "contexto_conversacion" in categories
        assert "escenario" in categories
        assert "reglas_negocio" in categories

    def test_required_fields_exist(self) -> None:
        """All required field names from REQUIRED_FIELDS_AUTOMOTRIZ are in the registry."""
        registry = SeedAutomotriz.get_field_registry()
        registry_names = {fm.field_name for fm in registry}
        for required in REQUIRED_FIELDS_AUTOMOTRIZ:
            assert required in registry_names, f"Required field '{required}' not in registry"

    def test_required_field_names_method(self) -> None:
        """required_field_names returns the expected frozenset."""
        assert SeedAutomotriz.required_field_names() == REQUIRED_FIELDS_AUTOMOTRIZ

    def test_field_descriptions_not_empty(self) -> None:
        """All fields should have non-empty descriptions."""
        registry = SeedAutomotriz.get_field_registry()
        for fm in registry:
            assert fm.description, f"Field '{fm.field_name}' has empty description"


# ===================================================================
# SeedAutomotriz — get/set field values
# ===================================================================


class TestSeedAutomotrizFieldAccess:
    """Test dot-path field access methods."""

    def test_get_field_value(self) -> None:
        """get_field_value reads nested fields correctly."""
        seed = SeedAutomotriz(
            cliente_perfil=ClientePerfil(tipo_cliente="particular"),
        )
        assert seed.get_field_value("cliente_perfil.tipo_cliente") == "particular"
        assert seed.get_field_value("cliente_perfil.presupuesto_rango") is None

    def test_set_field_value(self) -> None:
        """set_field_value writes nested fields correctly."""
        seed = SeedAutomotriz()
        seed.set_field_value("cliente_perfil.tipo_cliente", "empresa")
        assert seed.cliente_perfil.tipo_cliente == "empresa"

    def test_get_nonexistent_path(self) -> None:
        """get_field_value returns None for invalid paths."""
        seed = SeedAutomotriz()
        assert seed.get_field_value("nonexistent.field") is None

    def test_to_extraction_dict(self) -> None:
        """to_extraction_dict includes set fields and excludes None."""
        seed = SeedAutomotriz(
            cliente_perfil=ClientePerfil(tipo_cliente="flotilla"),
        )
        d = seed.to_extraction_dict()
        assert "cliente_perfil.tipo_cliente" in d
        assert d["cliente_perfil.tipo_cliente"] == "flotilla"

    def test_industry_methods(self) -> None:
        """industry_name and industry_display return expected values."""
        assert SeedAutomotriz.industry_name() == "automotive"
        assert SeedAutomotriz.industry_display("es") == "Ventas Automotrices"
        assert SeedAutomotriz.industry_display("en") == "Automotive Sales"


# ===================================================================
# Category models — individual validation
# ===================================================================


class TestCategoryModels:
    """Test individual category model creation."""

    def test_cliente_perfil_all_fields(self) -> None:
        """ClientePerfil accepts all expected fields."""
        cp = ClientePerfil(
            tipo_cliente="particular",
            nivel_experiencia_compra="primera_vez",
            urgencia="explorando",
            presupuesto_rango="300000-500000",
            tiene_vehiculo_actual=True,
            vehiculo_actual_descripcion="Honda Civic 2020",
            forma_pago_preferida="financiamiento",
        )
        assert cp.tipo_cliente == "particular"
        assert cp.tiene_vehiculo_actual is True

    def test_intencion_list_fields(self) -> None:
        """Intencion handles list fields correctly."""
        intent = Intencion(
            caracteristicas_importantes=["seguridad", "tecnología"],
            factores_decision=["precio", "garantía"],
        )
        assert len(intent.caracteristicas_importantes) == 2
        assert "seguridad" in intent.caracteristicas_importantes

    def test_escenario_booleans(self) -> None:
        """Escenario boolean fields work correctly."""
        esc = Escenario(
            tipo_escenario="venta_directa",
            complejidad="simple",
            tono_esperado="formal",
            incluir_objeciones=False,
            incluir_negociacion=True,
        )
        assert esc.incluir_objeciones is False
        assert esc.incluir_negociacion is True

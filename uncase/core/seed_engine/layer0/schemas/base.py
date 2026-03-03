"""Abstract base schema for agentic seed extraction across any industry.

Provides the foundational models that all industry-specific seed schemas
extend. The key abstractions are:

- ``FieldMeta`` — Per-field tracking metadata (status, confidence, required).
- ``BaseSeedExtraction`` — Root model that any industry schema inherits from,
  providing field introspection and completion-checking helpers used by the
  State Manager.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class FieldStatus(StrEnum):
    """Lifecycle status of a single field in the extraction schema."""

    EMPTY = "empty"
    EXTRACTED = "extracted"
    CONFIRMED = "confirmed"
    AMBIGUOUS = "ambiguous"


class FieldMeta(BaseModel):
    """Metadata tracking the extraction state of a single schema field.

    The State Manager reads and writes ``FieldMeta`` instances to decide
    whether additional questions are needed for each field.
    """

    field_name: str = Field(..., description="Dot-path name of the field (e.g. 'cliente_perfil.tipo_cliente').")
    status: FieldStatus = Field(default=FieldStatus.EMPTY, description="Current extraction status.")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score (0.0-1.0).")
    is_required: bool = Field(default=False, description="Whether this field is required for completion.")
    category: str = Field(default="", description="Logical category the field belongs to.")
    description: str = Field(default="", description="Human-readable description of the field.")


class BaseSeedExtraction(BaseModel):
    """Abstract root model for industry-specific seed extraction schemas.

    Subclasses define the actual domain fields (e.g. ``SeedAutomotriz``).
    This base provides helpers used by the State Manager and Extractor.
    """

    idioma: str = Field(
        default="es",
        description="Language for the interview conversation (ISO 639-1). Asked before starting the interview.",
    )

    # ── Introspection helpers ────────────────────────────────────────

    @classmethod
    def get_field_registry(cls) -> list[FieldMeta]:
        """Build a list of ``FieldMeta`` for every leaf field in the schema.

        Required fields are those without a default of ``None`` and that are
        not ``Optional[...]``.  The method walks nested ``BaseModel`` sub-models
        recursively to produce dot-separated field paths.

        Returns:
            A list of ``FieldMeta`` with ``is_required`` correctly set.
        """
        registry: list[FieldMeta] = []
        cls._walk_fields(cls, prefix="", registry=registry)
        return registry

    @classmethod
    def _walk_fields(
        cls,
        model: type[BaseModel],
        *,
        prefix: str,
        registry: list[FieldMeta],
        category: str = "",
    ) -> None:
        """Recursively walk Pydantic model fields to build field metadata."""
        for name, field_info in model.model_fields.items():
            path = f"{prefix}.{name}" if prefix else name
            annotation = field_info.annotation

            # Resolve Optional[X] -> X
            origin = getattr(annotation, "__origin__", None)
            args = getattr(annotation, "__args__", ())

            is_optional = False
            inner_type = annotation

            # typing.Optional[X] is Union[X, None]
            if origin is type(None):
                is_optional = True
            # Handle Optional as Union[X, NoneType]
            import types
            import typing

            if origin is typing.Union or isinstance(annotation, types.UnionType):
                non_none = [a for a in args if a is not type(None)]
                if len(non_none) < len(args):
                    is_optional = True
                    inner_type = non_none[0] if len(non_none) == 1 else annotation

            is_required = not is_optional and field_info.default is None and field_info.default_factory is None

            # If inner_type is a BaseModel subclass, recurse into it
            try:
                if isinstance(inner_type, type) and issubclass(inner_type, BaseModel) and inner_type is not BaseModel:
                    cat = category if category else name
                    cls._walk_fields(inner_type, prefix=path, registry=registry, category=cat)
                    continue
            except TypeError:
                pass

            description = field_info.description or ""
            registry.append(
                FieldMeta(
                    field_name=path,
                    is_required=is_required,
                    category=category or (prefix.split(".")[0] if prefix else ""),
                    description=description,
                )
            )

    def get_field_value(self, dot_path: str) -> Any:
        """Get a field value by dot-separated path (e.g. 'cliente_perfil.tipo_cliente').

        Returns ``None`` if the path is invalid or the intermediate object is ``None``.
        """
        obj: Any = self
        for part in dot_path.split("."):
            if obj is None:
                return None
            if isinstance(obj, BaseModel):
                obj = getattr(obj, part, None)
            elif isinstance(obj, dict):
                obj = obj.get(part)
            else:
                return None
        return obj

    def set_field_value(self, dot_path: str, value: Any) -> None:
        """Set a field value by dot-separated path.

        Creates intermediate nested models if they are ``None``.
        """
        parts = dot_path.split(".")
        obj: Any = self
        for part in parts[:-1]:
            child = getattr(obj, part, None)
            if child is None:
                # Get the field info to create a default instance
                field_info = obj.model_fields.get(part)
                if field_info and field_info.annotation:
                    annotation = field_info.annotation
                    # Unwrap Optional
                    args = getattr(annotation, "__args__", ())
                    origin = getattr(annotation, "__origin__", None)
                    import types
                    import typing

                    if origin is typing.Union or isinstance(annotation, types.UnionType):
                        non_none = [a for a in args if a is not type(None)]
                        if non_none:
                            annotation = non_none[0]
                    try:
                        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                            child = annotation()
                            setattr(obj, part, child)
                    except TypeError:
                        return
                else:
                    return
            obj = child
        if obj is not None and isinstance(obj, BaseModel):
            setattr(obj, parts[-1], value)

    def to_extraction_dict(self) -> dict[str, Any]:
        """Serialize the schema to a flat dict keyed by dot-path field names.

        Only includes fields that have non-None values. Used by the Extractor
        to compare current state before and after extraction.
        """
        result: dict[str, Any] = {}
        registry = self.get_field_registry()
        for meta in registry:
            val = self.get_field_value(meta.field_name)
            if val is not None:
                result[meta.field_name] = val
        return result

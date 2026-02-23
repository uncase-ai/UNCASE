"""Domain registry and configuration loader."""

from __future__ import annotations

from uncase.domains.automotive.config import AUTOMOTIVE_SALES_CONFIG
from uncase.domains.base import DomainConfig
from uncase.exceptions import DomainNotFoundError


class DomainRegistry:
    """Simple dict-based registry for domain configurations.

    Usage::

        registry = DomainRegistry()
        registry.register(my_config)
        config = registry.get("automotive.sales")
    """

    def __init__(self) -> None:
        self._configs: dict[str, DomainConfig] = {}

    def register(self, config: DomainConfig) -> None:
        """Register a domain configuration by its namespace."""
        self._configs[config.namespace] = config

    def get(self, namespace: str) -> DomainConfig:
        """Return the configuration for *namespace* or raise ``DomainNotFoundError``."""
        try:
            return self._configs[namespace]
        except KeyError:
            raise DomainNotFoundError(f"Domain '{namespace}' is not registered") from None

    def list_namespaces(self) -> list[str]:
        """Return all registered domain namespaces."""
        return list(self._configs.keys())

    def __contains__(self, namespace: str) -> bool:
        return namespace in self._configs

    def __len__(self) -> int:
        return len(self._configs)


# ---------------------------------------------------------------------------
# Module-level singleton -- auto-registers the pilot domain
# ---------------------------------------------------------------------------

_default_registry = DomainRegistry()
_default_registry.register(AUTOMOTIVE_SALES_CONFIG)


def get_domain_config(domain: str) -> DomainConfig:
    """Retrieve a domain configuration from the default registry.

    Parameters
    ----------
    domain:
        Dot-separated domain namespace, e.g. ``"automotive.sales"``.

    Raises
    ------
    DomainNotFoundError
        If the domain is not registered.
    """
    return _default_registry.get(domain)


__all__ = [
    "DomainConfig",
    "DomainRegistry",
    "get_domain_config",
]

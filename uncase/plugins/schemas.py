"""Pydantic models for the UNCASE plugin system.

Defines the data contracts for plugin manifests (available packages)
and installed plugin records.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from uncase.tools.schemas import ToolDefinition


class PluginManifest(BaseModel):
    """Declarative specification of a plugin available in the catalog.

    A plugin is a packaged collection of ``ToolDefinition``s targeting
    one or more domains.  Plugins can be official (built-in) or
    community-contributed.
    """

    id: str = Field(
        ...,
        description="Unique slug identifier (e.g. 'medical-consultation-toolkit').",
    )
    name: str = Field(
        ...,
        description="Human-readable display name.",
    )
    description: str = Field(
        ...,
        description="Rich description of what the plugin provides.",
    )
    version: str = Field(
        default="1.0.0",
        description="Semantic version of the plugin.",
    )
    author: str = Field(
        default="UNCASE Team",
        description="Plugin author or organization.",
    )
    domains: list[str] = Field(
        default_factory=list,
        description="Domain namespaces targeted by this plugin.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Search tags for discovery.",
    )
    tools: list[ToolDefinition] = Field(
        default_factory=list,
        description="Tool definitions included in this plugin.",
    )
    icon: str = Field(
        default="puzzle",
        description="Icon identifier (emoji or lucide icon name).",
    )
    license: str = Field(
        default="MIT",
        description="License under which the plugin is distributed.",
    )
    homepage: str | None = Field(
        default=None,
        description="URL to the plugin's homepage or repository.",
    )
    source: Literal["official", "community"] = Field(
        default="official",
        description="Whether this is an official UNCASE plugin or community-contributed.",
    )
    verified: bool = Field(
        default=False,
        description="Whether the plugin has been verified by the UNCASE team.",
    )
    downloads: int = Field(
        default=0,
        description="Number of times this plugin has been installed.",
    )


class InstalledPlugin(BaseModel):
    """Record of a plugin that has been installed and activated."""

    plugin_id: str = Field(
        ...,
        description="ID of the installed plugin.",
    )
    name: str = Field(
        ...,
        description="Display name of the installed plugin.",
    )
    version: str = Field(
        ...,
        description="Version that was installed.",
    )
    tools_registered: list[str] = Field(
        default_factory=list,
        description="Names of tools that were registered from this plugin.",
    )
    domains: list[str] = Field(
        default_factory=list,
        description="Domains covered by this plugin.",
    )

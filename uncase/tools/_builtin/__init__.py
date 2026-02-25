"""Built-in tool definitions — auto-registered on import.

Only the **automotive.sales** pilot domain auto-registers its tools here.
All other domain tool packs (medical, legal, finance, industrial, education)
are available as plugins and are registered on-demand via the plugin system.
"""

from __future__ import annotations

from uncase.tools._builtin.automotive import AUTOMOTIVE_TOOLS

__all__ = ["AUTOMOTIVE_TOOLS"]

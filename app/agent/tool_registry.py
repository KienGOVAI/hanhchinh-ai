"""
Tool Registry
-------------

Quản lý danh sách Tool của Agent.
"""

from __future__ import annotations

from typing import Dict, List

from app.agent.tools.tool import Tool


class ToolRegistry:
    """
    Registry quản lý toàn bộ Tool.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    # ==========================================
    # Register
    # ==========================================

    def register(
        self,
        tool: Tool,
    ) -> None:

        name = tool.name.strip().lower()

        if name in self._tools:
            raise ValueError(
                f"Tool '{name}' already registered."
            )

        self._tools[name] = tool

    # ==========================================
    # Unregister
    # ==========================================

    def unregister(
        self,
        name: str,
    ) -> None:

        self._tools.pop(
            name.lower(),
            None,
        )

    # ==========================================
    # Get
    # ==========================================

    def get(
        self,
        name: str,
    ) -> Tool:

        key = name.strip().lower()

        if key not in self._tools:
            raise KeyError(
                f"Tool '{name}' not found."
            )

        return self._tools[key]

    # ==========================================
    # Exists
    # ==========================================

    def exists(
        self,
        name: str,
    ) -> bool:

        return (
            name.strip().lower()
            in self._tools
        )

    # ==========================================
    # List
    # ==========================================

    def list_tools(
        self,
    ) -> List[Tool]:

        return list(
            self._tools.values()
        )

    # ==========================================
    # Count
    # ==========================================

    def count(
        self,
    ) -> int:

        return len(
            self._tools
        )

    # ==========================================
    # Clear
    # ==========================================

    def clear(
        self,
    ) -> None:

        self._tools.clear()
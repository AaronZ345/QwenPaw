# -*- coding: utf-8 -*-
"""Shared MCP tool-call timeout parsing."""

from __future__ import annotations

import math
from typing import Any

DEFAULT_MCP_TOOL_CALL_TIMEOUT_SECONDS: float = 60 * 5
MAX_MCP_TOOL_CALL_TIMEOUT_SECONDS: float = 24 * 60 * 60
MCP_TOOL_CALL_TIMEOUT_FIELD = "tool_call_timeout"
LEGACY_MCP_TOOL_CALL_TIMEOUT_FIELD = "timeout"

_MISSING = object()


def get_mcp_tool_call_timeout(endpoint: dict[str, Any]) -> float:
    """Return a validated tool-call timeout from an MCP endpoint."""
    if MCP_TOOL_CALL_TIMEOUT_FIELD in endpoint:
        return parse_mcp_tool_call_timeout(
            endpoint[MCP_TOOL_CALL_TIMEOUT_FIELD],
        )
    if LEGACY_MCP_TOOL_CALL_TIMEOUT_FIELD in endpoint:
        return parse_mcp_tool_call_timeout(
            endpoint[LEGACY_MCP_TOOL_CALL_TIMEOUT_FIELD],
        )
    return DEFAULT_MCP_TOOL_CALL_TIMEOUT_SECONDS


def parse_mcp_tool_call_timeout(value: Any = _MISSING) -> float:
    """Parse a configured MCP tool-call timeout in seconds."""
    if value is _MISSING:
        return DEFAULT_MCP_TOOL_CALL_TIMEOUT_SECONDS
    if value is None:
        raise ValueError("must be provided when present")
    if isinstance(value, str):
        if not value.strip():
            raise ValueError("must be a positive number")
        raw_value = value.strip()
    else:
        raw_value = value
    try:
        timeout = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("must be a positive number") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("must be a positive number")
    if timeout > MAX_MCP_TOOL_CALL_TIMEOUT_SECONDS:
        raise ValueError(
            "must be less than or equal to "
            f"{MAX_MCP_TOOL_CALL_TIMEOUT_SECONDS:g}",
        )
    return timeout

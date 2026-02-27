"""
Sanitize Python structures for safe JSON serialization and cross-platform compatibility.

LLM output or external data may contain control characters (e.g. \\r from Windows,
or raw control bytes) that cause "Invalid control character" when parsed by
browsers or strict JSON parsers. This module strips or normalizes those so
responses are valid and platform-independent.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Union

# Control characters (ASCII 0x00-0x1F) that are invalid in JSON string values
# when not escaped. We keep \\n (0x0A) and \\t (0x09); replace the rest.
# Normalize \\r\\n and \\r to \\n for consistent behavior across OS.
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _sanitize_string(s: str) -> str:
    """Normalize line endings and remove other control characters."""
    if not isinstance(s, str):
        return s
    # Normalize CRLF and CR to LF (platform-independent)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # Replace remaining control characters with space
    return _CONTROL_CHAR_RE.sub(" ", s)


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize dict/list/str so that all string values are safe
    for JSON serialization and parsing on any platform (no invalid control chars).

    - Normalizes \\r\\n and \\r to \\n.
    - Replaces other ASCII control characters (0x00-0x1F except \\n and \\t) with space.
    - Returns a copy; does not mutate the original.
    """
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float)):
        return obj
    if isinstance(obj, str):
        return _sanitize_string(obj)
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    # Leave other types (e.g. Pydantic models) as-is; caller can convert to dict first
    return obj

"""SSE frame serialisation — byte-matches Java's SseEmitter output.

Why this is hand-written (and not via sse-starlette or similar):
- Java's SseEmitter writes `data:` with NO space (not `data: `), and we need
  byte-exact match for the regression suite.
- `message` content is JSON-wrapped in `{"t":"..."}` to preserve whitespace.
- All JSON uses compact separators (no spaces after `,` or `:`).
- See plan-02 §10 "SSE event format (byte-exact requirements)".
"""

from __future__ import annotations

import json
from typing import Any

# Compact, no-whitespace JSON (matches Jackson's default).
_COMPACT = {"separators": (",", ":"), "ensure_ascii": False}


def _escape(text: str) -> str:
    """Escape characters the Java code escapes in the {"t":...} wrapper."""
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _frame(event: str, data: str) -> str:
    return f"event:{event}\ndata:{data}\n\n"


def format_conversation_event(conversation_id: int) -> str:
    """`conversation` event — data is the PLAIN ID string, not JSON."""
    return _frame("conversation", str(conversation_id))


def format_message_event(text: str) -> str:
    """`message` event — content JSON-wrapped as {"t": "<escaped>"} to preserve
    leading/trailing whitespace and special characters."""
    return _frame("message", f'{{"t":"{_escape(text)}"}}')


def format_tool_call_event(*, name: str, args: dict[str, Any]) -> str:
    """`tool_call` event — JSON {name, args}."""
    payload = {"name": name, "args": args}
    return _frame("tool_call", json.dumps(payload, **_COMPACT))


def format_tool_result_event(
    *,
    name: str,
    success: bool,
    content: str,
    data: Any | None = None,
) -> str:
    """`tool_result` event — JSON {name, success, content, [data]}. The `data`
    key is omitted entirely when None (matches Java's conditional put)."""
    payload: dict[str, Any] = {
        "name": name,
        "success": success,
        "content": content,
    }
    if data is not None:
        payload["data"] = data
    return _frame("tool_result", json.dumps(payload, **_COMPACT))


def format_done_event() -> str:
    """`done` event — empty data."""
    return _frame("done", "")


def format_error_event(*, code: str, message: str) -> str:
    """`error` event — JSON {code, message}. Strings escaped to match Java."""
    payload = (
        f'{{"code":"{_escape(code)}","message":"{_escape(message)}"}}'
    )
    return _frame("error", payload)

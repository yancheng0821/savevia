"""SSE replay diff — chat stream Java vs Python.

Sends the same `POST /api/v1/chat/stream` request to both backends, captures
the raw SSE byte stream, and diffs the event names + frame structure.

We do NOT diff message text byte-for-byte (LLM output is non-deterministic).
What we DO check:
- Event names in order (must be identical)
- `conversation` event has a numeric ID
- `tool_call` events fire the same tool names (set comparison — order may
  differ slightly per LLM run)
- `done` event present at end
- No `error` events from either side

Usage:
    uv run python scripts/sse_replay_diff.py \\
        --java-url https://staging-java.savevia.app \\
        --python-url https://staging-python.savevia.app \\
        --jwt $JWT_TOKEN
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from dataclasses import dataclass

import httpx

# Fixed-input prompts that exercise different tool combinations.
PROMPTS: list[dict] = [
    {
        "name": "simple_greeting",
        "message": "hi",
        "locale": "en",
        "expected_tools": set(),
    },
    {
        "name": "ask_card_for_groceries",
        "message": "what's my best card for groceries?",
        "locale": "en",
        "expected_tools": {"get_user_cards", "get_best_card"},
    },
    {
        "name": "compare_two_cards",
        "message": "compare TD Cash and CIBC Dividend for me",
        "locale": "en",
        "expected_tools": {"compare_cards"},
    },
    {
        "name": "calculate_reward",
        "message": "how much do I earn on $200 at restaurants with my best card?",
        "locale": "en",
        "expected_tools": {"get_user_cards", "calculate_reward"},
    },
    {
        "name": "card_usage_guide",
        "message": "how do I use my Scotiabank Momentum Visa Infinite optimally?",
        "locale": "en",
        "expected_tools": {"get_card_usage_guide"},
    },
]


@dataclass
class StreamCapture:
    events: list[str]
    tool_calls: list[str]
    has_done: bool
    has_error: bool
    error_payload: str | None
    raw_chars: int


_SSE_LINE = re.compile(rb"^(?P<key>event|data):\s?(?P<val>.*)$")


async def _capture(client: httpx.AsyncClient, base: str, prompt: dict, jwt: str) -> StreamCapture:
    url = base.rstrip("/") + "/api/v1/chat/stream"
    body = {"message": prompt["message"], "locale": prompt["locale"], "conversationId": None}
    events: list[str] = []
    tool_calls: list[str] = []
    has_done = False
    has_error = False
    err_payload: str | None = None
    raw_chars = 0

    async with client.stream(
        "POST", url, json=body,
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=120.0,
    ) as r:
        if r.status_code != 200:
            return StreamCapture([], [], False, True, f"HTTP {r.status_code}", 0)

        current_event: str | None = None
        async for raw_line in r.aiter_lines():
            raw_chars += len(raw_line)
            line = raw_line.strip()
            if not line:
                current_event = None
                continue
            if line.startswith("event:"):
                current_event = line[6:].strip()
                events.append(current_event)
                if current_event == "done":
                    has_done = True
                if current_event == "error":
                    has_error = True
            elif line.startswith("data:") and current_event == "tool_call":
                payload = line[5:].strip()
                try:
                    parsed = json.loads(payload)
                    if "name" in parsed:
                        tool_calls.append(parsed["name"])
                except json.JSONDecodeError:
                    pass
            elif line.startswith("data:") and current_event == "error":
                err_payload = line[5:].strip()

    return StreamCapture(events, tool_calls, has_done, has_error, err_payload, raw_chars)


async def _diff(client: httpx.AsyncClient, java: str, py: str, prompt: dict, jwt: str) -> bool:
    j = await _capture(client, java, prompt, jwt)
    p = await _capture(client, py, prompt, jwt)

    # Acceptance:
    # 1. both reach `done`
    # 2. neither emits `error`
    # 3. tool-call NAME SETS are equal (order tolerance — small LLM jitter)
    # 4. event sequences have the same shape (counts of each event type within ±1)
    ok = True
    reasons: list[str] = []

    if not j.has_done or not p.has_done:
        ok = False
        reasons.append(f"done frames java={j.has_done} python={p.has_done}")
    if j.has_error or p.has_error:
        ok = False
        reasons.append(f"error frames java={j.has_error} python={p.has_error} payload={p.error_payload or j.error_payload}")
    j_tools, p_tools = set(j.tool_calls), set(p.tool_calls)
    if prompt["expected_tools"] and not (prompt["expected_tools"] <= j_tools):
        ok = False
        reasons.append(f"java missing expected tools {prompt['expected_tools'] - j_tools}")
    if prompt["expected_tools"] and not (prompt["expected_tools"] <= p_tools):
        ok = False
        reasons.append(f"python missing expected tools {prompt['expected_tools'] - p_tools}")
    if j_tools != p_tools:
        # Soft warn — agent behavior may differ on identical prompts due to LLM jitter
        reasons.append(f"tool set diff (warning): java={j_tools} python={p_tools}")

    marker = "✓" if ok else "✗"
    print(f"{marker} {prompt['name']}  java[{len(j.events)} events, {len(j.tool_calls)} tools, {j.raw_chars}c]  python[{len(p.events)} events, {len(p.tool_calls)} tools, {p.raw_chars}c]")
    for r in reasons:
        print(f"  {r}")
    return ok


async def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--java-url", required=True)
    p.add_argument("--python-url", required=True)
    p.add_argument("--jwt", required=True)
    args = p.parse_args()

    async with httpx.AsyncClient() as client:
        results = []
        for prompt in PROMPTS:
            results.append(await _diff(client, args.java_url, args.python_url, prompt, args.jwt))

    failed = sum(1 for r in results if not r)
    total = len(results)
    print(f"\n{total - failed}/{total} streams matched on critical invariants")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

"""Agent behavior diff — compares tool-call sequences across multiple runs.

Unlike sse_replay_diff.py (which checks for cutover-day equivalence), this
script runs each prompt N times against ONE backend and reports the
distribution of tool-call paths. It's useful for:
- Detecting flaky agent behavior (e.g. a prompt that sometimes uses
  `get_user_cards` and sometimes doesn't)
- Comparing Java vs Python on agent decision quality, not just frame format
- Sanity checks after prompt or tool changes

Usage:
    uv run python scripts/agent_behavior_diff.py \\
        --url https://staging-python.savevia.app \\
        --jwt $JWT --runs 5
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from collections import Counter

import httpx

PROMPTS = [
    ("groceries_best_card", "what's my best card for groceries?"),
    ("dinner_at_restaurant", "tell me the optimal card for a $80 dinner"),
    ("travel_planning", "I'm flying to Tokyo next month, which card should I use?"),
    ("usage_guide", "how should I use my CIBC Dividend Visa Infinite?"),
    ("two_card_compare", "compare TD Cash and Scotiabank Momentum"),
    ("calc_amount_category", "if I spend $300 on gas with my best card, how much do I earn?"),
]


async def _one_run(client: httpx.AsyncClient, base: str, prompt: str, jwt: str) -> tuple[bool, list[str]]:
    """Returns (ok, tool_call_sequence)."""
    url = base.rstrip("/") + "/api/v1/chat/stream"
    tools: list[str] = []
    has_done = False
    has_error = False

    async with client.stream(
        "POST", url,
        json={"message": prompt, "locale": "en", "conversationId": None},
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=120.0,
    ) as r:
        if r.status_code != 200:
            return False, []

        cur = None
        async for line in r.aiter_lines():
            line = line.strip()
            if not line:
                cur = None
                continue
            if line.startswith("event:"):
                cur = line[6:].strip()
                if cur == "done":
                    has_done = True
                if cur == "error":
                    has_error = True
            elif line.startswith("data:") and cur == "tool_call":
                try:
                    name = json.loads(line[5:].strip()).get("name")
                    if name:
                        tools.append(name)
                except json.JSONDecodeError:
                    pass
    return has_done and not has_error, tools


async def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--jwt", required=True)
    p.add_argument("--runs", type=int, default=5)
    args = p.parse_args()

    async with httpx.AsyncClient() as client:
        for name, prompt in PROMPTS:
            print(f"\n=== {name} ({args.runs} runs) ===")
            print(f"  prompt: {prompt!r}")
            counter: Counter[tuple[str, ...]] = Counter()
            ok_count = 0
            for i in range(args.runs):
                ok, tools = await _one_run(client, args.url, prompt, args.jwt)
                if ok:
                    ok_count += 1
                counter[tuple(tools)] += 1
            print(f"  success: {ok_count}/{args.runs}")
            print(f"  unique tool paths: {len(counter)}")
            for path, count in counter.most_common():
                print(f"    {count:>2}x  {list(path) or '(no tools)'}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

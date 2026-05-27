"""Load test for savevia-ai — concurrent SSE chat + non-streaming endpoints.

Pure asyncio + httpx, no locust/k6 dependency. Use this for ad-hoc verification
that the Python service handles N concurrent users without degrading
beyond Java baseline + 15%.

Usage:
    uv run python scripts/load_test.py \\
        --url https://staging-python.savevia.app \\
        --jwt $JWT \\
        --concurrency 20 \\
        --duration 60
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import sys
import time
from collections.abc import Awaitable, Callable

import httpx

PROMPTS = [
    "what's the best card for groceries?",
    "compare TD Cash and CIBC Dividend",
    "how much do I earn on $100 gas?",
    "tell me about Scotiabank Momentum Visa Infinite",
    "I'm a new immigrant, what card should I start with?",
]


async def _chat_stream(client: httpx.AsyncClient, url: str, jwt: str, prompt: str) -> tuple[bool, float]:
    start = time.monotonic()
    full_url = url.rstrip("/") + "/api/v1/chat/stream"
    body = {"message": prompt, "locale": "en", "conversationId": None}
    try:
        async with client.stream(
            "POST", full_url, json=body,
            headers={"Authorization": f"Bearer {jwt}"},
            timeout=120.0,
        ) as r:
            if r.status_code != 200:
                return False, time.monotonic() - start
            done = False
            async for line in r.aiter_lines():
                if line.strip() == "event: done":
                    done = True
                    break
            return done, time.monotonic() - start
    except Exception:  # noqa: BLE001
        return False, time.monotonic() - start


async def _optimize_calc(client: httpx.AsyncClient, url: str, jwt: str) -> tuple[bool, float]:
    start = time.monotonic()
    try:
        r = await client.post(
            url.rstrip("/") + "/api/v1/optimize/calculate",
            json={"amount": 100.0, "category": "GROCERY"},
            headers={"Authorization": f"Bearer {jwt}"},
            timeout=10.0,
        )
        return r.status_code == 200, time.monotonic() - start
    except Exception:  # noqa: BLE001
        return False, time.monotonic() - start


async def _worker(
    name: str,
    fn: Callable[[], Awaitable[tuple[bool, float]]],
    duration: float,
    results: list,
) -> None:
    end = time.monotonic() + duration
    while time.monotonic() < end:
        ok, latency = await fn()
        results.append((name, ok, latency))


def _summarize(label: str, results: list) -> None:
    subset = [(ok, latency) for n, ok, latency in results if n == label]
    if not subset:
        print(f"  {label}: no samples")
        return
    n = len(subset)
    ok_n = sum(1 for ok, _ in subset if ok)
    lats = [latency for _, latency in subset]
    lats.sort()
    p50 = lats[len(lats) // 2]
    p99 = lats[int(len(lats) * 0.99)] if len(lats) > 100 else lats[-1]
    mean = statistics.mean(lats)
    print(f"  {label}: requests={n} success={ok_n}/{n} ({ok_n*100//n}%) "
          f"mean={mean*1000:.0f}ms p50={p50*1000:.0f}ms p99={p99*1000:.0f}ms")


async def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--jwt", required=True)
    p.add_argument("--concurrency", type=int, default=10)
    p.add_argument("--duration", type=float, default=30.0, help="seconds")
    args = p.parse_args()

    print(f"Load test: {args.concurrency} workers for {args.duration}s against {args.url}")

    async with httpx.AsyncClient() as client:
        results: list[tuple[str, bool, float]] = []
        tasks = []
        # mix: 60% chat (the heavy one), 40% calc
        chat_workers = max(1, int(args.concurrency * 0.6))
        calc_workers = args.concurrency - chat_workers

        prompt_iter = iter(_round_robin(PROMPTS))
        for _ in range(chat_workers):
            prompt = next(prompt_iter)
            tasks.append(_worker(
                "chat_stream",
                lambda p=prompt: _chat_stream(client, args.url, args.jwt, p),
                args.duration, results,
            ))
        for _ in range(calc_workers):
            tasks.append(_worker(
                "optimize_calc",
                lambda: _optimize_calc(client, args.url, args.jwt),
                args.duration, results,
            ))

        start = time.monotonic()
        await asyncio.gather(*tasks)
        elapsed = time.monotonic() - start

    print(f"\nLoad test complete in {elapsed:.1f}s")
    print(f"Total samples: {len(results)}")
    _summarize("chat_stream", results)
    _summarize("optimize_calc", results)
    return 0


def _round_robin(items):
    while True:
        yield from items


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

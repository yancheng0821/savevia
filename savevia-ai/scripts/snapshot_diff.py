"""API snapshot diff harness — Java vs Python.

Sends the same authenticated request to both backends and diffs the JSON.
Use this before cutover to verify the Python ports return identical (or
near-identical) responses for non-streaming endpoints.

Usage:
    uv run python scripts/snapshot_diff.py \\
        --java-url https://staging-java.savevia.app \\
        --python-url https://staging-python.savevia.app \\
        --jwt $JWT_TOKEN

Exit code 0 if all snapshots match (modulo timestamps / IDs).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass

import httpx

# Fields that are expected to differ (timestamps, random IDs) — strip before diffing.
IGNORE_PATHS = {
    "timestamp",
    "createdAt",
    "updatedAt",
    "data.timestamp",
    "data.createdAt",
    "data.updatedAt",
}


@dataclass
class Case:
    name: str
    method: str
    path: str
    body: dict | None = None
    params: dict | None = None


CASES: list[Case] = [
    # /optimize/calculate
    Case(
        name="optimize_calculate_grocery_100",
        method="POST",
        path="/api/v1/optimize/calculate",
        body={"amount": 100.0, "category": "GROCERY"},
    ),
    Case(
        name="optimize_calculate_gas_50",
        method="POST",
        path="/api/v1/optimize/calculate",
        body={"amount": 50.0, "category": "GAS"},
    ),
    # /optimize/transactions
    Case(
        name="transactions_recent",
        method="GET",
        path="/api/v1/optimize/transactions",
        params={"limit": 10},
    ),
    Case(
        name="transactions_summary",
        method="GET",
        path="/api/v1/optimize/transactions/summary",
    ),
    # /optimize/share + /optimize/user-result (saved-results)
    Case(
        name="user_result_list",
        method="GET",
        path="/api/v1/optimize/user-result",
    ),
    # /chat/suggestions
    Case(
        name="chat_suggestions_en",
        method="GET",
        path="/api/v1/chat/suggestions",
        params={"locale": "en"},
    ),
    Case(
        name="chat_suggestions_zh",
        method="GET",
        path="/api/v1/chat/suggestions",
        params={"locale": "zh"},
    ),
]


def _strip_ignored(obj, prefix: str = ""):
    """Recursively strip IGNORE_PATHS from a dict/list snapshot."""
    if isinstance(obj, dict):
        return {
            k: _strip_ignored(v, f"{prefix}{k}.")
            for k, v in obj.items()
            if (prefix + k) not in IGNORE_PATHS and k not in IGNORE_PATHS
        }
    if isinstance(obj, list):
        return [_strip_ignored(v, prefix) for v in obj]
    return obj


async def _request(client: httpx.AsyncClient, base: str, case: Case, jwt: str) -> tuple[int, dict]:
    url = base.rstrip("/") + case.path
    headers = {"Authorization": f"Bearer {jwt}"}
    try:
        r = await client.request(
            case.method, url, json=case.body, params=case.params,
            headers=headers, timeout=15.0,
        )
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        return r.status_code, body
    except Exception as e:  # noqa: BLE001
        return -1, {"_error": str(e)}


async def _diff_case(client: httpx.AsyncClient, java: str, py: str, case: Case, jwt: str) -> bool:
    j_status, j_body = await _request(client, java, case, jwt)
    p_status, p_body = await _request(client, py, case, jwt)

    j_clean = _strip_ignored(j_body)
    p_clean = _strip_ignored(p_body)

    matched = j_status == p_status and j_clean == p_clean
    marker = "✓" if matched else "✗"
    print(f"{marker} {case.name}  java={j_status} python={p_status}")

    if not matched:
        print(f"  Java   : {json.dumps(j_clean, ensure_ascii=False)[:200]}")
        print(f"  Python : {json.dumps(p_clean, ensure_ascii=False)[:200]}")
        # show first divergent key path
        _show_first_diff(j_clean, p_clean, prefix="")
    return matched


def _show_first_diff(a, b, prefix: str = "") -> None:
    if type(a) is not type(b):
        print(f"  diff at {prefix or '/'}: type {type(a).__name__} vs {type(b).__name__}")
        return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                print(f"  diff at {prefix}{k}: missing on Java")
                return
            if k not in b:
                print(f"  diff at {prefix}{k}: missing on Python")
                return
            if a[k] != b[k]:
                _show_first_diff(a[k], b[k], f"{prefix}{k}.")
                return
    elif isinstance(a, list):
        if len(a) != len(b):
            print(f"  diff at {prefix}: list length {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                _show_first_diff(x, y, f"{prefix}[{i}].")
                return
    else:
        print(f"  diff at {prefix or '/'}: {a!r} vs {b!r}")


async def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--java-url", required=True, help="e.g. https://staging-java.savevia.app")
    p.add_argument("--python-url", required=True, help="e.g. https://staging-python.savevia.app")
    p.add_argument("--jwt", required=True, help="A valid user JWT for both backends")
    args = p.parse_args()

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[
            _diff_case(client, args.java_url, args.python_url, c, args.jwt)
            for c in CASES
        ])

    failed = sum(1 for r in results if not r)
    total = len(results)
    print(f"\n{total - failed}/{total} snapshots matched")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

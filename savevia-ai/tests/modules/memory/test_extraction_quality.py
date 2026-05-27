"""Quality regression suite — hits the real OpenAI API. Skipped in default
runs. Enable with `pytest -m live`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "sample_conversations.json"
CASES = json.loads(FIXTURES.read_text())

MIN_MATCH_RATIO = 0.80  # 80% of expected fields must match


def _flatten(d: dict, prefix: str = "") -> dict:
    """{'identity': {'user_type': 'x'}} -> {'identity.user_type': 'x'}."""
    out: dict = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, prefix=f"{key}."))
        else:
            out[key] = v
    return out


def _match_ratio(expected: dict, actual: dict) -> float:
    flat_e = _flatten(expected)
    flat_a = _flatten(actual)
    if not flat_e:
        return 1.0
    matches = sum(1 for k, v in flat_e.items() if flat_a.get(k) == v)
    return matches / len(flat_e)


@pytest.mark.live
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY")
    or os.environ["OPENAI_API_KEY"] in ("sk-test", ""),
    reason="needs a real OPENAI_API_KEY",
)
@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
async def test_extraction_meets_quality_threshold(case):
    from app.modules.memory.extraction_chain import build_extraction_chain
    from app.modules.memory.extraction_service import _build_conversation_text

    chain = build_extraction_chain()
    conversation = _build_conversation_text(case["messages"])
    result = await chain.ainvoke({"conversation": conversation})

    actual = result.model_dump(exclude_none=True)
    ratio = _match_ratio(case["expected"], actual)

    assert ratio >= MIN_MATCH_RATIO, (
        f"Quality below threshold for {case['id']}: {ratio:.0%} matches\n"
        f"Expected: {case['expected']}\n"
        f"Actual: {actual}\n"
    )

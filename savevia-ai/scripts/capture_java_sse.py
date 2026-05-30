"""Capture + build SSE regression fixtures from a live Java optimizer.

LIVE CAPTURE (one-time; needs the Java stack up — eureka + card + user +
optimizer on :8083, plus a user id that owns some cards, e.g. 4):

    mkdir -p captures
    curl -sN -X POST http://localhost:8083/api/v1/chat/stream \\
      -H 'Content-Type: application/json' -H 'X-User-Id: 4' \\
      -d '{"message":"Hi there!","locale":"en"}' > captures/01_greeting.txt
    # ... repeat per case id in CASE_META ...

Then build the fixtures (writes cases.json + <id>.expected.txt):

    python scripts/capture_java_sse.py captures tests/fixtures/sse_replay

SCOPE — what is byte-comparable across Java(Jackson) and Python(json):
- conversation / message ({"t":...}) / done / error frames: YES (byte-for-byte).
- tool_result DATA: NO. Java serialises BigDecimal as e.g. ``15.0000000`` /
  ``0.05000``; Python's json.dumps emits ``15.0`` / ``0.05``. Tool-frame
  *structure* is covered by tests/modules/chat/test_sse.py instead. Tool-using
  prompts are therefore intentionally excluded from the byte-match fixtures.

NORMALIZATION — empty-content message frames (``data:{"t":""}``) are dropped
from both the stub script and the expected bytes. Java forwards OpenAI's
leading empty-content chunk; Python intentionally suppresses empty deltas
(ChatService ``if text:``). The frame is a frontend no-op (appends ""), so the
fixture asserts parity on the meaningful frames.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# id -> request metadata used to replay each capture through Python.
CASE_META = {
    "01_greeting": {"user_id": 4, "message": "Hi there!", "locale": "en"},
    "07_chinese": {"user_id": 4, "message": "你好", "locale": "zh"},
    "09_invalid_input": {"user_id": 4, "message": "", "locale": "en"},
}


def parse_frames(raw: str) -> list[tuple[str, str]]:
    frames: list[tuple[str, str]] = []
    for block in raw.strip("\n").split("\n\n"):
        if not block.strip():
            continue
        lines = block.split("\n")
        event = lines[0].removeprefix("event:")
        data = lines[1].removeprefix("data:") if len(lines) > 1 else ""
        frames.append((event, data))
    return frames


def build_case(case_id: str, raw: str) -> tuple[dict, str]:
    """Return (case dict, normalized expected SSE text).

    Empty-content message frames are dropped from both the stub script and the
    expected bytes (see NORMALIZATION note above). Kept frames retain Java's
    exact ``data:`` bytes.
    """
    meta = CASE_META[case_id]
    conv_id: int | None = None
    stub: list[dict] = []
    kept_frames: list[tuple[str, str]] = []
    for event, data in parse_frames(raw):
        if event == "conversation":
            conv_id = int(data)
            kept_frames.append((event, data))
        elif event == "message":
            delta = json.loads(data)["t"]
            if delta == "":
                continue  # frontend no-op; Python suppresses empty deltas
            stub.append({"type": "text", "text": delta})
            kept_frames.append((event, data))
        else:  # done / error — terminal, emitted by ChatService not the stub
            kept_frames.append((event, data))

    case: dict = {"id": case_id, **meta, "stub_llm": stub, "user_cards": []}
    if conv_id is not None:
        case["conversation_id"] = conv_id

    expected = "".join(f"event:{ev}\ndata:{dt}\n\n" for ev, dt in kept_frames)
    return case, expected


def main() -> None:
    captures_dir = Path(sys.argv[1])
    fixtures_dir = Path(sys.argv[2])
    cases = []
    for case_id in CASE_META:
        raw = (captures_dir / f"{case_id}.txt").read_text(encoding="utf-8")
        case, expected = build_case(case_id, raw)
        cases.append(case)
        (fixtures_dir / f"{case_id}.expected.txt").write_text(expected, encoding="utf-8")
    (fixtures_dir / "cases.json").write_text(
        json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"built {len(cases)} cases -> {fixtures_dir}/cases.json")


if __name__ == "__main__":
    main()

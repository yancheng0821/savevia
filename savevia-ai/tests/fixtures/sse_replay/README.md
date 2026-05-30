# SSE replay fixtures

Byte-for-byte regression suite for `POST /api/v1/chat/stream`. Captures the
raw SSE body Java emits for canonical prompts, then replays each through
Python (with a stubbed LLM that mimics the original turn) and asserts equality.

The LLM is intentionally faked here — the goal is **format parity**, not
response parity. (Response-quality parity is its own QA pass after cutover.)

## How to record a fixture from Java

1. Bring up the Java stack (eureka + card + user + optimizer on `:8083`). The
   optimizer jar needs Java 17 (`JAVA_HOME=$(/usr/libexec/java_home -v 17)`).
2. Pick a test user that owns some cards (e.g. `4`); pass it as `X-User-Id`
   (the gateway normally injects this from the JWT).
3. Capture each case into `captures/<case-id>.txt`:

   ```bash
   curl -sN -X POST http://localhost:8083/api/v1/chat/stream \
       -H 'Content-Type: application/json' \
       -H 'X-User-Id: 4' \
       -d '{"message":"<prompt>","locale":"<locale>"}' \
       > captures/<case-id>.txt
   ```

4. Build the fixtures (parses the raw Java bytes into `cases.json` +
   `<id>.expected.txt`, deriving the stub LLM script):

   ```bash
   python scripts/capture_java_sse.py captures tests/fixtures/sse_replay
   ```

## Cases

**Recorded (byte-for-byte vs live Java, 2026-05-30):**

| id | covers |
|----|---|
| `01_greeting` | bare text response, no tools |
| `07_chinese` | non-English language directive (unicode emitted unescaped) |
| `09_invalid_input` | `INVALID_INPUT` error frame, no conversation |

These exercise the highest-risk format surface: the `conversation` plain-id
frame, `message` `{"t":...}` compact wrapper (incl. unescaped CJK), the empty
`done` frame, and the `error` frame.

**Not recorded as byte-match fixtures (documented reasons):**

| id | reason |
|----|---|
| `02`–`06`, `10` (tool paths) | `tool_result` DATA isn't byte-comparable: Java Jackson serialises `BigDecimal` as `15.0000000` / `0.05000`; Python `json.dumps` emits `15.0` / `0.05`. Tool-frame **structure** is asserted in `tests/modules/chat/test_sse.py`. |
| `08_quota_exceeded` | the Java path requires a real over-quota user; the error-frame format is already covered byte-for-byte by `09_invalid_input` + `test_sse.py`. |

The capture tool drops empty-content `message` frames (`{"t":""}`) — Java
forwards OpenAI's leading empty chunk, Python suppresses empty deltas
(`ChatService` `if text:`); the frame is a frontend no-op. See
`scripts/capture_java_sse.py` for the full normalization note.

## Stub LLM script

For each fixture we record both:
- the **Java SSE bytes** (`<id>.expected.txt`)
- the **stub LLM script** in `cases.json` describing the text chunks and
  tool calls the agent would emit on that turn

The Python regression test feeds the stub script through the production
`ChatService` + SSE serializer and diffs the result against `expected.txt`.

## Status

- `cases.json` holds 3 byte-for-byte fixtures recorded from live Java (2026-05-30).
- `tests/modules/chat/test_sse_regression.py` asserts each case (no longer skipped).
- To add more, capture into `captures/` and re-run `scripts/capture_java_sse.py`.

# SSE replay fixtures

Byte-for-byte regression suite for `POST /api/v1/chat/stream`. Captures the
raw SSE body Java emits for canonical prompts, then replays each through
Python (with a stubbed LLM that mimics the original turn) and asserts equality.

The LLM is intentionally faked here — the goal is **format parity**, not
response parity. (Response-quality parity is its own QA pass after cutover.)

## How to record a fixture from Java

1. Bring up the Java optimizer service (`./restart-backend.sh` → choose `o`).
2. Pick or create a test user; mint an `X-User-Id` value (gateway-equivalent).
3. For each scripted prompt in [`cases.json`](./cases.json), run:

   ```bash
   curl -sN -X POST http://localhost:8083/api/v1/chat/stream \
       -H 'Content-Type: application/json' \
       -H 'X-User-Id: <user-id>' \
       -d '{"message":"<prompt>","locale":"<locale>"}' \
       > tests/fixtures/sse_replay/<case-id>.expected.txt
   ```

4. Inspect the captured file — every frame should start with `event:` (no
   space after colon) and end with a blank line. Tool-call data should be
   compact JSON with no whitespace.

## Cases

The canonical 10 prompts cover the SSE format surface:

| id | covers |
|----|---|
| `01_greeting` | bare text response, no tools |
| `02_no_cards_recommend` | `search_cards` tool path |
| `03_best_card_groceries` | `get_user_cards` + `get_best_card` |
| `04_calc_reward_dining` | `calculate_reward` |
| `05_compare_two_cards` | `compare_cards` |
| `06_usage_guide` | `get_card_usage_guide` |
| `07_chinese_locale` | non-English language directive |
| `08_quota_exceeded` | single `error` frame, no tools |
| `09_invalid_input` | `INVALID_INPUT` error |
| `10_long_response_with_tool_chain` | multi-tool + long text |

## Stub LLM script

For each fixture we record both:
- the **Java SSE bytes** (`<id>.expected.txt`)
- the **stub LLM script** in `cases.json` describing the text chunks and
  tool calls the agent would emit on that turn

The Python regression test feeds the stub script through the production
`ChatService` + SSE serializer and diffs the result against `expected.txt`.

## Status

- `cases.json` is currently empty pending recording from a live Java instance.
- The harness (`tests/modules/chat/test_sse_regression.py`) is in place and
  will pick up fixtures automatically once they're added.

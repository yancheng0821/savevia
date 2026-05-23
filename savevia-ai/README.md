# savevia-ai

Python rewrite of `savevia-optimizer`. See `docs/superpowers/specs/2026-05-23-python-rewrite-design.md`.

## Dev

```bash
cd savevia-ai
uv sync
uv run uvicorn app.main:app --reload --port 8002
```

## Test

```bash
uv run pytest
```

# savevia-ai Cutover Runbook (Partial — chat / optimize / transactions / saved-results)

**Scope:** Move chat (`/api/v1/chat/stream`, `/api/v1/chat/suggestions`), single-purchase optimize (`/api/v1/optimize/calculate`), and other `/api/v1/optimize/**` routes (transactions / share / user-result) from Java `savevia-optimizer` to Python `savevia-ai`.

**Flinks (`/api/v1/optimize/bank/**`):** kept on Java for THIS interim cutover via the higher-priority `optimizer-bank` route rule. **Superseded 2026-05-30** — Flinks/bank-connection is now ported to Python (see `docs/superpowers/plans/2026-05-30-p4-flinks-port-and-regression.md`); once that port is validated, a follow-up cutover flips `optimizer-bank` to `${SAVEVIA_AI_URL}` and `savevia-optimizer/` is deleted in full.

**Cutover window:** ~30 minutes, off-peak (3-5 AM ET recommended).

**Rollback target:** ≤5 minutes (gateway-only env-var flip + restart).

---

## Roles

- **Lead:** runs the gateway flip; calls go/no-go.
- **Backup:** monitors dashboards, ready to execute rollback runbook.

---

## T-7 days

- [ ] All Phase 3 + Phase 4 partial tests green (`pytest -q` in `savevia-ai/`)
- [ ] Live extraction quality regression passing 10/10 (`pytest -m live tests/modules/memory/test_extraction_quality.py`)
- [ ] `savevia-ai` Docker image builds locally: `./deploy.sh build savevia-ai`
- [ ] `savevia-ai` deployed to staging (see "Deploy to staging" below)
- [ ] Snapshot diff harness green against staging
- [ ] SSE replay diff harness green against staging
- [ ] Agent behavior diff harness green against staging
- [ ] Load test: p99 latency on chat ≤ Java baseline × 1.15
- [ ] iOS + Android + Web manual regression through staging gateway, 24h soak with no SSE drops
- [ ] On-call schedule confirmed for cutover window

## T-1 day

- [ ] All-hands notice posted (24h advance)
- [ ] Java optimizer code freeze (no `savevia-optimizer/` merges)
- [ ] Confirm rollback runbook recently executed in staging
- [ ] `SAVEVIA_AI_URL` env var set in prod `.env` (`http://savevia-ai:8002`)
- [ ] OPENAI_API_KEY set in prod `.env`
- [ ] Verify prod RDS `user_profile_facts` / `user_conversation_summaries` / `merchant_categories` tables exist (migrations 28, 29 applied)

---

## T-time (cutover, ~30 min)

### Step 1: Build + push savevia-ai image (T+0, ~5 min)

```bash
cd /path/to/savevia
./deployment/deploy.sh build savevia-ai
./deployment/deploy.sh upload savevia-ai
```

Verify on EC2:
```bash
ssh -i ~/.ssh/savevia-prod.pem ubuntu@<EC2_HOST> \
    'docker images | grep savevia-ai'
```

### Step 2: Start savevia-ai container (T+5, ~5 min)

```bash
./deployment/deploy.sh start savevia-ai
```

Direct (bypass gateway) verify on EC2:
```bash
curl -s http://localhost:8002/ready
# expect: {"status":"ready","db":"ok","redis":"ok"} or similar HTTP 200
```

If this fails, **STOP** — do not flip routes. Container is unhealthy; debug logs and abort.

### Step 3: Flip gateway routes (T+10, ~2 min)

Gateway config (`savevia-gateway/src/main/resources/application.yml`) already points at `${SAVEVIA_AI_URL:http://savevia-ai:8002}` for the 4 routes. Two cutover modes:

**Mode A — full flip (recommended):**

The change has already been committed to `application.yml`. Restart gateway to pick up the new config:

```bash
./deployment/deploy.sh restart gateway
```

**Mode B — partial via env override (if testing first):**

Set `SAVEVIA_AI_URL=lb://savevia-optimizer` in the prod env to **keep Java serving**. Default value is Python. Flip the env to switch.

### Step 4: Smoke test through gateway (T+12, ~3 min)

```bash
# Public health (no auth)
curl -sS https://savevia.app/api/v1/app/version | jq

# Chat suggestions (needs JWT — paste a real token)
curl -sS -H "Authorization: Bearer $JWT" \
    "https://savevia.app/api/v1/chat/suggestions?locale=en" | jq

# Optimize calculate (POST, needs JWT)
curl -sS -X POST -H "Authorization: Bearer $JWT" -H 'Content-Type: application/json' \
    -d '{"amount": 100, "category": "GROCERY"}' \
    https://savevia.app/api/v1/optimize/calculate | jq

# Bank/Flinks — must STILL hit Java
curl -sS -H "Authorization: Bearer $JWT" \
    https://savevia.app/api/v1/optimize/bank/flinks-config | jq
```

Acceptance:
- Chat returns SSE frames in the Python format (sample one frame, compare event names).
- Optimize calculate returns within p99 baseline.
- Bank/Flinks returns Java response (look at `X-Forwarded-Service` if header is set, or log lines).

If any test fails: **execute rollback runbook**.

### Step 5: Monitor (T+15 through T+1h)

Watch dashboards continuously:

| Metric | Threshold | Action if breached |
|---|---|---|
| Error rate (5xx) | < 0.5% (matches Java baseline) | Rollback |
| Chat p99 latency | ≤ Java p99 × 1.15 | Investigate; rollback if not fixable in 15 min |
| Open SSE connections | within ±20% of Java baseline | Investigate connection drops |
| `savevia-ai` container memory | < 80% of 768M limit | Restart if OOM imminent |
| `savevia-ai` container CPU | < 80% sustained | Check load; consider scaling |

Also tail logs:
```bash
./deployment/deploy.sh logs savevia-ai
./deployment/deploy.sh logs gateway
```

Red flags in logs:
- Repeated `JavaServiceError` on memory/quota writeback → user service degradation
- `agent_invocation_failed` spikes → OpenAI rate limit / quota
- `_stream_uncaught` → bug

### Step 6: T+1h soak (T+1h through T+24h)

- On-call ready, no manual intervention if metrics stable.
- Check dashboards every hour for first 6 hours, then end of day.
- If any single anomaly persists > 15 minutes: rollback and post-mortem.

---

## T+7 days: Cleanup decision

If 7 days clean (no rollback, no incidents):

- Tag the cutover commit: `git tag python-ai-cutover-partial && git push --tags` (interim, chat/optimize only).
- Java `savevia-optimizer` keeps running as the interim Flinks server + rollback net.
- **Follow-up cutover (after the Python Flinks port is validated):** flip the `optimizer-bank` route to `${SAVEVIA_AI_URL}`, then delete `savevia-optimizer/` in full and remove it from `savevia-parent/pom.xml`. See `docs/superpowers/plans/2026-05-30-p4-flinks-port-and-regression.md`.
- Update root `README.md` + `CLAUDE.md` to single-Python-AI architecture once the directory is removed.

If any rollback within 7d: full retro, fix, re-attempt cutover.

---

## Appendix A — Deploy to staging

```bash
# From your dev machine, with prod .env staged for staging:
EC2_HOST=<staging-ip> ./deployment/deploy.sh deploy savevia-ai gateway
```

The gateway needs a redeploy because `application.yml` baked in the route flip — re-uploading + restarting is required for the flip to take effect.

## Appendix B — Reading gateway logs for a single request

```bash
# Filter gateway access log by path:
ssh ubuntu@<EC2_HOST> 'docker logs savevia-gateway 2>&1 | grep "/api/v1/chat/stream" | tail -20'
```

Gateway forwards via Reactor Netty; the `uri:` line in the route config determines downstream host. After cutover, that should be `http://savevia-ai:8002` for the 4 routes (verify with `docker inspect savevia-gateway | jq '.[].Config.Env'`).

# savevia-ai Rollback Runbook

**SLA:** ≤ 5 minutes from "execute rollback" to "Java serves all traffic again."

**Premise:** Python `savevia-ai` is serving chat / optimize / transactions / saved-results in prod, and something is wrong (high error rate, p99 latency spike, SSE drops, OOM, mobile crash, etc.).

**Goal:** restore the pre-cutover state — gateway routes the 4 endpoint groups back to Java `savevia-optimizer`. Java optimizer is still running (it never stopped — it kept serving `/api/v1/optimize/bank/**`), so this is a route flip, not a service redeploy.

---

## Decision matrix

| Symptom | Rollback now? |
|---|---|
| Error rate spike > 1% for > 2 min | Yes |
| Chat p99 > Java baseline × 1.5 for > 5 min | Yes |
| SSE active connections drop > 30% suddenly | Yes |
| Mobile reports crash on chat send | Yes |
| `savevia-ai` container OOM-killed > 1× in 10 min | Yes |
| `savevia-ai` returning 5xx for any specific tool | Investigate first; rollback if not fixable in 10 min |
| Slow tool call response, but no errors | Investigate first; consider increasing container CPU |
| OpenAI rate limit warnings in logs | Throttle / wait — rollback only if user-facing errors |

When in doubt, **rollback**. Cost of rollback is ~5 min of confusion; cost of bad cutover is hours of user-facing failures.

---

## Rollback procedure (5 minutes)

### Step 1: Flip env var (T+0, 30 sec)

The gateway config uses `${SAVEVIA_AI_URL:http://savevia-ai:8002}` for the 4 cutover routes. Override it to point back at Eureka load-balanced Java optimizer:

```bash
# On EC2 (or wherever .env lives for the gateway container):
ssh -i ~/.ssh/savevia-prod.pem ubuntu@<EC2_HOST>

cd ~/savevia
# Edit .env — add or set:
echo "SAVEVIA_AI_URL=lb://savevia-optimizer" >> .env
```

> Note: `lb://savevia-optimizer` requires Eureka. The gateway already uses `lb://` for other routes, so this is a known-good form.

### Step 2: Restart gateway (T+1m, 1-2 min)

```bash
docker-compose up -d --force-recreate gateway
# OR
docker-compose restart gateway
```

The container picks up the new env var on restart. Eureka-discovered `savevia-optimizer` is the new target.

### Step 3: Verify Java is serving (T+3m, 30 sec)

```bash
# Hit chat suggestions through the gateway — should land on Java optimizer
curl -sS -H "Authorization: Bearer $JWT" \
    "https://savevia.app/api/v1/chat/suggestions?locale=en" | jq

# Inspect downstream container logs to confirm Java optimizer received the request
docker logs savevia-optimizer --tail 20 | grep "/api/v1/chat/suggestions"
```

Acceptance: a request through the gateway shows up in `savevia-optimizer` logs (not `savevia-ai`).

### Step 4: Stop savevia-ai container (T+4m, 30 sec, optional)

Keep it stopped to free memory and confirm no traffic leaks:

```bash
docker-compose stop savevia-ai
```

> Do **not** delete the image or volumes. We may attempt cutover again after the fix.

### Step 5: All-hands notice (T+5m)

Post to team channel:
- "Rolled back savevia-ai cutover at <time>"
- Symptom that triggered it (1 sentence)
- Java is serving 100% AI traffic again
- Post-mortem will be scheduled

---

## Post-rollback

- File a post-mortem doc within 24h
- Root-cause the failure
- Fix in code / config / infra
- Verify in staging with a fresh soak test
- Re-attempt cutover only after green staging + retro signoff

---

## Permanent rollback (if Python rewrite is abandoned)

Not in scope for this runbook. If a decision is made to permanently revert:

1. Revert `savevia-gateway/src/main/resources/application.yml` to point all 4 routes at `lb://savevia-optimizer`.
2. Re-add the `optimizer-bank` route or remove it (no longer needed for path arbitration).
3. Remove `savevia-ai` from `deployment/docker-compose.production.yml`.
4. Remove `savevia-ai` entries from `deployment/deploy.sh`.
5. Commit, redeploy gateway, post-deploy retro on what didn't work in the Python rewrite.

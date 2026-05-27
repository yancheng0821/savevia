# savevia-ai Cutover — Implementation Plan (Phase 5 + 6 + 7)

> **Status:** SKELETON. Scope revised 2026-05-27 — **partial cutover**, Java optimizer is NOT decommissioned.

**Goal (revised):** Cut over the Python-ported endpoint subset (chat / transactions / saved-results / optimize) from Java optimizer to `savevia-ai`. Java optimizer **stays in production** to keep serving Flinks / bank-connection / connection-limit endpoints (those tasks were deferred in Phase 4). No `savevia-optimizer/` deletion.

**Architecture:** Spring Cloud Gateway routes for the ported endpoints flip from `lb://savevia-optimizer` to `http://savevia-ai:8002`. Flinks-related routes (`/api/v1/bank-connections/**`, Flinks webhook path, etc.) stay pointing at Java. Both services run side by side indefinitely. No data migration — Python and Java share MySQL/Redis.

**Reference spec:** `docs/superpowers/specs/2026-05-23-python-rewrite-design.md` §8, §9, §10 (Phases 5-7)

**Estimated effort:** 6 person-days (1.5 weeks calendar — most of P6+P7 is passive observation).

---

## File Structure (additions / modifications)

```
# Modified:
savevia-gateway/src/main/resources/application.yml      # route flips for ported endpoints only
docker-compose.yml                                       # uncomment savevia-ai service (alongside savevia-optimizer)
deployment/deploy.sh                                     # add savevia-ai build/push

# Created:
savevia-ai/scripts/
├── snapshot_diff.py                # API snapshot diff Java vs Python (chat / transactions / saved-results / optimize only)
├── sse_replay_diff.py              # SSE format diff
├── agent_behavior_diff.py          # tool-call sequence diff
├── load_test.py                    # locust / k6 wrapper
└── smoke_test.py                   # cutover-day end-to-end script

docs/runbooks/
├── cutover-runbook.md              # step-by-step cutover procedure
└── rollback-runbook.md             # ≤5min rollback steps

# NOT deleted (scope revised — Flinks/bank-connections deferred):
savevia-optimizer/                  # remains in repo and in prod; serves Flinks routes only
```

---

## Task List

### Phase 5: Pre-cutover (5 days)

| # | Task | Files | Days |
|---|---|---|---|
| 1 | Gateway config: add 4 routes for AI service (commented out, behind feature flag) | `savevia-gateway/src/main/resources/application.yml` | 0.5 |
| 2 | Gateway config rollback script + DNS/upstream switch procedure | `docs/runbooks/cutover-runbook.md`, `docs/runbooks/rollback-runbook.md` | 0.5 |
| 3 | docker-compose: uncomment savevia-ai entry; verify local stack runs all 7 services | `docker-compose.yml`, manual verification | 0.5 |
| 4 | Deployment script: add savevia-ai image build, push to ECR, deploy to EC2 | `deployment/deploy.sh` | 1 |
| 5 | API snapshot diff harness — hits both Java and Python with same inputs, diffs JSON | `savevia-ai/scripts/snapshot_diff.py` | 1 |
| 6 | SSE replay diff harness — replays recorded streams, diffs Python output | `savevia-ai/scripts/sse_replay_diff.py` | 0.5 |
| 7 | Agent behavior diff harness — fixed prompts, compare tool-call sequences | `savevia-ai/scripts/agent_behavior_diff.py` | 0.5 |
| 8 | Load test (k6 or locust) — verify p99 within +15% of Java baseline | `savevia-ai/scripts/load_test.py` | 0.5 |
| 9 | Deploy savevia-ai to staging EC2 (connect to prod RDS read-replica) | manual + deployment script | 1 |
| 10 | Run full regression suite against staging; fix any diffs | (test runs) | 1 |
| 11 | Device regression: iOS + Android + web through staging gateway, 24h soak | manual | 0.5 |

### Phase 6: Cutover day (2 days)

| # | Task | Files | Days |
|---|---|---|---|
| 12 | T-1: freeze Java optimizer code; close Flinks new-connection acceptance for 1h | Flinks dashboard, deployment lock | 0.25 |
| 13 | T-time (3-5 AM): deploy savevia-ai to prod | deployment script | 0.25 |
| 14 | T-time: flip Gateway routes (Java → Python); restart Gateway | `application.yml`, gateway restart | 0.25 |
| 15 | T+5min through T+1h: monitor error rate, p99 latency, SSE conn count, tool-call success rate | dashboards | 0.25 |
| 16 | T+1h through T+1d: passive observation, on-call ready | dashboards | 1 |

### Phase 7: Post-cutover cleanup (scope revised — partial)

| # | Task | Files | Days |
|---|---|---|---|
| 17 | T+7d: trim Java optimizer config — remove dead chat/transactions/saved-results/optimize controllers & services from `savevia-optimizer` (Flinks-related code stays) | `savevia-optimizer/` | 1 |
| 18 | Update root README + CLAUDE.md: dual-service architecture (Python AI + Java Flinks) | `README.md`, `CLAUDE.md` | 0.25 |
| | **Subtotal (cutover only)** | | **~5** |

> Java optimizer is **not** deleted. Future plan needed to port Flinks before the directory can be fully removed.

---

## Cutover Runbook (skeleton — flesh out in Phase 5 Task 2)

### T-7 days
- [ ] Deploy savevia-ai to staging
- [ ] All regression suites green
- [ ] Mobile QA sign-off

### T-1 day
- [ ] All hands aware of cutover window
- [ ] Java code freeze on optimizer
- [ ] Pause Flinks new-connection acceptance
- [ ] Confirm rollback procedure tested

### T-time (3:00 AM ET)
1. [ ] Deploy savevia-ai container to prod
2. [ ] Verify `/health` and `/ready` from outside gateway (direct port)
3. [ ] Apply gateway config: change AI routes to `http://savevia-ai:8002`
4. [ ] Restart gateway (or `actuator/refresh`)
5. [ ] Curl one AI endpoint through gateway, verify Python response

### T+0 to T+1h
- [ ] Monitor: error rate < 0.5% (matches Java baseline)
- [ ] Monitor: p99 < Java baseline + 15%
- [ ] Monitor: SSE active connections normal
- [ ] Monitor: no spike in 5xx
- [ ] Anomaly: execute rollback runbook

### Rollback (if needed, must complete in ≤5 min)
1. [ ] Revert gateway config to `lb://savevia-optimizer`
2. [ ] Restart gateway
3. [ ] Verify AI endpoint hits Java
4. [ ] Post-mortem scheduled

### T+7d
- [ ] No incidents → schedule Java decommission
- [ ] Drain Java optimizer (no traffic for 7 days already, safe to remove)
- [ ] Delete code, tag final commit `java-optimizer-final`

---

## Definition of Done (revised — partial cutover)

- [ ] Chat / transactions / saved-results / optimize endpoints serve from Python in production
- [ ] Flinks / bank-connections / connection-limits endpoints still serve from Java (no change)
- [ ] 7 days post-cutover with no rollback needed
- [ ] Java `savevia-optimizer/` trimmed to Flinks-only (chat / optimizer / transactions / saved-results controllers + services removed)
- [ ] `docker-compose.yml` has both `savevia-ai` AND `savevia-optimizer`
- [ ] README + CLAUDE.md updated; runbooks committed under `docs/runbooks/`
- [ ] Tag `python-ai-cutover-partial` on final commit
- [ ] Retrospective written and shared
- [ ] Follow-up issue filed: "Port Flinks integration to Python (future Phase 4.5)"

---

## Risks Active During This Phase

(See full register in spec §12. The high-impact risks for cutover specifically:)

| Risk | Trigger | Action |
|---|---|---|
| SSE event format mismatch surfaces only on real frontend | First real iOS/Android user hits Python | Rollback; fix; retry next window |
| Tool call latency higher than expected under prod load | T+15min metrics show p99 > +15% | Investigate (Java service slow? httpx pool exhausted?); rollback if not fixable in 30min |
| Flinks webhook fails to route to Python | Bank connection callbacks failing | Verify webhook URL in Flinks dashboard; check gateway route for webhook path; rollback if needed |
| MemoryExtraction background tasks pile up in event loop | Memory usage climbing in Python process | Add concurrency limit (semaphore); restart |

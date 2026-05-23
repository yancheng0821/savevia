# savevia-ai Cutover — Implementation Plan (Phase 5 + 6 + 7)

> **Status:** SKELETON. Step-level detail to be written when Phase 5 begins, after Phase 4 is feature-complete.

**Goal:** Gateway configuration update, staging deployment, full regression validation, production cutover, observation period, and Java optimizer cleanup. After this plan, `savevia-ai` serves 100% of AI traffic in production and `savevia-optimizer` is deleted from the repo.

**Architecture:** Spring Cloud Gateway routes flip from `lb://savevia-optimizer` to `http://savevia-ai:8002` in a single config change. Java optimizer stays running 7 days post-cutover as a rollback safety net. No data migration — Python and Java share MySQL/Redis.

**Reference spec:** `docs/superpowers/specs/2026-05-23-python-rewrite-design.md` §8, §9, §10 (Phases 5-7)

**Estimated effort:** 6 person-days (1.5 weeks calendar — most of P6+P7 is passive observation).

---

## File Structure (additions / modifications)

```
# Modified:
savevia-gateway/src/main/resources/application.yml      # route flips + Python URL
docker-compose.yml                                       # uncomment savevia-ai service
deployment/deploy.sh                                     # add savevia-ai build/push

# Created:
savevia-ai/scripts/
├── snapshot_diff.py                # API snapshot diff Java vs Python
├── sse_replay_diff.py              # SSE format diff
├── agent_behavior_diff.py          # tool-call sequence diff
├── load_test.py                    # locust / k6 wrapper
└── smoke_test.py                   # cutover-day end-to-end script

deployment/
├── savevia-ai.dockerfile           # (or use savevia-ai/Dockerfile) prod variant
└── nginx/                          # if Nginx replaces Spring Cloud Gateway later (out of scope here)

docs/runbooks/
├── cutover-runbook.md              # step-by-step cutover procedure
└── rollback-runbook.md             # ≤5min rollback steps

# Deleted (after T+7 observation):
savevia-optimizer/                  # entire directory
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

### Phase 7: Post-cutover cleanup (1 day, anytime in T+7 to T+14 window)

| # | Task | Files | Days |
|---|---|---|---|
| 17 | T+7d (clean): shut down Java optimizer container | `docker-compose.yml`, deployment | 0.25 |
| 18 | Remove `savevia-optimizer` from `savevia-parent/pom.xml` | `savevia-parent/pom.xml` | 0.25 |
| 19 | Delete `savevia-optimizer/` directory | `git rm -r savevia-optimizer/` | 0.25 |
| 20 | Update root README to reflect new architecture | `README.md`, `CLAUDE.md` | 0.25 |
| | **Subtotal** | | **6** |

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

## Definition of Done

- [ ] All AI endpoints serve from Python in production
- [ ] 7 days post-cutover with no rollback needed
- [ ] Java `savevia-optimizer/` directory deleted from repo
- [ ] `savevia-parent/pom.xml` no longer references optimizer module
- [ ] `docker-compose.yml` no longer has optimizer service
- [ ] README updated; runbooks committed under `docs/runbooks/`
- [ ] Tag `python-ai-cutover-complete` on final commit
- [ ] Retrospective written and shared

---

## Risks Active During This Phase

(See full register in spec §12. The high-impact risks for cutover specifically:)

| Risk | Trigger | Action |
|---|---|---|
| SSE event format mismatch surfaces only on real frontend | First real iOS/Android user hits Python | Rollback; fix; retry next window |
| Tool call latency higher than expected under prod load | T+15min metrics show p99 > +15% | Investigate (Java service slow? httpx pool exhausted?); rollback if not fixable in 30min |
| Flinks webhook fails to route to Python | Bank connection callbacks failing | Verify webhook URL in Flinks dashboard; check gateway route for webhook path; rollback if needed |
| MemoryExtraction background tasks pile up in event loop | Memory usage climbing in Python process | Add concurrency limit (semaphore); restart |

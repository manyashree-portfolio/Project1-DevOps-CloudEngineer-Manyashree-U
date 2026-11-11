# Incident Simulation: Friday 5 PM Production Incident (Level 5, "The Incident")

**Author:** Manyashree U | **Playbook used:** [Incident playbook](../../runbooks/incident-playbook.md) | **Rollback design:** [Deliverable 6](../06-rollback-specification/rollback-specification.md) | **Post-mortem:** [post-mortem-INC-SIM-001.md](post-mortem-INC-SIM-001.md)

> **This is a tabletop exercise.** Nothing here was run against a real cluster. All times are the *designed* response times from the playbook and rollback specification, not measurements. Details that the brief does not give (the root cause, the 2% canary share, the recovery curve) are **scenario assumptions** and are marked as such.

## 1. The scenario (from the brief, Section B5)
It is **Friday 5:07 PM IST**. A developer pushed a "critical hotfix" that **bypassed staging**. The canary has been running for **8 minutes** (started about 4:59 PM). Three alerts fire at the same moment:

| Alert | Value | Severity | Matching trigger in [Deliverable 6](../06-rollback-specification/rollback-specification.md) |
|-------|-------|----------|--------------------------------|
| HTTP 500 error rate | 12% (threshold 5%) | CRITICAL | **A1**: 5xx rate > 5% for 60 s, automatic |
| PostgreSQL connection-pool exhaustion on primary | pool exhausted | HIGH | **A5**: > 10 pending connections for 30 s, automatic |
| Downstream payment-gateway timeout rate | 35% | CRITICAL | **Category C** pattern (downstream correlation), manual decision |

**Assumptions made for the exercise:** the canary was in phase 1 (at most about 2% of traffic, per the canary progression in [Deliverable 2](../02-deployment-strategies/deployment-strategies.md)); the 12% figure is measured on canary traffic; the `for:` windows of A1 and A5 had already elapsed when the alerts reached people.

## 2. Decision timeline (IST)
Format follows the playbook's seven steps. **Bold step numbers** match [playbook section 3](../../runbooks/incident-playbook.md#3-seven-step-incident-response-workflow).

| Time | T+ | Step | Who | Action or decision | Why |
|------|----|------|-----|--------------------|-----|
| 16:59:00 | - | context | Developer | Hotfix deployed to canary, staging skipped | Starting condition of the scenario |
| 17:07:00 | T+0 | **1 Detect** | Alertmanager, rollback controller | Three alerts fire. PagerDuty pages SRE on-call. **Category A rollback starts automatically** because A1 and A5 are both active | Category A needs no human ([rollback spec section 2](../06-rollback-specification/rollback-specification.md)) |
| 17:07:10 | T+10 s | **2 Acknowledge** | SRE on-call | Acknowledges the page, opens the Engineering dashboard | Playbook: acknowledge within 30 s |
| 17:07:30 | T+30 s | **2 Triage** | SRE on-call | Classifies **SEV-1**; declares self **Incident Commander** out loud | Playbook rule: money movement is SEV-1 until proven otherwise |
| 17:07:35 | T+35 s | **2 Correlate** | IC | `novapay_deploy_info` shows a release 8 minutes ago and no staging record. Hypothesis: **the hotfix is the cause** | Playbook golden rule: release within 2 hours means roll back first |
| 17:07:40 | T+40 s | **4 Freeze** | Ops lead | Confirms promotion freeze, no further syncs; production ArgoCD app is manual-sync, so nothing can re-apply the hotfix | Rollback must not fight GitOps |
| 17:07:55 | T+55 s | **4 Rollback** | Rollback controller | Canary aborted, Istio VirtualService set to 100% stable. Traffic back on the stable version | Category A target: under 60 s from trigger |
| 17:08:05 | T+65 s | **3 Mobilise** | IC | Opens incident channel, pages escalation path **CTO + CISO + VP Eng** (SEV-1), pulls in Compliance liaison, assigns Ops lead, Comms lead, Scribe | Playbook section 4, SEV-1 procedure |
| 17:09:00 | T+2 m | **3 Communicate** | Comms lead | **Initial acknowledgement (template A1)** to the internal incident channel and status page: "A subset of payment requests failed between 4:59 and 5:08 PM; a change was rolled back; investigating" | Honest, no cause speculation |
| 17:09:30 | T+2.5 m | **5 Verify** | Ops lead | 5xx back under 0.1% on all pods; `SHOW POOLS;` on pgBouncer shows no waiting clients; single image digest across the fleet | Post-rollback verification list |
| 17:10:30 | T+3.5 m | **5 Correlate (gateway)** | Ops lead + IC | Gateway timeouts falling (35% to about 4%) **after** rollback. Gateway's own status page is green. Conclusion: the timeouts were caused by our change (retry load and held connections), **not** a gateway outage | Scenario C check: rollback helps only if our release changed the gateway call |
| 17:12:00 | T+5 m | **5 Monitor** | Ops lead | Metrics inside 10% of the 7-day baseline; keeps the freeze | Verification needs 10 minutes of steady metrics |
| 17:15:00 | T+8 m | **6 Decide on regulators** | Compliance liaison | Customer impact lasted about 9 minutes (4:59 to 5:08), **below the 30-minute reporting trigger**. Decision recorded; to be confirmed with Compliance | Playbook section 6 |
| 17:17:30 | T+10.5 m | **6 Resolve** | Comms lead | **Resolution notice (template A4)** with impact summary; status page set to resolved; incident downgraded to SEV-3 follow-up | Verification window passed |
| 17:20:00 | T+13 m | **6 Close** | IC | Freeze stays on until the post-mortem owner releases it; no weekend deploys without IC approval | Friday evening, peak hours |
| Mon | T+3 d | **7 Post-mortem** | Author | Blameless review, draft within 48 h ([post-mortem](post-mortem-INC-SIM-001.md)) | SEV-1 rule |

**Design note on the brief's example timing.** The brief's example puts "rollback initiated" at T+5m. In this design the rollback starts at **T+0 automatically**, and the human steps (triage, communication, verification) run alongside it. That is the main benefit of Category A automation.

## 3. Communications sent
| Time | Audience | Template | Content summary |
|------|----------|----------|-----------------|
| T+65 s | CTO, CISO, VP Eng | Page | SEV-1 declared, payments affected, rollback already executed |
| T+2 m | Internal channel and status page | A1 Initial acknowledgement | Subset of payments failing, change rolled back, investigating |
| T+5 m | Executive bridge | A3 Mitigation notice | Rollback complete, metrics recovering |
| T+10.5 m | Internal and status page | A4 Resolution | Window 4:59 to 5:08 PM, canary cohort only, root cause under review |
| T+8 m | Compliance | Decision record | Under 30 minutes; filing not triggered, confirm with Compliance |

SEV-1 update cadence (every 30 minutes) was not reached because the incident resolved first.

## 4. Root cause (scenario assumption) and which gate was bypassed
**Direct cause (assumed for the exercise):** the hotfix added a synchronous payment-gateway call **inside a database transaction without a timeout or circuit breaker**. Slow gateway responses kept connections checked out, so the pool ran dry (alert 2), requests failed (alert 1), and client retries pushed more load at the gateway, so its timeout rate climbed (alert 3).

**What was bypassed:** the hotfix skipped staging, so it never met **Stage 5 (integration and contract testing)**, the **performance baseline under 2x load** and **Stage 6 (DAST)**. Each of these would have caught a pool-exhaustion regression before production.

## 5. Evaluation: did the pipeline design prevent this?
**Short answer: it limited the damage but did not prevent the release.**

| What worked | Evidence in the design |
|-------------|------------------------|
| Small blast radius | Canary phase 1 caps traffic at about 2% |
| Fast, human-free recovery | Category A rollback, under 60 s from trigger |
| Correct handling of the ambiguous alert | Playbook scenario C stopped the team blaming the gateway |
| No schema damage | Expand-contract migrations ([Deliverable 4](../04-database-migration/migration-strategy.md)) mean rollback needs no schema change |

**Gaps this exercise exposes (the missing gates):**

| # | Missing or weak gate | Fix (proposed, not yet implemented in this repo) |
|---|---------------------|-----------------------------------------------|
| G1 | **No proof-of-promotion check at deploy time.** The hotfix path allowed a production canary without evidence that staging gates passed | Add a signed **promotion-evidence attestation** (Cosign) produced by the staging stage, and a Kyverno `verifyImages` attestation rule that rejects any production pod whose image lacks it. This extends the existing signature and SBOM admission rules |
| G2 | **Deployment-window check not enforced for hotfixes.** 4:59 PM on a Friday is inside the daily 5 PM to 8 PM UPI peak window | The ArgoCD sync windows in [appproject.yaml](../../pipeline/helm/argocd/appproject.yaml) block this for GitOps syncs. Close the remaining gap by also checking the window in the pipeline's production job, and by removing direct cluster deploy rights (segregation of duties) |
| G3 | **No pool-saturation gate in performance testing** | Add pgBouncer and HikariCP pending-connection thresholds as pass/fail criteria in the staging performance test |
| G4 | **No resilience rule for outbound calls** | Add a code-review checklist item and a SAST rule: outbound HTTP calls need timeouts; Istio outlier detection in the Helm chart already ejects failing pods |
| G5 | **Emergency rollback depends on a person noticing a bad freeze state** | Covered by the break-glass script; test it in a real cluster (not yet done) |

**Hotfix principle from the brief:** hotfixes should be "expedited but not bypassed". The fix for G1 makes that technically enforceable instead of a convention.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U. The scenario details marked as assumptions are invented for the exercise.

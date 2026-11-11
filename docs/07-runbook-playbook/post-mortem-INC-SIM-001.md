# Post-mortem: Hotfix bypassed staging, canary failed on payments (INC-SIM-001)

Date: Friday (simulated)   Severity: SEV-1   Author: Manyashree U   Status: draft (tabletop exercise)

> Blameless format from [playbook appendix C](../../runbooks/incident-playbook.md). Companion: [incident simulation](incident-simulation-friday-5pm.md). This is a **simulated** incident; times are designed targets, not measurements.

## Summary
A "critical hotfix" that skipped staging reached the production canary at about 4:59 PM IST on a Friday. At 5:07 PM three alerts fired together (HTTP 500s at 12%, database connection-pool exhaustion, payment-gateway timeouts at 35%). The automatic Category A rollback returned all traffic to the stable version within about 55 seconds, and metrics were back to baseline within about 5 minutes.

## Impact
Users/customers affected: canary cohort only (assumed at most about 2% of traffic)   Failed or delayed transactions: not measured in a tabletop   Duration: about 9 minutes (4:59 to 5:08 PM)
Revenue / regulatory impact: none expected; below the 30-minute RBI reporting trigger (confirm with Compliance)   SLO / error budget consumed: not calculated for a simulation

## Timeline (IST)
| Time | Event |
|------|-------|
| 16:59 | Hotfix deployed to canary, staging skipped |
| T+0 (17:07:00) | Alerts fired: HTTP 500 rate 12%, pool exhaustion, gateway timeouts 35%. Automatic rollback started |
| T+10 s | On-call acknowledged |
| T+30 s | Triage, classified SEV-1, Incident Commander declared |
| T+35 s | Correlated with the release from 8 minutes earlier |
| T+55 s | Traffic restored to stable (rollback done) |
| T+65 s | Escalation path paged, incident channel opened |
| T+2 m | Initial acknowledgement sent (template A1) |
| T+3.5 m | Gateway timeouts falling after rollback; gateway status green, so cause is internal |
| T+5 m | Metrics within 10% of baseline |
| T+8 m | Compliance liaison: below 30-minute threshold, decision recorded |
| T+10.5 m | Resolution notice sent (template A4) |

## Root cause analysis
Direct cause (scenario assumption): the hotfix called the payment gateway inside a database transaction with no timeout and no circuit breaker.
Contributing factors (5 whys):
1. Pool exhausted because connections were held while waiting on the gateway.
2. Nothing in the hotfix path exercised the service under load or against the gateway sandbox, because staging was skipped.
3. Staging could be skipped because the hotfix path relied on convention, not on a technical check.
4. Nothing at deploy time asked for proof that staging gates had passed.
5. The release went out during the UPI evening peak on a Friday because the window check was not enforced for hotfixes outside GitOps.

Which pipeline gate should have caught this, and why it did not: **Stage 5 (integration and contract testing) plus the 2x-load performance baseline** would have caught it; they did not run because the hotfix never went through staging. The missing control is a **promotion-evidence check at admission** (see action 1).

## What went well / what went badly / where we got lucky
- **Went well:** automatic rollback in under a minute; correct reading of the ambiguous gateway alert; communication inside 2 minutes; no schema rollback needed.
- **Went badly:** a production canary started without staging evidence; the release landed inside the UPI evening peak on a Friday.
- **Got lucky:** the canary was small (phase 1) and the failure was loud. A subtler leak could have run for the full 15-minute phase.

## Action items (tracked in Jira until closed)
| # | Action | Type | Owner | Due date | Ticket |
|---|--------|------|-------|----------|--------|
| 1 | Add Cosign promotion-evidence attestation and a Kyverno rule that rejects production images without it | prevent | Platform/SRE | +14 days | NOVA-1xx |
| 2 | Enforce the deployment-window check in the pipeline's production job for all paths, including hotfixes | prevent | Release Manager | +7 days | NOVA-1xx |
| 3 | Remove direct cluster-deploy rights from developers (segregation of duties) | prevent | SRE Lead | +7 days | NOVA-1xx |
| 4 | Add pgBouncer/HikariCP pending-connection thresholds to the staging performance gate | detect | QA lead | +14 days | NOVA-1xx |
| 5 | Add a SAST/review rule: outbound calls need timeouts and circuit breakers | prevent | Tech Lead | +14 days | NOVA-1xx |
| 6 | Run the break-glass rollback script in a test cluster and record the result | mitigate | SRE | +10 days | NOVA-1xx |

(Ticket numbers are placeholders for the exercise.)

## Lessons learned and pipeline improvements
Speed and safety did not conflict here: the part of the design built for speed (automatic rollback) is what contained the damage. The part that failed was the *preventive* side, where a convention ("hotfixes still go through gates") was not backed by a technical control. The improvements above turn that convention into something the cluster itself enforces.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

# NovaPay Incident Response Playbook

**Owner:** SRE Lead | **Related:** [Deployment runbook](deployment-runbook.md), [Rollback specification](../docs/06-rollback-specification/rollback-specification.md), [Observability and alerting](../docs/08-observability/observability.md)

> **Golden rule: restore service first, find the cause later.** For any incident that started within 2 hours of a release, **roll back first** ([runbook section 5](deployment-runbook.md#5-rollback-in-60-seconds)).

## 1. Severity classification
| Severity | Definition | Response time | Escalation path | Update cadence |
|----------|-----------|---------------|-----------------|----------------|
| **SEV-1** | Complete service outage or data-integrity risk | < 5 minutes | CTO + CISO + VP Engineering | Every 30 min |
| **SEV-2** | Major feature degradation affecting > 10% of users | < 15 minutes | VP Engineering + SRE Lead | Hourly |
| **SEV-3** | Minor degradation, workaround exists | < 1 hour | SRE on-call + Tech Lead | Every 4 h |
| **SEV-4** | Cosmetic issue, no user impact | Next business day | Assigned engineer | On resolution |

**When unsure, classify one level higher** and downgrade later. Anything touching money movement, ledger integrity or card data is SEV-1 until proven otherwise.

## 2. Roles
| Role | Responsibility |
|------|----------------|
| **Incident Commander (IC)** | Owns the incident, makes decisions, assigns work. First responder is IC until someone senior takes over, and it is announced out loud |
| **Operations lead** | Hands-on mitigation (rollback, scaling, flags) |
| **Communications lead** | Sends all updates using the templates in appendix A; only person who posts externally |
| **Scribe** | Keeps the timestamped timeline (appendix C needs it) |
| **Compliance liaison** | Joins for SEV-1/SEV-2: regulatory notification decision |

## 3. Seven-step incident response workflow
| # | Step | What to do | Target time |
|---|------|-----------|-------------|
| 1 | **Detect and alert** | Alert fires (Prometheus to Alertmanager to PagerDuty). Category A alerts already trigger automatic rollback | T+0 |
| 2 | **Acknowledge and triage** | Acknowledge the page. Open the Engineering dashboard. Decide the severity (section 1). Name the IC | T+30 s |
| 3 | **Mobilise and communicate** | Open an incident channel, page the escalation path, send the **initial acknowledgement** (appendix A1) | T+2 min |
| 4 | **Mitigate** | Roll back if a release is the likely cause; otherwise use the scenario below (scale, flag off, fail over). Automatic rollback for Category A runs at about T+60 s; if it did not, run it manually | T+5 min at the latest |
| 5 | **Verify and monitor** | Post-rollback verification (smoke tests, metrics within 10% of baseline for 10 min, one image digest) | T+10 min |
| 6 | **Resolve and close** | Send the **resolution notice** (A4) with impact summary; downgrade/close the incident; decide regulatory notification (section 6) | On recovery |
| 7 | **Postmortem** | Blameless review using the template in appendix C; action items tracked to closure | SEV-1: draft in 48 h; others within 5 working days |

## 4. Procedures per severity
- **SEV-1:** IC + Ops + Comms + Scribe all active. Executive bridge open (CTO, CISO, VP Eng). Updates every 30 min on the internal channel and the status page. Compliance liaison engaged immediately. No deployments allowed until the IC clears the freeze.
- **SEV-2:** IC + Ops + Comms. VP Eng and SRE Lead informed. Hourly updates. Status page updated if customer-visible.
- **SEV-3:** On-call SRE owns it with the Tech Lead. Slack updates every 4 h. Fix in working hours if no user is blocked.
- **SEV-4:** Ticket only; fix in normal sprint flow.

## 5. Scenario playbooks

### Scenario A: Bad deployment
Signs: error ratio or latency rises within minutes of a rollout; Category A/B alert with a recent `novapay_deploy_info`.
1. Confirm a release is in the last 2 hours (Argo revision history).
2. `./pipeline/scripts/emergency-rollback.sh canary "<reason>"` (or let the automatic rollback finish).
3. Verify (step 5), keep the freeze on, open the incident, find the cause in staging.
4. Check whether a DB migration was part of the release: expand-phase changes need no schema rollback; contract changes need the DBA ([migration strategy](../docs/04-database-migration/migration-strategy.md)).

### Scenario B: Database connection pool exhaustion
Signs: pending connections above 10, timeouts on payment calls, PostgreSQL primary alert.
1. Rollback first if a release is recent (a new query or leaked connection is common).
2. Otherwise check pgBouncer (`SHOW POOLS;`) for long-running or idle-in-transaction sessions; DBA terminates offenders.
3. Temporarily scale replicas **down** if each pod holds a large pool (more pods means more connections).
4. Raise SEV-1 if payments are failing. Do not restart the primary without the DBA.

### Scenario C: Downstream payment-gateway timeouts
Signs: gateway adapter 5xx or timeouts, payment success falls, but internal health is fine (Category C pattern).
1. Rolling back will **not** help unless the release changed the gateway call. Check the gateway's own status.
2. Enable the circuit breaker / degrade gracefully (queue payments for retry; idempotency keys protect against double charges).
3. Communicate honestly that a third party is affected; engage the vendor.
4. If the outage exceeds 30 minutes, start the regulatory workflow.

### Scenario D: Peak-hour degradation (salary days, festivals)
Signs: gradual latency rise at predictable high-traffic times, CPU above 70%.
1. Check autoscaling (HPA at CPU 70%); manually raise `minReplicas` if it lags.
2. Confirm no deployment is in progress (the blackout calendar should have blocked it); freeze if there is.
3. Shed load: tighten non-critical background jobs and reporting queries.

## 6. Regulatory notification
For any incident lasting more than **30 minutes** that affects customers, the Compliance liaison decides on and files the notification to the RBI. Cyber-security incidents have separate timelines (CERT-In requires reporting within hours, not days). **Confirm the current RBI and CERT-In deadlines and formats with Compliance**; this playbook does not replace their guidance. The Scribe's timeline is the evidence. The counter `novapay_incident_over_30m_total` tracks these.

## 7. Escalation and handover
Escalate up one level if: no progress in 15 minutes (SEV-1) or 30 minutes (SEV-2); the cause is unknown; a security compromise is suspected (CISO immediately); or data may be corrupted. Hand over to the next shift with a written summary: current state, actions tried, next steps, open risks.

---

# Appendix A: Communication templates
Replace the bracketed fields. Keep messages factual: what we know, what we do not, what we are doing, when the next update is.

## A1. Initial acknowledgement
**Internal (Slack #novapay-incidents)**
```
[SEV-<n>] <short title> - INVESTIGATING
Started: <time IST>   Incident Commander: <name>
Impact: <what users cannot do / % affected, or "unknown yet">
We are: <what is being done, e.g. rolling back release <version>>
Next update: <time IST, 30 min for SEV-1 / 60 min for SEV-2>
```
**External (status page)**
```
Investigating: Some customers may be experiencing <issue, e.g. delays with UPI payments>.
We are aware and working to resolve it. We will update you by <time IST>.
```

## A2. Regular update (every 30 min for SEV-1, hourly for SEV-2)
```
[SEV-<n>] <title> - UPDATE <number>
Status: <Investigating | Identified | Mitigating | Monitoring>
What we know: <facts only>
Impact now: <current, with numbers if possible>
Actions in progress: <list>
Next update: <time IST>
```
**External:** "Update: <plain-language status>. Payments made during this time <were / were not> affected. Next update by <time>."

## A3. Mitigation / rollback notice
```
[SEV-<n>] <title> - MITIGATED
At <time IST> we rolled back release <version> to <version>. Service metrics are returning to normal.
We are monitoring for <duration>. Customers who saw failed transactions should <instruction>.
```

## A4. Resolution notification (with impact summary)
```
[SEV-<n>] <title> - RESOLVED
Duration: <start> to <end IST> (<minutes> min)
Impact: <services>, approx. <number> customers, <number> failed / delayed transactions, <amount if relevant>
Cause (preliminary): <one sentence>
Customer action needed: <none / specific steps>
Follow-up: post-mortem to be published by <date>
```
**External:** "Resolved: <service> is operating normally since <time IST>. We apologise for the inconvenience. Any payment debited without a successful credit will be reversed automatically within <timeframe per policy>."

## A5. Regulator / executive summary (SEV-1, drafted by Compliance liaison)
```
Incident <ID> - technology incident report
Detected: <time>  Resolved: <time>  Duration: <minutes>
Systems and services affected: <list>   Customer impact: <numbers>
Root cause (preliminary): <text>   Immediate actions: <text>   Preventive actions: <text, dates, owners>
Data integrity / security impact: <none confirmed | details>
```

---

# Appendix B: Incident record (fill in during the incident)
| Field | Value |
|-------|-------|
| Incident ID / severity | |
| IC, Ops, Comms, Scribe | |
| Detected at / by | |
| Related release / change record | |
| Timeline (every action with timestamp) | |
| Decisions and who made them | |

---

# Appendix C: Post-mortem report template (blameless)
```
# Post-mortem: <title> (<Incident ID>)
Date: <date>   Severity: <SEV-n>   Author: <name>   Status: <draft | reviewed | closed>

## Summary
<3 sentences: what happened, impact, how it was resolved>

## Impact
Users/customers affected: <n>   Failed or delayed transactions: <n>   Duration: <min>
Revenue / regulatory impact: <text>   SLO / error budget consumed: <%>

## Timeline (IST)
| Time | Event |
| T+0  | Alert fired: <alert name> |
| T+30s | Triage, severity classified |
| T+2m | Communication sent |
| T+5m | Rollback initiated |
| ...  | ... |

## Root cause analysis
Direct cause: <text>
Contributing factors (5 whys): <list>
Which pipeline gate should have caught this, and why it did not: <text>

## What went well / what went badly / where we got lucky
<lists>

## Action items (tracked in Jira until closed)
| # | Action | Type (prevent / detect / mitigate) | Owner | Due date | Ticket |

## Lessons learned and pipeline improvements
<text>
```
Blameless means the review asks what in the system allowed this, never who is at fault.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

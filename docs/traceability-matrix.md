# Traceability matrix: brief requirement to repository

Maps requirements in the brief (Parts A to D) to where this repository answers them, with an honest status. **Covered** = answered in a document or file. **Partial** = answered in part. **Gap** = not yet done. Statuses for batches 1 to 3 are from the delivery notes, so re-check them when you do the Day 13 read-through.

| Brief requirement | Where | Status |
|-------------------|-------|--------|
| 8+ canonical stages with tools, thresholds, failure modes | [architecture.md](01-pipeline-architecture/architecture.md) | Covered |
| Blue-green and canary with statistical analysis | [deployment-strategies.md](02-deployment-strategies/deployment-strategies.md), `pipeline/scripts/canary_analysis.py` | Covered (script run on sample data) |
| 6+ compliance gates with thresholds, exceptions, audit format, RBI/PCI mapping | [compliance-gates.md](03-compliance-gates/compliance-gates.md) | Covered (Rego tests need to be run) |
| 3+ sample OPA policies | `pipeline/policies/` | Covered (not executed unless you ran `opa test`) |
| Expand-contract migration, compatibility matrix, rollback per phase | [migration-strategy.md](04-database-migration/migration-strategy.md) | Covered |
| 4-environment promotion, criteria, RBAC, config hierarchy, drift | [environment-promotion.md](05-environment-promotion/environment-promotion.md), `pipeline/helm/` | Covered |
| Category A (5+), B (4+), C triggers; 8-step workflow | [rollback-specification.md](06-rollback-specification/rollback-specification.md) | Covered |
| Prometheus alert rule examples | [rollback-rules.yaml](06-rollback-specification/alerts/rollback-rules.yaml) | Covered (not run through promtool) |
| 8-item pre-deployment checklist, decision trees | [deployment-runbook.md](../runbooks/deployment-runbook.md) | Covered |
| 4 severity levels, 7-step workflow, communication templates, post-mortem template | [incident-playbook.md](../runbooks/incident-playbook.md) | Covered |
| 4 DORA metrics, 15+ pipeline metrics, 3 dashboards, alert routing | [observability.md](08-observability/observability.md), [metrics-catalog.md](08-observability/metrics-catalog.md), `dashboards/` | Covered (dashboards are mockups) |
| Terraform modules, Helm templates, ArgoCD manifests | `pipeline/terraform/`, `pipeline/helm/novapay/templates/`, `pipeline/helm/argocd/` | Covered (Helm rendered; Terraform formatted only, not planned) |
| Friday 5 PM incident simulation with timestamps and post-mortem | [simulation](07-runbook-playbook/incident-simulation-friday-5pm.md), [post-mortem](07-runbook-playbook/post-mortem-INC-SIM-001.md) | Covered (tabletop) |
| TRC presentation, max 20 slides, PDF | [trc-presentation.pdf](../evidence/trc-presentation.pdf) | Covered |
| ERRATA.md with 3 errors | [ERRATA.md](../ERRATA.md) | Covered |
| Self-assessment and 5 reflections | [self-assessment.md](../evidence/self-assessment.md), [reflections.md](../evidence/reflections.md) | Covered |

## Part C "Your Simulation Scenario" prompts
| Case study | What the brief asks for | Where | Status |
|-----------|-------------------------|-------|--------|
| Knight Capital | Verification step: same image hash on all pods, fleet config consistency, automatic kill-switch on version mismatch, pre-deployment inventory of running vs target version | `pipeline/scripts/check-same-artifact.sh` (digest across environments), post-rollback "one image digest" check in the [playbook](../runbooks/incident-playbook.md) | **Partial**: no explicit per-pod hash check with kill-switch and no pre-deployment version inventory |
| YES Bank | Observability stack detecting UPI failures within 30 s, Prometheus rules, escalation, status-page automation, RBI notification for incidents over 30 minutes | [observability.md](08-observability/observability.md), [alertmanager.yml](08-observability/alerting/alertmanager.yml), [playbook section 6](../runbooks/incident-playbook.md) | **Partial**: detection time of 30 s and status-page automation not confirmed |
| Cloudflare | Configuration (WAF/security rule) change pipeline with canary, CPU/memory/latency baseline comparison, rollback independent of the deploy path, circuit breaker at CPU 80% | Independent rollback: [Deliverable 6](06-rollback-specification/rollback-specification.md) | **Gap**: no dedicated config-change pipeline for WAF rules |
| SBI YONO | Blackout calendar (salary days 1/7/15, month-end 28-31, festivals, RBI settlement, filings, campaigns), autoscaling at CPU 70% / queue depth 1000 / p99 300 ms, performance test within 48 h of a high-traffic window | [appproject.yaml](../pipeline/helm/argocd/appproject.yaml) (calendar), [hpa.yaml](../pipeline/helm/novapay/templates/hpa.yaml) (CPU 70%, queue depth) | **Partial**: p99 > 300 ms scaling trigger and the 48-hour pre-test rule are not implemented; festival dates are a template to fill in |

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

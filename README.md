# NovaPay Digital Bank - Zero-Downtime CI/CD Pipeline with Compliance Gates

**Author:** Manyashree U
**Track:** DevOps & Cloud Engineer (ZeTheta Project 1A)
**Status:** In progress - Deliverable 1 drafted

## Executive summary
_(max 250 words - written on Day 14)_

## Table of contents
| # | Deliverable | Location | Status |
|---|-------------|----------|--------|
| 1 | 8+ stage pipeline architecture | [docs/01-pipeline-architecture](docs/01-pipeline-architecture/architecture.md) | Drafted |
| 2 | Blue-green + canary strategies | [docs/02-deployment-strategies](docs/02-deployment-strategies/) | Pending |
| 3 | 6+ compliance gates | [docs/03-compliance-gates](docs/03-compliance-gates/) | Pending |
| 4 | Zero-downtime DB migration | [docs/04-database-migration](docs/04-database-migration/) | Pending |
| 5 | 4-environment promotion | [docs/05-environment-promotion](docs/05-environment-promotion/) | Pending |
| 6 | Automated rollback spec | [docs/06-rollback-specification](docs/06-rollback-specification/) | Pending |
| 7 | Runbook + incident playbook | [docs/07-runbook-playbook](docs/07-runbook-playbook/), [runbooks/](runbooks/) | Pending |
| 8 | DORA metrics + dashboards | [docs/08-observability](docs/08-observability/) | Pending |
| - | Errata (3 deliberate errors) | [ERRATA.md](ERRATA.md) | Pending |

## Architecture overview
_(embed final diagram on Day 14; draft: [pipeline-flow.mmd](docs/01-pipeline-architecture/diagrams/pipeline-flow.mmd))_

## Navigation guide
- `docs/` - the 8 deliverable documents
- `pipeline/` - GitHub Actions, Helm, Terraform, OPA/Kyverno policies, scripts
- `dashboards/` - Grafana JSON and wireframes
- `runbooks/` - deployment runbook and incident playbook
- `evidence/` - self-assessment, reflections, screenshots, test results, TRC deck

> **Note on workflow location:** the brief prescribes `pipeline/.github/workflows/`. GitHub only executes workflows from `.github/workflows/` at the repository root, so copy these files there to run them.

## Tools used
GitHub Actions, SonarQube, Trivy, OWASP ZAP, OPA/Conftest, Kyverno, Cosign, Checkov, ArgoCD, Argo Rollouts, Istio, Helm, Terraform, Prometheus, Grafana, Loki, OpenTelemetry.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

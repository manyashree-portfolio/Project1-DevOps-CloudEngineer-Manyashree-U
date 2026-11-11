# Self-assessment

**Author:** Manyashree U. The brief scores projects on a 1000-point rubric across seven dimensions but does not publish the weight of each dimension, so each is scored here out of 10 with a justification. The scores are deliberately conservative.

## Scores by dimension
| Dimension | Score /10 | Justification |
|-----------|-----------|---------------|
| Problem understanding | 8 | Every requirement from the task statement is mapped in the [traceability matrix](../docs/traceability-matrix.md), including the three deliberate errors. Part C simulation prompts are only partly covered (see the matrix) |
| Solution quality | 7 | Eight deliverables plus IaC, an incident simulation and a post-mortem. Weak points: policies, alert rules, the emergency rollback script and the Terraform have not been run against real systems |
| Research and analysis | 7 | Regulatory mappings follow the brief and were cross-checked for PCI numbering; the Cloudflare and gh-ost claims were checked against primary sources. RBI section numbers follow the brief and have **not** been checked against the Master Direction |
| Presentation and clarity | 7 | Consistent structure, cross-links, a README with navigation and a diagram, and a 16-slide TRC deck. Diagram PNG exports from Mermaid must be added by hand |
| Innovation and creativity | 6 | A "fast lane" to reach elite lead time, blackout calendar enforced by ArgoCD sync windows, and a promotion-evidence attestation proposal from the incident simulation. No Sandbox-mode topic is fully implemented |
| Feasibility and practicality | 6 | Realistic tools (all in the brief's free list). Costs, staffing and migration effort are covered at TRC-deck level only, and no part has been tested in a live cluster |
| CV alignment | 8 | Matches Docker, GitHub Actions, AWS, Terraform-style IaC and Prometheus/Grafana experience, extended to Kubernetes, Helm, ArgoCD, OPA and Istio, which are new to this project |

## Badge self-check (Section B4)
| Badge | Claim? | Why |
|-------|--------|-----|
| Pipeline Architect (50) | Yes | 8-stage architecture with diagram (check the PNG export is committed) |
| Security Guardian (50) | Yes | Gates with numeric thresholds; policy tests still to be run |
| Zero-Downtime Deployer (50) | Yes | Blue-green and canary specs, statistical analysis script run on synthetic data, rollback |
| DORA Elite (40) | Partly | Elite targets are designed; lead time reaches under one hour only on the fast lane (estimate about 56 minutes), and the standard path is about 1 hour 46 minutes |
| Runbook Author (40) | Yes | Runbook and playbook written to the 3 AM standard; not yet tested with a real on-call exercise |
| Crisis Commander (40) | Yes | Full decision timeline and post-mortem, as a tabletop |
| TRC Champion (50) | Partly | Presentation created; approval is simulated, as the badge allows |
| Error Hunter (45) | Yes, with a caveat | Three errors documented; the Part C item is the least certain (see [ERRATA.md](../ERRATA.md)) |
| Innovation Pioneer (35) | No | No Sandbox-mode topic is implemented in full |
| Database Guardian (40) | Yes | Expand-contract strategy with compatibility matrix |

## Deployment Velocity Audit (appendix of the brief)
| Metric | Target | Status |
|--------|--------|--------|
| Commit to production | under 2 hours | Standard path about 1 h 46 min (estimate); fast lane about 56 min (estimate) |
| Stage parallelisation | over 40% | See the timing table in [architecture.md](../docs/01-pipeline-architecture/architecture.md) and fill in the measured percentage |
| Developer feedback loop | under 10 minutes | See architecture.md; fill in |
| Automated steps | over 90% | See architecture.md; fill in |
| Rollback execution time | under 5 minutes (2 minutes for full points) | Design target under 2 minutes; Category A is under 60 seconds from trigger. Not measured on a real cluster |

## Known limitations
1. **Not executed on real systems:** Terraform (formatted only, no `plan`), OPA policies and tests, Prometheus rules (no `promtool`), `emergency-rollback.sh` (syntax-checked only).
2. **Dashboards are mockups** that use metric names which do not exist until exporters are built.
3. **Timings are estimates**, not measurements.
4. **Regulatory deadlines** (RBI, CERT-In) are deliberately left to Compliance to confirm.
5. **Part C simulation prompts:** the Cloudflare configuration pipeline and the 48-hour pre-test rule are open gaps (see the matrix).

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U. Replace any score you disagree with after your own review.

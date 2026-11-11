# Stage 8: Deployment & Verification

| Item | Specification |
|------|---------------|
| Tool | ArgoCD (GitOps), Argo Rollouts + Istio VirtualService (traffic shifting), Prometheus analysis, smoke/synthetic tests |
| Inputs | Signed image digest, Helm values, approvals |
| Outputs | Live release, verification report, deployment record (DORA data) |
| SLA | Standard canary <= 40 min to 100%; rollback <= 2 min |
| Regulatory mapping | RBI 4.2 (rollback), RBI 6.3 (continuity), PCI-DSS 6.5 |

## Strategy selection
| Change type | Strategy |
|-------------|----------|
| Stateless services (most changes) | Canary |
| Payment-settlement or schema-affecting releases | Blue-green (atomic switch, instant revert) |
| Configuration / WAF / routing rules | Same pipeline, canary to one region/AZ first |

## Canary profiles
| Profile | When | Phases | Duration to 100% |
|---------|------|--------|------------------|
| Standard (compressed) | Normal changes | 1-2% (10 min) -> 10% (10 min) -> 50% (15 min) -> 100% (5 min) | 40 min |
| Full (reference) | High-risk-tagged changes | 1-2% (15) -> 5-10% (30) -> 25-50% (60) -> 100% + 24 h bake | 105 min + bake |

Promotion is automatic only while error rate and p99 latency stay within limits (statistical tests detailed in Deliverable 2).

## Verification (Knight Capital lesson)
1. **Pre-deployment inventory:** record running versions per pod vs. target.
2. **Image-hash check:** every pod must report the same image digest (`scripts/verify-deployment.sh`).
3. **Config consistency:** ConfigMap/Secret versions identical across the fleet.
4. **Smoke tests:** health, login, balance enquiry, UPI collect in sandbox mode.
5. **Synthetic transactions:** every minute from outside the cluster.
6. **Kill-switch:** on any version mismatch or failed check the rollout aborts and traffic reverts automatically.

## Rollback triggers (summary - Deliverable 6)
Category A (< 60 s, automatic): 5xx > 5% for 60 s, 3 failed health checks, OOM kill, CrashLoopBackOff, DB pool exhaustion. Category B (< 15 min): p99 > 2x baseline for 5 min, burn rate > 10x, transaction success drop > 2%, CPU > 90% / memory > 85% for 5 min. Category C: human decision.

## Retry / skip logic
Rollout steps are not retried; an abort triggers rollback. Smoke tests retry once for transient network errors.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

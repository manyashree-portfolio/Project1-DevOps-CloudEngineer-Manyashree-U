# Pipeline-specific metrics catalogue (generated)

| # | Metric | Category | Definition | Source | Target | Alert |
|---|--------|----------|------------|--------|--------|-------|
| 1 | `novapay_ci_builds_total{result}` | Build | Build success rate = success / all builds | GitHub Actions webhook exporter | > 95% | < 90% over 1 d |
| 2 | `novapay_ci_test_flaky_total / novapay_ci_tests_total` | Build | Flaky test rate: tests that failed then passed on retry | Test report parser | < 1% | > 2% over 7 d |
| 3 | `topk(10, novapay_ci_test_flaky_total{test})` | Build | Top 10 flaky tests (quarantine candidates) | Test report parser | Zero tests flaky twice in 7 d | Any test flaky twice -> ticket |
| 4 | `novapay_ci_cache_hits_total / (hits + misses)` | Build | Gradle + Docker layer cache hit rate | Build logs | > 80% | < 60% over 1 d |
| 5 | `novapay_ci_pr_feedback_seconds` | Build | Developer feedback loop: PR push to first full result (p50) | GitHub API | < 10 min | p50 > 15 min |
| 6 | `novapay_ci_queue_seconds` | Build | Time a job waits for a runner (p90) | GitHub Actions | < 2 min | p90 > 5 min |
| 7 | `novapay_ci_coverage_ratio{type}` | Build | Line and branch coverage on main | JaCoCo / SonarQube | >= 80% line, >= 70% branch | Any drop of > 2 points |
| 8 | `novapay_gate_results_total{gate,result}` | Compliance | Gate pass rate per gate type (SAST, DAST, dependency, licence, policy, infra, SoD, provenance) | Gate audit records | > 90% first-time pass | < 80% for any gate |
| 9 | `novapay_scan_false_positives_total{tool} / novapay_scan_findings_total{tool}` | Compliance | False-positive rate per scanning tool (SonarQube, ZAP, Trivy) | Triage workflow | < 10% | > 20% (tune rules) |
| 10 | `novapay_vulns_open{severity}` | Compliance | Open vulnerabilities and median age by severity | Trivy / SonarQube | 0 Critical; High < 7 days | Any Critical |
| 11 | `novapay_exceptions_active{gate}` | Compliance | Active gate exceptions and those expiring within 7 days | Exception register | < 5 total | Any expired and still in use |
| 12 | `novapay_images_signed_ratio, novapay_sbom_coverage_ratio` | Compliance | Share of running images that are signed / have an SBOM | Kyverno + registry | 100% | < 100% |
| 13 | `novapay_audit_records_total / novapay_deployments_total` | Compliance | Audit-record completeness per production deployment | Audit store | 100% | < 100% |
| 14 | `novapay_sod_violations_total` | Compliance | Segregation-of-duties violations | SoD gate | 0 | Any |
| 15 | `novapay_deploy_duration_seconds` | Deployment | Rollout duration from first canary step to 100% | Argo Rollouts | < 40 min standard | > 60 min |
| 16 | `novapay_canary_outcomes_total{outcome}` | Deployment | Canary promotion success rate (promoted vs rolled back) | Argo Rollouts | > 95% promoted | < 90% over 30 d |
| 17 | `novapay_rollbacks_total{category,trigger}` | Deployment | Rollback frequency and trigger distribution | Rollback controller | < 5% of deployments | > 10% over 30 d |
| 18 | `novapay_deploy_blocked_total{reason}` | Deployment | Deployments held by the blackout calendar or deploy freeze | Pipeline | Informational | n/a |
| 19 | `novapay_drift_events_total{env}` | Deployment | Configuration drift events detected by ArgoCD | ArgoCD notifications | 0 in production | Any production drift |
| 20 | `novapay_approval_wait_seconds{stage}` | Deployment | Time spent waiting for a human approval | GitHub Environments | < 10 min | > 30 min |

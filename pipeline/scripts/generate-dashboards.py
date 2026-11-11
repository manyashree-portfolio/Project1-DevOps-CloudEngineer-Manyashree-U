#!/usr/bin/env python3
"""Generates the Deliverable 8 artefacts from ONE definition so names/queries never drift apart:
   dashboards/grafana/*.json (importable Grafana dashboards), dashboards/mockups/*.svg (wireframes),
   docs/08-observability/metrics-catalog.md (pipeline-specific metrics).  Run from the repo root."""
import json, os, html

DS = {"type": "prometheus", "uid": "${DS_PROMETHEUS}"}
R = lambda e: {"expr": e}

# ---------------------------------------------------------------- dashboards
# panel = (title, type, [(expr, legend)], unit, x, y, w, h, thresholds[(value,color)])
GREEN, YEL, RED = "green", "yellow", "red"
DASHBOARDS = {
 "engineering": dict(title="NovaPay - Engineering (real-time ops)", audience="SRE / on-call, refresh 30 s", panels=[
  ("Error ratio (1 m)", "timeseries", [("novapay:error_ratio:1m", "5xx ratio")], "percentunit", 0, 0, 8, 7, [(0, GREEN), (0.001, YEL), (0.05, RED)]),
  ("p99 latency vs 7-day baseline", "timeseries", [("novapay:p99_ms:5m", "p99"), ("novapay:p99_ms:baseline_7d", "baseline")], "ms", 8, 0, 8, 7, [(0, GREEN), (200, YEL), (500, RED)]),
  ("Payment success ratio", "timeseries", [("novapay_payment_success_ratio", "success")], "percentunit", 16, 0, 8, 7, [(0, RED), (0.97, YEL), (0.99, GREEN)]),
  ("Traffic by version (canary split)", "timeseries", [('sum by (destination_version) (rate(istio_requests_total{destination_service_name="novapay-app"}[1m]))', "{{destination_version}}")], "reqps", 0, 7, 8, 7, []),
  ("Firing alerts by category", "bargauge", [('count by (category) (ALERTS{alertstate="firing"})', "{{category}}")], "short", 8, 7, 4, 7, [(0, GREEN), (1, RED)]),
  ("Rollbacks (24 h)", "stat", [("sum(increase(novapay_rollbacks_total[24h]))", "rollbacks")], "short", 12, 7, 4, 7, [(0, GREEN), (1, YEL), (3, RED)]),
  ("Deploy freeze active", "stat", [("max(novapay_deploy_freeze_active)", "freeze")], "bool", 16, 7, 4, 7, [(0, GREEN), (1, RED)]),
  ("DB pool pending connections", "stat", [("sum(hikaricp_connections_pending{application=\"novapay-app\"})", "pending")], "short", 20, 7, 4, 7, [(0, GREEN), (5, YEL), (10, RED)]),
  ("Gate pass rate (24 h)", "bargauge", [('sum by (gate) (increase(novapay_gate_results_total{result="pass"}[1d])) / sum by (gate) (increase(novapay_gate_results_total[1d]))', "{{gate}}")], "percentunit", 0, 14, 12, 7, [(0, RED), (0.9, YEL), (0.95, GREEN)]),
  ("CI queue time p90", "timeseries", [("histogram_quantile(0.9, sum by (le) (rate(novapay_ci_queue_seconds_bucket[1h])))", "p90")], "s", 12, 14, 12, 7, [(0, GREEN), (120, YEL), (300, RED)]),
 ]),
 "management": dict(title="NovaPay - Management (DORA, weekly/monthly)", audience="CTO / VP Eng, refresh 5 min", panels=[
  ("Deployment frequency (per day)", "stat", [("novapay:deployment_frequency:1d", "deploys/day")], "short", 0, 0, 6, 6, [(0, RED), (1, YEL), (3, GREEN)]),
  ("Lead time for changes (p50)", "stat", [("novapay:lead_time_seconds:p50_7d", "p50")], "s", 6, 0, 6, 6, [(0, GREEN), (3600, YEL), (7200, RED)]),
  ("Change failure rate (30 d)", "stat", [("novapay:change_failure_rate:30d", "CFR")], "percentunit", 12, 0, 6, 6, [(0, GREEN), (0.05, YEL), (0.15, RED)]),
  ("MTTR (30 d)", "stat", [("novapay:mttr_seconds:30d", "MTTR")], "s", 18, 0, 6, 6, [(0, GREEN), (900, YEL), (3600, RED)]),
  ("Deployments per week (trend)", "timeseries", [('sum(increase(novapay_deployments_total{env="production",status="success"}[7d]))', "deploys / 7 d")], "short", 0, 6, 12, 7, []),
  ("Availability (30 d, synthetic)", "stat", [('avg_over_time(probe_success{job="novapay-synthetic"}[30d])', "availability")], "percentunit", 12, 6, 6, 7, [(0, RED), (0.9999, YEL), (0.99999, GREEN)]),
  ("Error budget remaining (99.99% SLO)", "gauge", [("1 - (sum(increase(istio_requests_total{destination_service_name=\"novapay-app\",response_code=~\"5..\"}[30d])) / sum(increase(istio_requests_total{destination_service_name=\"novapay-app\"}[30d]))) / 0.0001", "budget")], "percentunit", 18, 6, 6, 7, [(0, RED), (0.25, YEL), (0.5, GREEN)]),
  ("Open Critical/High vulnerabilities", "timeseries", [("sum by (severity) (novapay_vulns_open)", "{{severity}}")], "short", 0, 13, 12, 7, []),
  ("Rollbacks by trigger category", "piechart", [("sum by (category) (increase(novapay_rollbacks_total[30d]))", "{{category}}")], "short", 12, 13, 12, 7, []),
 ]),
 "regulatory": dict(title="NovaPay - Regulatory (audit-ready compliance)", audience="Compliance, RBI auditor, refresh 15 min", panels=[
  ("Gate results per release (7 d)", "table", [("sum by (gate, result) (increase(novapay_gate_results_total[7d]))", "")], "short", 0, 0, 12, 8, []),
  ("Audit-record completeness", "stat", [("sum(increase(novapay_audit_records_total[30d])) / sum(increase(novapay_deployments_total{env=\"production\"}[30d]))", "completeness")], "percentunit", 12, 0, 4, 8, [(0, RED), (0.999, GREEN)]),
  ("Segregation-of-duties violations", "stat", [("sum(increase(novapay_sod_violations_total[90d]))", "SoD")], "short", 16, 0, 4, 8, [(0, GREEN), (1, RED)]),
  ("Dual-approved production changes", "stat", [("sum(increase(novapay_prod_changes_dual_approved_total[90d])) / sum(increase(novapay_deployments_total{env=\"production\"}[90d]))", "dual approval")], "percentunit", 20, 0, 4, 8, [(0, RED), (1, GREEN)]),
  ("Active exceptions by gate", "bargauge", [("sum by (gate) (novapay_exceptions_active)", "{{gate}}")], "short", 0, 8, 8, 7, [(0, GREEN), (3, YEL), (6, RED)]),
  ("Exceptions expiring within 7 days", "stat", [("count(novapay_exception_expiry_timestamp_seconds - time() < 604800 and novapay_exception_expiry_timestamp_seconds > time())", "expiring")], "short", 8, 8, 4, 7, [(0, GREEN), (1, YEL)]),
  ("Signed images / SBOM coverage", "gauge", [("novapay_images_signed_ratio", "signed"), ("novapay_sbom_coverage_ratio", "SBOM")], "percentunit", 12, 8, 6, 7, [(0, RED), (1, GREEN)]),
  ("Incidents > 30 min (RBI notification candidates)", "stat", [("sum(increase(novapay_incident_over_30m_total[90d]))", "incidents")], "short", 18, 8, 6, 7, [(0, GREEN), (1, YEL)]),
  ("Change records: immutable store write failures", "stat", [("sum(increase(novapay_audit_write_failures_total[30d]))", "failures")], "short", 0, 15, 12, 6, [(0, GREEN), (1, RED)]),
 ]),
}

def grafana(uid, d):
    panels = []
    for i, (title, typ, targets, unit, x, y, w, h, th) in enumerate(d["panels"], 1):
        steps = [{"color": th[0][1] if th else "green", "value": None}] + [{"color": c, "value": v} for v, c in th[1:]]
        panels.append({"id": i, "title": title, "type": typ, "datasource": DS,
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [dict(R(e), legendFormat=l, refId=chr(65 + j)) for j, (e, l) in enumerate(targets)],
            "fieldConfig": {"defaults": {"unit": unit, "thresholds": {"mode": "absolute", "steps": steps}}, "overrides": []},
            "options": {}})
    return {"uid": f"novapay-{uid}", "title": d["title"], "tags": ["novapay", "mockup"], "timezone": "browser",
            "schemaVersion": 39, "version": 1, "refresh": "30s", "time": {"from": "now-6h", "to": "now"},
            "templating": {"list": [{"name": "DS_PROMETHEUS", "type": "datasource", "query": "prometheus", "label": "Prometheus"}]},
            "panels": panels}

def svg(d):
    S, W = 38, 24 * 38; H = (max(p[5] + p[7] for p in d["panels"]) + 3) * S
    cols = {"stat": "#dbeafe", "gauge": "#dcfce7", "bargauge": "#fef9c3", "timeseries": "#f1f5f9", "table": "#fae8ff", "piechart": "#ffedd5"}
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W+20} {H+20}" font-family="Arial,Helvetica,sans-serif">',
         f'<rect width="{W+20}" height="{H+20}" fill="#ffffff"/>',
         f'<text x="10" y="26" font-size="20" font-weight="bold" fill="#111">{html.escape(d["title"])}</text>',
         f'<text x="10" y="46" font-size="12" fill="#555">Wireframe - audience: {html.escape(d["audience"])}</text>']
    for title, typ, targets, unit, x, y, w, h, th in d["panels"]:
        X, Y, PW, PH = 10 + x * S, 60 + y * S, w * S - 6, h * S - 6
        o.append(f'<rect x="{X}" y="{Y}" width="{PW}" height="{PH}" rx="6" fill="{cols.get(typ, "#eee")}" stroke="#64748b"/>')
        o.append(f'<text x="{X+8}" y="{Y+18}" font-size="12" font-weight="bold" fill="#111">{html.escape(title)}</text>')
        o.append(f'<text x="{X+8}" y="{Y+PH-8}" font-size="10" fill="#555">[{typ}] {html.escape(unit)}</text>')
        if typ == "timeseries":
            o.append(f'<polyline fill="none" stroke="#2563eb" stroke-width="2" points="{X+10},{Y+PH-30} {X+PW*0.3},{Y+PH*0.55} {X+PW*0.5},{Y+PH*0.65} {X+PW*0.75},{Y+PH*0.4} {X+PW-10},{Y+PH*0.5}"/>')
        elif typ in ("stat", "gauge"):
            o.append(f'<text x="{X+PW/2}" y="{Y+PH/2+10}" font-size="26" text-anchor="middle" fill="#1e3a8a">123</text>')
        elif typ in ("bargauge", "table", "piechart"):
            for k in range(3):
                o.append(f'<rect x="{X+10}" y="{Y+30+k*22}" width="{(PW-20)*(0.9-0.2*k)}" height="12" rx="3" fill="#94a3b8"/>')
    return "\n".join(o + ["</svg>"])

# ---------------------------------------------------------------- metrics catalogue
# (metric, category, definition, source, target, alert)
CATALOG = [
 ("novapay_ci_builds_total{result}", "Build", "Build success rate = success / all builds", "GitHub Actions webhook exporter", "> 95%", "< 90% over 1 d"),
 ("novapay_ci_test_flaky_total / novapay_ci_tests_total", "Build", "Flaky test rate: tests that failed then passed on retry", "Test report parser", "< 1%", "> 2% over 7 d"),
 ("topk(10, novapay_ci_test_flaky_total{test})", "Build", "Top 10 flaky tests (quarantine candidates)", "Test report parser", "Zero tests flaky twice in 7 d", "Any test flaky twice -> ticket"),
 ("novapay_ci_cache_hits_total / (hits + misses)", "Build", "Gradle + Docker layer cache hit rate", "Build logs", "> 80%", "< 60% over 1 d"),
 ("novapay_ci_pr_feedback_seconds", "Build", "Developer feedback loop: PR push to first full result (p50)", "GitHub API", "< 10 min", "p50 > 15 min"),
 ("novapay_ci_queue_seconds", "Build", "Time a job waits for a runner (p90)", "GitHub Actions", "< 2 min", "p90 > 5 min"),
 ("novapay_ci_coverage_ratio{type}", "Build", "Line and branch coverage on main", "JaCoCo / SonarQube", ">= 80% line, >= 70% branch", "Any drop of > 2 points"),
 ("novapay_gate_results_total{gate,result}", "Compliance", "Gate pass rate per gate type (SAST, DAST, dependency, licence, policy, infra, SoD, provenance)", "Gate audit records", "> 90% first-time pass", "< 80% for any gate"),
 ("novapay_scan_false_positives_total{tool} / novapay_scan_findings_total{tool}", "Compliance", "False-positive rate per scanning tool (SonarQube, ZAP, Trivy)", "Triage workflow", "< 10%", "> 20% (tune rules)"),
 ("novapay_vulns_open{severity}", "Compliance", "Open vulnerabilities and median age by severity", "Trivy / SonarQube", "0 Critical; High < 7 days", "Any Critical"),
 ("novapay_exceptions_active{gate}", "Compliance", "Active gate exceptions and those expiring within 7 days", "Exception register", "< 5 total", "Any expired and still in use"),
 ("novapay_images_signed_ratio, novapay_sbom_coverage_ratio", "Compliance", "Share of running images that are signed / have an SBOM", "Kyverno + registry", "100%", "< 100%"),
 ("novapay_audit_records_total / novapay_deployments_total", "Compliance", "Audit-record completeness per production deployment", "Audit store", "100%", "< 100%"),
 ("novapay_sod_violations_total", "Compliance", "Segregation-of-duties violations", "SoD gate", "0", "Any"),
 ("novapay_deploy_duration_seconds", "Deployment", "Rollout duration from first canary step to 100%", "Argo Rollouts", "< 40 min standard", "> 60 min"),
 ("novapay_canary_outcomes_total{outcome}", "Deployment", "Canary promotion success rate (promoted vs rolled back)", "Argo Rollouts", "> 95% promoted", "< 90% over 30 d"),
 ("novapay_rollbacks_total{category,trigger}", "Deployment", "Rollback frequency and trigger distribution", "Rollback controller", "< 5% of deployments", "> 10% over 30 d"),
 ("novapay_deploy_blocked_total{reason}", "Deployment", "Deployments held by the blackout calendar or deploy freeze", "Pipeline", "Informational", "n/a"),
 ("novapay_drift_events_total{env}", "Deployment", "Configuration drift events detected by ArgoCD", "ArgoCD notifications", "0 in production", "Any production drift"),
 ("novapay_approval_wait_seconds{stage}", "Deployment", "Time spent waiting for a human approval", "GitHub Environments", "< 10 min", "> 30 min"),
]

def catalog_md():
    rows = ["| # | Metric | Category | Definition | Source | Target | Alert |", "|---|--------|----------|------------|--------|--------|-------|"]
    for i, (m, c, d, s, t, a) in enumerate(CATALOG, 1):
        rows.append(f"| {i} | `{m}` | {c} | {d} | {s} | {t} | {a} |")
    return "\n".join(rows) + "\n"

if __name__ == "__main__":
    os.makedirs("dashboards/grafana", exist_ok=True); os.makedirs("dashboards/mockups", exist_ok=True)
    for uid, d in DASHBOARDS.items():
        json.dump(grafana(uid, d), open(f"dashboards/grafana/{uid}-dashboard.json", "w"), indent=2)
        open(f"dashboards/mockups/{uid}-wireframe.svg", "w").write(svg(d))
    open("docs/08-observability/metrics-catalog.md", "w").write("# Pipeline-specific metrics catalogue (generated)\n\n" + catalog_md())
    print("generated", len(DASHBOARDS), "dashboards,", len(CATALOG), "metrics")

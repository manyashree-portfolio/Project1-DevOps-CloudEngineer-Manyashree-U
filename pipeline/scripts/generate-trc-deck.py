#!/usr/bin/env python3
"""Generate evidence/trc-presentation.pdf (Technology Risk Committee deck, max 20 slides).
Run from the repo root:  python pipeline/scripts/generate-trc-deck.py
Needs: pip install reportlab. Uses DejaVu Sans if present (fallback: Helvetica).
"""
import os, sys
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

W, H = 960, 540
NAVY, TEAL, AMBER, RED, GREEN = map(HexColor, ["#12263F", "#0E7C86", "#E8A317", "#C0392B", "#2E8B57"])
LIGHT, GREY, INK = map(HexColor, ["#EEF3F7", "#5B6B7A", "#1C2733"])

F, FB = "Helvetica", "Helvetica-Bold"
for d in ["/usr/share/fonts/truetype/dejavu", "C:/Windows/Fonts"]:
    a, b = os.path.join(d, "DejaVuSans.ttf"), os.path.join(d, "DejaVuSans-Bold.ttf")
    if os.path.exists(a) and os.path.exists(b):
        pdfmetrics.registerFont(TTFont("DV", a)); pdfmetrics.registerFont(TTFont("DVB", b))
        pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB")
        F, FB = "DV", "DVB"
        break

OUT = "evidence/trc-presentation.pdf"
os.makedirs("evidence", exist_ok=True)
c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("NovaPay zero-downtime CI/CD with compliance gates: TRC presentation")
c.setAuthor("Manyashree U")
state = {"n": 0}
TOTAL = 18


def sty(size=13, color=INK, bold=False, lead=None, align=0):
    return ParagraphStyle("s", fontName=FB if bold else F, fontSize=size, textColor=color,
                          leading=lead or size * 1.3, alignment=align)


def para(text, x, ytop, w, size=13, color=INK, bold=False):
    p = Paragraph(text, sty(size, color, bold))
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, ytop - h)
    return h


def bullets(items, x, ytop, w, size=14, gap=7):
    y = ytop
    for it in items:
        c.setFillColor(TEAL); c.circle(x + 4, y - size * 0.55, 2.6, fill=1, stroke=0)
        h = para(it, x + 16, y, w - 16, size)
        y -= h + gap
    return y


def new(title, sub=None):
    if state["n"]:
        c.showPage()
    state["n"] += 1
    c.setFillColor(white); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(NAVY); c.rect(0, H - 74, W, 74, fill=1, stroke=0)
    c.setFillColor(AMBER); c.rect(0, H - 78, W, 4, fill=1, stroke=0)
    c.setFillColor(white); c.setFont(FB, 24); c.drawString(36, H - 46, title)
    if sub:
        c.setFont(F, 12); c.setFillColor(HexColor("#BFD3E6")); c.drawString(36, H - 66, sub)
    c.setFillColor(GREY); c.setFont(F, 9)
    c.drawString(36, 16, "NovaPay Digital Bank | Technology Risk Committee | Manyashree U | design package, not a production system")
    c.drawRightString(W - 36, 16, f"{state['n']} / {TOTAL}")


def table(data, x, ytop, widths, size=11, head=NAVY, zebra=True, hl=None):
    rows = [[Paragraph(str(cell), sty(size, white if r == 0 else INK, r == 0)) for cell in row]
            for r, row in enumerate(data)]
    t = Table(rows, colWidths=widths)
    st = [("BACKGROUND", (0, 0), (-1, 0), head), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#C9D3DC")),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if zebra:
        for r in range(1, len(rows)):
            if r % 2 == 0:
                st.append(("BACKGROUND", (0, r), (-1, r), LIGHT))
    t.setStyle(TableStyle(st))
    _, h = t.wrap(sum(widths), 1000)
    t.drawOn(c, x, ytop - h)
    return h


def box(x, y, w, h, text, fill=TEAL, size=11, color=white, bold=True):
    c.setFillColor(fill); c.roundRect(x, y, w, h, 6, fill=1, stroke=0)
    p = Paragraph(text, sty(size, color, bold, align=1))
    _, ph = p.wrap(w - 10, 500)
    p.drawOn(c, x + 5, y + (h - ph) / 2)


def callout(text, x, y, w, h, fill=LIGHT, edge=AMBER, size=12):
    c.setFillColor(fill); c.rect(x, y, w, h, fill=1, stroke=0)
    c.setFillColor(edge); c.rect(x, y, 5, h, fill=1, stroke=0)
    p = Paragraph(text, sty(size))
    _, ph = p.wrap(w - 22, 500)
    p.drawOn(c, x + 14, y + (h - ph) / 2)


# 1 ---------------------------------------------------------------------------------------------
c.setFillColor(NAVY); c.rect(0, 0, W, H, fill=1, stroke=0)
state["n"] = 1
c.setFillColor(AMBER); c.rect(36, 330, 90, 5, fill=1, stroke=0)
c.setFillColor(white); c.setFont(FB, 38)
c.drawString(36, 270, "Zero-downtime CI/CD with")
c.drawString(36, 222, "compliance gates for NovaPay")
c.setFont(F, 17); c.setFillColor(HexColor("#BFD3E6"))
c.drawString(36, 176, "Proposal to the Technology Risk Committee")
c.setFont(F, 14)
c.drawString(36, 140, "Manyashree U | DevOps Lead (project scenario) | NovaPay Digital Bank, RBI-licensed")
c.setFont(F, 11); c.setFillColor(HexColor("#8FA9C2"))
c.drawString(36, 60, "A design and configuration package for a fictional bank. Estimates are labelled; items not run on real systems are labelled.")

# 2 ---------------------------------------------------------------------------------------------
new("Why change: the problem today", "Current state of NovaPay, from the scenario briefing")
rows = [["Area", "Today", "Target"],
        ["Deployment method", "Manual SSH to production", "Automated, signed, audited pipeline"],
        ["Deployment frequency", "Once every 2 weeks", "Multiple times per day"],
        ["Recovery (MTTR)", "4.5 hours", "Under 15 minutes"],
        ["Compliance scanning", "None; 17 RBI non-conformances in the last audit", "Automated gates with evidence for every change"],
        ["Database migrations", "Manual, 2 AM maintenance windows", "Zero-downtime expand-contract"],
        ["Observability", "Customers find the incidents", "Systems detect and page first"],
        ["Recent history", "3 production incidents in Q4 2025 traced to untested code", "Tested, scanned, verified before and after release"]]
table(rows, 36, H - 100, [190, 330, 370], 12)
callout("<b>Why it matters:</b> UPI handles over 12 billion transactions a month. Even a 30-second outage at peak affects millions of payments and draws NPCI and RBI scrutiny.", 36, 40, 888, 52)

# 3 ---------------------------------------------------------------------------------------------
new("What we are asking the Committee to approve", "One decision, four measurable outcomes")
bullets(["<b>Approve</b> the eight-stage pipeline architecture and its operating model (runbook, incident playbook, observability).",
         "<b>Approve</b> the compliance-gates design as the control framework for RBI Master Direction and PCI-DSS v4.0 change management.",
         "<b>Approve</b> a phased rollout inside the CTO's 90-day window, starting with non-production environments."], 36, H - 104, 888, 15, 10)
for i, (big, small) in enumerate([("< 2 h", "commit to production (from about 2 weeks)"), ("< 15 min", "recovery time (from 4.5 hours)"),
                                  ("99.999%", "availability design target (five nines)"), ("100%", "of changes with audit evidence")]):
    x = 36 + i * 226
    box(x, 120, 214, 120, f"<font size=30>{big}</font><br/><font size=11>{small}</font>", [TEAL, NAVY, TEAL, NAVY][i], 12)
callout("Reduction in recovery time: 4.5 h (270 min) to under 15 min is a drop of at least 94%. Same-day deploys replace a 14-day cycle.", 36, 48, 888, 48)

# 4 ---------------------------------------------------------------------------------------------
new("Solution architecture: eight stages, each with a gate", "Every stage can block; none is advisory")
stages = [("1 Source control", "signed commits,<br/>branch protection"), ("2 Build", "SemVer, lockfiles,<br/>80% line / 70% branch"),
          ("3 SAST", "SonarQube<br/>0 Critical, max 2 High"), ("4 Dependency +<br/>container scan", "Trivy, SBOM,<br/>licence check"),
          ("5 Integration +<br/>contract tests", "Pact, ephemeral<br/>namespaces"), ("6 DAST", "OWASP ZAP<br/>0 Critical/High"),
          ("7 Policy +<br/>compliance gates", "OPA, Kyverno,<br/>Cosign signing"), ("8 Deploy +<br/>verify", "blue-green or canary,<br/>smoke tests")]
for i, (t, s) in enumerate(stages):
    row, col = divmod(i, 4)
    x, y = 36 + col * 226, H - 210 - row * 150
    box(x, y + 50, 200, 52, t, NAVY, 13)
    para(s, x, y + 44, 200, 11, GREY)
    if col < 3:
        c.setStrokeColor(AMBER); c.setLineWidth(2); c.line(x + 202, y + 76, x + 224, y + 76)
callout("<b>Parallel work:</b> SAST and dependency/container scanning run side by side after the build; DAST waits for a running deployment. Full stage specifications and timings are in Deliverable 1.", 36, 40, 888, 52)

# 5 ---------------------------------------------------------------------------------------------
new("Speed without skipping gates", "Estimated commit-to-production time, design estimates not measurements")
rows = [["Path", "Estimate", "What differs"],
        ["Standard path", "about 1 h 46 min", "All gates, manual approvals, full soak. Meets the under-2-hour target"],
        ["Fast lane (pre-approved, low-risk changes)", "about 56 min", "Same mandatory gates, run in parallel; no manual approval wait because the change category was approved in advance"]]
table(rows, 36, H - 104, [250, 150, 488], 13)
bullets(["The brief's elite benchmark is a lead time under 1 hour; recent DORA reports describe the top band as under one day. We design for both.",
         "The fast lane <b>never skips</b> SAST, scanning, signing or policy gates; it removes waiting, not checking.",
         "Hotfixes are expedited, <b>not bypassed</b>: the incident simulation (slide 14) shows why this must be enforced by the cluster, not by convention."],
        36, H - 250, 888, 14, 9)
callout("<b>Honest caveat:</b> timings are estimates from stage budgets. They must be measured on real pipeline runs before the Committee relies on them.", 36, 44, 888, 48, edge=RED)

# 6 ---------------------------------------------------------------------------------------------
new("Zero-downtime deployment: blue-green and canary", "Traffic managed by Istio; both versions share a backward-compatible database")
rows = [["Canary phase", "Traffic", "Duration", "Success criteria", "If it fails"],
        ["Canary", "1-2%", "15 min", "Error rate < 0.1%, p99 < 200 ms", "Automatic rollback"],
        ["Early adopter", "5-10%", "30 min", "Error rate < 0.05%, no critical alerts", "Automatic rollback"],
        ["Expansion", "25-50%", "60 min", "All SLOs met, no degradation vs baseline", "Proceed or roll back"],
        ["Full rollout", "100%", "24 h bake", "Full SLO compliance for 24 hours", "Mark stable"]]
table(rows, 36, H - 100, [150, 90, 100, 360, 188], 12)
bullets(["<b>Blue-green:</b> two identical environments, atomic switch by VirtualService update, connection draining (30-60 s for HTTP, up to 5 min for settlement jobs), shared Redis sessions.",
         "<b>Statistics decide:</b> Welch's t-test for latency, chi-squared for error rates, 95% confidence, 7-day rolling baseline. A script implements this and was run on synthetic samples (healthy: promote, faulty: roll back)."],
        36, 225, 888, 13, 8)

# 7 ---------------------------------------------------------------------------------------------
new("Rollback guarantees", "Three categories; automation is the safety net that makes frequent release safe")
rows = [["Category", "Speed", "Examples of triggers", "Who acts"],
        ["A: immediate", "under 60 s from trigger", "5xx rate > 5% for 60 s; 3 failed health checks; OOM kill; CrashLoopBackOff; DB pool exhaustion (> 10 pending for 30 s)", "Nobody: fully automatic"],
        ["B: escalated", "under 15 min", "p99 > 2x baseline for 5 min; error-budget burn > 10x; payment success down > 2 points; CPU > 90% or memory > 85% for 5 min", "On-call has 10 min to acknowledge, then automatic"],
        ["C: manual", "human judgement", "Slow degradation, customer reports, retroactive compliance failure, downstream-dependency correlation", "Incident Commander"]]
table(rows, 36, H - 100, [120, 150, 428, 190], 12)
bullets(["<b>Rollback does not depend on the deployment path.</b> It runs inside the cluster, with a break-glass script that needs only kubectl (Cloudflare's 2019 outage lasted 27 minutes partly because rollback shared the broken path).",
         "<b>No schema rollback is ever needed</b>, because migrations use expand-contract.",
         "<b>Status:</b> rule definitions are valid YAML; they have not been run through promtool, and the break-glass script has only been syntax-checked."], 36, 230, 888, 13, 8)

# 8 ---------------------------------------------------------------------------------------------
new("Database changes without downtime", "Expand, migrate, contract: each phase deployable and reversible")
for i, (t, s, col) in enumerate([("EXPAND", "Add new columns/tables beside the old ones. App V(N-1) and V(N) both work. Roll back by dropping the new objects.", TEAL),
                                 ("MIGRATE", "Backfill in throttled batches; idempotent, retryable. Abort and alert the DBA if query latency rises by more than 20%.", NAVY),
                                 ("CONTRACT", "Remove old columns only after every service has moved. Forward-only, separate deployment, separate approval gate.", RED)]):
    x = 36 + i * 300
    box(x, 340, 280, 44, t, col, 16)
    callout(s, x, 220, 280, 110, size=12)
bullets(["Tools for PostgreSQL 16: pgroll or native expand-contract with <i>CREATE INDEX CONCURRENTLY</i>; compatibility matrix shows which app version works with each schema state.",
         "Designed for tables of 100 million rows or more; DBA approval gate and review checklist before any contract phase.",
         "Note: the brief's reference to gh-ost for this stack is an error (gh-ost is MySQL-only); see ERRATA.md."], 36, 195, 888, 13, 8)

# 9 ---------------------------------------------------------------------------------------------
new("Compliance gates mapped to RBI and PCI-DSS v4.0", "Automated, numeric, with exception paths and an audit record per gate")
rows = [["Gate", "Threshold", "On failure", "Regulatory mapping"],
        ["SAST (SonarQube)", "0 Critical, at most 2 High, 80% coverage", "Pipeline blocked", "PCI-DSS 6.2; RBI 5.1"],
        ["Dependency (Trivy)", "0 Critical CVE; SBOM generated", "Blocked; 72 h remediation window", "PCI-DSS 6.3; RBI 5.1, 7.2"],
        ["DAST (OWASP ZAP)", "0 Critical/High from OWASP Top 10", "Blocked; risk acceptance + TRC", "PCI-DSS 6.4, 11.4"],
        ["Licence", "No GPL / AGPL / SSPL dependencies", "Legal review", "RBI 7.2"],
        ["Policy (OPA / Kyverno)", "All Kubernetes policies pass; images signed; TLS 1.3", "Deployment rejected", "RBI 5.4; PCI-DSS 6.5"],
        ["Change control", "Dual approval; segregation of duties", "Promotion blocked", "RBI 4.2, 4.3; PCI-DSS 6.5"],
        ["Audit logging", "Immutable record for every gate run", "Blocked if not written", "RBI 6.1; PCI-DSS 10.2"]]
table(rows, 36, H - 100, [170, 290, 200, 228], 11)
callout("<b>Exceptions</b> are time-bound, named-approver, auto-expiring. <b>Correction:</b> penetration testing is PCI-DSS requirement 11.4 (11.3 is vulnerability scanning); the brief's table has this wrong, recorded in ERRATA.md. RBI section numbers follow the brief and need Compliance confirmation.", 36, 36, 888, 62, size=11)

# 10 --------------------------------------------------------------------------------------------
new("Four environments, one artefact", "The same signed image digest is promoted; only configuration changes")
envs = [("Development", "Synthetic data", "All developers", "Automatic on merge"), ("Staging", "Anonymised data", "Dev team + QA", "Automatic after dev gates"),
        ("Pre-production", "Masked subset", "QA + Compliance + DBA", "Tech Lead approval"), ("Production", "Real data", "SRE + Release Manager", "Dual approval")]
for i, e in enumerate(envs):
    x = 36 + i * 226
    box(x, 330, 200, 40, e[0], [TEAL, TEAL, NAVY, RED][i], 14)
    para(f"<b>Data:</b> {e[1]}<br/><b>Access:</b> {e[2]}<br/><b>Trigger:</b> {e[3]}", x, 322, 200, 12)
bullets(["<b>Segregation of duties:</b> production needs the Release Manager and the SRE Lead; developers cannot approve their own change.",
         "<b>Same image everywhere:</b> promoted by digest; a check fails the pipeline if two environments reference different digests. No environment-specific branches.",
         "<b>Config hierarchy:</b> base values, environment override, service override. Secrets come from a vault with 90-day (database) and 30-day (API key) rotation, never from Git.",
         "<b>Drift:</b> ArgoCD compares Git with the live cluster about every 3 minutes and notifies Slack."], 36, 235, 888, 13, 7)

# 11 --------------------------------------------------------------------------------------------
new("Supply-chain security and admission control", "A chain of trust from commit to running container")
for i, t in enumerate(["Signed commit", "Build + SBOM", "Scan", "Cosign signature", "Admission check (Kyverno)", "Running pod"]):
    x = 36 + i * 150
    box(x, 380, 136, 46, t, [NAVY, NAVY, NAVY, TEAL, RED, TEAL][i], 11)
    if i < 5:
        c.setStrokeColor(AMBER); c.setLineWidth(2); c.line(x + 138, 403, x + 148, 403)
bullets(["The cluster rejects any image that is unsigned or has no SBOM, so a bypassed pipeline cannot reach production quietly.",
         "Pods run as non-root with a read-only filesystem, dropped capabilities, resource limits and probes; default-deny network policies provide segmentation (PCI-DSS intent).",
         "Terraform provisions private-subnet clusters with encrypted Kubernetes secrets, audit logging and flow logs; the code is formatted and statically checked but has not been planned against a real account.",
         "<b>Gap found in simulation:</b> the cluster does not yet check that an image went through staging. Proposal: a signed promotion-evidence attestation (slide 14)."], 36, 350, 888, 13, 8)

# 12 --------------------------------------------------------------------------------------------
new("Observability and DORA metrics", "Systems detect incidents before customers do")
rows = [["DORA metric", "Elite target", "How measured"],
        ["Deployment frequency", "Multiple per day", "Production deployments per day"],
        ["Lead time for changes", "Under 1 hour (brief); fast lane about 56 min", "Commit timestamp to production deploy"],
        ["Change failure rate", "Under 5%", "(Rollbacks + hotfixes) / deploys"],
        ["MTTR", "Under 1 hour (internal target: 15 min)", "Detection to resolution"]]
table(rows, 36, H - 100, [220, 330, 338], 12)
bullets(["20 pipeline metrics (build success, flaky tests, cache hits, gate pass rate, false positives, deployment duration, rollback triggers and more).",
         "Three dashboards: Engineering (live operations), Management (weekly trends), Regulatory (audit-ready evidence). Alertmanager routes by severity to on-call, the SRE Lead and leadership.",
         "<b>Status:</b> dashboards are mockups that use metric names which exist only after exporters are built."], 36, 300, 888, 13, 8)

# 13 --------------------------------------------------------------------------------------------
new("Incident response", "Written for the on-call engineer at 3 AM")
rows = [["Severity", "Definition", "Response", "Escalation"],
        ["SEV-1", "Complete outage or data-integrity risk", "under 5 min", "CTO + CISO + VP Eng"],
        ["SEV-2", "Major degradation, over 10% of users", "under 15 min", "VP Eng + SRE Lead"],
        ["SEV-3", "Minor degradation, workaround exists", "under 1 hour", "SRE on-call + Tech Lead"],
        ["SEV-4", "Cosmetic, no user impact", "next business day", "Assigned engineer"]]
table(rows, 36, H - 100, [100, 380, 140, 268], 12)
para("<b>Seven steps:</b> detect, acknowledge and triage, mobilise and communicate, mitigate (roll back first if a release is recent), verify, resolve and close, blameless post-mortem.", 36, 292, 888, 14)
bullets(["Communication templates for every stage, update cadence of 30 min (SEV-1) and hourly (SEV-2).",
         "Incidents over 30 minutes that affect customers go to the Compliance liaison for RBI notification. <b>Deadlines and formats to be confirmed with Compliance</b>; they are not stated in the playbook."], 36, 240, 888, 13, 8)

# 14 --------------------------------------------------------------------------------------------
new("Stress test: the Friday 5 PM simulation", "Tabletop exercise; a hotfix skipped staging and three alerts fired together")
rows = [["Alert", "Handled by", "Result in the simulation"],
        ["HTTP 500 rate 12% (limit 5%)", "Category A rollback, automatic", "Traffic back on stable in about 55 s"],
        ["DB connection pool exhaustion", "Category A rollback, automatic", "Pool cleared after rollback"],
        ["Payment-gateway timeouts 35%", "Category C check: is it us or the vendor?", "Fell after rollback, so the cause was our change"]]
table(rows, 36, H - 100, [270, 300, 318], 12)
para("<b>Did the pipeline prevent it? No: it contained it.</b> Blast radius was one small canary and recovery needed no human. Gaps found:", 36, 330, 888, 14)
bullets(["No proof-of-staging check at admission: add a signed promotion-evidence attestation.",
         "Deployment-window check not enforced on every path (it was Friday, inside the 5-8 PM UPI peak): enforce it in the pipeline; remove direct deploy rights.",
         "No connection-pool threshold in the staging performance gate; no outbound-call timeout rule in review.",
         "These are proposals, not yet implemented controls."], 36, 290, 888, 13, 6)

# 15 --------------------------------------------------------------------------------------------
new("Key risks and mitigations", "What could still go wrong, and what we do about it")
rows = [["Risk", "Mitigation"],
        ["Gates slow developers down (VP Engineering's concern)", "Parallel stages, feedback inside minutes for early stages, fast lane for pre-approved changes; measure feedback time as a metric"],
        ["Pipeline becomes a single point of failure", "Break-glass rollback independent of CI and GitOps; read-only mode keeps running pods unaffected"],
        ["False positives block release", "Triaged exception workflow with time-bound approval and false-positive rate tracked per tool"],
        ["On-call burden (SRE team of 8)", "Category A automation removes first-response toil; runbook and playbook; alert tuning by severity"],
        ["Designs not proven in a live cluster", "Pilot in dev and staging first; run policy tests, rollback drill and Terraform plan before production"],
        ["Regulatory interpretation errors", "Mappings reviewed by Compliance and the external auditor before sign-off"]]
table(rows, 36, H - 100, [320, 568], 12)

# 16 --------------------------------------------------------------------------------------------
new("Evidence and current status", "What has been checked, and what has not")
c.setFillColor(GREEN); c.setFont(FB, 15); c.drawString(36, H - 106, "Checked")
bullets(["Canary analysis script run on synthetic data (promote and rollback cases)", "Helm chart renders; guard rails reject 'latest' and tag-only production images",
         "YAML and JSON files parse; Terraform is formatted; validation and link-check scripts included", "Cloudflare and gh-ost claims in the brief checked against published sources"],
        36, H - 120, 430, 12, 5)
c.setFillColor(RED); c.setFont(FB, 15); c.drawString(490, H - 106, "Not yet verified")
bullets(["OPA/Kyverno policy tests in a real cluster", "Prometheus rules through promtool", "Break-glass rollback script on a cluster",
         "Terraform plan and apply", "Grafana dashboards (mockups only)", "All timings (estimates)", "RBI section numbers and reporting deadlines"],
        490, H - 120, 434, 12, 5)
callout("The Committee is asked to approve a <b>design</b> and a <b>pilot plan</b>, not to treat these artefacts as production-ready.", 36, 40, 888, 46, edge=TEAL)

# 17 --------------------------------------------------------------------------------------------
new("Implementation plan inside the 90-day window", "Proposed phasing; durations are planning estimates")
rows = [["Phase", "Weeks", "Deliverables", "Exit criterion"],
        ["1 Foundation", "1-3", "Repository standards, signed commits, build and test stages, Terraform for dev and staging", "Dev pipeline green end to end"],
        ["2 Security gates", "3-6", "SAST, dependency, container, SBOM and signing; policy tests run in a test cluster", "Gates block known-bad samples"],
        ["3 Zero-downtime", "6-9", "Canary and blue-green, rollback automation, break-glass drill, expand-contract migration trial", "Rollback drill under 2 minutes"],
        ["4 Operations", "9-11", "Dashboards on real metrics, alert routing, runbook and incident exercises", "Tabletop and live game-day completed"],
        ["5 Production cut-over", "11-13", "Pre-prod soak, dual approval, first production release in an off-peak window", "Audit evidence pack accepted by Compliance"]]
table(rows, 36, H - 100, [150, 70, 460, 208], 12)
para("<b>Dependencies:</b> cloud account and budget approval, SonarQube/Artifactory licences, on-call rota agreement, Compliance reviewer time.", 36, 190, 888, 13)

# 18 --------------------------------------------------------------------------------------------
new("Questions we expect, and straight answers", "Q&A preparation notes by stakeholder")
rows = [["Who", "Likely question", "Answer"],
        ["CTO", "What is the business return?", "Same-day releases instead of fortnightly; recovery 4.5 h to under 15 min; audit evidence automatic. Cost figures need cloud and licence quotes (not yet gathered)"],
        ["CISO", "How do you stop a bypass?", "Cluster rejects unsigned images; simulation shows a gap (no proof of staging) with a concrete fix proposed"],
        ["Head of Compliance", "Can you prove each change was tested and approved?", "Immutable audit record per gate, exception records, dual approval log. Section numbers still need confirming"],
        ["VP Engineering", "Will developers hate it?", "Fast feedback early in the pipeline, fast lane for pre-approved changes, friction tracked as a metric"],
        ["RBI auditor", "Has any of this actually run?", "Partly: see slide 16. The package is a validated design plus a pilot plan"],
        ["SRE team", "Who is paged and when?", "Category A needs no human; Category B pages with a 10-minute window; playbook defines roles"]]
table(rows, 36, H - 100, [130, 250, 508], 11)

c.save()
print(f"wrote {OUT} ({state['n']} slides)")
if state["n"] != TOTAL:
    print(f"NOTE: update TOTAL to {state['n']}")

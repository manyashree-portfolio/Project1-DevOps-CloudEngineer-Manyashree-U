# Deliverable 7: Operational Runbook and Incident Playbook - Overview

**Author:** Manyashree U | The documents themselves live in [runbooks/](../../runbooks/) as the repository layout requires; this page explains the design and maps them to the brief.

| Document | Purpose |
|----------|---------|
| [Deployment runbook](../../runbooks/deployment-runbook.md) | Step-by-step production deployment, usable at 3 AM |
| [Incident playbook](../../runbooks/incident-playbook.md) | Classify, respond to and learn from incidents |

## 1. The "3 AM test"
A runbook passes if an on-call engineer who did not write it, is half asleep and has minimal context can use it correctly. Design choices that serve that test:
- **The emergency action is at the top**: "roll back in 60 seconds" is one link away from the first line, and rolling back never needs permission.
- **Every step names an exact command or screen** and the expected result; no "check that things look fine".
- **Decision trees, not prose** at each step: if X then do Y; the default for anything unclear is *stop and escalate* or *roll back*.
- **Hard stops are explicit**: any unchecked pre-deployment item means do not deploy.
- **Scripts do the risky work** ([emergency-rollback.sh](../../pipeline/scripts/emergency-rollback.sh), [verify-deployment.sh](../../pipeline/scripts/verify-deployment.sh), [check-deploy-window.sh](../../pipeline/scripts/check-deploy-window.sh)), so the human types one command.
- **Evidence is captured as you go** for the RBI and PCI audit trail.

## 2. Coverage of the brief
| Requirement | Where |
|-------------|-------|
| 8-item pre-deployment checklist with evidence requirements | [Runbook section 1](../../runbooks/deployment-runbook.md#1-pre-deployment-checklist-all-8-must-be-yes-evidence-attached-to-the-change-record) |
| Step-by-step execution with decision trees at each step | [Runbook section 2](../../runbooks/deployment-runbook.md#2-execution-procedure-canary) |
| Post-deployment verification with expected outcomes | [Runbook section 3](../../runbooks/deployment-runbook.md#3-post-deployment-verification) |
| 4-level severity classification with response times | [Playbook section 1](../../runbooks/incident-playbook.md#1-severity-classification) |
| 7-step incident response workflow | [Playbook section 3](../../runbooks/incident-playbook.md#3-seven-step-incident-response-workflow) |
| Communication templates for each stage and severity | [Playbook appendix A](../../runbooks/incident-playbook.md#appendix-a-communication-templates) |
| Post-mortem report template (timeline, root cause, tracked actions) | [Playbook appendix C](../../runbooks/incident-playbook.md#appendix-c-post-mortem-report-template-blameless) |

## 3. How the runbook ties to the other deliverables
- **Rollback triggers and workflow:** [Deliverable 6](../06-rollback-specification/rollback-specification.md) defines when rollback is automatic; the runbook says what the human does.
- **Alerts link to the playbook:** each rollback alert carries a `runbook` annotation ([rules](../06-rollback-specification/alerts/rollback-rules.yaml)), so the page opens the right procedure.
- **Environment promotion and gates:** checklist items 1-4 verify the evidence from [Deliverable 5](../05-environment-promotion/environment-promotion.md) and [Deliverable 3](../03-compliance-gates/compliance-gates.md).
- **Database safety:** checklist item 5 and Scenario B rely on [Deliverable 4](../04-database-migration/migration-strategy.md).
- **Dashboards:** the Engineering dashboard in [Deliverable 8](../08-observability/observability.md) is the screen used in every step.

## 4. Keeping the documents alive
Runbooks that are written and forgotten fail (the YES Bank lesson). Policy: a tabletop exercise each quarter (the Friday 5 PM simulation in the incident playbook scenarios), the runbook is updated within 5 working days of any incident or process change, and the SRE Lead signs off the version used for each production release (pre-prod to production criterion).

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

# Stage 6: Dynamic Analysis & DAST

| Item | Specification |
|------|---------------|
| Tool | OWASP ZAP (Automation Framework, API scan) |
| Inputs | Staging deployment URL, OpenAPI spec |
| Outputs | ZAP JSON/HTML/SARIF report, findings ticket |
| SLA | <= 12 min scoped scan on each build; full active scan nightly |
| Regulatory mapping | PCI-DSS 6.4, 11.3; RBI 5.1 |

## Configuration
| Parameter | Value |
|-----------|-------|
| Scan types | Passive baseline on every build; active scan on staging (never production) |
| API scanning | OpenAPI/Swagger import so every endpoint is exercised |
| Authentication | Authenticated scan using test users; credentials fetched from Vault with a 1 h TTL, never stored in Git |
| Blocking threshold | 0 Critical / High findings mapped to OWASP Top 10 (2021) |
| Medium | Ticket with 30-day SLA; Low/Info reported |
| False-positive workflow | Rule suppressed in `zap-rules.tsv` only with a justification, owner and 30-day expiry, approved by a Security Champion; reviewed monthly |

## Failure modes and remediation
Pipeline blocked at promotion to pre-prod. Remediation links point to the OWASP cheat sheet for the finding. Exception: risk acceptance form + Technology Risk Committee (TRC) approval.

## Retry / skip logic
Retry once if the target is unreachable. Skipped only on documentation-only changes (path filter), never on code changes.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

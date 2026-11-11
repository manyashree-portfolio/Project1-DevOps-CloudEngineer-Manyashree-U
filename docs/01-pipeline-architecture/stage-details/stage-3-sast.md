# Stage 3: Static Analysis & SAST

| Item | Specification |
|------|---------------|
| Tool | SonarQube Server (LTA release) with a custom "NovaPay Banking" quality profile; Semgrep optional second opinion |
| Inputs | Source, JaCoCo XML from Stage 2 |
| Outputs | Quality gate result, SARIF report, auto-created ticket on failure |
| SLA | <= 5 min (runs in parallel with Stages 4 and 5) |
| Regulatory mapping | PCI-DSS 6.2 (bespoke software security), RBI 5.1 (vulnerability assessment) |

## Quality gate thresholds
| Metric | Threshold | Applies to |
|--------|-----------|------------|
| Blocker / Critical issues | 0 | New code |
| High issues | <= 2 | New code |
| Line coverage | >= 80% | New code |
| Technical debt ratio | <= 5% | New code |
| Duplicated lines | <= 3% | New code |
| Security hotspots reviewed | 100% | New code |
| Trend gate | No worsening of reliability/security rating vs. main | Overall |

## Custom banking rules
- PII (account number, PAN, Aadhaar, email, mobile) must never be logged or written to exceptions.
- Weak crypto banned: MD5, SHA-1 for security use, DES, AES-ECB, static IVs.
- SQL built by string concatenation = Critical (use parameterised queries / JPA).
- Hard-coded secrets, keys or connection strings = Blocker.
- Insecure deserialisation and permissive CORS / TLS configuration = High.

## Failure modes and remediation
Pipeline blocked and a ticket is auto-created with the rule key, file and line. The developer fixes the finding or marks a hotspot as "Safe" with justification (reviewed by a Security Champion). Exception: CISO approval within 24 h, auto-expiring.

## Retry / skip logic
Retry once on analysis-server timeout. Never skipped.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

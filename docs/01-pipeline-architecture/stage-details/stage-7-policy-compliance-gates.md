# Stage 7: Policy & Compliance Gates

| Item | Specification |
|------|---------------|
| Tool | OPA/Conftest (pipeline-time), Kyverno (cluster admission), Checkov (IaC), Cosign (signing/verification) |
| Inputs | Rendered Helm manifests, Terraform plan, SBOM, scan results, approval records |
| Outputs | Signed image + SBOM attestation, JSON audit record per gate, immutable change record |
| SLA | <= 3 min |
| Regulatory mapping | RBI 4.2, 4.3, 5.4, 6.1; PCI-DSS 6.3, 6.5, 10.2, 12.6 |

## Gates (summary - full definitions in Deliverable 3)
| # | Gate | Tool | Pass condition |
|---|------|------|----------------|
| 1 | SAST | SonarQube | 0 Critical, <= 2 High, >= 80% coverage |
| 2 | DAST | OWASP ZAP | 0 Critical/High (OWASP Top 10) |
| 3 | Dependency | Trivy | 0 Critical CVE, SBOM generated |
| 4 | Licence | Trivy / FOSSA | No GPL/AGPL/SSPL |
| 5 | Kubernetes policy | OPA / Kyverno | No privileged containers, limits set, signed image, non-root, no `latest` |
| 6 | Infrastructure | Checkov | No critical IaC misconfiguration, encryption on, TLS 1.3 |
| 7 | Segregation of duties | Custom OPA | Author, approver and deployer are three distinct identities |

## Image signing and admission
Image is signed with Cosign after all scan gates pass; the SBOM is attached as an attestation. Kyverno `verifyImages` rejects any unsigned or wrongly signed image at admission, so the chain of trust runs commit -> build -> scan -> signature -> running container.

## Audit record (JSON)
Each gate writes `{gate, run_id, commit_sha, image_digest, actor, result, thresholds, findings_summary, exception_id, timestamp, regulatory_refs}` to an append-only store (S3 Object Lock, WORM), supporting RBI 6.1 and PCI-DSS 10.2.

## Failure modes and remediation
Each failure returns remediation text, blocks promotion and (where applicable) starts the time-bound exception workflow (CISO 24 h, legal sign-off, dual approval, tech-lead exemption as defined in Deliverable 3).

## Retry / skip logic
Deterministic policy checks are not retried. No skipping; overrides exist only through the audited exception workflow.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

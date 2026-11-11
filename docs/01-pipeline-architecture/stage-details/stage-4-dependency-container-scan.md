# Stage 4: Dependency & Container Scanning

| Item | Specification |
|------|---------------|
| Tool | Trivy (filesystem + image), SBOM in CycloneDX 1.5 JSON, Trivy licence scanner (or FOSSA/ScanCode), Cosign for base-image provenance; Grype optional cross-check |
| Inputs | Image tarball, lock files |
| Outputs | Vulnerability report, SBOM (archived 7 years with the change record), licence report |
| SLA | <= 6 min (parallel) |
| Regulatory mapping | PCI-DSS 6.3, RBI 7.2 (third-party risk) |

## Thresholds
| Check | Rule |
|-------|------|
| Critical CVE (CVSS >= 9.0) | **Block**, 0 tolerated |
| High CVE | **Block if CVSS > 8.0** and a fix is available |
| Medium/Low | Reported; ticket if older than 30 days |
| SBOM | Must be generated and attached to the image as a Cosign attestation |
| Licences | GPL / AGPL / SSPL denied; MIT, Apache-2.0, BSD allowed; unknown = legal review |
| Base image | Only from the approved internal registry, pinned by digest, signature verified |

## Failure modes and remediation
| Failure | Remediation |
|---------|-------------|
| Vulnerable dependency | Upgrade to the fixed version (report lists it); if none, apply a time-bound exception |
| Denied licence | Replace the library; legal sign-off if unavoidable |
| Unapproved / unsigned base image | Rebase on the golden image |

Exception: 72 h remediation window with a risk acceptance, auto-expiring entry in `.trivyignore` (each entry carries CVE, owner, expiry date).

## Retry / skip logic
Retry once if the vulnerability DB download fails (DB is mirrored internally for availability). Never skipped.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

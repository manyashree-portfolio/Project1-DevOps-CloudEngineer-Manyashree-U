# Stage 1: Source Control & Trigger

| Item | Specification |
|------|---------------|
| Tool | GitHub Enterprise (branch protection, rulesets, CODEOWNERS), GitHub Actions triggers |
| Inputs | Developer commit (signed), pull request, tag |
| Outputs | Verified commit SHA, pipeline run ID, change record seed (author, reviewer, timestamp) |
| SLA | Trigger latency <= 30 s; commit verification <= 1 min |
| Regulatory mapping | RBI 4.2 (change management), RBI 4.3 (segregation of duties), PCI-DSS 6.2 / 6.5 |

## Branching model
Trunk-based. Feature branches live < 24 h and merge to `main` through short-lived PRs. `release/*` branches are cut only for emergency back-ports. `hotfix/*` branches follow the expedited path below.

## Configuration
| Parameter | Value |
|-----------|-------|
| Branch protection on `main` | PR required; direct push blocked; force-push and deletion blocked; linear history |
| Required reviewers | 1 approval (2 for paths owned by `payments/`, `auth/`, `ledger/` via CODEOWNERS) |
| Self-approval | Disabled - PR author cannot approve own PR (segregation of duties) |
| Signed commits | Mandatory (GPG or SSH); unverified commits rejected |
| Required status checks | `verify-commits`, `build`, `sast`, `dependency-scan`, `integration-tests` |
| Triggers | `push` (main, release/**, hotfix/**), `pull_request` (main), `workflow_dispatch` |
| Monorepo | `paths:` filters per service so only changed services build; shared libs trigger all dependants |

## Failure modes and remediation
| Failure | Behaviour | Remediation |
|---------|-----------|-------------|
| Unsigned / unverified commit | Pipeline blocked at `verify-commits` | Re-sign: `git rebase --exec 'git commit --amend --no-edit -S' origin/main`, force-push the feature branch |
| Missing review / CODEOWNER approval | Merge blocked | Request review from the owning team |
| Direct push to main | Rejected by ruleset | Open a PR |

## Retry / skip logic
No retry on policy failures (deterministic). Webhook delivery failures retried by GitHub; `workflow_dispatch` allows a manual re-run. **No stage skipping.**

## Hotfix path (expedited, not bypassed)
`hotfix/*` runs every gate. Differences: highest concurrency priority (never cancelled), compressed canary profile, and mandatory incident ID in the PR description. The only gate that may be shortened is the long DAST active scan (replaced by the passive baseline scan); this requires a CISO-approved exception that auto-expires after 24 h.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

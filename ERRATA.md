# ERRATA: Deliberate errors found in the project brief

**Author:** Manyashree U | The brief (Section A8) says it contains exactly three deliberate technical errors, one each in Part A, Part C and Part D. Each is listed with where it appears, why it is wrong, the correction, and how it was checked.

## Error 1 (Part A): PCI-DSS requirement 11.3 is not "Penetration Testing"
- **Where:** Section A.4.2 (PCI-DSS v4.0 table) lists "11.3 Penetration Testing". Day 1 also lists "11.3".
- **Why it is wrong:** In PCI-DSS v4.0, requirement **11.3** covers **vulnerability scans** (internal and external), and **11.4** covers **penetration testing**.
- **Correction:** Map the "DAST integration + periodic pen-test schedule" control to **11.4 (penetration testing)** and map the dependency and container vulnerability scans to **11.3**. The compliance gates document in this repo cites both numbers for this reason.
- **Check:** from my knowledge of the v4.0 requirement list; please confirm against the PCI SSC document library before relying on it.

## Error 2 (Part C): Cloudflare outage figures
- **Where:** Case Study 3 (Cloudflare, July 2019).
- **What the brief itself says:** a note under the case study says an earlier version gave the duration as **21 minutes** and that the actual duration was **27 minutes**. The copy of the brief I worked from already says 27, which is correct.
- **Second discrepancy:** the case study says the faulty rule caused Cloudflare to drop "approximately 50% of global HTTP traffic". Cloudflare's own post-mortem says traffic **dropped by 82% at its worst**.
- **Correction:** duration **27 minutes** (13:42 to 14:09 UTC on 2 July 2019); traffic drop **up to 82%** at the worst point.
- **Check:** Cloudflare's post-mortem "Details of the Cloudflare outage on July 2, 2019" (blog.cloudflare.com), plus secondary write-ups that agree on 27 minutes and 82%.
- **Note on certainty:** the brief's own note points at the duration. I am also flagging the 50% figure as a likely error. If only one is the intended error, the other is a bonus catch.

## Error 3 (Part D): gh-ost is a MySQL tool, and it is not trigger-based
- **Where:** Day 6 says to study "gh-ost trigger-based replication approach" for a PostgreSQL 16 stack (the stack is given in Section B2).
- **Why it is wrong:** two things. (1) **gh-ost works only with MySQL**, so it cannot be used on PostgreSQL. (2) gh-ost is **triggerless**: it reads the binary log, unlike pt-online-schema-change, which uses triggers.
- **Correction:** for PostgreSQL use **pgroll** (as Section A.3.3 itself says), or expand-contract with `CREATE INDEX CONCURRENTLY` and batched backfills. If the trigger-based approach is the one to study, that is **pt-online-schema-change** (MySQL).
- **Check:** the gh-ost project README describes it as a triggerless online schema migration tool for MySQL that uses the binary log.
- **In this repo:** [migration strategy](docs/04-database-migration/migration-strategy.md) uses expand-contract with PostgreSQL-compatible tooling.

## Other inconsistencies noticed (not counted among the three)
These are observations, listed so a reviewer can see they were noticed. I am less sure that any of them is deliberate.

| # | Where | Observation | How handled |
|---|-------|-------------|-------------|
| 4 | A.2.2 stage 4 vs A.4.3 Dependency gate | Stage 4 says High findings block if CVSS **> 8.0**; the gate table says the pipeline is blocked if CVSS **>= 9.0**. Those are different cut-offs (and 9.0 and above is the Critical band) | Gate definitions state the thresholds explicitly and use one rule |
| 5 | A5 DORA table | "Elite" lead time is shown as **under 1 hour**. Recent DORA reports use **under one day** for the top band | Observability document explains the difference and designs a "fast lane" to reach about 56 minutes |
| 6 | Part F vs D2 | Part F says repository name `Project1A-DevOps&CloudEngineer-[First]-[Last]`; Part D2 says `DOC5A-CICD-Pipeline-[Name]` | Confirm with the mentor which one applies |
| 7 | Part D Day 14 | Mentions "AI Attribution Blocks" but I could not find their required format in the brief | A short attribution block is included in each document; confirm the format with the mentor |

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U. Error 1 and the PCI numbering should be checked against the standard before submission.

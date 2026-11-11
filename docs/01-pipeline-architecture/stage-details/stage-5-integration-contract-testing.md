# Stage 5: Integration & Contract Testing

| Item | Specification |
|------|---------------|
| Tool | Testcontainers, Pact + Pact Broker (`can-i-deploy`), openapi-diff, k6, Flyway |
| Inputs | Built image, DB migration scripts |
| Outputs | Test reports, contract verification results, performance baseline |
| SLA | <= 12 min (parallel with Stages 3 and 4) |
| Regulatory mapping | RBI 4.2 (testing before change), PCI-DSS 6.5 |

## Configuration
| Area | Specification |
|------|---------------|
| Isolation | Ephemeral namespace per run (`it-<pr>-<runid>`) with 2 h TTL, auto-deleted on completion |
| Dependencies | PostgreSQL 16, Redis 7, RabbitMQ 3.13 (same versions as production) |
| Database | Flyway migrations applied from scratch **and** upgraded from the previous release; tests run against app V(N-1) and V(N) for expand-contract safety |
| Test data | Synthetic only, seeded by fixture scripts |
| Contract tests | Consumer-driven (Pact); `can-i-deploy` must return true for every consumer |
| API compatibility | openapi-diff against the last released spec; breaking change = fail |
| Performance baseline | k6 smoke at 1x load; p99 < 500 ms recorded as baseline (full 2x load test runs in staging) |

## Failure modes and remediation
Contract broken -> provider fixes or negotiates with the consumer team via the Pact Broker. Breaking API change -> version the endpoint (`/v2`). Migration failure -> fix script; never edit an applied migration.

## Retry / skip logic
Flaky tests are retried once; a test that passes on retry is flagged "flaky" and counted in the flaky-test-rate metric. Two flaky flags in 7 days quarantine the test and open a ticket. Never skipped.

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

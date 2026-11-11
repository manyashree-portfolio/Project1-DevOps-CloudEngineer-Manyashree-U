# Stage 2: Build & Compilation

| Item | Specification |
|------|---------------|
| Tool | Gradle 8.x, JDK 21 (Temurin), Docker Buildx, JaCoCo |
| Inputs | Verified commit SHA |
| Outputs | Container image tarball (not yet pushed), JaCoCo reports, SemVer version, build metadata |
| SLA | <= 8 min cold, <= 5 min with cache |
| Regulatory mapping | PCI-DSS 6.2 (secure build), RBI 4.2 |

## Configuration
| Parameter | Value |
|-----------|-------|
| Reproducibility | Gradle dependency locking (`gradle.lockfile`) + dependency verification (`verification-metadata.xml`); build fails if the lock file is stale |
| Docker build | Multi-stage Dockerfile (JDK build stage, distroless/JRE runtime stage), BuildKit layer cache |
| Unit tests | 100% must pass; zero tolerated failures |
| Coverage gate (JaCoCo) | >= 80% line, >= 70% branch |
| Build matrix | JDK 21 / linux/amd64 for production; linux/arm64 added only if Graviton nodes are used |

## Versioning
`MAJOR.MINOR.PATCH+build.<sha7>.<timestamp>.<runid>` for artefact metadata, e.g. `2.4.1+build.a1b2c3d.20261110T0912Z.8841`.
Docker tags cannot contain `+`, so the image carries two tags: `2.4.1-build.a1b2c3d` and `sha-<fullsha>`. **`latest` is never used.**

## Failure modes and remediation
| Failure | Remediation |
|---------|-------------|
| Compile / unit test failure | Fix code; PR blocked |
| Coverage below threshold | Add tests; `check-coverage.sh` prints the uncovered classes |
| Stale lock file | Run `./gradlew dependencies --write-locks` and commit |

## Retry / skip logic
One automatic retry for infrastructure errors only (runner lost, cache restore failure). Test failures are never retried (prevents masking flaky tests - flaky tests are quarantined and tracked, see Deliverable 8).

> **AI Attribution:** Drafted with AI assistance (Claude, Anthropic). Author review: Manyashree U.

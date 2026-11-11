#!/usr/bin/env bash
# Usage: run-perf-test.sh --load-factor 2 --p99-ms 500
set -euo pipefail
LOAD=2; P99=500
while [[ $# -gt 0 ]]; do case "$1" in --load-factor) LOAD="$2"; shift 2;; --p99-ms) P99="$2"; shift 2;; *) exit 2;; esac; done
k6 run --env LOAD_FACTOR="$LOAD" --threshold "http_req_duration{p(99)}<${P99}" tests/perf/payments.js

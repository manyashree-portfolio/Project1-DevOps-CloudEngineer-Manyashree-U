#!/usr/bin/env bash
# "Same artefact, different config": every environment must reference the IDENTICAL image digest.
# Usage: check-same-artifact.sh overlays/staging/values.yaml overlays/pre-prod/values.yaml overlays/production/values.yaml
set -euo pipefail
[ $# -ge 2 ] || { echo "usage: $0 <values-file> <values-file> [...]"; exit 2; }
digests=$(python3 - "$@" <<'PY'
import sys, yaml
for f in sys.argv[1:]:
    d = yaml.safe_load(open(f)) or {}
    print(f"{f}\t{(d.get('image') or {}).get('digest', '')}")
PY
)
echo "$digests"
uniq_count=$(echo "$digests" | cut -f2 | sort -u | wc -l)
if echo "$digests" | cut -f2 | grep -qE '^$'; then echo "::error::An environment has no image digest"; exit 1; fi
if [ "$uniq_count" -ne 1 ]; then echo "::error::Environments reference different artefacts - promotion blocked"; exit 1; fi
echo "OK: all environments run the same artefact"

#!/usr/bin/env bash
# Usage: verify-deployment.sh <namespace> <image-ref>
# Knight Capital lesson: every pod must run the same image digest; abort + rollback if not.
set -euo pipefail
NS="${1:?namespace}"; IMAGE="${2:?image ref}"
digests=$(kubectl -n "$NS" get pods -l app=novapay-app -o jsonpath='{range .items[*]}{.status.containerStatuses[0].imageID}{"\n"}{end}' | sort -u)
count=$(echo "$digests" | grep -c . || true)
echo "Distinct image digests in $NS: $count"; echo "$digests"
if [[ "$count" -ne 1 ]]; then
  echo "::error::Version mismatch detected across pods - triggering kill-switch (rollback)"
  kubectl argo rollouts abort novapay-app -n "$NS" || true
  exit 1
fi

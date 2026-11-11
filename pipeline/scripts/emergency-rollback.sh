#!/usr/bin/env bash
# Break-glass rollback - independent of the CI/CD pipeline and the registry (Cloudflare lesson):
# needs only kubectl + the argo-rollouts plugin + out-of-band cluster credentials.
# Usage: emergency-rollback.sh canary|bluegreen [reason]       (blue-green: set TARGET_COLOUR=blue|green, default blue)
set -euo pipefail
MODE="${1:?mode: canary|bluegreen}"; REASON="${2:-unspecified}"
NS=novapay-prod; APP=novapay-app; TARGET_COLOUR="${TARGET_COLOUR:-blue}"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "$(ts) [rollback] $*"; }

log "START mode=$MODE reason='$REASON' operator=${USER:-unknown}"

# 1. FREEZE: stop further promotions and stop ArgoCD from re-applying the bad desired state while we revert
kubectl -n "$NS" create configmap deploy-freeze --from-literal=reason="$REASON" --from-literal=since="$(ts)" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n argocd patch application novapay-production --type merge -p '{"spec":{"syncPolicy":{"automated":null}}}' || log "WARN: could not pause auto-sync"

# 2. ROLLBACK (seconds)
case "$MODE" in
  canary)
    PHASE=$(kubectl -n "$NS" get rollout "$APP" -o jsonpath='{.status.phase}')
    log "rollout phase: $PHASE"
    if [[ "$PHASE" == "Healthy" ]]; then
      kubectl argo rollouts undo "$APP" -n "$NS"        # already fully promoted: go back one revision
    else
      kubectl argo rollouts abort "$APP" -n "$NS"       # in progress: canary weight -> 0, stable keeps traffic
    fi ;;
  bluegreen)
    OTHER=$([[ "$TARGET_COLOUR" == "blue" ]] && echo green || echo blue)
    log "reverting VirtualService to $TARGET_COLOUR"
    kubectl -n istio-system get virtualservice novapay-app -o json | python3 -c "
import json,sys
vs=json.load(sys.stdin)
for r in vs['spec']['http']:
    if r.get('name')=='primary':
        for d in r['route']:
            d['weight']=100 if '$TARGET_COLOUR' in d['destination']['host'] else 0
json.dump(vs,sys.stdout)" | kubectl apply -f - ;;
  *) echo "unknown mode"; exit 2 ;;
esac

# 3. VERIFY every pod serves the same version, then smoke-test
"$(dirname "$0")/verify-deployment.sh" "$NS" "${EXPECTED_IMAGE:-$(kubectl -n "$NS" get rollout "$APP" -o jsonpath='{.spec.template.spec.containers[0].image}')}" || log "WARN: verification failed - escalate to SRE Lead"

log "DONE. Next: notify (comms template), open incident, commit a Git revert so GitOps matches reality, then re-enable auto-sync."

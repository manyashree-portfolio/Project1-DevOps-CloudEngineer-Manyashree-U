#!/usr/bin/env bash
# Usage: gitops-promote.sh <env> <image-tag>
# Updates the image tag in the GitOps repo values file; ArgoCD syncs it. Only configuration changes per env.
set -euo pipefail
ENVIRONMENT="${1:?env: staging|pre-prod|production}"; TAG="${2:?image tag}"
: "${GITOPS_TOKEN:?deploy token required (separate from developer credentials)}"
git clone "https://x-access-token:${GITOPS_TOKEN}@github.com/novapay/k8s-manifests.git" /tmp/gitops
cd /tmp/gitops
yq -i ".image.tag = \"${TAG}\"" "overlays/${ENVIRONMENT}/values.yaml"
git config user.name "novapay-deploy-bot"; git config user.email "deploy-bot@novapay.example"
git commit -am "deploy(${ENVIRONMENT}): ${TAG} [run ${GITHUB_RUN_ID:-local}]"
git push origin HEAD:main

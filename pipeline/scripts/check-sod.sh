#!/usr/bin/env bash
# Segregation of duties: PR author, approver and deploy actor must be three distinct identities.
set -euo pipefail
AUTHOR="${PR_AUTHOR:?}"; APPROVER="${PR_APPROVER:?}"; DEPLOYER="${GITHUB_ACTOR:?}"
if [[ "$AUTHOR" == "$APPROVER" || "$AUTHOR" == "$DEPLOYER" || "$APPROVER" == "$DEPLOYER" ]]; then
  echo "::error::Segregation-of-duties violation (author=$AUTHOR approver=$APPROVER deployer=$DEPLOYER)"; exit 1
fi
echo "SoD verified"

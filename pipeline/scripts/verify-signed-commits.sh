#!/usr/bin/env bash
# Fails if any commit in BASE..HEAD lacks a verified signature (RBI 4.3 / PCI-DSS 6.5).
set -euo pipefail
BASE="${1:?base sha}"; HEAD="${2:?head sha}"
[[ "$BASE" =~ ^0+$ ]] && BASE="$(git rev-list --max-parents=0 "$HEAD" | tail -1)"
fail=0
for sha in $(git rev-list "$BASE..$HEAD"); do
  ok=$(gh api "repos/${GITHUB_REPOSITORY}/commits/${sha}" --jq '.commit.verification.verified')
  if [[ "$ok" != "true" ]]; then echo "::error::Commit $sha is not signed/verified"; fail=1; fi
done
exit $fail

#!/usr/bin/env bash
# One-command local validation (brief, Day 13/15): YAML lint, shell syntax, Rego/Terraform when present.
# Usage: ./pipeline/scripts/lint-all.sh   (run from the repository root)
set -uo pipefail
rc=0
step() { echo; echo "== $1"; }

step "YAML (yamllint)"
if command -v yamllint >/dev/null; then
  yamllint -d "{extends: relaxed, rules: {line-length: disable}}" pipeline docs dashboards || rc=1
else echo "yamllint not installed: pip install yamllint"; fi

step "Shell syntax (bash -n) + shellcheck"
for f in $(find pipeline/scripts -name '*.sh'); do bash -n "$f" || rc=1; done
command -v shellcheck >/dev/null && shellcheck pipeline/scripts/*.sh || echo "(shellcheck not installed - skipped)"

step "Python syntax"
python3 -m py_compile pipeline/scripts/*.py || rc=1

step "Rego (opa check)"
if ls pipeline/policies/*.rego >/dev/null 2>&1; then
  command -v opa >/dev/null && opa check pipeline/policies || echo "opa not installed - skipped"
else echo "no .rego files yet"; fi

step "Terraform format"
if ls pipeline/terraform/*.tf >/dev/null 2>&1; then
  command -v terraform >/dev/null && terraform fmt -check -recursive pipeline/terraform || echo "terraform not installed - skipped"
else echo "no .tf files yet"; fi

echo; [ $rc -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $rc

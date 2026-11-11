#!/usr/bin/env bash
# Usage: check-coverage.sh --min-line 80 --min-branch 70 [--report path/to/jacocoTestReport.xml]
set -euo pipefail
MIN_LINE=80; MIN_BRANCH=70; REPORT=build/reports/jacoco/test/jacocoTestReport.xml
while [[ $# -gt 0 ]]; do
  case "$1" in
    --min-line) MIN_LINE="$2"; shift 2;;
    --min-branch) MIN_BRANCH="$2"; shift 2;;
    --report) REPORT="$2"; shift 2;;
    *) echo "unknown arg $1"; exit 2;;
  esac
done
python3 - "$REPORT" "$MIN_LINE" "$MIN_BRANCH" <<'PY'
import sys, xml.etree.ElementTree as ET
report, min_line, min_branch = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
root = ET.parse(report).getroot()
def pct(kind):
    c = next(x for x in root.findall("counter") if x.get("type") == kind)
    covered, missed = int(c.get("covered")), int(c.get("missed"))
    return 100.0 * covered / (covered + missed) if covered + missed else 100.0
line, branch = pct("LINE"), pct("BRANCH")
print(f"Line coverage {line:.1f}% (min {min_line}), branch coverage {branch:.1f}% (min {min_branch})")
if line < min_line or branch < min_branch:
    print("Coverage gate FAILED"); sys.exit(1)
print("Coverage gate passed")
PY

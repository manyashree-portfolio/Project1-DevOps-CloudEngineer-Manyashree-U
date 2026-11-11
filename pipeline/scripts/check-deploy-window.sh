#!/usr/bin/env bash
# Blocks production deploys in peak hours (10-12, 17-20 IST), on salary days (1,7,15), month-end (28-31).
set -euo pipefail
export TZ=Asia/Kolkata
H=$(date +%-H); D=$(date +%-d)
if { [ "$H" -ge 10 ] && [ "$H" -lt 12 ]; } || { [ "$H" -ge 17 ] && [ "$H" -lt 20 ]; }; then
  echo "::error::Peak-hour deployment blackout"; exit 1; fi
case "$D" in 1|7|15|28|29|30|31) echo "::error::Blackout day $D (salary/month-end)"; exit 1;; esac
echo "Deployment window OK"

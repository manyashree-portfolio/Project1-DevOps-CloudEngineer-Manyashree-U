#!/usr/bin/env python3
"""Canary statistical analysis for NovaPay (Deliverable 2).

Compares canary vs. baseline using:
  * Welch's t-test (one-sided: is canary latency WORSE?)
  * chi-squared test on error counts (one-sided: is canary error rate WORSE?)
  * resource utilisation ratio
and combines them into a weighted composite score (0-100).

Exit codes: 0 = promote, 2 = hold (extend current phase), 1 = rollback.

Input JSON (file passed as --input):
{
  "baseline_latency_ms": [..samples from rolling 7-day baseline..],
  "canary_latency_ms":   [..samples..],
  "baseline_errors": 120, "baseline_requests": 400000,
  "canary_errors": 9,     "canary_requests": 8000,
  "cpu_ratio": 1.04, "mem_ratio": 1.02
}
"""
import argparse, json, math, statistics, sys

try:
    from scipy import stats as sp
except ImportError:          # fall back to a normal approximation (fine for n > 30)
    sp = None

ALPHA = 0.05                  # 95% confidence
MIN_LATENCY_DELTA_PCT = 10.0  # practical significance: ignore statistically-significant but trivial shifts
MIN_ERROR_DELTA_ABS = 0.0002  # 0.02 percentage points
MIN_SAMPLES = 100
WEIGHTS = {"latency": 0.35, "errors": 0.45, "resources": 0.20}
PROMOTE_AT, HOLD_AT = 90.0, 70.0


def welch_one_sided(base, canary):
    n1, n2 = len(base), len(canary)
    m1, m2 = statistics.fmean(base), statistics.fmean(canary)
    v1, v2 = statistics.variance(base), statistics.variance(canary)
    se = math.sqrt(v1 / n1 + v2 / n2)
    t = (m2 - m1) / se if se else 0.0
    df = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    p = sp.t.sf(t, df) if sp else 0.5 * math.erfc(t / math.sqrt(2))
    return t, df, p, (m2 - m1) / m1 * 100.0


def chi2_one_sided(e1, n1, e2, n2):
    """2x2 chi-squared (errors/successes x baseline/canary). One-sided: canary rate > baseline rate."""
    total, errs = n1 + n2, e1 + e2
    if errs == 0 or errs == total:
        return 0.0, 1.0, 0.0
    chi2 = 0.0
    for obs, row, col in ((e1, errs, n1), (n1 - e1, total - errs, n1), (e2, errs, n2), (n2 - e2, total - errs, n2)):
        exp = row * col / total
        chi2 += (obs - exp) ** 2 / exp
    p_two = math.erfc(math.sqrt(chi2 / 2))        # chi-squared, 1 degree of freedom
    r1, r2 = e1 / n1, e2 / n2
    p_one = p_two / 2 if r2 > r1 else 1 - p_two / 2
    return chi2, p_one, r2 - r1


def analyse(d):
    out = {"checks": {}}
    n_canary = len(d["canary_latency_ms"])
    if n_canary < MIN_SAMPLES or d["canary_requests"] < MIN_SAMPLES:
        return {"verdict": "hold", "reason": "insufficient samples", "score": None, **out}
    # Bonferroni: 3 metric families are tested per phase
    alpha = ALPHA / 3

    t, df, p_lat, delta_pct = welch_one_sided(d["baseline_latency_ms"], d["canary_latency_ms"])
    lat_sig = p_lat < alpha
    lat_score = 0 if (lat_sig and delta_pct > MIN_LATENCY_DELTA_PCT) else 50 if lat_sig else 100
    out["checks"]["latency"] = {"t": round(t, 3), "df": round(df, 1), "p_one_sided": p_lat, "delta_pct": round(delta_pct, 2), "score": lat_score}

    chi2, p_err, delta_abs = chi2_one_sided(d["baseline_errors"], d["baseline_requests"], d["canary_errors"], d["canary_requests"])
    err_sig = p_err < alpha
    err_score = 0 if (err_sig and delta_abs > MIN_ERROR_DELTA_ABS) else 50 if err_sig else 100
    out["checks"]["errors"] = {"chi2": round(chi2, 3), "p_one_sided": p_err, "delta_abs": delta_abs, "score": err_score}

    worst = max(d.get("cpu_ratio", 1.0), d.get("mem_ratio", 1.0))
    res_score = 100 if worst <= 1.10 else 50 if worst <= 1.25 else 0
    out["checks"]["resources"] = {"worst_ratio": worst, "score": res_score}

    score = sum(WEIGHTS[k] * out["checks"][k]["score"] for k in WEIGHTS)
    hard_fail = lat_score == 0 or err_score == 0
    verdict = "rollback" if hard_fail or score < HOLD_AT else "hold" if score < PROMOTE_AT else "promote"
    return {"verdict": verdict, "score": round(score, 1), **out}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="JSON file with baseline/canary samples")
    args = ap.parse_args()
    result = analyse(json.load(open(args.input)))
    print(json.dumps(result, indent=2, default=float))
    sys.exit({"promote": 0, "hold": 2, "rollback": 1}[result["verdict"]])

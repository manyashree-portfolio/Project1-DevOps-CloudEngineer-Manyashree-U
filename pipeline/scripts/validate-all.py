#!/usr/bin/env python3
"""Validate every config file in the repo (Day 13 and Day 15 checks in the brief).

Always runs (needs only Python + PyYAML): YAML parse, JSON parse.
Runs if the tool is on PATH, otherwise prints SKIP: terraform fmt, opa check, helm lint.
Usage (from repo root):  python pipeline/scripts/validate-all.py
Exit code 1 if anything fails.
"""
import json, os, shutil, subprocess, sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML missing: pip install pyyaml")

SKIP_DIRS = {".git", "node_modules", ".terraform", "templates"}  # Helm templates hold {{ }} and are not plain YAML
failures = 0


def ok(msg):
    print("PASS ", msg)


def bad(msg):
    global failures
    failures += 1
    print("FAIL ", msg)


def walk(exts):
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(exts):
                yield os.path.join(root, f)


for path in walk((".yaml", ".yml")):
    if os.sep + "templates" + os.sep in path:
        continue
    try:
        with open(path, encoding="utf-8") as fh:
            list(yaml.safe_load_all(fh))
        ok(path)
    except Exception as e:  # noqa: BLE001
        bad(f"{path}: {str(e).splitlines()[0]}")

for path in walk((".json",)):
    try:
        with open(path, encoding="utf-8") as fh:
            json.load(fh)
        ok(path)
    except Exception as e:  # noqa: BLE001
        bad(f"{path}: {e}")


def run(label, cmd, cwd=None):
    exe = shutil.which(cmd[0])
    if not exe:
        print(f"SKIP  {label} ({cmd[0]} not on PATH)")
        return
    r = subprocess.run([exe] + cmd[1:], cwd=cwd, capture_output=True, text=True)
    if r.returncode == 0:
        ok(label)
    else:
        bad(f"{label}\n{(r.stdout + r.stderr).strip()[:600]}")


if os.path.isdir("pipeline/terraform"):
    run("terraform fmt -check", ["terraform", "fmt", "-check", "-recursive"], cwd="pipeline/terraform")
if os.path.isdir("pipeline/policies"):
    opa = "opa" if shutil.which("opa") else (".\\opa.exe" if os.path.exists("opa.exe") else "opa")
    if opa != "opa":
        r = subprocess.run([opa, "check", "pipeline/policies"], capture_output=True, text=True)
        ok("opa check") if r.returncode == 0 else bad("opa check\n" + (r.stdout + r.stderr)[:600])
    else:
        run("opa check", ["opa", "check", "pipeline/policies"])
if os.path.isdir("pipeline/helm/novapay") and os.path.exists("pipeline/helm/novapay/Chart.yaml"):
    run("helm lint", ["helm", "lint", "pipeline/helm/novapay"])

print("\nFAILED" if failures else "\nALL CHECKS PASSED", f"({failures} failure(s))" if failures else "")
sys.exit(1 if failures else 0)

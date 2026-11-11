#!/usr/bin/env python3
"""Check that every relative Markdown link points to a file or folder that exists
(Day 15: "Check all Markdown links"). Run from the repo root:
    python pipeline/scripts/check-links.py
Ignores http(s)/mailto links and anchors-only links. Strips #anchors from file links.
"""
import os, re, sys

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
missing = 0
checked = 0
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".terraform"}]
    for f in files:
        if not f.endswith(".md"):
            continue
        path = os.path.join(root, f)
        in_code = False
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if line.strip().startswith("```"):
                    in_code = not in_code
                if in_code:
                    continue
                for target in LINK.findall(line):
                    if re.match(r"^(https?:|mailto:|#)", target):
                        continue
                    t = target.split("#")[0]
                    if not t:
                        continue
                    checked += 1
                    dest = os.path.normpath(os.path.join(root, t))
                    if not os.path.exists(dest):
                        missing += 1
                        print(f"BROKEN  {path}:{n} -> {target}")
print(f"\n{checked} relative links checked, {missing} broken")
sys.exit(1 if missing else 0)

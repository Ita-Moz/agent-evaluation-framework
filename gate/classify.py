#!/usr/bin/env python3
"""Deterministic risk classifier for an agent-authored diff.

Outputs a risk tier (low/medium/high) from the changed files and diff size only.
No model is involved. Exits 0 and prints a JSON result, plus a machine-readable
"TIER=<tier>" line for GitHub Actions ::set-output style capture.
"""
import json
import os
import re
import subprocess
import sys

SENSITIVE_PATTERNS = [
    r"(^|/)(auth|authorization|authentication)(/|\.|$)",
    r"(^|/)(crypto|cryptography)(/|\.|$)",
    r"(^|/)(secret|secrets|credential|token|password)(/|\.|$)",
    r"(^|/)(payment|billing|invoice|checkout)(/|\.|$)",
    r"(^|/)(permission|iam|rbac|acl)(/|\.|$)",
    r"(^|/)(cert|tls|ssl|keystore)(/|\.|$)",
    r"(^|/)migrations?(/|\.|$)",
    r"(^|/)key(store|ring)?(/|\.|$)",
]

SENSITIVE_RE = re.compile("|".join(SENSITIVE_PATTERNS), re.IGNORECASE)

INFRA_PATTERNS = [
    r"(^|/)(\.github/workflows|ci)(/|\.|$)",
    r"(^|/)(Dockerfile|docker-compose.*|Makefile|Jenkinsfile)(/|$)",
    r"(^|/)(pyproject\.toml|package\.json|Cargo\.toml|go\.mod|requirements.*)(/|$)",
]

INFRA_RE = re.compile("|".join(INFRA_PATTERNS), re.IGNORECASE)


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout.strip()


def base_ref() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    if os.environ.get("GITHUB_BASE_SHA"):
        return os.environ["GITHUB_BASE_SHA"]
    return "origin/main"


def changed_files(base: str) -> list[str]:
    out = run(["git", "diff", "--name-only", f"{base}...HEAD"])
    return [f for f in out.splitlines() if f]


def diff_lines(base: str) -> int:
    out = run(["git", "diff", "--numstat", f"{base}...HEAD"])
    total = 0
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            total += int(parts[0]) + int(parts[1])
    return total


def classify(files: list[str], lines: int) -> dict:
    sensitive = [f for f in files if SENSITIVE_RE.search(f)]
    infra = [f for f in files if INFRA_RE.search(f)]
    n_files = len(files)

    if sensitive or lines > 1000 or n_files > 50:
        tier = "high"
    elif lines > 100 or n_files > 10 or infra:
        tier = "medium"
    else:
        tier = "low"

    return {
        "tier": tier,
        "changedFiles": n_files,
        "diffLines": lines,
        "sensitiveFiles": sensitive,
        "infraFiles": infra,
    }


def main() -> None:
    base = base_ref()
    files = changed_files(base)
    lines = diff_lines(base)
    result = classify(files, lines)
    print(json.dumps(result, indent=2))
    print(f"TIER={result['tier']}")


if __name__ == "__main__":
    main()

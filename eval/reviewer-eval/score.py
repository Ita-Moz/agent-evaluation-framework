#!/usr/bin/env python3
"""Score a reviewer verdict against seeded bugs (precision/recall/F1).

Usage:
  score.py <scenario-dir> <agent-or-file>

`<agent-or-file>` is either an agent name (reads `<scenario>/<agent>.raw.txt`)
or a path to a raw verdict file.
"""
import json
import os
import re
import sys

REQUIRED = ("risk", "verdict", "confidence", "evidence", "issues", "unverified")


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s).lower()


def extract_verdict(text: str):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        obj = json.loads(text[start : end + 1])
    except Exception:
        return None
    if not all(k in obj for k in REQUIRED):
        return None
    return obj


def loc_file(location: str):
    location = location.strip()
    m = re.match(r"^(.*?)(?::(\d+))?$", location)
    return (norm(m.group(1)), m.group(2) if m.group(2) else None)


def issue_matches_seed(issue: dict, seed: dict) -> bool:
    f_i, l_i = loc_file(issue.get("location", ""))
    f_s, l_s = loc_file(seed.get("location", ""))
    file_match = f_i == f_s
    if not file_match and f_s:
        base_s = f_s.rstrip("/").split("/")[-1]
        file_match = bool(base_s) and (base_s in f_i)
    if not file_match:
        return False
    if l_i and l_s and l_i == l_s:
        return True
    if issue.get("severity") == seed.get("severity"):
        return True
    d_i = norm(issue.get("detail", ""))
    d_s = norm(seed.get("detail", ""))
    if d_i and d_s and (d_i in d_s or d_s in d_i):
        return True
    return False


def score_verdict(seeds: list, issues: list):
    """Return (tp, fp, fn, precision, recall, f1, used_issues, used_seeds)."""
    used_seeds: set[int] = set()
    used_issues: set[int] = set()
    tp = 0
    for i_idx, issue in enumerate(issues):
        for s_idx, seed in enumerate(seeds):
            if s_idx in used_seeds:
                continue
            if issue_matches_seed(issue, seed):
                used_seeds.add(s_idx)
                used_issues.add(i_idx)
                tp += 1
                break
    fp = len(issues) - tp
    fn = len(seeds) - tp
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return tp, fp, fn, precision, recall, f1, used_issues, used_seeds


def main() -> None:
    scen = sys.argv[1]
    target = sys.argv[2]
    if target.endswith(".raw.txt"):
        raw_path = target
        label = os.path.basename(target).removesuffix(".raw.txt")
    else:
        raw_path = os.path.join(scen, f"{target}.raw.txt")
        label = target

    with open(os.path.join(scen, "seeds.json"), "r", encoding="utf-8") as fh:
        seeds = json.load(fh)["bugs"]

    with open(raw_path, "r", encoding="utf-8") as fh:
        verdict = extract_verdict(fh.read())

    if verdict is None:
        print(f"[{label}] verdict unparseable (no valid JSON object found)")
        print(f"  precision=n/a recall=n/a (seeds={len(seeds)})")
        sys.exit(2)

    issues = verdict.get("issues", [])
    tp, fp, fn, precision, recall, f1, used_issues, used_seeds = score_verdict(seeds, issues)

    print(f"[{label}] verdict={verdict.get('verdict')} confidence={verdict.get('confidence')}")
    print(f"  TP={tp} FP={fp} FN={fn}")
    print(f"  precision={precision:.3f}  recall={recall:.3f}  F1={f1:.3f}")

    if fp:
        print("  FP (issues reported but not in seeds — review whether they are real):")
        for i_idx, issue in enumerate(issues):
            if i_idx not in used_issues:
                print(f"    - {issue.get('severity')} @ {issue.get('location')}: {issue.get('detail')}")
    if fn:
        print("  FN (seeds missed by the reviewer):")
        for s_idx, seed in enumerate(seeds):
            if s_idx not in used_seeds:
                print(f"    - {seed.get('id')} ({seed.get('severity')} @ {seed.get('location')}): {seed.get('detail')}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Unified per-agent comparison: coder pass-rate + reviewer precision/recall.

Reads eval/results/*/*.json (coder) and eval/reviewer-eval/scenarios/*/<agent>.raw.txt
(reviewer), then prints one table per role plus a simple recommendation.
"""
import glob
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location(
    "revscore", os.path.join(HERE, "reviewer-eval", "score.py")
)
revscore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(revscore)

# --- coder results ---
coder: dict = {}
for path in sorted(glob.glob(os.path.join(HERE, "results", "*", "*.json"))):
    agent = os.path.basename(os.path.dirname(path))
    with open(path, "r", encoding="utf-8") as fh:
        coder.setdefault(agent, []).append(json.load(fh))

# --- reviewer results ---
reviewer: dict = {}
for seeds_file in sorted(glob.glob(os.path.join(HERE, "reviewer-eval", "scenarios", "*", "seeds.json"))):
    scen = os.path.dirname(seeds_file)
    with open(seeds_file, "r", encoding="utf-8") as fh:
        seeds = json.load(fh)["bugs"]
    for raw in sorted(glob.glob(os.path.join(scen, "*.raw.txt"))):
        agent = os.path.basename(raw).removesuffix(".raw.txt")
        with open(raw, "r", encoding="utf-8") as fh:
            verdict = revscore.extract_verdict(fh.read())
        if verdict is None:
            reviewer.setdefault(agent, []).append(None)
            continue
        _, _, _, prec, rec, f1, _, _ = revscore.score_verdict(seeds, verdict.get("issues", []))
        reviewer.setdefault(agent, []).append({"prec": prec, "rec": rec, "f1": f1})

agents = sorted(set(coder) | set(reviewer))

print("=== Coder (golden tasks) ===")
print(f"{'agent':<10}{'tasks':>6}{'passed':>8}{'pass%':>8}{'avg_s':>8}{'avg_att':>9}")
for a in agents:
    recs = coder.get(a, [])
    if not recs:
        print(f"{a:<10}{'-':>6}")
        continue
    n = len(recs)
    passed = sum(1 for r in recs if r.get("passed"))
    avg_s = sum(int(r.get("durationSec", 0)) for r in recs) / n
    avg_att = sum(int(r.get("attempts", 1)) for r in recs) / n
    print(f"{a:<10}{n:>6}{passed:>8}{100.0 * passed / n:>7.1f}%{avg_s:>8.1f}{avg_att:>9.1f}")

print("\n=== Reviewer (seed bugs) ===")
print(f"{'agent':<10}{'scenarios':>10}{'precision':>10}{'recall':>8}{'F1':>7}")
for a in agents:
    rs = reviewer.get(a, [])
    if not rs:
        print(f"{a:<10}{'-':>10}")
        continue
    for r in rs:
        if r is None:
            print(f"{a:<10}{'n/a':>10}{'n/a':>10}{'n/a':>8}{'n/a':>7}")
        else:
            print(f"{a:<10}{'':>10}{r['prec']:>10.3f}{r['rec']:>8.3f}{r['f1']:>7.3f}")

# --- recommendation (naive, only from available numbers) ---
print("\n=== Gợi ý (chỉ từ số đo hiện có, chưa phải kết luận) ===")
best_coder = None
best_coder_rate = -1.0
for a, recs in coder.items():
    if recs:
        rate = sum(1 for r in recs if r.get("passed")) / len(recs)
        if rate > best_coder_rate:
            best_coder, best_coder_rate = a, rate
print(f"  coder gợi ý : {best_coder or 'n/a'} (pass-rate {100*best_coder_rate:.0f}%)")

best_rev = None
best_rev_f1 = -1.0
for a, rs in reviewer.items():
    valid = [r for r in rs if r]
    if valid:
        f1_avg = sum(r["f1"] for r in valid) / len(valid)
        if f1_avg > best_rev_f1:
            best_rev, best_rev_f1 = a, f1_avg
print(f"  reviewer gợi ý: {best_rev or 'n/a'} (F1 trung bình {best_rev_f1:.3f})")
print("\n  Nhắc lại: reviewer dùng để chặn/đề xuất, còn merge do gate deterministic quyết định.")

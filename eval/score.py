#!/usr/bin/env python3
"""Aggregate eval/results/<agent>/*.json into a comparison table."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def load() -> dict[str, list[dict]]:
    data: dict[str, list[dict]] = {}
    for path in sorted(glob.glob(os.path.join(RESULTS, "*", "*.json"))):
        agent = os.path.basename(os.path.dirname(path))
        with open(path, "r", encoding="utf-8") as fh:
            data.setdefault(agent, []).append(json.load(fh))
    return data


def main() -> None:
    data = load()
    if not data:
        print("No results yet. Run eval/runner.sh first.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for agent, recs in sorted(data.items()):
        n = len(recs)
        passed = sum(1 for r in recs if r.get("passed"))
        avg_dur = sum(int(r.get("durationSec", 0)) for r in recs) / n if n else 0
        avg_att = sum(int(r.get("attempts", 1)) for r in recs) / n if n else 0
        rows.append((agent, n, passed, round(100.0 * passed / n, 1), round(avg_dur, 1), round(avg_att, 1)))

    print("| agent | tasks | passed | pass-rate % | avg duration s | avg attempts |")
    print("|---|---|---|---|---|---|")
    for agent, n, passed, rate, avg_dur, avg_att in rows:
        print(f"| {agent} | {n} | {passed} | {rate} | {avg_dur} | {avg_att} |")

    if any("--csv" == a for a in sys.argv):
        print("\nagent,tasks,passed,pass_rate_pct,avg_duration_s,avg_attempts")
        for agent, n, passed, rate, avg_dur, avg_att in rows:
            print(f"{agent},{n},{passed},{rate},{avg_dur},{avg_att}")


if __name__ == "__main__":
    main()

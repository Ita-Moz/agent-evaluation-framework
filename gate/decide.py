#!/usr/bin/env python3
"""Deterministic merge decision from risk tier + reviewer verdict.

Rules (edit thresholds here, not in the model):
- tier == high        -> request_human        (human approval always required)
- verdict != approve  -> request_changes
- confidence < MIN_CONFIDENCE -> request_changes
- otherwise           -> auto_merge           (enable auto-merge via `gh`)

The decision is made by this script (deterministic), never by the model.
"""
import json
import os
import subprocess
import sys

MIN_CONFIDENCE = int(os.environ.get("MIN_CONFIDENCE", "8"))
VERDICT_PATH = os.environ.get("VERDICT_PATH", "review/verdict.json")


def gh_auto_merge() -> None:
    if not os.environ.get("GH_TOKEN"):
        print("NOTE: GH_TOKEN not set; skipping `gh pr merge --auto`.")
        return
    subprocess.run(
        ["gh", "pr", "merge", "--auto", "--squash"],
        check=False,
    )


def main() -> None:
    if len(sys.argv) > 1:
        tier = sys.argv[1]
    elif os.environ.get("TIER"):
        tier = os.environ["TIER"]
    else:
        # Fallback: recompute via classify.py if both run in the same job.
        import importlib.util
        spec = importlib.util.spec_from_file_location("classify", "classify.py")
        classify = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(classify)  # type: ignore
        tier = classify.classify(classify.changed_files(classify.base_ref()),
                                 classify.diff_lines(classify.base_ref()))["tier"]

    with open(VERDICT_PATH, "r", encoding="utf-8") as fh:
        verdict = json.load(fh)

    decision = {
        "tier": tier,
        "verdict": verdict.get("verdict"),
        "confidence": verdict.get("confidence"),
        "risk": verdict.get("risk"),
    }

    if tier == "high":
        decision["decision"] = "request_human"
    elif verdict.get("verdict") != "approve":
        decision["decision"] = "request_changes"
    elif int(verdict.get("confidence", 0)) < MIN_CONFIDENCE:
        decision["decision"] = "request_changes"
    else:
        decision["decision"] = "auto_merge"

    print(json.dumps(decision, indent=2))
    print(f"DECISION={decision['decision']}")

    if decision["decision"] == "auto_merge":
        gh_auto_merge()

    # request_human and request_changes leave the PR open; a follow-up comment
    # job (not shown here) can label/comment. Exit 0 so the gate itself does not
    # fail the PR — the decision is informational and enforced via branch protection.
    sys.exit(0)


if __name__ == "__main__":
    main()

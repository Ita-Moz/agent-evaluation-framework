#!/usr/bin/env bash
# Run the whole coder suite: every adapter × every golden task, then score.
#
# Usage:
#   REPO_DIR=<repo> [AGENTS="claude codex"] [TIMEOUT_SEC=600] ./run-suite.sh
#
# REPO_DIR must be the repository your golden tasks were generated from
# (make-task.sh). Reviewer scenarios are run separately (each may review a
# different repo) via eval/reviewer-eval/run.sh.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS="${AGENTS:-claude codex}"
REPO_DIR="${REPO_DIR:?set REPO_DIR to the repo your golden tasks were generated from}"
TIMEOUT_SEC="${TIMEOUT_SEC:-600}"

for agent in $AGENTS; do
  if [ ! -f "$HERE/adapters/$agent.sh" ]; then
    echo "[suite] skip $agent (no adapter)"
    continue
  fi
  for task in "$HERE"/tasks/*/; do
    [ -f "$task/task.md" ] || continue
    echo "=========================================================="
    echo "[suite] $agent @ $(basename "$task")"
    AGENT="$agent" REPO_DIR="$REPO_DIR" TIMEOUT_SEC="$TIMEOUT_SEC" \
      "$HERE/runner.sh" "$task" || echo "[suite]   (task failed, continuing)"
  done
done

echo "=========================================================="
echo "[suite] scores"
python3 "$HERE/score.py" --csv || true
echo "----------------------------------------------------------"
python3 "$HERE/compare.py"

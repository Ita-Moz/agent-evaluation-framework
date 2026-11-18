#!/usr/bin/env bash
# Agent-agnostic evaluation runner.
#
# Usage:
#   AGENT=<adapter> [REPO_DIR=<path>] [TIMEOUT_SEC=600] ./runner.sh eval/tasks/<task-id>
#
# - AGENT: name of an adapter in eval/adapters/ (e.g. claude, codex).
# - REPO_DIR: local path to the repo under test. The harness clones it into an
#   isolated temp checkout per run so agents never touch your working tree.
# - Each run writes a JSON result to eval/results/<agent>/<task-id>.json.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK="${1:?usage: AGENT=<adapter> runner.sh <task-dir>}"
# Resolve to an absolute path: adapters and setup/verify run after `cd` into the checkout.
TASK="$(cd "$(dirname "$TASK")" && pwd)/$(basename "$TASK")"
AGENT="${AGENT:?set AGENT to an adapter name in eval/adapters/}"
REPO_DIR="${REPO_DIR:?set REPO_DIR to the local path of the repo under test}"
TIMEOUT_SEC="${TIMEOUT_SEC:-600}"

ADAPTER="$HERE/adapters/$AGENT.sh"
[ -f "$ADAPTER" ] || { echo "adapter not found: $ADAPTER" >&2; exit 2; }
[ -f "$TASK/task.md" ] || { echo "missing $TASK/task.md" >&2; exit 2; }
[ -f "$TASK/verify.sh" ] || { echo "missing $TASK/verify.sh" >&2; exit 2; }

# shellcheck disable=SC1090
source "$ADAPTER"   # defines run_agent <prompt-file> <workdir>

run_with_timeout() {
  local secs=$1; shift
  "$@" &
  local pid=$!
  local deadline=$(( $(date +%s) + secs ))
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$(date +%s)" -ge "$deadline" ]; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      return 124
    fi
    sleep 1
  done
  wait "$pid"
}

task_id="$(basename "$TASK")"
RETRIES="${RETRIES:-1}"

start=$(date +%s)
attempt=1
verify_rc=1
agent_rc=-1
while [ "$attempt" -le "$RETRIES" ]; do
  workdir="$(mktemp -d)"
  echo "[runner] attempt $attempt/$RETRIES: $AGENT on $task_id"
  git clone -q "$REPO_DIR" "$workdir/repo"

  if [ -f "$TASK/setup.sh" ]; then
    echo "[runner] setup.sh"
    (cd "$workdir/repo" && bash "$TASK/setup.sh")
  fi

  echo "[runner] running $AGENT (timeout ${TIMEOUT_SEC}s)"
  run_with_timeout "$TIMEOUT_SEC" run_agent "$TASK/task.md" "$workdir/repo"
  agent_rc=$?

  echo "[runner] verifying (verify.sh)"
  set +e
  (cd "$workdir/repo" && bash "$TASK/verify.sh")
  verify_rc=$?
  set -e

  rm -rf "$workdir"
  [ "$verify_rc" -eq 0 ] && break
  attempt=$((attempt + 1))
done
end=$(date +%s)

out="$HERE/results/$AGENT/$task_id.json"
mkdir -p "$(dirname "$out")"
python3 - "$out" "$AGENT" "$task_id" "$verify_rc" "$agent_rc" "$start" "$end" "$attempt" <<'PY'
import json, sys, datetime
out, agent, task_id, verify_rc, agent_rc, start, end, attempt = sys.argv[1:9]
rec = {
    "agent": agent,
    "task": task_id,
    "passed": int(verify_rc) == 0,
    "verifyExit": int(verify_rc),
    "agentExit": int(agent_rc),
    "attempts": int(attempt),
    "durationSec": int(end) - int(start),
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
with open(out, "w") as fh:
    json.dump(rec, fh, indent=2)
print(f"[runner] wrote {out}")
print(f"[runner] result: passed={rec['passed']} verifyExit={verify_rc} agentExit={agent_rc} attempts={attempt} duration={rec['durationSec']}s")
PY

[ "$verify_rc" -eq 0 ] && exit 0 || exit 1

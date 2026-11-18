#!/usr/bin/env bash
# Run a reviewer agent on a scenario and capture its raw verdict text.
#
# Usage:
#   AGENT=<adapter> [REPO_DIR=<path>] [TIMEOUT_SEC=600] ./run.sh scenarios/<id>
#
# The reviewer must run against the repo/diff under review. If REPO_DIR is set,
# the harness clones it into an isolated checkout and runs the reviewer there;
# otherwise it runs in an empty temp dir (for prompt-only scenarios).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCEN="${1:?usage: AGENT=<adapter> run.sh <scenario-dir>}"
SCEN="$(cd "$(dirname "$SCEN")" && pwd)/$(basename "$SCEN")"
AGENT="${AGENT:?set AGENT to an adapter name in eval/adapters/}"
TIMEOUT_SEC="${TIMEOUT_SEC:-600}"

ADAPTER="$HERE/../adapters/$AGENT.sh"
[ -f "$ADAPTER" ] || { echo "adapter not found: $ADAPTER" >&2; exit 2; }
[ -f "$SCEN/prompt.md" ] || { echo "missing $SCEN/prompt.md" >&2; exit 2; }

# shellcheck disable=SC1090
source "$ADAPTER"

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

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
target="$workdir/repo"

if [ -n "${REPO_DIR:-}" ]; then
  echo "[reviewer] cloning $REPO_DIR -> $target"
  git clone -q "$REPO_DIR" "$target"
else
  echo "[reviewer] no REPO_DIR; running in empty temp dir"
  mkdir -p "$target"
fi

echo "[reviewer] $AGENT on $(basename "$SCEN") (timeout ${TIMEOUT_SEC}s)"
run_with_timeout "$TIMEOUT_SEC" run_agent "$SCEN/prompt.md" "$target" > "$SCEN/$AGENT.raw.txt"
echo "[reviewer] wrote $SCEN/$AGENT.raw.txt"

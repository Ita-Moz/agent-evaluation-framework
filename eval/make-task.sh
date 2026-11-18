#!/usr/bin/env bash
# Golden-task generator: turn a merged commit range into an eval task.
#
# Usage:
#   ./make-task.sh <repo> <base-ref> <head-ref> <task-id> [test-glob] [test-cmd]
#
#   <base-ref>/<head-ref>: the commit before/after a change you already merged.
#   [test-glob]: extended regexp for held-out test files (default: test|spec|check).
#   [test-cmd]:  command run by verify.sh (default: auto-detect).
#
# Produces eval/tasks/<task-id>/{task.md,setup.sh,verify.sh}:
#   - task.md   = the change spec (commit message + files to modify). Tests are NOT shown.
#   - setup.sh  = reset the checkout to <base> (agent sees the "before" state).
#   - verify.sh = materialize held-out tests from <head>, then run <test-cmd>.
#
# This is the standard "held-out tests" setup: the agent never sees the tests it
# must satisfy; verify.sh brings them in only after the agent finishes.
set -euo pipefail

REPO="${1:?usage: make-task.sh <repo> <base> <head> <task-id> [test-glob] [test-cmd]}"
BASE="${2:?}"; HEAD="${3:?}"; TASK_ID="${4:?}"
TEST_GLOB="${5:-test|spec|check}"
TEST_CMD="${6:-}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$HERE/tasks/$TASK_ID"
mkdir -p "$OUT"

cd "$REPO"
BASE_SHA="$(git rev-parse "$BASE")"
HEAD_SHA="$(git rev-parse "$HEAD")"
SUBJECT="$(git log -1 --format=%s "$HEAD_SHA")"
BODY="$(git log -1 --format=%b "$HEAD_SHA")"

CHANGED="$(git diff --name-only "$BASE_SHA" "$HEAD_SHA")"
TARGET="$(printf '%s\n' "$CHANGED" | grep -vE "$TEST_GLOB" || true)"
TESTS="$(printf '%s\n' "$CHANGED" | grep -E "$TEST_GLOB" || true)"

if [ -z "$TEST_CMD" ]; then
  if [ -f pytest.ini ] || [ -f conftest.py ] || grep -q 'pytest' pyproject.toml 2>/dev/null; then
    TEST_CMD="pytest"
  elif [ -f package.json ]; then
    TEST_CMD="npm test"
  elif [ -f go.mod ]; then
    TEST_CMD="go test ./..."
  elif [ -n "$TESTS" ] && printf '%s\n' "$TESTS" | grep -qE '\.py$'; then
    TEST_CMD="python3 $(printf '%s\n' "$TESTS" | tr '\n' ' ')"
  else
    TEST_CMD="make test"
  fi
fi

cat > "$OUT/task.md" <<EOF
# ${SUBJECT}

${BODY}

Recreate this change. Files you are expected to modify:

$(printf '%s\n' "$TARGET" | sed 's/^/- /')

Held-out tests will be applied separately to verify your work; implement the intended behavior so those tests pass.
EOF

cat > "$OUT/setup.sh" <<EOF
#!/usr/bin/env bash
# Reset the checkout to the "before" state (held-out tests are not present here).
set -euo pipefail
git reset --hard ${BASE_SHA}
EOF

{
  echo "#!/usr/bin/env bash"
  echo "# Materialize held-out tests from the target commit, then run them."
  echo "set -euo pipefail"
  if [ -n "$TESTS" ]; then
    echo "git checkout ${HEAD_SHA} -- $(printf '%s\n' "$TESTS" | tr '\n' ' ')"
  fi
  echo "${TEST_CMD}"
  echo ""
  echo "# Also run the project's domain invariants if present (business rules)."
  echo "git checkout ${HEAD_SHA} -- .agent-framework/domain 2>/dev/null || true"
  echo 'if [ -x .agent-framework/domain/invariants/run.sh ]; then ./.agent-framework/domain/invariants/run.sh; fi'
} > "$OUT/verify.sh"

chmod +x "$OUT/setup.sh" "$OUT/verify.sh"

echo "[make-task] wrote $OUT"
echo "  target files: $(printf '%s\n' "$TARGET" | tr '\n' ' ')"
echo "  held-out tests: $(printf '%s\n' "$TESTS" | tr '\n' ' ')"
echo "  test cmd: $TEST_CMD"

# Adapter: Claude Code (claude CLI)
# Verify flags against your installed version: `claude --help`
run_agent() {
  local prompt=$1 workdir=$2
  (
    cd "$workdir" || return 1
    # -p: print/non-interactive mode; prompt passed via stdin.
    # --dangerously-skip-permissions: run autonomously in the isolated checkout.
    # Pin a model with: --model <model>
    claude -p --dangerously-skip-permissions < "$prompt"
  )
}

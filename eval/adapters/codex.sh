# Adapter: OpenAI Codex (codex CLI)
# Verify flags against your installed version: `codex exec --help`
#
# Notes:
#   - Requires authentication first: run `codex login` (or set OPENAI_API_KEY).
#     Unauthenticated runs fail with HTTP 401 from api.openai.com.
#   - Under a sandbox that blocks writes to ~/.codex, point CODEX_HOME at a
#     writable dir (the harness already runs in an isolated checkout):
#       CODEX_HOME=/tmp/codex-home ./eval/runner.sh ...
run_agent() {
  local prompt=$1 workdir=$2
  (
    cd "$workdir" || return 1
    # `exec`: non-interactive run; prompt via stdin, workspace-write sandbox
    # (the checkout is isolated, so writes are safe). Pin a model with: -m <model>
    codex exec --sandbox workspace-write < "$prompt"
  )
}


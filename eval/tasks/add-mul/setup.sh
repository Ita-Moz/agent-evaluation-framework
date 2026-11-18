#!/usr/bin/env bash
# Reset the checkout to the "before" state (held-out tests are not present here).
set -euo pipefail
git reset --hard 0a8ca6faf3e95ed30491af7c8f86cf5c17a6857b

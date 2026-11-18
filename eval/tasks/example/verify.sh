#!/usr/bin/env bash
# Held-out check: the agent must not see this file until verify runs.
set -euo pipefail
grep -qx '42' answer.txt

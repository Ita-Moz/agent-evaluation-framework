#!/usr/bin/env bash
# Materialize held-out tests from the target commit, then run them.
set -euo pipefail
git checkout 46966b77c3f17ff30f499f778ad22949b6d5489f -- check.py 
python3 check.py 

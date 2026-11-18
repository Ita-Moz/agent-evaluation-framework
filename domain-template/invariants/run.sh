#!/usr/bin/env bash
# Chạy TẤT CẢ invariant / acceptance test (máy kiểm được) của dự án.
#
# Quy ước: mỗi file *.py (hoặc *.sh) trong thư mục này là một invariant.
#   exit 0 = nghiệp vụ đúng, exit khác 0 = vi phạm.
# Runner này được verify.sh của golden task và job CI deterministic gọi tới.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fail=0

for f in "$HERE"/*.py; do
  [ -e "$f" ] || continue
  echo "[invariant] $(basename "$f")"
  python3 "$f" || { echo "[invariant] FAIL: $(basename "$f")"; fail=1; }
done

for f in "$HERE"/*.sh; do
  [ "$f" = "$HERE/run.sh" ] && continue
  [ -e "$f" ] || continue
  echo "[invariant] $(basename "$f")"
  bash "$f" || { echo "[invariant] FAIL: $(basename "$f")"; fail=1; }
done

if [ "$fail" -ne 0 ]; then
  echo "[invariant] CÓ invariant sai — nghiệp vụ bị vi phạm"
  exit 1
fi
echo "[invariant] tất cả invariant pass"

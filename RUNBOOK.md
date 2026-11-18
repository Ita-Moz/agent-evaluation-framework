# Runbook — từ repo thật đến quyết định chọn agent

Quy trình end-to-end dùng bộ khung `agent-framework/`. Mọi lệnh agent-agnostic
(chỉ cần adapter có sẵn trong `eval/adapters/`).

## Bước 0 — chuẩn bị agent

```sh
claude --version        # đã có: 2.1.327
codex --version         # đã có: 0.157.1, nhưng cần `codex login` (hoặc OPENAI_API_KEY)
```

Chạy codex trong sandbox cần `CODEX_HOME` trỏ thư mục ghi được:
```sh
export CODEX_HOME=/tmp/codex-home
```

## Bước 0.5 — nạp tri thức nghiệp vụ (domain pack)

Bộ khung **không tự biết** nghiệp vụ. Copy `domain-template/` vào repo dự án tại
`.agent-framework/domain/` rồi điền `RULES.md`, `GLOSSARY.md`, `RUBRIC.md`,
`decisions/`, và viết invariant máy kiểm được vào `invariants/`.

- Cái gì **kiểm được bằng máy** (tiền, quyền, trạng thái, làm tròn) → viết thành
  `invariants/*.py|sh`; CI và golden task sẽ chạy và **chặn tự động**.
- Cái gì là **phán đoán** (UX, diễn giải pháp lý) → ghi vào `RUBRIC.md` như tiêu
  chí leo thang cho người; không giả vờ đo được bằng máy.

Xem `domain-template/README.md` để biết cách nối vào golden task, reviewer, gate.

## Bước 1 — sinh bộ golden task từ repo của bạn

Lấy các commit đã merge làm task mẫu (held-out tests sẽ được giữ riêng):

```sh
cd agent-framework
./eval/make-task.sh /path/to/repo <base-sha> <head-sha> task-01
# lặp lại cho mỗi việc bạn muốn test (10+ task để có con số tin cậy)
```

Mỗi task tạo ra `eval/tasks/<id>/{task.md,setup.sh,verify.sh}`. Kiểm tra `task.md`
không lộ nội dung test (chỉ mô tả việc cần làm).

## Bước 2 — chạy head-to-head (coder)

```sh
AGENTS="claude codex" REPO_DIR=/path/to/repo ./eval/run-suite.sh
```

Hoặc chạy từng cái: `AGENT=claude REPO_DIR=... ./eval/runner.sh eval/tasks/task-01`.
Kết quả ghi vào `eval/results/<agent>/<task>.json`.

## Bước 3 — đo reviewer (precision/recall)

Nhét lỗi (seed bugs) vào một diff đã đúng, tạo scenario (xem `eval/reviewer-eval/README.md`), rồi:

```sh
AGENT=claude REPO_DIR=/path/to/repo ./eval/reviewer-eval/run.sh eval/reviewer-eval/scenarios/<id>
python3 eval/reviewer-eval/score.py eval/reviewer-eval/scenarios/<id> claude
```

Đọc danh sách FP/FN ở cuối output để hoàn thiện `seeds.json` (precision chỉ có nghĩa
khi seed set đầy đủ).

## Bước 4 — so sánh và chọn

```sh
python3 eval/compare.py
```

Chọn **coder** theo pass-rate/chi phí/thời gian; chọn **reviewer** theo F1 (cân bằng
precision + recall). Chạy "shadow" song song với người review trước khi nới auto-merge.

## Bước 5 — bật gate trong CI

1. Copy `gate/{classify.py,decide.py,verdict.schema.json,agent-gate.yml}` vào repo.
2. Sửa lệnh test/lint/build trong job `deterministic-checks`, **và chạy `.agent-framework/domain/invariants/run.sh`** (quy tắc nghiệp vụ máy kiểm được).
3. Bật branch protection + `Allow auto-merge`; tạo fine-grained PAT vào `GH_TOKEN`.
4. Đặt `MIN_CONFIDENCE` trong `decide.py` theo recall đo được ở bước 3.

Luồng merge: agent mở PR → CI chạy deterministic checks → đọc `review/verdict.json`
(do reviewer tạo) → `classify.py` ra tier → `decide.py` quyết định **auto-merge**
(low/medium + approve + đủ confidence) hoặc **chờ người** (high).

## Theo dõi liên tục

- **revert rate** và **incident rate** là chỉ số giám sát số một.
- Ghi lại mỗi lần gate chặn sai / bỏ sót để quay lại tinh chỉnh tier và ngưỡng.
- Mỗi lỗi **nghiệp vụ** lọt lưới → viết ngay một invariant để lần sau chặn tự động
  (cùng triết lý "mỗi lần sửa lỗi thành một lint rule" của Grok Bot).

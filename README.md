# Coding-agent evaluation framework

Bộ khung **nghiên cứu và đánh giá** các coding agent (Claude Code, Codex, DeepSeek, Gemini CLI, Cursor, Aider, …) để chọn agent phù hợp cho phát triển phần mềm/AI, và thiết lập quy trình review + merge đáng tin cậy mà **không phụ thuộc một agent/harness cụ thể**.

Mục tiêu không phải "build một con agent riêng", mà là **đo được** ai viết tốt, ai review đáng tin, rồi dùng kết quả đo để dựng một *quality gate* chạy quanh bất kỳ agent nào — nhằm gỡ nút thắt review thủ công.

## Ba câu hỏi bộ khung này trả lời

| Câu hỏi | Công cụ trong repo | Kết quả |
|---|---|---|
| Agent nào viết code đúng? | `eval/` + golden tasks + held-out tests | pass-rate, cost, latency theo agent |
| Agent nào review đáng tin? | seeded bugs → precision/recall | ngưỡng confidence dùng được |
| Làm sao merge an toàn? | `gate/` (agent-agnostic) | tier + verdict → auto-merge / human |
| Đúng **nghiệp vụ** của dự án? | `domain-template/` + invariants | chặn vi phạm máy kiểm được; phần còn lại leo thang người |

## Cấu trúc

```
agent-framework/
├── README.md                     # file này
├── RUNBOOK.md                    # quy trình end-to-end (repo → chọn agent → gate)
├── research/
│   └── state-of-the-art.md       # tổng hợp hiện trạng + so sánh agent
├── eval/
│   ├── methodology.md            # phương pháp đo (metrics, golden tasks, reviewer eval)
│   ├── make-task.sh              # sinh golden task từ một commit range (held-out tests)
│   ├── runner.sh                 # harness chạy một agent trên một task, đo kết quả
│   ├── score.py                  # gộp kết quả → bảng so sánh
│   ├── compare.py                # báo cáo gộp coder + reviewer, gợi ý chọn
│   ├── run-suite.sh              # chạy cả bộ task × nhiều agent
│   ├── adapters/                 # mỗi agent một adapter (claude, codex, …)
│   ├── tasks/example/            # mẫu golden task
│   └── reviewer-eval/            # đo reviewer: seed bugs → precision/recall/F1
├── domain-template/              # copy vào repo dự án: tri thức nghiệp vụ
│   ├── README.md · RULES.md · GLOSSARY.md · RUBRIC.md
│   ├── decisions/                # ADR: vì sao quyết định như vậy
│   └── invariants/run.sh         # quy tắc nghiệp vụ máy kiểm được
└── gate/
    ├── verdict.schema.json       # hợp đồng verdict (dùng chung mọi agent)
    ├── classify.py               # phân loại rủi ro deterministic
    ├── decide.py                 # quyết định merge deterministic
    └── agent-gate.yml            # GitHub Actions workflow mẫu
```

## Quy trình đánh giá (tóm tắt)

1. **Dựng bộ golden task** từ repo thật của bạn, mỗi task kèm `verify.sh` (test giữ riêng, agent không thấy).
2. **Chạy từng agent** qua `eval/runner.sh` trên cùng bộ task → `score.py` so sánh pass-rate / chi phí / thời gian.
3. **Đo chất lượng reviewer**: nhét lỗi (seed bugs) vào diff đã đúng, đo precision/recall.
4. **Chọn cặp coder + reviewer**, đặt ngưỡng tier/confidence theo số đo được, rồi bật `gate/` trong CI.

Chi tiết đầy đủ nằm ở [research/state-of-the-art.md](research/state-of-the-art.md) và [eval/methodology.md](eval/methodology.md).

## Làm sao gate biết đúng nghiệp vụ? (câu hỏi cốt lõi)

Bộ khung **không tự biết** nghiệp vụ — nó chỉ so được với thứ **máy kiểm được**. Bạn nạp tri thức nghiệp vụ qua `domain-template/` (copy vào dự án tại `.agent-framework/domain/`), theo 3 nguồn:

| Nguồn | Dạng | Gate tự kiểm được? |
|---|---|---|
| `invariants/*.py|sh` | test/assert chạy được (tiền, quyền, trạng thái) | ✅ deterministic — chặn được |
| `RULES.md` · `GLOSSARY.md` · `decisions/` | văn bản | ❌ giảm sai trước khi code, không xác minh |
| `RUBRIC.md` | tiêu chí chấm + escalation | ⚠️ phán đoán → **leo thang người** |

Và golden task **thừa hưởng** nghiệp vụ: `make-task.sh` lấy task từ **commit đã merge thật**, nên test held-out chính là tri thức nghiệp vụ con người đã chấp nhận. Đây là cách bộ khung "biết" dự án mà không cần viết lại từ đầu.

**Nguyên tắc:** cái gì kiểm được bằng máy → viết thành invariant ngay; cái gì là phán đoán (UX, pháp lý) → ghi vào RUBRIC như tiêu chí leo thang, không giả vờ đo được bằng máy.

## Trạng thái trên máy bạn

- Đã cài và chạy được: `claude` (Claude Code **2.1.327**) và `codex` (codex-cli **0.157.1**).
- **codex chưa đăng nhập**: chạy trong sandbox được khi `CODEX_HOME` trỏ thư mục ghi được (vd `/tmp/codex-home`), nhưng cần `codex login` (hoặc `OPENAI_API_KEY`) — hiện trả HTTP 401 từ api.openai.com.
- Chưa thấy trên PATH: `gemini`, `aider`, `cursor`, `dsh`.
- Adapter mẫu cho claude/codex nằm ở `eval/adapters/`; thêm agent khác bằng cách viết adapter theo cùng hợp đồng.

## Đã kiểm chứng trong session này

- `runner.sh` chạy end-to-end với adapter **claude** trên `eval/tasks/example`: clone, chạy agent, `verify.sh` pass, ghi `eval/results/claude/example.json` (passed=true, 6s).
- `make-task.sh` sinh golden task từ commit range và chạy end-to-end: repo `add()` + commit `mul()`, sinh `eval/tasks/add-mul` (held-out `check.py`), claude tự thêm `mul()` → `verify.sh` pass.
- `reviewer-eval` chạy claude trên repo thật 2 bug nhét vào → recall 1.0 (chi tiết trong `eval/reviewer-eval/README.md`).
- `classify.py` phân loại đúng file `src/auth/login.py` → tier **high**; `decide.py` đúng ánh xạ (medium + confidence 5 → request_changes; high → request_human).
- `agent-gate.yml`, `verdict.schema.json` parse hợp lệ; toàn bộ script python/bash qua kiểm tra cú pháp.
- `make-task.sh` sinh `verify.sh` có hook chạy `.agent-framework/domain/invariants/run.sh` (kiểm nghiệp vụ held-out) — đã kiểm chứng bằng repo tạm.
- **codex**: chạy được trong sandbox khi `CODEX_HOME` trỏ thư mục ghi được, nhưng cần `codex login` (hiện 401) — chưa thể chạy vòng so sánh codex.

## Nguyên tắc xuyên suốt (đừng quên)

- **Không tin một lần LLM đơn lẻ đóng vai review.** Luôn xếp lớp: deterministic checks → model reviewer (có ngưỡng) → human chỉ cho rủi ro cao.
- **Merge do bước deterministic quyết định, không do model.** Model chỉ đề xuất.
- **Đo tỉ lệ thất bại, không chỉ tỉ lệ thành công** (revert rate, incident rate, precision/recall). Đây là thứ phân biệt gate thật với marketing.

# Domain pack — dạy bộ khung biết "đúng nghiệp vụ" là gì

Bộ khung **không tự biết** nghiệp vụ của dự án. Nó chỉ so sánh được với thứ bạn
biến thành **máy kiểm tra được**. Domain pack là nơi bạn nạp tri thức nghiệp vụ
để golden task, reviewer và quality gate dùng chung.

## Cài vào dự án của bạn

Copy thư mục này vào **repo của dự án** tại `.agent-framework/domain/`, commit nó
(cùng với `gate/`). Đường dẫn chuẩn mà tooling tìm:

```
<your-repo>/.agent-framework/domain/
├── RULES.md              # quy tắc nghiệp vụ (có thể test được + không)
├── GLOSSARY.md           # thuật ngữ nghiệp vụ → tên/mã trong code
├── RUBRIC.md             # tiêu chí reviewer chấm + khi nào leo thang cho người
├── decisions/            # ADR: vì sao quyết định như vậy (context cho agent)
└── invariants/run.sh     # chạy các invariant/acceptance test máy kiểm được
```

## Ba nguồn sự thật (và nguồn nào gate tự kiểm được)

| Nguồn | Dạng | Ai dùng | Tự động kiểm được? |
|---|---|---|---|
| `invariants/` | test/assert/property chạy được | CI + verify.sh | ✅ có (deterministic) |
| `RULES.md` + `GLOSSARY.md` + `decisions/` | văn bản | agent đọc trước khi code | ❌ (giảm sai, không xác minh) |
| `RUBRIC.md` | tiêu chí chấm + escalation | reviewer model | ⚠️ phán đoán, cần người xác nhận |

**Nguyên tắc vàng:** cái gì kiểm tra được bằng máy → viết thành invariant ngay.
Cái gì thật sự là phán đoán (UX, diễn giải pháp lý, đánh đổi sản phẩm) → ghi vào
`RUBRIC.md` như tiêu chí leo thang, **không giả vờ đo được**.

## Nó nối vào bộ khung thế nào

1. **Golden tasks**: `make-task.sh` sinh `verify.sh` tự chạy
   `.agent-framework/domain/invariants/run.sh` (held-out) — nên mọi task đều kiểm
   cả nghiệp vụ, không chỉ unit test của thay đổi.
2. **Reviewer**: prompt reviewer được nhúng nội dung `RULES.md` + `RUBRIC.md` để
   chấm theo nghiệp vụ, không chỉ theo "code đẹp".
3. **Gate**: job deterministic trong CI chạy `invariants/run.sh` như một required
   check — đây là lớp chặn nghiệp vụ mà model không thể bỏ qua.
4. **make-task.sh** lấy task từ **commit đã merge thật** → test held-out chính là
   tri thức nghiệp vụ đã được con người chấp nhận trước đó. Đây là cách bộ khung
   "thừa hưởng" nghiệp vụ của dự án mà không cần bạn viết lại từ đầu.

## Bắt đầu từ đâu

1. Viết 5–10 invariant quan trọng nhất (tiền, tồn kho, quyền, thời hạn, trạng thái).
2. Điền `GLOSSARY.md` để agent không đoán sai thuật ngữ.
3. Viết `RUBRIC.md` với 3–5 tiêu chí "phải leo thang cho người".
4. Chạy `make-task.sh` trên vài commit đã merge → bộ eval đầu tiên đã có nghiệp vụ.

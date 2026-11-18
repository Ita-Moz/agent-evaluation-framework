# Phương pháp đánh giá coding agent (agent-agnostic)

Mục tiêu: đo được **ai viết đúng**, **ai review đáng tin**, rồi dùng số đo để chọn agent + đặt ngưỡng cho quality gate. Không dùng benchmark chung (SWE-bench…) làm quyết định cuối — chỉ tin số đo trên **repo của bạn**.

## 1. Bộ golden task (đầu vào quan trọng nhất)

Mỗi task là một thư mục:

```
eval/tasks/<task-id>/
├── task.md          # prompt tự chứa: cần làm gì, tiêu chí đúng (tiếng Anh)
├── setup.sh         # (tuỳ chọn) reset checkout về baseline
├── verify.sh        # test giữ riêng (held-out); exit 0 = pass; agent KHÔNG thấy file này trước
└── review-inject.md # (tuỳ chọn, cho đánh giá reviewer) mô tả lỗi đã nhét
```

Nguyên tắc xây task:
- Lấy từ **công việc thật** đã merge trước đây (cách của Databricks: PR đã merge + test giữ riêng thành benchmark). Càng sát việc thật càng tốt.
- `verify.sh` phải **độc lập** với lời giải: là test/kiểm tra không lộ cho agent. Giữ ở nhánh/tệp mà prompt `task.md` không mô tả.
- Trộn độ khó: fix bug đơn giản → feature nhỏ → refactor có ràng buộc → chạm code rủi ro cao.
- Cần đủ mẫu để kết luận (tối thiểu ~10 task/agent cho con số sơ bộ; vài chục để tin cậy).

## 2. Đánh giá coder

Chạy: `AGENT=claude ./eval/runner.sh eval/tasks/<task-id>` cho từng task × từng agent, rồi `./eval/score.py`.

| Metric | Định nghĩa | Ý nghĩa |
|---|---|---|
| **pass-rate** | tỉ lệ task `verify.sh` pass | độ đúng thực chất |
| **pass@k** | đúng trong ≤ k lần thử (cho phép tự sửa) | độ ổn định |
| **cost/task** | token/$ nếu adapter ghi được | kinh tế |
| **latency** | thời gian hoàn thành | trải nghiệm + chi phí chờ |
| **diff size** | số dòng đổi | rủi ro đi kèm |

## 3. Đánh giá reviewer (quan trọng với nút thắt merge)

Phương pháp **seed bugs**: lấy một diff **đã đúng**, nhét lỗi có chủ đích (bug logic, race, lỗi bảo mật, thiếu test), rồi cho reviewer duyệt. Công cụ có sẵn ở [`reviewer-eval/`](reviewer-eval/): `run.sh` chạy reviewer bất kỳ, `score.py` đối chiếu verdict với `seeds.json` để ra precision/recall/F1. Với mỗi reviewer đo:

| Metric | Công thức | Ngưỡng mục tiêu |
|---|---|---|
| **precision** | lỗi báo đúng / tổng lỗi báo | cao (không chặn nhầm code tốt) |
| **recall** | lỗi thật bắt được / tổng lỗi thật | cao (không bỏ sót bug) |
| **false-positive rate** | chặn nhầm diff đúng | thấp |
| **confidence calibration** | confidence cao có tương ứng đúng không | dùng để đặt ngưỡng trong `gate/decide.py` |

Tham chiếu công bố: DoorDash recall 53,6% / precision 87%; Snap recall 80%; Uber 75% comment hữu ích. **Ngưỡng confidence phải đến từ recall đo được**, không phải cảm giác.

## 4. Đánh giá cả vòng gate (khi đã bật)

Theo dõi liên tục trong production:

- **revert rate** — tỉ lệ PR merge xong phải gỡ lại. Là tín hiệu chất lượng số một (Meta ~1/13,3; Grok ~0,5%).
- **incident rate** — tỉ lệ diff gây sự cố production.
- **time-to-merge** — tốc độ đi qua cổng.
- **human-touch rate** — % diff cần người duyệt (mục tiêu: thấp nhưng không bao giờ 0 ở rủi ro cao).

## 5. Quyết định dựa trên số liệu

1. Chọn **coder** theo pass-rate/cost/latency.
2. Chọn **reviewer** theo recall/precision (có thể khác agent với coder).
3. Đặt ngưỡng `MIN_CONFIDENCE` và tier trong `gate/` theo recall đo được.
4. Chạy song song một thời gian **có người duyệt song song** (shadow), so sánh, rồi mới nới auto-merge cho tier thấp.

> Đừng tin vendor chỉ khoe "N% PR merged". Luôn hỏi denominator: bao nhiêu bị revert, bao nhiêu bị chặn, precision/recall là bao nhiêu.

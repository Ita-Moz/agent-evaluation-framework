# Decisions (ADR log) — context cho agent

Mỗi quyết định quan trọng một file, để agent/reviewer hiểu **vì sao** và tránh
đề xuất thay đổi trái với quyết định đã chốt.

Tên file: `decisions/NNNN-<ten-ngan>.md`

## Mẫu

```markdown
# 0001 — Làm tròn tiền theo HALF_UP

- **Ngày**: 2026-01-15
- **Bối cảnh**: khách phản ánh chênh 0.01 so với hoá đơn giấy.
- **Quyết định**: dùng HALF_UP ở bước cuối, không làm tròn từng dòng.
- **Hệ quả**: mọi service tính tiền phải gọi `round_money()` chung.
- **Người chốt**: <tên/kế toán trưởng>
- **Invariant liên quan**: `invariants/check_order_total.py`
```

Chỉ ghi quyết định **đã chốt**, không ghi đề xuất. Agent đọc thư mục này như
context; reviewer dùng để phát hiện thay đổi trái quyết định cũ.

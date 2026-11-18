# RULES — quy tắc nghiệp vụ

Mỗi quy tắc một mục, đánh số, ghi rõ **kiểm được bằng máy hay không**.
Quy tắc kiểm được → tạo invariant tương ứng ở `invariants/`. Quy tắc không kiểm được → ghi "NGƯỜI" và nêu lý do.

## Template

### R-001 — <tên quy tắc>
- **Quy tắc**: <mô tả ngắn, không mơ hồ>
- **Phạm vi code**: <module/hàm/service liên quan>
- **Kiểm được**: MÁY | NGƯỜI
- **Invariant / test**: <đường dẫn tới invariants/... hoặc "—">
- **Ví dụ**: <input → output mong đợi>
- **Sai thì hậu quả**: <tiền/uy tín/pháp lý/...>

---

### R-001 — Ví dụ: tổng tiền đơn hàng
- **Quy tắc**: tổng tiền = sum(giá × số lượng) − giảm giá, làm tròn 2 chữ số, không âm.
- **Phạm vi code**: `src/orders/total.py`
- **Kiểm được**: MÁY
- **Invariant / test**: `invariants/check_order_total.py`
- **Ví dụ**: 2 × 10.5 với giảm 1 → 20.00
- **Sai thì hậu quả**: thu sai tiền khách.

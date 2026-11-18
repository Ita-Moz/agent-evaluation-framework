# GLOSSARY — thuật ngữ nghiệp vụ → code

Điền để agent/reviewer không đoán sai tên gọi. Mỗi dòng: thuật ngữ nghiệp vụ | tên trong code | ghi chú.

| Thuật ngữ nghiệp vụ | Trong code | Ghi chú |
|---|---|---|
| Đơn hàng | `Order` | khác "giỏ hàng" (`Cart`) |
| Khách VIP | `customer.tier == "vip"` | >= 10 đơn trong 12 tháng |
| Hoàn tiền | `refund()` | chỉ khi `order.status == "paid"` |

Quy ước:
- Không dùng từ đồng nghĩa tuỳ tiện giữa docs và code.
- Thuật ngữ mới trong task → cập nhật bảng này trong cùng PR.

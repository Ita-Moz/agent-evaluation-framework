# RUBRIC — reviewer chấm theo nghiệp vụ

Dùng trong prompt của reviewer (sau khi nhúng `RULES.md`). Mục tiêu: chấm cả
**đúng nghiệp vụ**, không chỉ "code sạch".

## Checklist bắt buộc cho mọi diff

- [ ] Thay đổi có vi phạm quy tắc nào trong `RULES.md` không? (liệt kê mã R-xxx)
- [ ] Có dùng sai thuật ngữ / ánh xạ sai trong `GLOSSARY.md` không?
- [ ] Invariant liên quan có còn đúng không (chạy `invariants/run.sh`)?
- [ ] Có thay đổi hành vi không được task mô tả (scope creep) không?

## Tiêu chí LEO THANG cho người (không tự duyệt)

Diff chạm bất kỳ mục nào dưới đây → **bắt buộc người duyệt**, bất kể verdict model:

1. Tiền, thuế, làm tròn, hoàn tiền, tỉ giá.
2. Quyền truy cập, vai trò, dữ liệu cá nhân.
3. Trạng thái đơn/đơn hàng, migration dữ liệu.
4. Thay đổi public API / schema có consumer bên ngoài.
5. Diễn giải pháp lý/nội quy (không máy nào kiểm được).

## Mẫu verdict (giữ nguyên schema trong gate/)

`issues[].severity` nên map từ RULES: vi phạm R-xxx → `severity: "bug"` (hoặc
`security` nếu là quyền/tiền). Ghi mã quy tắc trong `detail`.

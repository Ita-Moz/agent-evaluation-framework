# Đánh giá reviewer (precision/recall)

Đo chất lượng **reviewer** — phần trực tiếp gỡ nút thắt "phải review thủ công".
Phương pháp: nhét lỗi có chủ đích (seed bugs) vào một diff, cho reviewer duyệt,
rồi đối chiếu verdict với danh sách lỗi đã biết để tính precision/recall/F1.

## Cấu trúc một scenario

```
eval/reviewer-eval/scenarios/<id>/
├── seeds.json            # ground truth: các lỗi đã nhét (id, severity, location, detail)
├── prompt.md             # prompt gửi reviewer (nói rõ phải xuất JSON verdict)
└── <agent>.raw.txt       # kết quả thô của reviewer (do run.sh ghi)
```

`seeds.json`:
```json
{
  "bugs": [
    { "id": "B1", "severity": "bug", "location": "src/calc.py:4", "detail": "off-by-one in range loop" }
  ]
}
```

## Cách chạy

```sh
# 1) Chạy reviewer (agent bất kỳ) trên một repo có diff đã nhét lỗi:
AGENT=claude REPO_DIR=/path/to/repo ./eval/reviewer-eval/run.sh eval/reviewer-eval/scenarios/<id>

# 2) Chấm điểm: đối chiếu verdict với seeds
python3 eval/reviewer-eval/score.py eval/reviewer-eval/scenarios/<id> claude
```

`score.py` báo TP/FP/FN → **precision, recall, F1** cho từng agent.

## Quy ước quan trọng để matching khớp

- `prompt.md` phải yêu cầu reviewer xuất **đúng JSON verdict** với `issues[].location` dạng `path:line`.
- `seeds.json` dùng **cùng** định dạng `location` (đường dẫn + số dòng thật trong diff).
- `score.py` khớp theo thứ tự ưu tiên: cùng file + cùng dòng → cùng file + cùng severity → trùng `detail`.

## Đọc kết quả

- **precision** thấp = reviewer chặn nhầm code tốt (gây nhiễu, mất niềm tin).
- **recall** thấp = bỏ sót bug thật (nguy hiểm khi auto-merge).
- Ngưỡng `MIN_CONFIDENCE` trong `gate/decide.py` phải đặt theo recall đo được, không phải cảm giác.

## Bài học từ lần chạy thật (scenario `python-bugs/`)

Chạy `claude` trên repo thật nhỏ (2 bug nhét vào: off-by-one + `eval()`), kết quả:

```
[claude] verdict=block confidence=9
  TP=2 FP=5 FN=0
  precision=0.286  recall=1.000  F1=0.444
```

**recall=1.0** (bắt đủ cả 2 bug), nhưng precision=0.286 — vì claude báo thêm 5 vấn đề *hợp lệ* (edge case list rỗng, gợi ý design, thiếu test) mà `seeds.json` chưa liệt kê. Chúng không phải "reviewer dở" mà là **seed set chưa đầy đủ**.

→ Kết luận thực hành:
- Muốn đo **recall** (có bắt được bug nhét vào không) → seed set chỉ cần bug nhét vào là đủ.
- Muốn đo **precision** → `seeds.json` phải liệt kê *đầy đủ mọi* phát hiện mong đợi; nếu không, hãy đọc danh sách FP (đã in ở cuối output) để hoàn thiện seeds thay vì kết luận vội.

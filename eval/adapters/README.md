# Agent adapters

Mỗi file định nghĩa hàm `run_agent <prompt-file> <workdir>`: chạy agent **không tương tác**
trong `<workdir>`, đọc prompt từ `<prompt-file>`, trả kết quả qua stdout.

Hợp đồng này là thứ duy nhất harness (`runner.sh`) biết — viết adapter mới cho agent khác
(DeepSeek/dsh, Gemini CLI, Aider, …) bằng cách copy một file và sửa lệnh gọi.

Lưu ý chung:
- Codex còn có sẵn `codex exec review` (review repo hiện tại) — có thể dùng trực tiếp làm
  reviewer trong mục "đánh giá reviewer", không cần tự viết prompt.
- Pin model cho từng adapter để so sánh công bằng (`--model`, `--model-name`, …).
- Kiểm tra cờ CLI theo đúng bản đang cài: `claude --help`, `codex exec --help`, …
- Bật chế độ tự chạy không hỏi quyền chỉ trong **checkout cô lập** của harness (runner đã clone riêng).

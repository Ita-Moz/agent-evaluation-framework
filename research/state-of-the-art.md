# Hiện trạng & so sánh coding agent (tổng hợp nghiên cứu)

> Cập nhật 2026-11. Tổng hợp từ các bài nói/paper/bài blog công khai của Meta, Cloudflare, Uber, xAI (Grok Bot), DoorDash, Snap, Wealthfront. Xem link nguồn ở cuối.

## 1. Kết luận quan trọng nhất

Nút thắt review là thật và đã được đo: **Meta** ghi nhận số dòng code mỗi diff tăng **105,9%** khi agent tham gia viết code — con người không kịp đọc. Giải pháp đã trở thành chuẩn ngành là **quality gate** (cổng chất lượng): mọi diff do agent viết đi qua một cổng, cổng quyết định *tự merge hay leo lên cho người*, và **không bao giờ là một lần LLM đơn lẻ**.

Trường hợp được nhắc nhiều nhất — **nhóm Grok Bot ở xAI** (Lauren Tan, bài nói *"All Code Is Slop (Except Mine)"*): ~11.000 PR hợp nhất/tháng, revert ~0,5%. Bí quyết **không phải model mạnh hơn**, mà là lớp kiểm tra quanh agent:

- Biến mọi lỗi lặp lại thành **lint rule** (thay vì comment) — codebase là input lớn nhất của agent.
- Bắt agent **tự chứng minh** bằng bằng chứng: chạy app, quay/chụp màn hình, dùng TLA+/Lean kiểm chứng hình thức.
- Review xem **bằng chứng**, không đọc từng dòng.
- Sửa API nền tảng để những chỗ dễ dùng sai (vd `useEffect`) không còn là bẫy.

## 2. Thang độ tin cậy (trust ladder) chung cho mọi agent

| Tầng | Làm gì | Ai đã làm |
|---|---|---|
| 0. Deterministic | test, build, typecheck, lint, quét secrets/SAST/SCA | mọi nơi |
| 1. Phân loại rủi ro theo diff | diff nhỏ → review rẻ; `auth/crypto/migration` → luôn full | Cloudflare |
| 2. Reviewer model + ngưỡng tin cậy | phải ≥ 8/10 mới approve | Meta RADAR |
| 3. Nhiều reviewer / đối kháng | "công kích vs bào chữa" rồi model thứ 3 phân xử | Wealthfront (~$4/PR), Doist (7 lượt) |
| 4. Bằng chứng tự kiểm chứng | ảnh/video/kiểm chứng hình thức | Grok Bot |
| 5. Leo lên cho người | chỉ rủi ro cao cần người; còn lại merge qua job deterministic | agent-squad-hq |

Hai bài học về **thiết kế** gate:
- **"Block hay chỉ advise" là quyết định niềm tin, chọn trước.** Uber làm uReview dạng *advisory* (reviewer thứ hai) để kỹ sư giữ niềm tin, không phải gatekeeper; kết quả ~65k diff/tuần, 75% comment hữu ích.
- **Công bố tỉ lệ thất bại.** Atlassian "59% PR merge" = "41% không merge"; Meta công bố revert ~1/13,3 và incident ~1/50. Ai chỉ khoe số thắng là chưa đủ tin.

## 3. Số liệu tham khảo (để đặt kỳ vọng)

| Tổ chức | Reviewer | Số đo công bố |
|---|---|---|
| Grok Bot (xAI) | nhiều lớp + bằng chứng | ~0,5% revert |
| Meta RADAR | rule tĩnh + LLM ≥8/10 + validate | revert ~1/13,3 |
| DoorDash (DashBench) | đo reviewer độc lập | recall 53,6%, precision 87% |
| Snap (CodePal) | 90% PR trong 5–10 phút | 200k+ review, recall 80% |
| Uber (uReview) | advisory, 6 monorepo | ~65k diff/tuần, 75% comment hữu ích |
| Wealthfront (Iris) | GPT vs Gemini + Opus phân xử | ~$4/PR |
| Doist | 7 lượt review song song, route model theo diff | ~4.500 review/tháng, <$2 |

## 4. Bảng so sánh agent (template — điền bằng kết quả `eval/`)

| Tiêu chí | Claude Code | Codex (OpenAI) | DeepSeek | Gemini CLI | Aider/Cursor |
|---|---|---|---|---|---|
| Phiên bản local | 2.1.327 | 0.157.1 | (DSH desktop) | — | — |
| Chế độ headless | `claude -p` | `codex exec` | dsh CLI | — | — |
| Pass-rate (golden tasks) | ? | ? | ? | ? | ? |
| Chi phí/task | ? | ? | ? | ? | ? |
| Reviewer precision/recall | ? | ? | ? | ? | ? |
| Tự chạy không cần confirm | cần flag quyền | có sandbox | có preset | ? | ? |

Cách điền: chạy `eval/runner.sh` + `eval/score.py` (xem [methodology](eval/methodology.md)).

## 5. Cách đọc kết quả đánh giá

- **Coder**: chọn theo pass-rate trên *repo của bạn* (không phải benchmark chung như SWE-bench), chi phí, thời gian.
- **Reviewer**: chọn theo precision (ít chặn nhầm code tốt) + recall (bắt được bug thật). Ngưỡng confidence trong `gate/decide.py` phải dựa trên recall đo được, không phải cảm giác.
- **Không có agent nào đáng tin "100%"** ở rủi ro cao — luôn giữ human escalation cho `auth/crypto/migration/payment`.

## Nguồn

- Grok Bot 11.000 PR + talk: [i10x.ai](https://i10x.ai/news/grob-bot-team-11000-pull-requests-lauren-tan), [tóm tắt podcast](https://podcasts.apple.com/tw/podcast/ep475-ai-%E5%AF%AB%E7%9A%84-code-%E6%80%8E%E9%BA%BC%E4%B8%8D%E8%AE%8A-slop-spacexsi-lauren-tan-%E6%BC%94%E8%AC%9B%E7%B2%BE%E8%8F%AF/id1817340034?i=1000802071604)
- Quality gate pattern (16 công ty): [software-factories.port.io](https://software-factories.port.io/patterns/quality-gate)
- Cloudflare AI review (risk tiers + diff noise filter): [blog.cloudflare.com](https://blog.cloudflare.com/ai-code-review/)
- Nút thắt review (Meta 105,9%): [rootly.com](https://rootly.com/blog/how-engineering-leaders-rethink-code-review-in-the-ai-era)
- Deterministic merge + least-privilege (agent-squad-hq): [pypi.org](https://pypi.org/project/agent-squad-hq/)

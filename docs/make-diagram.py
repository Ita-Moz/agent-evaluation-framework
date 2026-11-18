#!/usr/bin/env python3
"""Draw the framework overview diagram (PNG) with Pillow."""
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

W, H = 1600, 1080
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)

INK = (31, 41, 55)
GRAY = (100, 116, 139)

def wrap(text, fnt, maxw):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def box(x0, y0, x1, y1, fill, outline, title, body, tsize=18, bsize=15, tcolor=INK):
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=fill, outline=outline, width=3)
    ty = y0 + 14
    if title:
        tf = font(tsize, bold=True)
        d.text((x0 + 16, ty), title, font=tf, fill=tcolor)
        ty += tsize + 6
    bf = font(bsize)
    lh = bsize + 5
    for line in wrap(body, bf, (x1 - x0) - 32):
        d.text((x0 + 16, ty), line, font=bf, fill=INK)
        ty += lh

def arrow(x0, y0, x1, y1, color=GRAY, width=4):
    d.line([x0, y0, x1, y1], fill=color, width=width)
    # arrowhead
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    hl = 14
    for da in (math.radians(150), math.radians(-150)):
        d.line([x1, y1, x1 + hl * math.cos(ang + da), y1 + hl * math.sin(ang + da)],
               fill=color, width=width)

# ---- title ----
d.text((W // 2 - 560, 24), "Khung đánh giá coding agent — từ chọn agent đến merge an toàn",
       font=font(34, bold=True), fill=INK)

# ---- column headers ----
LX, LW = 40, 740
RX, RW = 820, 740
d.rounded_rectangle([LX, 84, LX + LW, 128], radius=12, fill=(37, 99, 235), outline=None)
d.text((LX + 18, 96), "①  ĐÁNH GIÁ  —  chọn agent nào", font=font(23, bold=True), fill="white")
d.rounded_rectangle([RX, 84, RX + RW, 128], radius=12, fill=(22, 163, 74), outline=None)
d.text((RX + 18, 96), "②  VẬN HÀNH  —  quality gate khi đã chọn", font=font(23, bold=True), fill="white")

BLUE_F = (239, 246, 255); BLUE_O = (37, 99, 235)
GRN_F = (236, 253, 245); GRN_O = (22, 163, 74)

# ---- left column boxes ----
box(LX, 148, LX+LW, 210, BLUE_F, BLUE_O, "1. Repo thật", "Các commit đã merge trước đây (dữ liệu chuẩn).")
box(LX, 226, LX+LW, 306, BLUE_F, BLUE_O, "2. Sinh dữ liệu đánh giá",
    "make-task.sh → golden tasks (test giữ riêng, agent không thấy).\nreviewer-eval → seed bugs (lỗi cố ý nhét vào diff).")
box(LX, 322, LX+LW, 386, BLUE_F, BLUE_O, "3. Chạy agent",
    "claude · codex · deepseek · gemini … qua adapter (agent-agnostic).")
box(LX, 402, LX+LW, 470, BLUE_F, BLUE_O, "4. Đo lường",
    "coder: pass-rate · chi phí · thời gian   |   reviewer: precision/recall/F1.")
box(LX, 486, LX+LW, 562, BLUE_F, BLUE_O, "5. Quyết định",
    "compare.py → chọn coder + reviewer, đặt ngưỡng confidence & tier cho gate.")

arrow(LX + LW//2, 562, LX + LW//2, 590)

# ---- right column boxes ----
box(RX, 148, RX+RW, 210, GRN_F, GRN_O, "1. Agent mở PR", "Coder đã chọn viết code, mở pull request.")
box(RX, 226, RX+RW, 306, GRN_F, GRN_O, "2. CI deterministic (không model)",
    "test · lint · build · quét secrets/SAST — bắt buộc pass.")
box(RX, 322, RX+RW, 386, GRN_F, GRN_O, "3. Phân loại rủi ro",
    "classify.py → tier: low / medium / high (auth, crypto, migration → high).")
box(RX, 402, RX+RW, 470, GRN_F, GRN_O, "4. Reviewer (model)",
    "Verdict JSON + confidence (đối kháng, có thể nhiều model).")
box(RX, 486, RX+RW, 562, GRN_F, GRN_O, "5. Quyết định merge (deterministic)",
    "decide.py: low/medium + approve + đủ confidence → auto-merge; high → chờ người.")

arrow(RX + RW//2, 562, RX + RW//2, 590)

# ---- handoff arrow left -> right ----
arrow(LX + LW, 355, RX, 355, color=(37, 99, 235), width=5)
d.text((LX + LW + 8, 366), "chọn xong → cấu hình gate", font=font(16, bold=True), fill=(37, 99, 235))

# ---- bottom band: trust ladder ----
band_y0, band_h = 640, 210
d.rounded_rectangle([40, band_y0, 1560, band_y0 + band_h], radius=14, fill=(248, 250, 252),
                    outline=(203, 213, 225), width=3)
d.text((60, band_y0 + 14), "Thang độ tin cậy (trust ladder) — luôn xếp lớp, không tin một lần LLM đơn lẻ",
       font=font(22, bold=True), fill=INK)

steps = [
    ("0", "Deterministic", "test/lint/build\nSAST (không model)"),
    ("1", "Tier rủi ro", "phân loại diff\nlàm gì rẻ, gì full"),
    ("2", "Reviewer model", "ngưỡng tin cậy\n≥ 8/10 mới duyệt"),
    ("3", "Đối kháng", "nhiều model\nbào chữa vs công kích"),
    ("4", "Bằng chứng", "ảnh/video/kiểm chứng\nhình thức (TLA+)"),
    ("5", "Human", "chỉ rủi ro cao\nauth/crypto/migration"),
]
sw = 230
gap = 16
sx = 60
sy = band_y0 + 58
for i, (num, t, b) in enumerate(steps):
    x1 = sx + sw
    accent = [(100,116,139),(37,99,235),(14,165,233),(168,85,247),(245,158,11),(220,38,38)][i]
    d.rounded_rectangle([sx, sy, x1, sy + 132], radius=12, fill="white", outline=accent, width=3)
    d.ellipse([sx+10, sy+10, sx+46, sy+46], fill=accent)
    d.text((sx+10+14, sy+14), num, font=font(22, bold=True), fill="white")
    d.text((sx+10, sy+56), t, font=font(18, bold=True), fill=INK)
    yy = sy + 78
    for ln in b.split("\n"):
        d.text((sx+10, yy), ln, font=font(15), fill=GRAY)
        yy += 19
    if i < len(steps) - 1:
        arrow(sx + sw + 4, sy + 66, sx + sw + gap - 4, sy + 66, color=(148,163,184), width=4)
    sx = x1 + gap

# ---- footer note ----
d.text((60, band_y0 + band_h + 16),
       "Cốt lõi: model chỉ đề xuất; bước deterministic quyết định merge. Đo revert-rate & precision/recall, không tin số PR đã merge.",
       font=font(17, bold=True), fill=(37, 99, 235))

out = "/Users/ita/Documents/deepseek-harness/default-workspace/agent-framework/docs/framework-overview.png"
import os
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print("saved", out)

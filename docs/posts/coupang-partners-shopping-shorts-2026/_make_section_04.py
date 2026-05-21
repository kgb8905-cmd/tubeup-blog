"""section_04.png 재제작 — TubeUp 쇼핑쇼츠 CTA 배너.
한글 글리프 깨짐 방지: Malgun Gothic Bold/Regular 직접 명시 + 텍스트 영역 사전 측정.
이모지·체크마크 등 특수 글리프 일체 미사용.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).with_name("section_04.png")
W, H = 1200, 630

# 폰트 절대 경로 — 시스템에 실존하는 파일만 사용
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_REG = "C:/Windows/Fonts/malgun.ttf"

# 색상
BG_TOP = (15, 23, 42)        # slate-900
BG_BOT = (30, 41, 89)        # slightly lighter navy
ACCENT = (34, 211, 238)      # cyan-400 (튜브업 시그니처 톤)
ACCENT_DIM = (148, 233, 245)
WHITE = (240, 248, 255)
SUB = (180, 195, 215)
PILL_BG = (51, 65, 96)
PILL_TXT = (210, 220, 235)
BTN_BG = (34, 211, 238)
BTN_TXT = (10, 20, 35)


def vgrad(w, h, top, bot):
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        r = top[0] + (bot[0] - top[0]) * y // h
        g = top[1] + (bot[1] - top[1]) * y // h
        b = top[2] + (bot[2] - top[2]) * y // h
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def rounded_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def text_center(draw, xy_center, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = xy_center[0] - tw // 2 - bbox[0]
    y = xy_center[1] - th // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)
    return tw, th


def main():
    img = vgrad(W, H, BG_TOP, BG_BOT)
    d = ImageDraw.Draw(img)

    # 우측 상단 워터마크 (TUBEUP 로고 텍스트)
    f_logo = ImageFont.truetype(FONT_BOLD, 28)
    d.text((W - 140, 36), "TUBEUP", font=f_logo, fill=ACCENT)

    # 좌측 상단 라벨 (쇼핑쇼츠 자동화)
    f_label = ImageFont.truetype(FONT_BOLD, 22)
    label_text = "쇼핑쇼츠 자동화 솔루션"
    lb = d.textbbox((0, 0), label_text, font=f_label)
    pad_x, pad_y = 18, 8
    lw = lb[2] - lb[0] + pad_x * 2
    lh = lb[3] - lb[1] + pad_y * 2
    rounded_rect(d, (60, 60, 60 + lw, 60 + lh), 18, PILL_BG)
    d.text((60 + pad_x - lb[0], 60 + pad_y - lb[1]), label_text, font=f_label, fill=ACCENT_DIM)

    # 메인 카피 (크게)
    f_main = ImageFont.truetype(FONT_BOLD, 72)
    text_center(d, (W // 2, 190), "쇼핑쇼츠, 20분이면 완성됩니다", f_main, WHITE)

    # 보조 카피
    f_sub = ImageFont.truetype(FONT_REG, 32)
    text_center(d, (W // 2, 270), "쿠팡파트너스 × AI 자동화 — 튜브업", f_sub, SUB)

    # 구분선
    d.line([(W // 2 - 180, 320), (W // 2 + 180, 320)], fill=PILL_BG, width=2)

    # 강조 포인트 3개 (필 형태, 이모지 없음)
    points = ["30~37초 최적화", "한국어 자막 자동", "BGM 자동 매칭"]
    f_pt = ImageFont.truetype(FONT_BOLD, 26)
    gap = 24
    measured = []
    total_w = 0
    for p in points:
        bb = d.textbbox((0, 0), p, font=f_pt)
        pw = bb[2] - bb[0] + 40  # padding
        measured.append((p, pw, bb))
        total_w += pw
    total_w += gap * (len(points) - 1)
    cur_x = (W - total_w) // 2
    y_pill = 370
    pill_h = 56
    for p, pw, bb in measured:
        rounded_rect(d, (cur_x, y_pill, cur_x + pw, y_pill + pill_h), 28, PILL_BG)
        text_center(d, (cur_x + pw // 2, y_pill + pill_h // 2), p, f_pt, ACCENT_DIM)
        cur_x += pw + gap

    # CTA 버튼
    f_btn = ImageFont.truetype(FONT_BOLD, 34)
    btn_text = "tubeup.kr 무료 시작"
    bbb = d.textbbox((0, 0), btn_text, font=f_btn)
    btn_w = bbb[2] - bbb[0] + 80
    btn_h = 76
    btn_x = (W - btn_w) // 2
    btn_y = 480
    rounded_rect(d, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), 38, BTN_BG)
    text_center(d, (btn_x + btn_w // 2 - 16, btn_y + btn_h // 2), btn_text, f_btn, BTN_TXT)
    # 화살표 (텍스트 우측에 단순 삼각형)
    arrow_cx = btn_x + btn_w - 36
    arrow_cy = btn_y + btn_h // 2
    d.polygon(
        [(arrow_cx - 10, arrow_cy - 12), (arrow_cx - 10, arrow_cy + 12), (arrow_cx + 12, arrow_cy)],
        fill=BTN_TXT,
    )

    # 하단 마이크로카피
    f_micro = ImageFont.truetype(FONT_REG, 20)
    text_center(d, (W // 2, 590), "쿠팡파트너스 연동 · 신용카드 없이 무료 크레딧 시작", f_micro, SUB)

    img.save(OUT, "PNG", optimize=True)
    print(f"[OK] saved: {OUT}  size={OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

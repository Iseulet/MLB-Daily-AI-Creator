"""
Pillow 스탯 카드 생성 모듈
- 선수 스탯을 시각적 카드로 생성
- 반투명 배경 + 텍스트 오버레이
- 영상 중간에 잠시 표시되는 용도
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CARD_WIDTH = 800
CARD_HEIGHT = 400
BG_COLOR = (20, 30, 60, 200)  # 반투명 네이비
ACCENT_COLOR = (255, 200, 50)  # 골드
TEXT_COLOR = (255, 255, 255)
FONT_SIZE_TITLE = 36
FONT_SIZE_STAT = 28
FONT_SIZE_LABEL = 20


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """시스템에서 사용 가능한 한국어 폰트 로드."""
    font_candidates = [
        "C:/Windows/Fonts/malgun.ttf",       # 맑은 고딕
        "C:/Windows/Fonts/NanumGothic.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for font_path in font_candidates:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()


def create_stat_card(
    player_name: str,
    stats: dict,
    output_dir: str | Path,
) -> str:
    """선수 스탯 카드 PNG 생성.

    Args:
        player_name: 선수 이름
        stats: {"타율": ".312", "홈런": "25", ...} 딕셔너리
        output_dir: 출력 디렉토리

    Returns:
        생성된 PNG 파일 경로
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    card_path = output_dir / "stat_card.png"

    img = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 둥근 배경
    draw.rounded_rectangle(
        [(0, 0), (CARD_WIDTH - 1, CARD_HEIGHT - 1)],
        radius=20,
        fill=BG_COLOR,
    )

    # 상단 악센트 라인
    draw.rectangle([(20, 15), (CARD_WIDTH - 20, 20)], fill=ACCENT_COLOR)

    # 선수 이름
    font_title = _get_font(FONT_SIZE_TITLE)
    draw.text((40, 35), player_name, font=font_title, fill=ACCENT_COLOR)

    # 스탯 항목들
    font_label = _get_font(FONT_SIZE_LABEL)
    font_stat = _get_font(FONT_SIZE_STAT)

    if stats:
        stat_items = list(stats.items())[:6]  # 최대 6개
        cols = min(3, len(stat_items))
        col_width = (CARD_WIDTH - 80) // cols
        y_start = 110

        for i, (label, value) in enumerate(stat_items):
            col = i % cols
            row = i // cols
            x = 40 + col * col_width
            y = y_start + row * 120

            draw.text((x, y), str(label), font=font_label, fill=(180, 190, 210))
            draw.text((x, y + 30), str(value), font=font_stat, fill=TEXT_COLOR)

    img.save(card_path, "PNG")
    return str(card_path)

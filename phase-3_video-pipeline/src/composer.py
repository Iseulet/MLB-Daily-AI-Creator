"""
MoviePy 영상 합성 모듈
- 배경 영상 + TTS 음성 + 자막 + 스탯 카드 합성
- 최종 출력: 1080x1920 세로 영상 (9:16)
"""

from pathlib import Path

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

from subtitle import parse_srt, group_subtitles

OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
FPS = 30


def _get_font_path() -> str:
    """자막용 한국어 폰트 경로."""
    candidates = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/NanumGothicBold.ttf",
        "C:/Windows/Fonts/gulim.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return "C:/Windows/Fonts/arial.ttf"


def _prepare_background(bg_path: str, duration: float) -> VideoFileClip:
    """배경 영상을 9:16 비율로 리사이즈/크롭하고 길이 맞춤."""
    clip = VideoFileClip(bg_path)

    # 영상 길이가 짧으면 반복
    if clip.duration < duration:
        repeats = int(duration / clip.duration) + 1
        clip = concatenate_videoclips([clip] * repeats)
    clip = clip.subclipped(0, duration)

    # 리사이즈: 세로 기준 맞춤
    w, h = clip.size
    target_ratio = OUTPUT_WIDTH / OUTPUT_HEIGHT  # 0.5625

    if w / h > target_ratio:
        # 가로가 넓으면 → 세로 기준 리사이즈 후 가로 크롭
        new_h = OUTPUT_HEIGHT
        new_w = int(w * (OUTPUT_HEIGHT / h))
        clip = clip.resized((new_w, new_h))
        x_center = new_w // 2
        clip = clip.cropped(
            x1=x_center - OUTPUT_WIDTH // 2,
            y1=0,
            x2=x_center + OUTPUT_WIDTH // 2,
            y2=OUTPUT_HEIGHT,
        )
    else:
        # 세로가 길거나 같으면 → 가로 기준 리사이즈 후 세로 크롭
        new_w = OUTPUT_WIDTH
        new_h = int(h * (OUTPUT_WIDTH / w))
        clip = clip.resized((new_w, new_h))
        y_center = new_h // 2
        clip = clip.cropped(
            x1=0,
            y1=y_center - OUTPUT_HEIGHT // 2,
            x2=OUTPUT_WIDTH,
            y2=y_center + OUTPUT_HEIGHT // 2,
        )

    return clip


def _create_subtitle_clips(srt_path: str, font_path: str) -> list:
    """SRT 자막 → TextClip 리스트."""
    entries = parse_srt(srt_path)
    grouped = group_subtitles(entries, max_chars=15)

    clips = []
    for entry in grouped:
        duration = entry["end"] - entry["start"]
        if duration <= 0:
            continue

        txt_clip = (
            TextClip(
                text=entry["text"],
                font=font_path,
                font_size=52,
                color="white",
                stroke_color="black",
                stroke_width=3,
                text_align="center",
                size=(OUTPUT_WIDTH - 100, None),
                method="caption",
            )
            .with_position(("center", OUTPUT_HEIGHT - 350))
            .with_start(entry["start"])
            .with_duration(duration)
        )
        clips.append(txt_clip)

    return clips


def _create_stat_overlay(stat_card_path: str, audio_duration: float) -> ImageClip | None:
    """스탯 카드 오버레이 (영상 중반에 3초간 표시)."""
    if not stat_card_path or not Path(stat_card_path).exists():
        return None

    show_at = max(audio_duration * 0.4, 3.0)  # 영상 40% 지점
    card = (
        ImageClip(stat_card_path)
        .resized(width=OUTPUT_WIDTH - 100)
        .with_position(("center", OUTPUT_HEIGHT // 2 - 200))
        .with_start(show_at)
        .with_duration(3.0)
    )
    return card


def compose_video(
    audio_path: str,
    bg_path: str,
    srt_path: str,
    output_path: str | Path,
    stat_card_path: str | None = None,
) -> str:
    """모든 요소를 합성하여 최종 영상 생성.

    Args:
        audio_path: TTS 음성 파일 경로
        bg_path: 배경 영상 파일 경로
        srt_path: SRT 자막 파일 경로
        output_path: 최종 영상 출력 경로
        stat_card_path: 스탯 카드 이미지 경로 (optional)

    Returns:
        최종 영상 파일 경로
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. 오디오 로드
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration  # 오디오 길이에 정확히 맞춤

    # 2. 배경 영상 준비
    bg_clip = _prepare_background(bg_path, total_duration)

    # 반투명 오버레이 (텍스트 가독성)
    dark_overlay = (
        ColorClip(size=(OUTPUT_WIDTH, OUTPUT_HEIGHT), color=(0, 0, 0))
        .with_opacity(0.3)
        .with_duration(total_duration)
    )

    # 3. 자막 클립
    font_path = _get_font_path()
    subtitle_clips = _create_subtitle_clips(srt_path, font_path)

    # 4. 합성
    layers = [bg_clip, dark_overlay] + subtitle_clips

    # 스탯 카드 (있으면)
    if stat_card_path:
        stat_clip = _create_stat_overlay(stat_card_path, audio.duration)
        if stat_clip:
            layers.append(stat_clip)

    final = CompositeVideoClip(layers, size=(OUTPUT_WIDTH, OUTPUT_HEIGHT))
    final = final.with_audio(audio)
    final = final.with_duration(total_duration)

    # 5. 인코딩
    final.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )

    # 리소스 정리
    audio.close()
    bg_clip.close()
    final.close()

    return str(output_path)

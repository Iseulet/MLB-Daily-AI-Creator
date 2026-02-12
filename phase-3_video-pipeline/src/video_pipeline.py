"""
MLB Daily AI Creator - Phase 3
영상 자동 생성 파이프라인 진입점

Usage:
    python main.py --script "대본 텍스트"
    python main.py --script-file script.json
"""

import argparse
import json
import sys
import io
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Windows 한글 출력 대응 (이미 래핑된 경우 스킵)
if sys.platform == "win32":
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if not isinstance(sys.stderr, io.TextIOWrapper) or sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from tts_engine import generate_tts
from background import download_background
from subtitle import parse_srt, group_subtitles
from graphics import create_stat_card
from composer import compose_video

# 기본 출력 디렉토리
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def run_pipeline(
    script_text: str,
    output_dir: str | Path | None = None,
    pexels_api_key: str | None = None,
    voice_type: str = "male",
    player_name: str | None = None,
    stats: dict | None = None,
    bg_query: str | None = None,
) -> str:
    """영상 생성 파이프라인 실행.

    Args:
        script_text: 대본 전체 텍스트
        output_dir: 출력 디렉토리 (None이면 기본 경로)
        pexels_api_key: Pexels API 키
        voice_type: "male" 또는 "female"
        player_name: 스탯 카드에 표시할 선수 이름
        stats: 스탯 딕셔너리
        bg_query: 배경 영상 검색 키워드

    Returns:
        최종 영상 파일 경로
    """
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_DIR / timestamp
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    work_dir = output_dir / "temp"
    work_dir.mkdir(exist_ok=True)

    # Step 1: TTS 음성 생성
    print("[1/4] TTS 음성 생성 중...")
    tts_result = generate_tts(script_text, work_dir, voice_type)
    print(f"  - 음성: {tts_result['audio_path']}")
    print(f"  - 자막: {tts_result['srt_path']}")

    # Step 2: 배경 영상 다운로드
    pexels_key = pexels_api_key or os.environ.get("PEXELS_API_KEY", "")
    if pexels_key:
        print("[2/4] 배경 영상 다운로드 중...")
        try:
            bg_path = download_background(pexels_key, work_dir, bg_query)
            print(f"  - 배경: {bg_path}")
        except Exception as e:
            print(f"  - 배경 다운로드 실패, 단색 배경 사용: {e}")
            bg_path = _create_solid_background(work_dir)
    else:
        print("[2/4] Pexels API 키 없음, 단색 배경 사용")
        bg_path = _create_solid_background(work_dir)

    # Step 3: 스탯 카드 생성
    stat_card_path = None
    if player_name and stats:
        print("[3/4] 스탯 카드 생성 중...")
        stat_card_path = create_stat_card(player_name, stats, work_dir)
        print(f"  - 카드: {stat_card_path}")
    else:
        print("[3/4] 스탯 카드 스킵 (선수 정보 없음)")

    # Step 4: 영상 합성
    print("[4/4] 영상 합성 중...")
    final_path = output_dir / "output.mp4"
    result = compose_video(
        audio_path=tts_result["audio_path"],
        bg_path=bg_path,
        srt_path=tts_result["srt_path"],
        output_path=final_path,
        stat_card_path=stat_card_path,
    )
    print(f"  - 완성: {result}")
    return result


def _create_solid_background(work_dir: Path) -> str:
    """Pexels 키가 없을 때 단색 배경 영상 생성."""
    from moviepy import ColorClip
    bg_path = work_dir / "background.mp4"
    clip = ColorClip(size=(1080, 1920), color=(15, 25, 55), duration=120)
    clip.write_videofile(str(bg_path), fps=30, codec="libx264", audio=False, logger=None)
    clip.close()
    return str(bg_path)


def main():
    parser = argparse.ArgumentParser(description="MLB 숏폼 영상 자동 생성")
    parser.add_argument("--script", type=str, help="대본 텍스트 (직접 입력)")
    parser.add_argument("--script-file", type=str, help="대본 JSON 파일 경로")
    parser.add_argument("--voice", type=str, default="male", choices=["male", "female"])
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--pexels-key", type=str, default=None)
    parser.add_argument("--bg-query", type=str, default=None)
    args = parser.parse_args()

    # 대본 텍스트 결정
    if args.script:
        script_text = args.script
        player_name = None
        stats = None
    elif args.script_file:
        with open(args.script_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        script_text = data.get("full_script", "")
        meta = data.get("_meta", {})
        player_name = meta.get("player_name")
        stats = meta.get("stats")
    else:
        print("--script 또는 --script-file 중 하나를 지정하세요.")
        sys.exit(1)

    if not script_text.strip():
        print("대본 텍스트가 비어있습니다.")
        sys.exit(1)

    result = run_pipeline(
        script_text=script_text,
        output_dir=args.output_dir,
        pexels_api_key=args.pexels_key,
        voice_type=args.voice,
        player_name=player_name,
        stats=stats,
        bg_query=args.bg_query,
    )
    print(f"\n영상 생성 완료: {result}")


if __name__ == "__main__":
    main()

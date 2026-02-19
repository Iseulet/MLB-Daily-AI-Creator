"""
MLB Daily AI Creator - 전체 파이프라인 오케스트레이터
DB조회 → 대본 → 영상 → 메타데이터 → YouTube 업로드 → 히스토리 저장

Usage:
    python full_pipeline.py --auto --tone 유머러스 --duration 30 --voice male --privacy private
    python full_pipeline.py --auto --skip-upload
"""

import argparse
import io
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable
from supabase import create_client, Client

# Windows 한글 출력 대응 (이미 래핑된 경우 스킵)
if sys.platform == "win32":
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if not isinstance(sys.stderr, io.TextIOWrapper) or sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 각 Phase src를 import 경로에 추가
# sys.path.insert(0, str(PROJECT_ROOT / "phase-1_research-automation" / "src")) # 의존성 제거
sys.path.insert(0, str(PROJECT_ROOT / "phase-2_app-prototype"))
sys.path.insert(0, str(PROJECT_ROOT / "phase-3_video-pipeline" / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "phase-4_integration" / "src"))

from pipeline_config import load_all_env, get_config, validate_config

# 환경변수 로드
load_all_env()


# ── 데이터 클래스 ──

@dataclass
class PipelineOptions:
    """파이프라인 실행 옵션."""
    tone: str = "유머러스"
    duration: int = 30
    voice: str = "male"
    news_rank: int = 1          # 뉴스 순위 (1-based)
    privacy: str = "private"    # YouTube 공개 설정
    skip_upload: bool = False
    # skip_email: bool = False # 의존성 제거


@dataclass
class PipelineResult:
    """파이프라인 실행 결과."""
    success: bool = False
    news_data: dict = field(default_factory=dict)
    selected_news: dict = field(default_factory=dict)
    script: dict = field(default_factory=dict)
    video_path: str = ""
    metadata: dict = field(default_factory=dict)
    upload_result: dict = field(default_factory=dict)
    history_path: str = ""
    errors: list = field(default_factory=list)
    stages_completed: list = field(default_factory=list)


# 콜백 타입: callback(stage_name, status, message)
StageCallback = Callable[[str, str, str], None]


def _noop_callback(stage: str, status: str, message: str) -> None:
    """기본 콜백 (아무것도 하지 않음)."""
    pass


def _print_callback(stage: str, status: str, message: str) -> None:
    """CLI용 콜백 (stdout 출력)."""
    icon = {"start": "⏳", "done": "✅", "error": "❌", "skip": "⏭️"}.get(status, "ℹ️")
    print(f"  {icon} [{stage}] {message}")


# ── 개별 스테이지 ──

def stage_fetch_news(config: dict, callback: StageCallback) -> dict:
    """Supabase에서 오늘 날짜의 뉴스 데이터 조회."""
    callback("research", "start", "Supabase에서 뉴스 데이터 조회 중...")
    
    url = config.get("SUPABASE_URL")
    key = config.get("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables.")

    supabase: Client = create_client(url, key)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    response = supabase.table("mlb_news").select("*").eq("date", today_str).single().execute()
    
    if not response.data:
        raise FileNotFoundError(f"Supabase에 오늘 날짜({today_str})의 뉴스 데이터가 없습니다.")
        
    news_data = response.data
    count = len(news_data.get("news", {}).get("main_news", []))
    callback("research", "done", f"뉴스 {count}건 조회 완료")
    return news_data


def stage_script(
    config: dict, news: dict, options: PipelineOptions, callback: StageCallback
) -> dict:
    """Phase 2: 숏폼 대본 생성."""
    callback("script", "start", f"대본 생성 중... (말투: {options.tone}, {options.duration}초)")

    from script_generator import generate_script
    script = generate_script(
        api_key=config["GEMINI_API_KEY"],
        news=news,
        tone=options.tone,
        duration=options.duration,
    )

    callback("script", "done", "대본 생성 완료")
    return script


def stage_video(
    config: dict, script: dict, news: dict, options: PipelineOptions, callback: StageCallback
) -> str:
    """Phase 3: 영상 생성."""
    callback("video", "start", f"영상 생성 중... (음성: {options.voice})")

    from video_pipeline import run_pipeline
    players = news.get("players", [])
    player_name = players[0] if players else None
    stats = news.get("stats", None)

    video_path = run_pipeline(
        script_text=script.get("full_script", ""),
        output_dir=None,
        pexels_api_key=config.get("PEXELS_API_KEY", ""),
        voice_type=options.voice,
        player_name=player_name,
        stats=stats if isinstance(stats, dict) else None,
    )

    callback("video", "done", f"영상 생성 완료: {video_path}")
    return video_path


def stage_metadata(
    config: dict, script: dict, news: dict, callback: StageCallback
) -> dict:
    """Phase 4: 메타데이터 생성."""
    callback("metadata", "start", "메타데이터 생성 중...")

    from metadata_generator import generate_metadata
    metadata = generate_metadata(
        api_key=config["GEMINI_API_KEY"],
        script_text=script.get("full_script", ""),
        headline=news.get("headline", ""),
    )

    callback("metadata", "done", "메타데이터 생성 완료")
    return metadata


def stage_upload(
    video_path: str, metadata: dict, options: PipelineOptions, callback: StageCallback
) -> dict:
    """Phase 4: YouTube 업로드."""
    callback("upload", "start", f"YouTube 업로드 중... (공개: {options.privacy})")

    from youtube_uploader import upload_to_youtube
    yt_meta = metadata.get("youtube", {})
    today = datetime.now().strftime("%Y-%m-%d")

    result = upload_to_youtube(
        video_path=video_path,
        title=yt_meta.get("title", f"MLB 숏폼 - {today}"),
        description=yt_meta.get("description", ""),
        tags=yt_meta.get("tags", []),
        privacy=options.privacy,
    )

    callback("upload", "done", f"업로드 완료: {result.get('url', '')}")
    return result


def stage_history(
    news: dict, video_path: str, upload_result: dict | None,
    metadata: dict | None, options: PipelineOptions, callback: StageCallback
) -> str:
    """히스토리 저장."""
    callback("history", "start", "히스토리 저장 중...")

    from history import save_history
    today = datetime.now().strftime("%Y-%m-%d")

    path = save_history(
        date=today,
        headline=news.get("headline", ""),
        video_path=video_path,
        upload_result=upload_result,
        metadata=metadata,
        tone=options.tone,
        duration=options.duration,
    )

    callback("history", "done", "히스토리 저장 완료")
    return path


# ── 메인 파이프라인 ──

def run_full_pipeline(
    options: PipelineOptions | None = None,
    callback: StageCallback | None = None,
) -> PipelineResult:
    """전체 파이프라인 실행.

    6개 스테이지를 순차 실행:
        research → script → video → metadata → upload → history

    Args:
        options: 파이프라인 옵션 (None이면 기본값)
        callback: 진행 상황 콜백 (stage, status, message)

    Returns:
        PipelineResult 객체
    """
    if options is None:
        options = PipelineOptions()
    if callback is None:
        callback = _noop_callback

    config = get_config()
    result = PipelineResult()

    # 필수 키 검증
    required = ["GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    if not options.skip_upload:
        pass  # YouTube는 OAuth 기반, API 키 불필요
    missing = validate_config(config, required)
    if missing:
        result.errors.append(f"필수 환경변수 누락: {', '.join(missing)}")
        callback("config", "error", f"환경변수 누락: {', '.join(missing)}")
        return result

    # ── Stage 1: Fetch News (from Supabase) ──
    try:
        news_data = stage_fetch_news(config, callback)
        result.news_data = news_data
        result.stages_completed.append("research")
    except Exception as e:
        result.errors.append(f"뉴스 조회 실패: {e}")
        callback("research", "error", f"뉴스 조회 실패: {e}")
        return result

    # 뉴스 선택
    main_news = news_data.get("news", {}).get("main_news", [])
    if not main_news:
        result.errors.append("수집된 뉴스가 없습니다")
        callback("research", "error", "수집된 메인 뉴스가 없습니다")
        return result

    rank_idx = min(options.news_rank - 1, len(main_news) - 1)
    rank_idx = max(0, rank_idx)
    selected_news = main_news[rank_idx]
    result.selected_news = selected_news

    # ── Stage 2: Script ──
    try:
        # 대본 생성 시 전체 뉴스 데이터(트랜잭션 등)를 함께 전달할 수 있도록 확장 가능
        script = stage_script(config, selected_news, options, callback)
        result.script = script
        result.stages_completed.append("script")
    except Exception as e:
        result.errors.append(f"대본 생성 실패: {e}")
        callback("script", "error", f"대본 생성 실패: {e}")
        return result

    # ── Stage 3: Video ──
    try:
        video_path = stage_video(config, script, selected_news, options, callback)
        result.video_path = video_path
        result.stages_completed.append("video")
    except Exception as e:
        result.errors.append(f"영상 생성 실패: {e}")
        callback("video", "error", f"영상 생성 실패: {e}")
        return result

    # 핵심 3단계 완료 → success=True
    result.success = True

    # ── Stage 4: Metadata ──
    try:
        metadata = stage_metadata(config, script, selected_news, callback)
        result.metadata = metadata
        result.stages_completed.append("metadata")
    except Exception as e:
        result.errors.append(f"메타데이터 생성 실패 (계속 진행): {e}")
        callback("metadata", "error", f"메타데이터 생성 실패: {e}")
        metadata = {}

    # ── Stage 5: Upload ──
    if options.skip_upload:
        callback("upload", "skip", "업로드 스킵 (--skip-upload)")
    else:
        try:
            upload_result = stage_upload(video_path, metadata, options, callback)
            result.upload_result = upload_result
            result.stages_completed.append("upload")
        except Exception as e:
            result.errors.append(f"YouTube 업로드 실패: {e}")
            callback("upload", "error", f"YouTube 업로드 실패: {e}")

    # ── Stage 6: History ──
    try:
        history_path = stage_history(
            selected_news, video_path,
            result.upload_result or None,
            result.metadata or None,
            options, callback,
        )
        result.history_path = history_path
        result.stages_completed.append("history")
    except Exception as e:
        result.errors.append(f"히스토리 저장 실패 (비치명적): {e}")
        callback("history", "error", f"히스토리 저장 실패: {e}")

    return result


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(
        description="MLB Daily AI Creator - 전체 파이프라인 (원클릭 실행)"
    )
    parser.add_argument("--auto", action="store_true", help="자동 실행 모드")
    parser.add_argument("--tone", type=str, default="유머러스",
                        choices=["유머러스", "분석적", "열정적"], help="대본 말투")
    parser.add_argument("--duration", type=int, default=30,
                        choices=[30, 45, 60], help="영상 길이 (초)")
    parser.add_argument("--voice", type=str, default="male",
                        choices=["male", "female"], help="TTS 음성")
    parser.add_argument("--news-rank", type=int, default=1, help="뉴스 순위 (1=1위)")
    parser.add_argument("--privacy", type=str, default="private",
                        choices=["private", "unlisted", "public"], help="YouTube 공개 설정")
    parser.add_argument("--skip-upload", action="store_true", help="YouTube 업로드 스킵")
    # parser.add_argument("--skip-email", action="store_true", help="이메일 발송 스킵") # 의존성 제거
    args = parser.parse_args()

    if not args.auto:
        print("전체 파이프라인을 실행하려면 --auto 플래그를 추가하세요.")
        print("예: python full_pipeline.py --auto --skip-upload")
        parser.print_help()
        sys.exit(1)

    print("=" * 60)
    print("  MLB Daily AI Creator - 전체 파이프라인")
    print("=" * 60)
    print(f"  옵션: 말투={args.tone}, 길이={args.duration}초, 음성={args.voice}")
    print(f"  업로드: {'스킵' if args.skip_upload else args.privacy}")
    print("=" * 60)

    options = PipelineOptions(
        tone=args.tone,
        duration=args.duration,
        voice=args.voice,
        news_rank=args.news_rank,
        privacy=args.privacy,
        skip_upload=args.skip_upload,
        # skip_email=args.skip_email, # 의존성 제거
    )

    result = run_full_pipeline(options, callback=_print_callback)

    print("\n" + "=" * 60)
    if result.success:
        print("  ✅ 파이프라인 완료!")
        print(f"  영상: {result.video_path}")
        if result.upload_result:
            print(f"  YouTube: {result.upload_result.get('url', '')}")
        print(f"  완료된 스테이지: {', '.join(result.stages_completed)}")
    else:
        print("  ❌ 파이프라인 실패")

    if result.errors:
        print("\n  에러:")
        for err in result.errors:
            print(f"    - {err}")
    print("=" * 60)

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()

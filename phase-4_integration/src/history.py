"""
히스토리 관리 모듈
- 생성/업로드된 영상 기록 관리
- JSON 파일 기반 저장
"""

import json
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"


def save_history(
    date: str,
    headline: str,
    video_path: str,
    upload_result: dict | None = None,
    metadata: dict | None = None,
    tone: str = "",
    duration: int = 0,
) -> str:
    """영상 생성/업로드 기록 저장.

    Returns:
        저장된 히스토리 파일 경로
    """
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "date": date,
        "headline": headline,
        "video_path": video_path,
        "tone": tone,
        "duration": duration,
        "created_at": datetime.now().isoformat(),
        "upload": upload_result,
        "metadata": metadata,
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{date}_{timestamp}.json"
    filepath = HISTORY_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

    return str(filepath)


def get_history(limit: int = 50) -> list[dict]:
    """히스토리 목록 조회 (최신순).

    Returns:
        히스토리 항목 리스트
    """
    if not HISTORY_DIR.exists():
        return []

    files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)[:limit]
    entries = []

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                data["_filename"] = f.name
                entries.append(data)
        except (json.JSONDecodeError, IOError):
            continue

    return entries


def get_history_by_date(date: str) -> list[dict]:
    """특정 날짜의 히스토리 조회."""
    if not HISTORY_DIR.exists():
        return []

    files = sorted(HISTORY_DIR.glob(f"{date}_*.json"), reverse=True)
    entries = []

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                data["_filename"] = f.name
                entries.append(data)
        except (json.JSONDecodeError, IOError):
            continue

    return entries

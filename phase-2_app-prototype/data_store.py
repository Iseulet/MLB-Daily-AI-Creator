"""
뉴스/대본 데이터 저장 및 조회
- Phase 1 outputs에서 뉴스 JSON 읽기
- 생성된 대본 저장/조회
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Phase 1 outputs 경로 (상대)
PHASE1_OUTPUTS = Path(__file__).resolve().parent.parent / "phase-1_research-automation" / "outputs"
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
SCRIPTS_DIR.mkdir(exist_ok=True)


def get_available_dates(limit: int = 14) -> list[str]:
    """뉴스 JSON이 있는 날짜 목록 반환 (최신순)."""
    if not PHASE1_OUTPUTS.exists():
        return []
    dates = []
    for f in sorted(PHASE1_OUTPUTS.glob("*.json"), reverse=True):
        dates.append(f.stem)
        if len(dates) >= limit:
            break
    return dates


def get_news(date: str) -> dict | None:
    """특정 날짜의 뉴스 JSON 반환."""
    path = PHASE1_OUTPUTS / f"{date}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_script(date: str, news_rank: int, script_data: dict) -> str:
    """생성된 대본 저장. 파일 경로 반환."""
    ts = datetime.now().strftime("%H%M%S")
    filename = f"{date}_news{news_rank}_{ts}.json"
    path = SCRIPTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    return str(path)


def get_scripts(date: str | None = None) -> list[dict]:
    """저장된 대본 목록 반환. date 지정 시 해당 날짜만."""
    scripts = []
    for f in sorted(SCRIPTS_DIR.glob("*.json"), reverse=True):
        if date and not f.stem.startswith(date):
            continue
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            data["_filename"] = f.name
            scripts.append(data)
    return scripts

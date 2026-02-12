"""
Pexels API 배경 영상 다운로드 모듈
- 무료 API, CC 라이선스
- 야구/스포츠 관련 영상 검색
- 세로 영상(9:16) 우선 검색
"""

import os
import requests
from pathlib import Path

PEXELS_API_URL = "https://api.pexels.com/videos/search"

SEARCH_QUERIES = [
    "baseball stadium",
    "baseball game",
    "baseball player",
    "sports stadium night",
    "baseball field",
]


def search_videos(api_key: str, query: str, per_page: int = 5) -> list[dict]:
    """Pexels에서 영상 검색."""
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "portrait",
        "size": "medium",
    }
    resp = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("videos", [])


def _pick_best_file(video: dict) -> str | None:
    """영상에서 적절한 해상도의 다운로드 URL 선택."""
    files = video.get("video_files", [])
    # HD 세로 영상 우선
    for f in files:
        w, h = f.get("width", 0), f.get("height", 0)
        if h >= 1080 and w < h:
            return f["link"]
    # HD 가로 영상
    for f in files:
        w, h = f.get("width", 0), f.get("height", 0)
        if h >= 720:
            return f["link"]
    # 아무거나
    if files:
        return files[0]["link"]
    return None


def download_background(api_key: str, output_dir: str | Path, query: str | None = None) -> str:
    """배경 영상 검색 및 다운로드.

    Args:
        api_key: Pexels API key
        output_dir: 저장 디렉토리
        query: 검색 키워드 (None이면 기본 키워드 순회)

    Returns:
        다운로드된 영상 파일 경로
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bg_path = output_dir / "background.mp4"

    queries = [query] if query else SEARCH_QUERIES

    for q in queries:
        try:
            videos = search_videos(api_key, q)
            for video in videos:
                url = _pick_best_file(video)
                if url:
                    resp = requests.get(url, timeout=60, stream=True)
                    resp.raise_for_status()
                    with open(bg_path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return str(bg_path)
        except Exception:
            continue

    raise RuntimeError("배경 영상을 다운로드할 수 없습니다. Pexels API 키를 확인하세요.")

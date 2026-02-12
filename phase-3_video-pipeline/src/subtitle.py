"""
SRT 자막 파싱 → MoviePy 자막 클립 생성 모듈
- Edge TTS가 출력하는 SRT 파일에서 타임스탬프 추출
- MoviePy TextClip 리스트 생성
"""

import re
from pathlib import Path


def parse_srt(srt_path: str | Path) -> list[dict]:
    """SRT 자막 파일 파싱.

    Returns:
        [{"start": float, "end": float, "text": str}, ...]
    """
    srt_path = Path(srt_path)
    content = srt_path.read_text(encoding="utf-8")

    entries = []
    # SRT 패턴: 숫자\n00:00:00,000 --> 00:00:02,500\n텍스트
    pattern = re.compile(
        r"\d+\s*\n(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n(.+?)(?=\n\n|\n\d+\s*\n|\Z)",
        re.DOTALL,
    )

    for m in pattern.finditer(content):
        start = _time_to_seconds(m.group(1))
        end = _time_to_seconds(m.group(2))
        text = m.group(3).strip()
        if text:
            entries.append({"start": start, "end": end, "text": text})

    return entries


def _time_to_seconds(time_str: str) -> float:
    """HH:MM:SS,mmm 또는 HH:MM:SS.mmm → 초 변환."""
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    h, m = int(parts[0]), int(parts[1])
    s = float(parts[2])
    return h * 3600 + m * 60 + s


def group_subtitles(entries: list[dict], max_chars: int = 20) -> list[dict]:
    """짧은 자막을 묶어서 자연스러운 단위로 그룹핑.

    Edge TTS는 단어 단위로 쪼개므로, 적절한 길이로 합침.
    """
    if not entries:
        return []

    grouped = []
    current = {
        "start": entries[0]["start"],
        "end": entries[0]["end"],
        "text": entries[0]["text"],
    }

    for entry in entries[1:]:
        combined = current["text"] + " " + entry["text"]
        if len(combined) <= max_chars:
            current["end"] = entry["end"]
            current["text"] = combined
        else:
            grouped.append(current)
            current = {
                "start": entry["start"],
                "end": entry["end"],
                "text": entry["text"],
            }

    grouped.append(current)
    return grouped

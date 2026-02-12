"""
Edge TTS 음성 생성 모듈
- Microsoft Edge TTS (무료, 무제한)
- 한국어 뉴럴 음성 지원
- 음성 MP3 + 자막 VTT 동시 출력
"""

import asyncio
import edge_tts
from pathlib import Path

VOICES = {
    "female": "ko-KR-SunHiNeural",
    "male": "ko-KR-InJoonNeural",
}


async def _generate(text: str, output_dir: Path, voice: str) -> dict:
    """Edge TTS로 음성 + 자막 생성 (async)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / "tts_audio.mp3"
    srt_path = output_dir / "tts_subtitle.srt"

    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()

    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(submaker.get_srt())

    return {
        "audio_path": str(audio_path),
        "srt_path": str(srt_path),
    }


def generate_tts(
    text: str,
    output_dir: str | Path,
    voice_type: str = "male",
) -> dict:
    """대본 텍스트 → MP3 음성 + VTT 자막 생성.

    Args:
        text: 대본 전체 텍스트
        output_dir: 출력 디렉토리
        voice_type: "male" 또는 "female"

    Returns:
        {"audio_path": str, "srt_path": str}
    """
    voice = VOICES.get(voice_type, VOICES["male"])
    output_dir = Path(output_dir)
    return asyncio.run(_generate(text, output_dir, voice))

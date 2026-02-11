"""
Gemini API로 MLB 숏폼 대본 생성
- 3가지 말투: 유머러스, 분석적, 열정적
- 3가지 길이: 30초, 45초, 60초
"""

import json
import re

from google import genai
from google.genai import types

TONE_PROMPTS = {
    "유머러스": "당신은 유머감각이 넘치는 MLB 유튜브 크리에이터입니다. 친근하고 유머러스하게, 드립과 비유를 활용하세요.",
    "분석적": "당신은 데이터 중심의 MLB 분석 전문가입니다. 객관적이고 분석적으로, 수치와 비교를 강조하세요.",
    "열정적": "당신은 열정적인 MLB 스포츠 캐스터입니다. 에너지 넘치는 실황 중계 스타일로 작성하세요.",
}

DURATION_WORDS = {
    30: 90,
    45: 135,
    60: 180,
}

SCRIPT_PROMPT = """\
{tone_description}

다음 MLB 뉴스를 기반으로 유튜브 쇼츠/릴스 대본을 작성해주세요.

뉴스:
- 제목: {headline}
- 요약: {summary}
- 선수: {players}
- 스탯: {stats}

조건:
- 길이: {duration}초 분량 (약 {word_count}단어 기준)
- 구조: 훅(첫 5초, 시청자를 사로잡는 한마디) -> 본문(핵심 내용) -> 마무리(구독/좋아요 유도)
- 핵심 스탯을 자연스럽게 포함
- 한국어로 작성

아래 JSON 형식으로만 출력하세요:

{{
  "hook": "첫 5초 대사 (시청자를 사로잡는 한마디)",
  "body": "본문 대사 (핵심 내용 전달)",
  "closing": "마무리 대사 (구독/좋아요 유도)",
  "full_script": "전체 대본 (hook + body + closing을 자연스럽게 이어붙인 것)",
  "estimated_duration": {duration},
  "suggested_hashtags": ["#태그1", "#태그2", "#태그3", "#태그4", "#태그5"]
}}
"""


def generate_script(
    api_key: str,
    news: dict,
    tone: str = "유머러스",
    duration: int = 30,
) -> dict:
    """뉴스 + 옵션으로 숏폼 대본 생성."""
    client = genai.Client(api_key=api_key)

    prompt = SCRIPT_PROMPT.format(
        tone_description=TONE_PROMPTS.get(tone, TONE_PROMPTS["유머러스"]),
        headline=news.get("headline", ""),
        summary=news.get("summary", ""),
        players=", ".join(news.get("players", [])) or "없음",
        stats=json.dumps(news.get("stats", {}), ensure_ascii=False) or "없음",
        duration=duration,
        word_count=DURATION_WORDS.get(duration, 90),
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=2048,
        ),
    )

    raw_text = response.text.strip()
    json_match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
    json_str = json_match.group(1) if json_match else raw_text

    data = json.loads(json_str)

    # 메타데이터 추가
    data["_meta"] = {
        "news_headline": news.get("headline", ""),
        "tone": tone,
        "duration": duration,
    }
    return data

"""
Gemini API를 사용한 MLB 뉴스 리서치 엔진 (google-genai SDK)
- Google Search grounding으로 실시간 뉴스 수집
- JSON 형식으로 파싱 및 검증
"""

import json
import re
import time
from datetime import datetime

from google import genai
from google.genai import types

MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]


RESEARCH_PROMPT = """\
당신은 MLB 전문 스포츠 기자입니다.
오늘 날짜: {date}

어제 밤~오늘 새벽 MLB 관련 최신 뉴스와 경기 결과를 분석해주세요.
(시즌 중이 아니면 오프시즌 뉴스, 스프링트레이닝, FA, 트레이드 등을 다뤄주세요.)

아래 JSON 형식으로만 출력하세요 (JSON 외 텍스트 금지):

{{
  "date": "{date}",
  "top_news": [
    {{
      "rank": 1,
      "headline": "한줄 제목",
      "summary": "3줄 이내 요약",
      "players": ["선수명1"],
      "stats": {{"관련 스탯 키": "값"}},
      "shorts_potential": "high | medium | low"
    }},
    {{
      "rank": 2,
      "headline": "...",
      "summary": "...",
      "players": [],
      "stats": {{}},
      "shorts_potential": "medium"
    }},
    {{
      "rank": 3,
      "headline": "...",
      "summary": "...",
      "players": [],
      "stats": {{}},
      "shorts_potential": "low"
    }}
  ],
  "korean_players": [
    {{
      "name": "선수명",
      "team": "팀명",
      "result": "경기 결과 또는 최신 동향",
      "highlight": "핵심 포인트"
    }}
  ],
  "recommended_shorts_topic": {{
    "topic": "숏폼 영상 주제",
    "reason": "추천 이유",
    "script_hook": "영상 첫 5초에 쓸 수 있는 후킹 멘트"
  }}
}}
"""


def research_mlb_news(api_key: str) -> dict:
    """Gemini API로 MLB 뉴스를 수집하고 JSON으로 반환한다."""
    client = genai.Client(api_key=api_key)

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = RESEARCH_PROMPT.format(date=today)

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                print(f"  [{model_name}] 시도 {attempt + 1}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=4096,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                    ),
                )
                raw_text = response.text.strip()

                json_match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
                json_str = json_match.group(1) if json_match else raw_text

                data = json.loads(json_str)
                _validate(data)
                return data

            except Exception as e:
                last_error = e
                print(f"  [WARN] {model_name} 시도 {attempt + 1} 실패: {e}")
                if "429" in str(e) and attempt == 0:
                    print("  60초 대기 후 재시도...")
                    time.sleep(60)

    raise RuntimeError(f"Gemini 리서치 실패: {last_error}")


def _validate(data: dict) -> None:
    """응답 JSON 구조 최소 검증."""
    assert "top_news" in data, "top_news 필드 누락"
    assert isinstance(data["top_news"], list), "top_news가 리스트가 아님"
    assert len(data["top_news"]) >= 1, "뉴스가 최소 1개 이상 필요"

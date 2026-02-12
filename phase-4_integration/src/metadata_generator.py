"""
Gemini API로 업로드 메타데이터 자동 생성
- YouTube 제목/설명/태그
- Instagram 캡션/해시태그
- Twitter 트윗 텍스트
"""

import json
import re

from google import genai
from google.genai import types

METADATA_PROMPT = """\
다음 MLB 숏폼 대본을 기반으로 각 소셜 미디어 플랫폼에 맞는 업로드 메타데이터를 생성해주세요.

대본:
{script}

뉴스 제목: {headline}

조건:
- YouTube 제목은 50자 이내, 클릭을 유도하는 제목
- YouTube 설명에 #Shorts 태그 포함
- Instagram 캡션은 이모지 활용, 해시태그 10개
- Twitter는 280자 이내

아래 JSON 형식으로만 출력하세요:

{{
  "youtube": {{
    "title": "영상 제목",
    "description": "영상 설명\\n\\n#Shorts #MLB",
    "tags": ["MLB", "야구", "오타니", "숏폼"]
  }},
  "instagram": {{
    "caption": "인스타그램 캡션 텍스트",
    "hashtags": ["#MLB", "#야구", "#숏폼"]
  }},
  "twitter": {{
    "tweet_text": "트위터 텍스트"
  }}
}}
"""


def generate_metadata(
    api_key: str,
    script_text: str,
    headline: str = "",
) -> dict:
    """대본 기반 업로드 메타데이터 생성.

    Args:
        api_key: Gemini API key
        script_text: 대본 전체 텍스트
        headline: 뉴스 제목

    Returns:
        {"youtube": {...}, "instagram": {...}, "twitter": {...}}
    """
    client = genai.Client(api_key=api_key)

    prompt = METADATA_PROMPT.format(
        script=script_text,
        headline=headline,
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1024,
        ),
    )

    raw_text = response.text.strip()
    json_match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
    json_str = json_match.group(1) if json_match else raw_text

    return json.loads(json_str)

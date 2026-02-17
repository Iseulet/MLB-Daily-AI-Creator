import os
import json
import time
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# NOTE: JSON 예시의 중괄호 {{}}는 Python str.format()과 충돌하므로 {{ }}로 이스케이프.
RESEARCH_PROMPT = """
당신은 메이저리그(MLB) 데이터를 엄격하게 검증하는 뉴스 리포터입니다.
주어진 시간 범위 내의 MLB 뉴스, 루머, 로스터 이동, 유망주 소식을 수집하여 아래 섹션별로 정리해주세요.

## [데이터 검색 및 수집 엄격 규칙] (CRITICAL - VIOLATION IS NOT ALLOWED)

1.  **검색 연산자 강제 사용**:
    - 검색 시 반드시 날짜 제한 연산자를 포함하세요. (예: `MLB news after:{start_date_only}`)
    - '최신순' 정렬 데이터를 우선 확인하세요.

2.  **데이터 무결성 검증 (Data Integrity)**:
    - **내용-날짜 일치 확인**: 기사 내용이 과거에 이미 종결된 사건(예: 수년 전의 연장 계약, 이미 복귀한 선수의 옛 부상 소식 등)인지 반드시 내부 지식과 대조하세요.
    - **날짜 날조 금지 (No Date Fabrication)**: 기사 원문의 메타데이터에 기록된 **실제 발행 연도**를 확인하세요. 만약 **{current_year}년**이 아닌 기사라면, 절대 날짜를 {current_year}년으로 바꾸어 출력하지 말고 **즉시 폐기(Discard)**하세요.
    - **이중 타임스탬프 검증**: 수집된 기사의 `published_at`이 {start_time} ~ {end_time} (KST) 범위를 벗어나면 폐기하세요.

3.  **최소 정보 원칙 (Minimum Information Principle)**:
    - 지난 24시간 이내의 "새로운(New)" 소식이 없다면 해당 섹션은 비워두거나 빈 리스트(`[]`)로 반환하세요.
    - **과거 기사를 최신인 것처럼 속여 보고하는 것은 치명적인 오류입니다.**

4.  **시스템 변수**:
    - CURRENT_YEAR: {current_year}
    - CURRENT_DATE: {current_date_str}
    - SEARCH_WINDOW: {start_time} ~ {end_time}

## 섹션별 작성 지침

### 1. 핵심 뉴스 (main_news)
- **내용**: 오늘({start_time} 이후) 발생한 가장 중요한 MLB 뉴스 10개를 선정합니다.
- **포함 대상**: 경기 결과, 주요 기록, 부상 소식, 인터뷰 등.
- **한국 선수**: 중요도에 따라 포함.
- **요약 방식**: "현상의 원인"이나 "향후 영향"을 포함하여 깊이 있게 요약. (한국어)
- **번역 규칙**: 팀명/선수명 **한국어** 표기.
- **필수 필드**: `headline`, `summary`, `published_at` (YYYY-MM-DD HH:MM), `source`, `source_url`

### 2. 선수 이동 (transactions)
- **조건**: 해당 내용이 없으면 빈 리스트.
- **포함 대상**: 공식 이적/계약, 루머, 로스터 변경.
- **필수 필드**: `headline`, `summary`, `type`, `published_at`

### 3. 유망주 (prospects)
- **조건**: 해당 내용이 없으면 빈 리스트.
- **포함 대상**: Top 5 유망주 콜업 소식.
- **필수 필드**: `headline`, `summary`, `team`, `player_name`, `published_at`

## 출력 형식 (JSON)
```json
{{
  "retrieved_at": "YYYY-MM-DD HH:MM",
  "data_reference_time": "{start_time} ~ {end_time}",
  "main_news": [
    {{
      "rank": 1,
      "headline": "...",
      "summary": "...",
      "published_at": "YYYY-MM-DD HH:MM",
      "source": "...",
      "source_url": "..."
    }}
  ],
  "transactions": [ ... ],
  "prospects": [ ... ]
}}
```
"""

def research_mlb_news(api_key: str) -> dict:
    # Use google.genai Client
    client = genai.Client(api_key=api_key)
    
    # 1. 7AM - 7AM 시간 윈도우 계산
    now = datetime.now()
    today_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    
    if now >= today_7am:
        end_time = today_7am
        start_time = end_time - timedelta(days=1)
    else:
        end_time = today_7am
        start_time = end_time - timedelta(days=1)

    start_str = start_time.strftime("%Y-%m-%d %H:%M")
    end_str = end_time.strftime("%Y-%m-%d %H:%M")
    current_date_str = now.strftime("%Y-%m-%d %H:%M")
    current_year = now.year
    start_date_only = start_time.strftime("%Y-%m-%d")

    print(f"[INFO] 검색 윈도우: {start_str} ~ {end_str}")

    full_prompt = RESEARCH_PROMPT.format(
        start_time=start_str, 
        end_time=end_str,
        current_date_str=current_date_str,
        current_year=current_year,
        start_date_only=start_date_only
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.8,
                top_k=40,
                max_output_tokens=8192,
                tools=[types.Tool(
                    google_search=types.GoogleSearch()
                )]
            )
        )
        
        text_response = response.text.strip()
        
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        try:
            data = json.loads(text_response)
        except json.JSONDecodeError as e:
             print(f"[ERROR] JSON Decode Error: {e}")
             print(f"[DEBUG] Full Raw Response: {text_response}")
             return {"main_news": [], "transactions": [], "prospects": []}
                
        _validate(data)
        
        # 2차: Python Level 날짜 필터링 (Double Verification)
        _filter_by_date_window(data, start_time, end_time)
        
        return data

    except Exception as e:
        print(f"[ERROR] Gemini API 호출 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {"main_news": [], "transactions": [], "prospects": []}

def _validate(data: dict) -> None:
    required_keys = ["main_news", "transactions", "prospects"]
    for key in required_keys:
        if key not in data:
            data[key] = []

def _filter_by_date_window(data: dict, start_dt: datetime, end_dt: datetime) -> None:
    """
    수집된 뉴스 중 start_dt ~ end_dt 범위를 벗어나는 것을 제거합니다.
    (엄격 모드: 범위를 벗어나면 폐기)
    """
    
    def is_in_window(date_str):
        if not date_str: return False
        try:
            formats = ["%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if dt:
                # Buffer reduced to 30 mins to be stricter.
                return (start_dt - timedelta(minutes=30)) <= dt <= (end_dt + timedelta(minutes=30))
            
            return False 
        except:
            return False

    keys = ["main_news", "transactions", "prospects"]
    for key in keys:
        if key in data:
            original_items = data[key]
            valid_items = [item for item in original_items if is_in_window(item.get("published_at"))]
            
            if len(valid_items) < len(original_items):
                rejected_items = [item for item in original_items if item not in valid_items]
                print(f"  [FILTER] {key}: {len(original_items)} -> {len(valid_items)} (Date Constraint Violation)")
                print(f"  [DEBUG] Rejected dates in {key}: {[item.get('published_at') for item in rejected_items]}")
            
            data[key] = valid_items

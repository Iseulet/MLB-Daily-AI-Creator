# Phase 1: Research Automation (리서치 자동화)

> 목표: Gemini API로 MLB 뉴스를 자동 수집하고, 매일 아침 요약본을 이메일/슬랙으로 받는 시스템 구축

## 왜 Phase 1부터 시작하는가?
- 앱 전체를 한 번에 만드는 것보다, 핵심 기능(리서치)을 먼저 검증
- Make.com 자동화에 익숙해지는 훈련
- 매일 실제 결과물을 받아보며 프롬프트를 튜닝할 수 있음

---

## Step 1-1: 사전 준비 (계정 및 API 키 발급)

### 필요 계정
- [ ] Google AI Studio 계정 (Gemini API 키 발급)
  - URL: https://aistudio.google.com/
  - 무료 티어로 시작 가능 (분당 15회 요청)
- [ ] Make.com 계정
  - URL: https://www.make.com/
  - 무료 플랜: 월 1,000 오퍼레이션
- [ ] (선택) Slack Workspace 또는 이메일 계정

### API 키 발급 절차
1. Google AI Studio 접속 → "Get API Key" 클릭
2. 프로젝트 생성 → API 키 복사
3. 키를 안전한 곳에 저장 (절대 공개 저장소에 올리지 않기)

---

## Step 1-2: Gemini 프롬프트 설계

### 리서치 프롬프트 (초안)

```
당신은 MLB 전문 스포츠 기자입니다.
오늘 날짜: {current_date}

아래 조건에 맞춰 어제 밤 MLB 경기 결과를 분석해주세요:

1. **핵심 뉴스 TOP 3**: 가장 주목할 만한 경기/선수 성과를 선정
2. **각 뉴스 요약**: 각각 3줄 이내로 요약
3. **한국 선수 동향**: 김하성, 이정후 등 한국 선수 출전 여부와 성적
4. **숏폼 콘텐츠 추천**: 위 뉴스 중 유튜브 쇼츠 영상으로 만들기 가장 좋은 주제 1개와 이유

출력 형식:
- JSON 형식으로 출력
- 각 뉴스에 "headline", "summary", "players", "stats" 필드 포함
```

### 예상 JSON 응답 구조

```json
{
  "date": "2025-04-15",
  "top_news": [
    {
      "rank": 1,
      "headline": "오타니, 시즌 10호 홈런 폭발",
      "summary": "오타니 쇼헤이가 양키스전에서 시즌 10호 홈런...",
      "players": ["Shohei Ohtani"],
      "stats": {"HR": 10, "AVG": ".315", "OPS": "1.050"},
      "shorts_potential": "high"
    }
  ],
  "korean_players": [
    {
      "name": "김하성",
      "team": "SD Padres",
      "result": "3타수 2안타 1타점",
      "highlight": "결승 적시타"
    }
  ],
  "recommended_shorts_topic": {
    "topic": "오타니 시즌 10호 홈런",
    "reason": "시각적 임팩트가 크고, 글로벌 관심도가 높음"
  }
}
```

---

## Step 1-3: Make.com 자동화 시나리오 구성

### 시나리오 흐름도

```
[트리거: 매일 오전 8시]
        │
        ▼
[HTTP Request: Gemini API 호출]
  - 리서치 프롬프트 전송
  - JSON 응답 수신
        │
        ▼
[JSON Parser: 응답 파싱]
  - top_news 배열 추출
  - korean_players 추출
        │
        ▼
[포맷터: 보기 좋은 메시지로 변환]
  - 마크다운 형식 정리
        │
        ├──→ [이메일 전송] (Gmail 모듈)
        │
        └──→ [슬랙 전송] (Slack 모듈) ← 선택
```

### Make.com 설정 상세

#### 모듈 1: Schedule (트리거)
- 유형: 매일 반복
- 시간: 오전 8:00 (KST)

#### 모듈 2: HTTP - Make a request
- URL: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- Method: POST
- Headers:
  ```
  Content-Type: application/json
  ```
- Query String:
  ```
  key: {YOUR_GEMINI_API_KEY}
  ```
- Body:
  ```json
  {
    "contents": [{
      "parts": [{
        "text": "리서치 프롬프트 (Step 1-2에서 작성한 내용)"
      }]
    }],
    "generationConfig": {
      "temperature": 0.7,
      "maxOutputTokens": 2048
    }
  }
  ```

#### 모듈 3: JSON Parse
- Gemini 응답에서 `candidates[0].content.parts[0].text` 추출

#### 모듈 4: Gmail - Send an email
- 수신자: 본인 이메일
- 제목: `[MLB Daily] {date} 오늘의 핵심 뉴스`
- 본문: 파싱된 뉴스 내용을 HTML 포맷으로

---

## Step 1-4: 테스트 및 튜닝

### 테스트 체크리스트
- [ ] Gemini API 단독 호출 테스트 (Google AI Studio에서)
- [ ] Make.com 시나리오 수동 실행 테스트
- [ ] 이메일/슬랙 수신 확인
- [ ] 프롬프트 튜닝 (결과물의 품질 개선)
  - 뉴스 선정 기준이 적절한가?
  - JSON 형식이 깨지지 않는가?
  - 한국 선수 정보가 정확한가?

### 주의사항
- Gemini 무료 티어 제한: 분당 15회 요청, 일일 1,500회
- Make.com 무료 플랜: 월 1,000 오퍼레이션 → 매일 1회 실행이면 충분
- Gemini의 실시간 정보는 Google Search grounding 기능 활용 필요

### 예상 소요 비용
| 항목 | 비용 |
|------|------|
| Gemini API (무료 티어) | $0 |
| Make.com (무료 플랜) | $0 |
| Gmail | $0 |
| **합계** | **$0** |

---

## Phase 1 완료 기준
- [ ] 매일 아침 8시에 MLB 뉴스 요약이 자동으로 이메일에 도착
- [ ] 뉴스 TOP 3가 일관된 JSON 형식으로 제공됨
- [ ] 한국 선수 동향이 포함됨
- [ ] 숏폼 콘텐츠 추천 주제가 포함됨

# Phase 3: Video Pipeline (영상 자동 생성)

> 목표: 확정된 대본을 넣으면 자막+TTS+배경이 포함된 영상이 자동 생성되는 파이프라인 구축

## 전제 조건
- Phase 2 완료 (대본 생성이 안정적으로 동작)
- 영상 생성 도구 API 접근권 확보

> **[MEMO] 유료/무료 스택 선택은 Phase 3 착수 시점에 결정**
> - 옵션 A (유료): HeyGen + ElevenLabs + Make.com (~$38/월)
> - 옵션 B (무료): MoviePy/FFmpeg + Edge TTS + GitHub Actions ($0/월)
> - Phase 1~2 진행 경험과 그 시점의 상황에 따라 판단
> - 상세 비교: `docs/07_COST-OPTIMIZATION-RESEARCH.md`

---

## Step 3-1: 영상 생성 도구 선택

### 옵션 비교

| 기준 | HeyGen | InVideo AI | Pictory | Runway |
|------|--------|------------|---------|--------|
| 주요 기능 | AI 아바타 영상 | 텍스트→영상 | 텍스트→영상 | AI 영상 생성 |
| API 지원 | O | O | O | O |
| 숏폼 최적화 | 우수 | 우수 | 양호 | 보통 |
| 자막 자동 삽입 | O | O | O | X |
| 한국어 TTS | O | 제한적 | X | X |
| 가격대 | $24/월~ | $25/월~ | $19/월~ | $12/월~ |
| Make.com 연동 | 공식 지원 | API 가능 | API 가능 | API 가능 |

### 권장 조합
- **메인**: HeyGen (AI 아바타 + 한국어 TTS + 자막 일체형)
- **대안**: InVideo AI (아바타 없이 b-roll 스타일)
- **TTS 보강**: ElevenLabs (더 자연스러운 음성이 필요할 경우)

---

## Step 3-2: TTS (Text-to-Speech) 설정

### ElevenLabs 설정 (선택적 보강)
- 한국어 음성 모델 선택
- 음성 스타일 프리셋 저장
  - "캐스터형": 빠르고 에너지 넘침
  - "분석가형": 차분하고 명료함
  - "유머형": 가볍고 친근함

### TTS API 호출 예시

```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}

Body:
{
  "text": "{대본 전체 텍스트}",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.8
  }
}

Response: audio/mpeg 파일
```

---

## Step 3-3: 배경 이미지/영상 소싱 전략

### 자동 이미지 소싱 파이프라인

```
[대본에서 키워드 추출 (Gemini)]
        │
        ▼
[이미지 검색 API 호출]
  - Unsplash API (무료, CC 라이선스)
  - Pexels API (무료, CC 라이선스)
  - Pixabay API (무료, CC 라이선스)
        │
        ▼
[이미지 선별 및 다운로드]
  - MLB 관련 키워드: "baseball", "stadium", "home run" 등
  - 선수 이름 → 팀 로고/유니폼 색상 매칭
```

### 저작권 안전 소스

| 소스 | 유형 | 라이선스 | API |
|------|------|----------|-----|
| Unsplash | 사진 | 무료 상업적 사용 | O |
| Pexels | 사진+영상 | 무료 상업적 사용 | O |
| Pixabay | 사진+영상 | 무료 상업적 사용 | O |
| MLB 공식 보도자료 | 사진 | 보도 목적 허용 | 수동 |

### 주의: 절대 사용 금지
- MLB 공식 중계 영상 캡처
- 선수 초상권이 있는 무단 사진
- 구단 로고 무단 사용

---

## Step 3-4: 영상 조립 파이프라인

### 자동 영상 생성 흐름

```
[확정된 대본]
     │
     ├──→ [TTS 생성] → 음성 파일 (.mp3)
     │
     ├──→ [배경 이미지/영상 수집] → 미디어 파일들
     │
     ├──→ [자막 생성] → 타임스탬프 포함 SRT
     │
     └──→ [스탯 그래픽 생성] → 선수 성적 오버레이
              │
              ▼
     [HeyGen/InVideo API: 영상 조립]
              │
              ▼
     [최종 영상 파일 (.mp4)]
        ├──→ 9:16 버전 (쇼츠/릴스)
        └──→ 16:9 버전 (트위터)
```

### HeyGen API 호출 구조

```
POST https://api.heygen.com/v2/video/generate

Body:
{
  "video_inputs": [{
    "character": {
      "type": "avatar",
      "avatar_id": "{선택한_아바타}",
      "avatar_style": "normal"
    },
    "voice": {
      "type": "text",
      "input_text": "{대본}",
      "voice_id": "{한국어_음성_ID}"
    },
    "background": {
      "type": "image",
      "url": "{배경_이미지_URL}"
    }
  }],
  "dimension": {
    "width": 1080,
    "height": 1920
  }
}
```

---

## Step 3-5: 실시간 스탯 오버레이 (차별화 기능)

### 스탯 그래픽 자동 생성

```
[Gemini 응답의 stats 필드]
        │
        ▼
[그래픽 템플릿에 데이터 삽입]
  - 선수 이름
  - AVG / HR / OPS 등 주요 스탯
  - 시즌 순위
        │
        ▼
[PNG 오버레이 이미지 생성]
  - Canva API 또는 HTML→이미지 변환
```

### 스탯 카드 디자인 (예시)

```
┌──────────────────┐
│  SHOHEI OHTANI   │
│  ─────────────── │
│  AVG    .315     │
│  HR     10       │
│  OPS    1.050    │
│  WAR    3.2      │
│  ─────────────── │
│  Season Rank: #2 │
└──────────────────┘
```

---

## Step 3-6: Make.com 시나리오 (Phase 3)

```
[Webhook: 대본 확정 신호 수신]
        │
        ├──→ [ElevenLabs API: TTS 생성]
        │
        ├──→ [Unsplash API: 배경 이미지 검색]
        │
        ├──→ [Gemini API: 스탯 데이터 추출]
        │
        ▼ (모두 완료 후)
[HeyGen API: 영상 생성 요청]
        │
        ▼
[대기: 영상 렌더링 완료 폴링]
        │
        ▼
[영상 URL → 앱으로 전달]
        │
        ├──→ [Google Drive에 백업]
        └──→ [앱: 영상 미리보기 표시]
```

---

## Step 3-7: 테스트 체크리스트

- [ ] TTS가 자연스러운 한국어로 대본을 읽는가
- [ ] 배경 이미지가 대본 내용과 관련 있는가
- [ ] 자막 타이밍이 음성과 일치하는가
- [ ] 9:16 비율이 정확한가
- [ ] 스탯 오버레이가 정확한 수치를 표시하는가
- [ ] 영상 렌더링 시간이 수용 가능한가 (목표: 5분 이내)
- [ ] 16:9 동시 렌더링이 동작하는가

---

## 예상 월간 운영 비용

### 옵션 A: 유료 스택 (편의성 우선)

| 항목 | 플랜 | 월 비용 |
|------|------|---------|
| HeyGen | Creator Plan | ~$24 |
| ElevenLabs | Starter Plan | ~$5 |
| Make.com | Core Plan | ~$9 |
| Gemini API | 무료 티어 | $0 |
| 이미지 API | 무료 티어 | $0 |
| **합계** | | **~$38/월** |

### 옵션 B: 무료 스택 (비용 최적화) -- 권장

| 항목 | 대안 도구 | 월 비용 |
|------|-----------|---------|
| ~~HeyGen~~ | MoviePy + FFmpeg (Python) | **$0** |
| ~~ElevenLabs~~ | Edge TTS 또는 Google Cloud TTS | **$0** |
| ~~Make.com~~ | GitHub Actions 또는 n8n 셀프호스팅 | **$0** |
| Gemini API | 무료 티어 | $0 |
| 이미지 API | Pexels/Unsplash 무료 | $0 |
| **합계** | | **$0/월** |

> 상세 비교는 `docs/07_COST-OPTIMIZATION-RESEARCH.md` 참조

---

## Phase 3 완료 기준
- [ ] 대본을 넣으면 60초 이내 숏폼 영상이 생성됨
- [ ] 영상에 TTS 음성 + 자막 + 배경이 포함됨
- [ ] 9:16과 16:9 두 가지 비율로 출력 가능
- [ ] 스탯 그래픽이 영상에 자동 삽입됨
- [ ] 앱에서 영상 미리보기가 가능함

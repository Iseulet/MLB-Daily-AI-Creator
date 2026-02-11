# Phase 4: Full Integration + 배포 (전체 통합)

> 목표: Phase 1~3을 하나의 앱으로 통합하고, 소셜 미디어 직접 업로드 기능 추가

## 전제 조건
- Phase 1~3 각각 독립적으로 안정 동작
- 각 API의 유료 플랜 전환 완료 (무료 스택 선택 시 불필요)

> **[MEMO] 유료/무료 스택 선택은 Phase 4 착수 시점에 결정**
> - 옵션 A (유료): Glide/FlutterFlow + Make.com (~$39~69/월)
> - 옵션 B (무료): Streamlit + GitHub Actions + YouTube API ($0~5/월)
> - Phase 3까지의 결과물과 운영 경험을 보고 판단
> - 상세 비교: `docs/07_COST-OPTIMIZATION-RESEARCH.md`

---

## Step 4-1: 전체 워크플로우 통합

### 통합 흐름도 (End-to-End)

```
[매일 오전 8시 자동 트리거]
        │
        ▼
[Gemini: MLB 뉴스 리서치]
        │
        ▼
[앱: 뉴스 카드 3개 표시] ← 사용자 앱 오픈
        │
        ▼
[사용자: 뉴스 선택 + 옵션 설정]
  - 말투 / 길이 / 플랫폼
        │
        ▼
[Gemini: 대본 생성]
        │
        ▼
[앱: 대본 표시 + 편집]
        │
        ▼
[사용자: 대본 확정]
        │
        ▼
[영상 자동 생성]
  - TTS + 배경 + 자막 + 스탯
        │
        ▼
[앱: 영상 미리보기]
        │
        ▼
[사용자: 승인]
        │
        ├──→ [YouTube Shorts 업로드]
        ├──→ [Instagram Reels 업로드]
        └──→ [Twitter/X 업로드]
```

---

## Step 4-2: 소셜 미디어 업로드 연동

### YouTube Shorts
- **도구**: YouTube Data API v3
- **Make.com 모듈**: YouTube - Upload a Video
- **필요 정보**:
  - OAuth 2.0 인증
  - 제목, 설명, 태그 (Gemini가 자동 생성)
  - 카테고리: Sports (17)
  - 공개 설정: Public / Unlisted / Scheduled

### Instagram Reels
- **도구**: Instagram Graph API (비즈니스 계정 필요)
- **Make.com 모듈**: Instagram - Create a Video Post
- **필요 정보**:
  - Facebook 페이지 연동
  - 영상 URL (클라우드 스토리지에 업로드 후)
  - 캡션 + 해시태그

### Twitter/X
- **도구**: Twitter API v2
- **Make.com 모듈**: Twitter - Create a Tweet (with media)
- **필요 정보**:
  - API Key + Bearer Token
  - 영상 파일 (최대 140초, 512MB)
  - 트윗 텍스트

### 업로드 메타데이터 자동 생성

```
Gemini 프롬프트:
"다음 대본을 기반으로 각 플랫폼별 업로드 메타데이터를 생성해주세요.

대본: {script}

출력:
{
  "youtube": {
    "title": "...",
    "description": "...",
    "tags": ["...", "..."]
  },
  "instagram": {
    "caption": "...",
    "hashtags": ["...", "..."]
  },
  "twitter": {
    "tweet_text": "..."
  }
}"
```

---

## Step 4-3: 앱 최종 화면 구성

### 전체 화면 맵

```
[메인 대시보드] ──→ [대본 생성] ──→ [영상 생성] ──→ [업로드]
      │                                                  │
      ├── [히스토리]                                     │
      │   (과거 생성 영상 목록)                          │
      │                                                  │
      ├── [분석 대시보드]                                │
      │   (업로드된 영상 성과 추적)                      │
      │                                                  │
      └── [설정]                                         │
          (API 키, 기본 말투, 스케줄 등)                 │
                                                         │
                                              [업로드 완료!]
                                              조회수 실시간 추적
```

### 추가 화면: 히스토리

```
┌─────────────────────────────┐
│  ← 히스토리                 │
├─────────────────────────────┤
│                             │
│  4/15 - 오타니 10호 홈런    │
│  YT: 12,340 views | IG: 8K │
│  [다시보기] [재활용]        │
│                             │
│  4/14 - 김하성 끝내기       │
│  YT: 8,920 views | IG: 5K  │
│  [다시보기] [재활용]        │
│                             │
│  4/13 - 다저스 신기록       │
│  YT: 25,100 views | IG: 15K│
│  [다시보기] [재활용]        │
│                             │
└─────────────────────────────┘
```

---

## Step 4-4: 에러 핸들링 및 모니터링

### 예상 장애 시나리오 및 대응

| 시나리오 | 대응 방안 |
|----------|-----------|
| Gemini API 일시 장애 | 캐시된 직전 결과 사용 + 수동 뉴스 입력 UI |
| TTS 생성 실패 | 대체 TTS(Google TTS) 자동 전환 |
| 영상 렌더링 타임아웃 | 재시도 로직 + 사용자 알림 |
| 업로드 실패 | 영상 로컬 저장 + 수동 업로드 안내 |
| API 무료 한도 초과 | 사전 경고 + 유료 전환 안내 |

### Make.com 에러 핸들링
- 각 모듈에 Error Handler 추가
- 실패 시 Slack/이메일 알림
- 재시도 정책: 3회까지 자동 재시도, 5분 간격

---

## Step 4-5: 성과 추적 (Analytics)

### 추적 지표

| 지표 | 소스 | 목적 |
|------|------|------|
| 조회수 | YouTube/IG API | 콘텐츠 인기도 |
| 좋아요/댓글 | YouTube/IG API | 참여도 |
| 시청 지속 시간 | YouTube Analytics | 콘텐츠 품질 |
| 구독자 증감 | YouTube Analytics | 채널 성장 |
| 뉴스 주제별 성과 | 내부 DB | 어떤 주제가 잘 되는지 |
| 말투별 성과 | 내부 DB | 어떤 스타일이 잘 되는지 |

### 주간 리포트 자동화
- 매주 월요일 아침, 지난주 성과 요약을 이메일로 전송
- Gemini가 "이번 주 가장 잘된 콘텐츠와 개선 포인트" 분석

---

## Step 4-6: 배포

### 배포 옵션

| 방식 | 장점 | 단점 |
|------|------|------|
| Glide PWA | 즉시 배포, URL 공유 | 앱스토어 없음 |
| FlutterFlow Web | 커스텀 도메인 가능 | 설정 필요 |
| FlutterFlow iOS/Android | 앱스토어 출시 | 심사 필요 |

### 권장 배포 순서
1. Glide PWA로 즉시 배포 (본인 사용)
2. 안정화 후 FlutterFlow로 마이그레이션
3. 필요시 앱스토어 출시

---

## 최종 월간 운영 비용 예상

### 옵션 A: 유료 스택

| 항목 | 플랜 | 월 비용 |
|------|------|---------|
| HeyGen | Creator | ~$24 |
| ElevenLabs | Starter | ~$5 |
| Make.com | Core | ~$9 |
| Gemini API | 무료 → Pay-as-you-go | $0~5 |
| Glide | Pro (필요시) | $0~25 |
| 도메인 (선택) | | ~$1 |
| **합계** | | **~$39~69/월** |

### 옵션 B: 무료 스택 (비용 최적화) -- 권장

| 항목 | 대안 도구 | 월 비용 |
|------|-----------|---------|
| ~~HeyGen~~ | MoviePy + FFmpeg (Python) | **$0** |
| ~~ElevenLabs~~ | Edge TTS / Google Cloud TTS | **$0** |
| ~~Make.com~~ | GitHub Actions / n8n 셀프호스팅 | **$0** |
| Gemini API | 무료 티어 | $0 |
| ~~Glide~~ | Streamlit Community Cloud | **$0** |
| 업로드 | YouTube Data API 무료 | $0 |
| **합계** | | **$0~5/월** |

> 상세 비교는 `docs/07_COST-OPTIMIZATION-RESEARCH.md` 참조

---

## Phase 4 완료 기준
- [ ] 앱에서 리서치 → 대본 → 영상 → 업로드 전 과정이 동작
- [ ] YouTube, Instagram, Twitter 중 최소 1곳에 자동 업로드
- [ ] 과거 영상 히스토리 조회 가능
- [ ] 에러 발생 시 알림이 오고 수동 대응 가능
- [ ] 성과 지표를 앱에서 확인 가능

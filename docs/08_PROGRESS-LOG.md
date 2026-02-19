# 진행 상황 기록 (Progress Log)

> 프로젝트 개발 및 문제 해결 과정을 시간 순으로 기록합니다.

---

## 2026-02-14: 뉴스 취합 로직 변경 및 API 오류 해결

### 1. 뉴스 취합 로직 및 구조 변경
- **요청 사항**: 사용자 요청에 따라 뉴스 취합 방식을 대대적으로 변경했습니다.
- **주요 변경 내용**:
    - **취합 시간**: `어제 오전 7시 ~ 오늘 오전 7시`로 변경
    - **구조 변경**: 기존의 단일 뉴스 목록에서 아래 3단 구조로 변경
        1.  `core_news`: 주요 뉴스 10개 요약 (한국 선수 포함)
        2.  `player_movement`: 선수 이적/계약, 루머, 로스터 변경
        3.  `prospects`: 최상위 유망주 콜업 소식
- **수정된 파일**:
    - `phase-1_research-automation/src/researcher.py`: Gemini 프롬프트 및 날짜 계산 로직 수정
    - `phase-1_research-automation/templates/email.html`: 새로운 데이터 구조를 반영하여 이메일 템플릿 전면 재작성

### 2. 뉴스 생성 테스트 및 API 오류 디버깅
- **문제 발생**: 변경된 로직으로 뉴스 생성을 테스트하는 과정에서 Gemini API 호출과 관련된 연속적인 오류가 발생했습니다.
- **오류 해결 과정 (요약)**:
    1.  **초기 오류**: `AttributeError` 및 `ImportError` 발생
        - **원인**: `google-genai`와 `google-generativeai` 라이브러리 간의 API 호출 방식 차이로 인한 혼란.
        - **조치**: `requirements.txt`를 수정하여 `google-generativeai` 라이브러리를 사용하도록 통일하고, 관련 import 문 및 API 호출 코드를 모두 수정.
    2.  **모델 조회 오류**: `404 model not found for API version v1beta` 오류 발생
        - **원인**: 사용자 API 키가 `v1beta`라는 구버전 API 엔드포인트에 연결되어 있어, `gemini-1.5-pro`와 같은 최신 모델을 인식하지 못하는 것으로 추정.
        - **조치**: `gemini-pro`와 같이 보다 범용적인 모델로 변경하여 테스트했으나 동일한 오류 발생.
- **최종 결론 및 해결 방안 제시**:
    - 코드 레벨의 문제가 아닌, 사용자 계정의 API 키 자체의 권한 또는 버전 문제로 최종 결론.
    - 사용자에게 **Google AI Studio에서 새 API 키를 발급받아 `.env` 파일에 업데이트**하는 방법을 안내.

---

---

## 2026-02-17: Phase 1 리서치 포맷 최종 개편 + Supabase 연동 + GitHub 배포

### 1. 문제 진단
- GitHub Actions(매일 KST 07:00)에 배포된 코드가 이전 포맷(Format A)이어서, 이메일이 `top_news`, `korean_players`, `recommended_shorts_topic` 기반으로 발송됨
- 로컬에서 수정한 새 포맷(Format C: `main_news`, `transactions`, `prospects`)이 push되지 않은 상태였음
- fantasyDraftApp 뉴스탭과 이메일 간 데이터 포맷 불일치

### 2. 변경 내용 및 배포

#### researcher.py — 수집 포맷 최종 확정
- `main_news` (핵심 뉴스 10선), `transactions` (선수 이동/루머), `prospects` (유망주 소식)
- Gemini 프롬프트에 엄격 날짜 검증 규칙 (날짜 날조 금지, 이중 타임스탬프 검증)
- Python 레벨 날짜 필터링 (`_filter_by_date_window`)

#### formatter.py — 이메일 본문 3섹션
- 핵심 뉴스: 순위 + 헤드라인 + 요약 + 출처 + 원문 링크
- 선수 이동 & 루머: 타입 배지 + 헤드라인 + 요약
- 유망주 소식: 팀 + 선수명 + 요약

#### uploader.py — Supabase 업로드 (신규)
- `mlb_news` 테이블에 upsert (Unique Key: `season, date`)
- 컬럼: `season`, `date`, `news`(JSONB), `transactions`(JSONB), `prospects`(JSONB), `asian_players`(JSONB)

#### mlb-daily.yml — 워크플로우 업데이트
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` 환경변수 추가

#### GitHub Secrets 설정
- `gh secret set`으로 `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` 추가 완료
- 총 6개 secrets: GEMINI_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL, SUPABASE_URL, SUPABASE_SERVICE_KEY

### 3. 현재 데이터 흐름

```
[매일 KST 07:00 - GitHub Actions]
  Gemini API (Google Search Grounding)
    ↓
  researcher.py → JSON (main_news, transactions, prospects)
    ↓
  ├─ formatter.py → HTML 이메일 → Gmail SMTP → 사용자 수신
  ├─ outputs/{date}.json 파일 저장 (Artifacts 30일 보관)
  └─ uploader.py → Supabase mlb_news 테이블
                      ↓
              fantasyDraftApp MLBNewsTab (실시간 구독)
```

### 4. Phase 2/4 호환성 참고
- Streamlit 대시보드 (`app.py`) 및 Full Pipeline (`full_pipeline.py`)는 아직 이전 포맷 (`top_news`) 참조
- 추후 통합 시 `top_news` → `main_news` 마이그레이션 필요

---

## 2026-02-18: 아키텍처 리팩토링 - Phase 1 레포지토리 분리

### 1. 변경 목적
- 모노레포 구조로 인해 발생했던 페이즈 간 강한 결합(strong coupling) 문제 해결
- 데이터 생산(Phase 1)과 소비(Phase 2, 4)를 명확히 분리하여 유지보수성 및 확장성 향상
- Supabase를 중앙 데이터 허브로 사용하여 비동기적 데이터 흐름 구축

### 2. 주요 변경 내용
- **`mlb-daily-research` 신규 레포지토리 생성**:
  - 기존 `phase-1_research-automation`의 모든 코드를 이전
  - GitHub Actions 워크플로우를 이전하여 매일 KST 07:00에 뉴스 수집, Supabase 업로드, 이메일 발송을 독립적으로 수행
- **`MLB-Daily-AI-Creator` 기존 레포지토리 변경**:
  - `phase-1_research-automation` 디렉토리 및 관련 워크플로우 완전 삭제
  - **Phase 2 (Streamlit)**: 로컬 파일 대신 Supabase DB에서 뉴스 데이터를 읽도록 `data_store.py`와 `app.py` 수정
  - **Phase 4 (통합 파이프라인)**: 로컬 함수 호출 대신 Supabase DB에서 데이터를 가져오도록 `full_pipeline.py`와 `pipeline_config.py` 수정
  - **의존성 정리**: 각 레포지토리에 필요한 `requirements.txt`를 재구성. 기존 레포에는 `supabase` 의존성 추가

### 3. 새로운 데이터 흐름

```
 [mlb-daily-research 레포]              [MLB-Daily-AI-Creator 레포]
 GitHub Actions (KST 07:00)             Streamlit / CLI
   researcher.py                          ↓
     ↓                                  Supabase mlb_news 테이블 READ
   Supabase mlb_news WRITE    →           ↓
     ↓                                  script_generator.py
   Email 발송                            video_pipeline.py
                                        youtube_uploader.py
```

### 4. 기대 효과
- 각 레포지토리의 역할이 명확해지고, 독립적인 개발 및 배포 가능
- `sys.path` 해킹과 같은 불안정한 코드 제거
- Supabase를 통해 데이터 포맷이 통일되어 시스템 안정성 향상

---

*마지막 업데이트: 2026-02-17*

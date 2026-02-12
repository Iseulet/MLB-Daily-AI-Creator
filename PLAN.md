# MLB Daily AI Creator - 프로젝트 계획

## 프로젝트 개요
매일 MLB 뉴스를 자동 수집하고, AI 대본 생성, 영상 제작, YouTube 업로드까지 원스톱 처리하는 콘텐츠 자동화 시스템.

## 아키텍처

```
Phase 1              Phase 2              Phase 3              Phase 4
Research          →  Script Gen        →  Video Production  →  Upload + Integration
(Gemini + Gmail)    (Streamlit UI)       (TTS + MoviePy)      (YouTube API)
```

**전체 파이프라인 (원클릭):**
```
뉴스 수집 → 대본 생성 → TTS 음성 → 배경 영상 → 자막/그래픽 합성 → 메타데이터 → YouTube 업로드
```

---

## Phase 1: Research Automation [완료]

**목적:** Gemini API로 매일 MLB 뉴스를 자동 수집하여 이메일로 전송

| 항목 | 내용 |
|------|------|
| AI | Gemini 2.0 Flash + Google Search grounding |
| 자동화 | GitHub Actions (cron: 매일 KST 08:00) |
| 전송 | smtplib + Gmail 앱 비밀번호 |
| 비용 | $0/월 |

**구현 파일:**
- `phase-1_research-automation/src/main.py` — 파이프라인 진입점
- `phase-1_research-automation/src/researcher.py` — Gemini 리서치 엔진
- `phase-1_research-automation/src/formatter.py` — JSON → HTML 변환
- `phase-1_research-automation/src/notifier.py` — Gmail 전송

---

## Phase 2: App Prototype + Script Generation [완료]

**목적:** Streamlit 대시보드로 뉴스 확인 + AI 대본 생성 + 전체 파이프라인 UI

| 항목 | 내용 |
|------|------|
| UI | Streamlit |
| 대본 AI | Gemini 2.0 Flash Lite |
| 톤 옵션 | 유머/분석/열정 (3종) |
| 길이 옵션 | 30초/45초/60초 |

**구현 파일:**
- `phase-2_app-prototype/app.py` — Streamlit 메인 앱 (4개 페이지)
- `phase-2_app-prototype/script_generator.py` — AI 대본 생성
- `phase-2_app-prototype/data_store.py` — 뉴스/대본 파일 관리

**페이지 구성:**
1. 원클릭 자동 생성 (전체 파이프라인)
2. 뉴스 대시보드
3. 대본 생성/편집
4. 업로드 히스토리

---

## Phase 3: Video Pipeline [완료]

**목적:** 대본 텍스트로부터 완전 자동화된 숏폼 영상 제작

| 항목 | 내용 |
|------|------|
| TTS | Edge TTS (한국어: InJoonNeural/SunHiNeural) |
| 배경 | Pexels API (야구 관련 세로 영상) |
| 합성 | MoviePy (1080x1920, 30fps) |
| 그래픽 | Pillow (선수 스탯 카드) |
| 자막 | SRT 파싱 + 15자 그룹핑 |

**구현 파일:**
- `phase-3_video-pipeline/src/video_pipeline.py` — 영상 생성 오케스트레이터
- `phase-3_video-pipeline/src/tts_engine.py` — Edge TTS + 자막 생성
- `phase-3_video-pipeline/src/background.py` — Pexels 배경 다운로드
- `phase-3_video-pipeline/src/composer.py` — MoviePy 영상 합성
- `phase-3_video-pipeline/src/graphics.py` — 스탯 카드 생성
- `phase-3_video-pipeline/src/subtitle.py` — SRT 파싱

---

## Phase 4: Full Integration + YouTube Upload [완료]

**목적:** 전체 파이프라인 통합 + YouTube 자동 업로드 + 메타데이터 생성

| 항목 | 내용 |
|------|------|
| 업로드 | YouTube Data API v3 + OAuth 2.0 |
| 메타데이터 | Gemini 자동 생성 (YouTube/Instagram/Twitter) |
| 히스토리 | JSON 파일 기반 업로드 기록 |
| 콜백 | Streamlit UI 연동용 진행 상태 콜백 |

**구현 파일:**
- `phase-4_integration/src/full_pipeline.py` — 6단계 통합 오케스트레이터
- `phase-4_integration/src/youtube_uploader.py` — YouTube API 업로더
- `phase-4_integration/src/metadata_generator.py` — 멀티 플랫폼 메타데이터
- `phase-4_integration/src/pipeline_config.py` — 통합 환경변수 로더
- `phase-4_integration/src/history.py` — 업로드 히스토리 관리

**파이프라인 6단계:**
1. Research (뉴스 수집)
2. Script (대본 생성)
3. Video (영상 제작)
4. Metadata (메타데이터 생성)
5. Upload (YouTube 업로드)
6. History (기록 저장)

---

## 기술 스택

| 영역 | 기술 | 용도 |
|------|------|------|
| AI/LLM | Gemini API (2.0 Flash / Flash Lite) | 리서치, 대본, 메타데이터 |
| TTS | Edge TTS | 한국어 음성 합성 (무료) |
| 영상 합성 | MoviePy | 배경 + 자막 + 오디오 합성 |
| 그래픽 | Pillow | 스탯 카드 이미지 |
| 배경 영상 | Pexels API | CC 라이선스 야구 영상 |
| 웹 UI | Streamlit | 대시보드 + 원클릭 파이프라인 |
| 이메일 | smtplib + Gmail | 뉴스 브리핑 전송 |
| 업로드 | YouTube Data API v3 | 영상 업로드 |
| CI/CD | GitHub Actions | Phase 1 일일 자동화 |
| 데이터 | JSON 파일 | 뉴스, 대본, 히스토리 저장 |

## 월간 비용: $0
모든 API의 무료 티어 내에서 운영 가능.

# MLB Daily AI Creator - Project Overview

## 프로젝트 비전
매일 아침 앱을 켜서 **리서치 → 대본 → 영상 편집**을 원스톱으로 처리하는
MLB 콘텐츠 자동 생성 대시보드

## 핵심 워크플로우

```
[Step 1]              [Step 2]              [Step 3]
Gemini Intelligence → Creative Scripting → Instant Production
(리서치/뉴스 수집)    (대본 자동 생성)      (영상 자동 생성)
```

## 타겟 플랫폼
- YouTube Shorts (9:16)
- Instagram Reels (9:16)
- Twitter/X (16:9)

## 기술 스택 요약

| 영역 | 도구 | 역할 |
|------|------|------|
| 인터페이스 | FlutterFlow 또는 Glide | 앱 UI |
| AI 두뇌 | Gemini API | 리서치 + 대본 |
| 영상 엔진 | HeyGen / InVideo AI | 영상 자동 생성 |
| 자동화 | Make.com | 전체 파이프라인 연결 |
| TTS | ElevenLabs / Google TTS | AI 성우 |

## 구현 단계 (Phase)

| Phase | 이름 | 목표 | 예상 기간 |
|-------|------|------|-----------|
| 1 | Research Automation | Gemini 리서치 자동화 + 이메일/슬랙 전송 | 1-2주 |
| 2 | App Prototype | 앱 UI 프로토타입 + 대본 생성 | 2-3주 |
| 3 | Video Pipeline | 영상 자동 생성 파이프라인 구축 | 2-3주 |
| 4 | Full Integration | 전체 통합 + 배포 | 2-3주 |

## 폴더 구조

```
MLB-Daily-AI-Creator/
├── docs/                          # 프로젝트 문서
│   ├── 00_PROJECT-OVERVIEW.md     # 이 파일
│   ├── 01_PHASE-1-PLAN.md        # Phase 1 상세 계획
│   ├── 02_PHASE-2-PLAN.md        # Phase 2 상세 계획
│   ├── 03_PHASE-3-PLAN.md        # Phase 3 상세 계획
│   ├── 04_PHASE-4-PLAN.md        # Phase 4 상세 계획
│   ├── 05_API-SETUP-GUIDE.md     # API 키 발급 및 설정 가이드
│   ├── 06_TECH-DECISION-LOG.md   # 기술 선택 근거 기록
│   └── 07_COST-OPTIMIZATION-RESEARCH.md  # 비용 최적화 리서치
├── phase-1_research-automation/   # Phase 1 작업 파일
├── phase-2_app-prototype/         # Phase 2 작업 파일
├── phase-3_video-pipeline/        # Phase 3 작업 파일
├── phase-4_integration/           # Phase 4 통합 작업
├── assets/
│   ├── images/                    # 이미지 리소스
│   └── templates/                 # 대본/영상 템플릿
└── config/                        # 설정 파일
```

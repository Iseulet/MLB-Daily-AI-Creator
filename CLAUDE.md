# MLB Daily AI Creator

MLB 뉴스 자동 수집 → AI 대본 생성 → 숏폼 영상 제작 → YouTube 업로드를 원스톱 처리하는 콘텐츠 자동화 시스템.

## 프로젝트 구조

```
MLB-Daily-AI-Creator/
├── .github/workflows/mlb-daily.yml    # Phase 1 일일 자동화 (cron)
├── phase-1_research-automation/       # Gemini 뉴스 수집 + 이메일
│   └── src/ (main.py, researcher.py, formatter.py, notifier.py)
├── phase-2_app-prototype/             # Streamlit 대시보드 + 대본 생성
│   ├── app.py, script_generator.py, data_store.py
├── phase-3_video-pipeline/            # TTS + 배경 + 자막 → MP4 생성
│   └── src/ (video_pipeline.py, tts_engine.py, background.py, composer.py, graphics.py, subtitle.py)
├── phase-4_integration/               # 통합 파이프라인 + YouTube 업로드
│   └── src/ (full_pipeline.py, youtube_uploader.py, metadata_generator.py, pipeline_config.py, history.py)
├── docs/                              # 프로젝트 기획 문서
├── .env.example                       # 환경변수 템플릿
├── requirements.txt                   # 통합 의존성
└── PLAN.md                            # 전체 Phase 계획
```

## 기술 스택

- **AI**: Google Gemini API (2.0 Flash / Flash Lite) — 리서치, 대본, 메타데이터
- **TTS**: Edge TTS (한국어 InJoonNeural/SunHiNeural, 무료)
- **영상**: MoviePy (합성) + Pillow (그래픽) + Pexels API (배경)
- **UI**: Streamlit
- **업로드**: YouTube Data API v3 + OAuth 2.0
- **이메일**: smtplib + Gmail
- **CI/CD**: GitHub Actions

## 실행 방법

### Phase 1 — 뉴스 수집 (단독 실행)
```bash
cd phase-1_research-automation
pip install -r requirements.txt
python src/main.py
```

### Phase 2 — Streamlit 대시보드 (전체 파이프라인 포함)
```bash
pip install -r requirements.txt    # 루트 requirements
cd phase-2_app-prototype
streamlit run app.py
```
대시보드에서 "원클릭 자동 생성"으로 전체 파이프라인 실행 가능.

### Phase 3 — 영상 생성 (단독 실행)
```bash
cd phase-3_video-pipeline
pip install -r requirements.txt
python src/video_pipeline.py
```

### Phase 4 — 통합 파이프라인 (CLI)
```bash
cd phase-4_integration
python src/full_pipeline.py
```

## 환경변수

`.env.example`을 `.env`로 복사 후 값 설정. 각 Phase 폴더에도 개별 `.env` 필요.

| 변수 | 용도 | 필수 |
|------|------|------|
| `GEMINI_API_KEY` | Gemini API 키 | O |
| `PEXELS_API_KEY` | 배경 영상 다운로드 | X (없으면 단색 배경) |
| `GMAIL_ADDRESS` | 뉴스 이메일 발신 | Phase 1만 |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 | Phase 1만 |
| `RECIPIENT_EMAIL` | 뉴스 이메일 수신 | Phase 1만 |

YouTube 업로드는 OAuth 2.0 인증 필요 (`client_secret.json` → 최초 실행 시 `token.json` 자동 생성).

## GitHub Actions

`.github/workflows/mlb-daily.yml`로 Phase 1이 매일 KST 08:00 자동 실행.
GitHub Secrets에 `GEMINI_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `RECIPIENT_EMAIL` 설정 필요.

## 주의사항

- `.env`, `token.json`, `client_secret.json`은 절대 커밋하지 않을 것 (`.gitignore`로 보호)
- `outputs/`, `temp/`, `history/`, `scripts/` 디렉토리는 런타임 생성 파일이므로 커밋 불필요
- 모든 API는 무료 티어 범위 내에서 운영 (월 $0)

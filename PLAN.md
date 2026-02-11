# Phase 1 구현 계획: MLB Daily Research Automation

## 선택된 스택
- **자동화**: GitHub Actions (cron 스케줄)
- **AI**: Gemini API (Google Search grounding)
- **이메일**: smtplib + Gmail 앱 비밀번호
- **비용**: $0/월

---

## 사전 준비 (유저가 직접 수행)

### 1. Gemini API 키 발급
1. https://aistudio.google.com/ 접속 → Google 로그인
2. 좌측 "Get API Key" → "Create API Key"
3. 발급된 키를 메모 (나중에 `.env`와 GitHub Secrets에 저장)

### 2. Gmail 앱 비밀번호 발급
1. Google 계정 → 보안 → 2단계 인증 활성화 (이미 되어있으면 스킵)
2. https://myaccount.google.com/apppasswords 접속
3. 앱 이름 입력 (예: "MLB Daily") → 16자리 앱 비밀번호 생성
4. 발급된 비밀번호를 메모

### 3. GitHub 리포지토리 생성
- `MLB-Daily-AI-Creator` 퍼블릭 리포로 생성 (GitHub Actions 무료 무제한)
- 또는 프라이빗 리포 (월 2,000분 무료 — 충분)

---

## 구현 단계

### Step 1: 프로젝트 구조 생성
`phase-1_research-automation/` 안에 아래 파일들 생성:

```
phase-1_research-automation/
├── src/
│   ├── main.py           # 진입점: 리서치 → 포맷 → 전송 파이프라인
│   ├── researcher.py     # Gemini API 호출 + JSON 파싱
│   ├── formatter.py      # JSON → HTML 이메일 변환
│   └── notifier.py       # smtplib로 Gmail 전송
├── templates/
│   └── email.html        # 이메일 HTML 템플릿
├── .env.example          # 환경변수 템플릿 (실제 키 없음)
└── requirements.txt      # google-generativeai, python-dotenv, jinja2
```

### Step 2: researcher.py — Gemini 리서치 엔진
- `google-generativeai` SDK 사용 (최신 Gemini 2.0 Flash)
- Google Search grounding 활성화 → 실시간 MLB 뉴스 수집
- 프롬프트: MLB 뉴스 TOP 3 + 한국 선수 동향 + 숏폼 추천
- JSON 형식 응답 파싱 + 검증
- 실패 시 재시도 로직 (최대 2회)

### Step 3: formatter.py — 이메일 포맷터
- Jinja2 템플릿 엔진으로 HTML 이메일 생성
- 뉴스 카드 형태의 깔끔한 레이아웃
- 한국 선수 섹션 별도 강조
- 숏폼 추천 주제 하이라이트

### Step 4: notifier.py — 이메일 전송
- `smtplib` + `ssl`로 Gmail SMTP 연결
- Gmail 앱 비밀번호 인증
- HTML 이메일 전송 (`email.mime` 사용)

### Step 5: main.py — 파이프라인 통합
- researcher → formatter → notifier 순서 실행
- 에러 발생 시 로그 출력 (GitHub Actions 로그로 확인 가능)
- 실행 결과 요약 출력

### Step 6: GitHub Actions 워크플로우
`.github/workflows/mlb-daily.yml` 작성:
- cron: 매일 UTC 23:00 (= KST 08:00)
- Python 3.11 환경 설정
- 의존성 설치 → main.py 실행
- Secrets: `GEMINI_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `RECIPIENT_EMAIL`

### Step 7: 로컬 테스트 + 검증
- `.env` 파일에 키 설정 후 로컬에서 `python src/main.py` 실행
- 이메일 수신 확인
- JSON 응답 구조 검증

---

## 완료 기준
- [ ] 로컬에서 `python src/main.py` 실행 시 MLB 뉴스 이메일 수신
- [ ] GitHub Actions에서 매일 KST 08:00에 자동 실행
- [ ] 뉴스 TOP 3 + 한국 선수 + 숏폼 추천이 포함된 이메일
- [ ] 에러 시 GitHub Actions 로그에서 원인 확인 가능

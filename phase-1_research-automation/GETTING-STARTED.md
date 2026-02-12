# Phase 1 시작하기

## 바로 할 일 (Quick Start)

### 1단계: API 키 발급 (10분)
1. [Google AI Studio](https://aistudio.google.com/) 접속 → Google 로그인
2. 좌측 "Get API Key" → "Create API Key" 클릭
3. 발급된 Gemini API 키를 메모

### 2단계: Gmail 앱 비밀번호 발급 (5분)
1. Google 계정 → 보안 → 2단계 인증 활성화
2. https://myaccount.google.com/apppasswords 접속
3. 앱 이름 입력 (예: "MLB Daily") → 16자리 앱 비밀번호 생성

### 3단계: 환경변수 설정 (2분)
```bash
cd phase-1_research-automation
cp .env.example .env
```
`.env` 파일을 열어 값 채우기:
```
GEMINI_API_KEY=발급받은_키
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=16자리_앱_비밀번호
RECIPIENT_EMAIL=수신할_이메일
```

### 4단계: 로컬 실행 테스트 (5분)
```bash
pip install -r requirements.txt
python src/main.py
```
- 실행 후 지정한 이메일로 MLB 뉴스 브리핑 수신 확인
- `outputs/` 폴더에 JSON 결과 파일 저장됨

### 5단계: GitHub Actions 자동화 설정 (5분)
1. GitHub 리포의 Settings → Secrets and variables → Actions
2. 아래 시크릿 추가:
   - `GEMINI_API_KEY`
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`
   - `RECIPIENT_EMAIL`
3. 매일 KST 08:00 (UTC 23:00)에 자동 실행됨
4. Actions 탭에서 "Run workflow"로 수동 실행도 가능

## 파이프라인 구조

```
researcher.py  →  formatter.py  →  notifier.py
(Gemini API)     (HTML 변환)      (Gmail 전송)
```

1. **researcher.py**: Gemini 2.0 Flash + Google Search grounding으로 실시간 MLB 뉴스 수집
2. **formatter.py**: JSON 결과를 Jinja2 HTML 이메일로 변환
3. **notifier.py**: smtplib로 Gmail SMTP 전송

## 문제 해결

| 문제 | 해결 방법 |
|------|-----------|
| API 키 오류 | Google AI Studio에서 키 재생성 |
| JSON 파싱 실패 | `outputs/` 폴더의 원본 응답 확인 후 프롬프트 조정 |
| 이메일 미수신 | Gmail 앱 비밀번호 확인, 스팸함 확인 |
| GitHub Actions 실패 | Actions 탭에서 로그 확인 → Secrets 설정 재확인 |
| 뉴스가 부정확 | Google Search grounding이 자동 활성화되어 있는지 확인 |

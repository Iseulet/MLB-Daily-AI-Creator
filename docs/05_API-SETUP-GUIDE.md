# API 설정 가이드

> 이 문서는 프로젝트에 필요한 모든 API 키 발급 방법을 정리합니다.
> Phase 1부터 순서대로 필요한 것만 발급하면 됩니다.

---

## Phase 1에서 필요

### 1. Gemini API Key

**발급 절차:**
1. https://aistudio.google.com/ 접속
2. Google 계정으로 로그인
3. 좌측 메뉴 "Get API Key" 클릭
4. "Create API Key" → 프로젝트 선택 또는 새로 생성
5. 생성된 API 키 복사

**무료 티어 한도:**
- Gemini 2.0 Flash: 분당 15회, 일일 1,500회
- 이 프로젝트에 충분한 수준

**테스트 방법:**
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello, test!"}]}]}'
```

### 2. Make.com 계정

**가입 절차:**
1. https://www.make.com/ 접속
2. "Get started free" 클릭
3. 이메일로 가입 또는 Google 로그인

**무료 플랜 한도:**
- 월 1,000 오퍼레이션
- 2개 활성 시나리오
- 매일 1회 실행이면 충분

---

## Phase 2에서 필요

### 3. Glide 계정 (앱 빌더)

**가입 절차:**
1. https://www.glideapps.com/ 접속
2. Google 계정으로 로그인
3. "New Project" → 템플릿 또는 빈 프로젝트

**무료 플랜 한도:**
- 앱 1개
- 500행 데이터
- 프로토타입에 충분

---

## Phase 3에서 필요

### 4. HeyGen API Key

**발급 절차:**
1. https://www.heygen.com/ 가입
2. 대시보드 → Settings → API
3. API Key 생성

**가격:**
- Creator Plan: ~$24/월
- 영상 크레딧 기반 과금

### 5. ElevenLabs API Key (선택)

**발급 절차:**
1. https://elevenlabs.io/ 가입
2. Profile → API Keys
3. 키 생성

**가격:**
- Free: 10,000 characters/월
- Starter: $5/월, 30,000 characters

### 6. Unsplash API Key (배경 이미지)

**발급 절차:**
1. https://unsplash.com/developers 접속
2. "Register as a Developer"
3. "New Application" 생성
4. Access Key 복사

**무료 한도:**
- 시간당 50회 요청
- 이 프로젝트에 충분

---

## Phase 4에서 필요

### 7. YouTube Data API

**발급 절차:**
1. https://console.cloud.google.com/ 접속
2. 프로젝트 생성
3. "YouTube Data API v3" 활성화
4. OAuth 2.0 클라이언트 ID 생성
5. 동의 화면 설정

### 8. Instagram Graph API

**발급 절차:**
1. Facebook 비즈니스 계정 필요
2. https://developers.facebook.com/ 에서 앱 생성
3. Instagram Basic Display API 추가
4. 비즈니스 인스타그램 계정 연결

### 9. Twitter API v2

**발급 절차:**
1. https://developer.twitter.com/ 접속
2. 개발자 계정 신청
3. 프로젝트 + 앱 생성
4. API Key, Secret, Bearer Token 발급

---

## API 키 관리 주의사항

1. **절대 공개 저장소(GitHub 등)에 API 키를 올리지 마세요**
2. Make.com의 Connection 기능을 사용하면 키가 안전하게 저장됩니다
3. 로컬 테스트 시 `.env` 파일에 저장하고 `.gitignore`에 추가
4. 키가 유출된 경우 즉시 재생성

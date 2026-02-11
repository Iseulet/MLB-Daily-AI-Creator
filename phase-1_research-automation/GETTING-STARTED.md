# Phase 1 시작하기

## 바로 할 일 (Quick Start)

### 1단계: 계정 만들기 (10분)
- [ ] Google AI Studio 가입 → Gemini API 키 발급
- [ ] Make.com 가입

### 2단계: Gemini 테스트 (15분)
- [ ] Google AI Studio에서 직접 프롬프트 테스트
- [ ] `docs/01_PHASE-1-PLAN.md`의 리서치 프롬프트를 복사해서 실행
- [ ] 결과가 JSON 형식으로 잘 나오는지 확인
- [ ] 프롬프트 수정/튜닝 반복

### 3단계: Make.com 시나리오 구축 (30분)
- [ ] 새 시나리오 생성
- [ ] Schedule 모듈 추가 (매일 오전 8시)
- [ ] HTTP Request 모듈 추가 (Gemini API 호출)
- [ ] JSON Parse 모듈 추가
- [ ] Gmail 모듈 추가 (결과 이메일 전송)
- [ ] 시나리오 수동 실행 테스트

### 4단계: 안정화 (1주일)
- [ ] 매일 아침 이메일 수신 확인
- [ ] 뉴스 품질 검토 및 프롬프트 개선
- [ ] Phase 2 진행 여부 판단

## 문제 해결

| 문제 | 해결 방법 |
|------|-----------|
| API 키 오류 | Google AI Studio에서 키 재생성 |
| JSON 파싱 실패 | Gemini 프롬프트에 "반드시 유효한 JSON만 출력" 강조 |
| 이메일 미수신 | Make.com 실행 로그 확인 → Gmail 모듈 연결 상태 확인 |
| 뉴스가 부정확 | Google Search grounding 옵션 활성화 |

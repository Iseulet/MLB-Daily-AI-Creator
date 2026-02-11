# 기술 선택 근거 기록 (Tech Decision Log)

> 프로젝트 진행 중 내린 기술적 결정과 그 근거를 기록합니다.
> 나중에 "왜 이 도구를 선택했지?"라는 질문에 답하기 위한 문서입니다.

---

## Decision #1: AI 모델 - Gemini 선택

**날짜:** 프로젝트 시작 시점
**선택:** Google Gemini API
**대안:** ChatGPT API, Claude API

**선택 근거:**
- Google Search와 네이티브 연동 (grounding) → 실시간 MLB 뉴스 수집에 최적
- 무료 티어가 넉넉 (일 1,500회)
- JSON 출력 안정성 양호
- Make.com과의 HTTP 연동 용이

**트레이드오프:**
- ChatGPT가 대본 창작 품질은 더 나을 수 있음
- 필요시 대본 생성 단계만 ChatGPT로 전환 가능 (하이브리드)

---

## Decision #2: 자동화 도구 - Make.com 선택

**날짜:** 프로젝트 시작 시점
**선택:** Make.com
**대안:** Zapier, n8n, Pipedream

**선택 근거:**
- 시각적 시나리오 빌더가 직관적
- HTTP 모듈이 유연 (어떤 API든 연동 가능)
- JSON 파싱 모듈 내장
- 무료 플랜으로 프로토타입 가능

**트레이드오프:**
- n8n이 셀프호스팅 시 무료이지만 설치/관리 필요
- Zapier가 더 많은 네이티브 연동을 제공하지만 비쌈

---

## Decision #3: 앱 빌더 - Glide → FlutterFlow 전략

**날짜:** 프로젝트 시작 시점
**선택:** 초기 Glide, 이후 FlutterFlow
**대안:** Bubble, Adalo, 직접 코딩

**선택 근거:**
- Glide: 가장 빠른 프로토타이핑 (스프레드시트 기반)
- FlutterFlow: 앱스토어 출시 가능, 커스터마이징 자유도 높음
- 2단계 전략으로 속도와 품질 모두 확보

**트레이드오프:**
- Glide에서 FlutterFlow로 마이그레이션 시 재작업 필요
- 직접 코딩(Flutter/React Native)이 가장 자유롭지만 개발 기간 길어짐

---

## Decision #4: 영상 생성 - HeyGen 선택

**날짜:** Phase 3 시작 시
**선택:** HeyGen
**대안:** InVideo AI, Pictory, Runway

**선택 근거:**
- AI 아바타로 차별화된 콘텐츠 가능
- 한국어 TTS 지원
- 자막 자동 삽입
- API 지원으로 자동화 가능

**트레이드오프:**
- 월 $24 비용 발생
- 아바타 스타일이 제한적
- InVideo AI가 b-roll 스타일에는 더 적합할 수 있음

---

## 향후 결정 필요 사항

| 결정 | 시점 | 옵션 |
|------|------|------|
| TTS 음성 스타일 최종 선택 | Phase 3 | ElevenLabs vs HeyGen 내장 TTS |
| 데이터 저장소 업그레이드 | Phase 4 | Google Sheets vs Firebase vs Supabase |
| 수익화 모델 | 출시 후 | 구독제 vs 광고 vs 프리미엄 기능 |
| 다국어 지원 | 확장 시 | 영어/일본어 대본 생성 추가 |

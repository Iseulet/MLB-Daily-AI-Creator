# 비용 최적화 리서치 결과

> Phase 3~4에서 발생하는 월 $39~69 비용을 최소화하기 위한 대안 조사
> 조사일: 2026-02-11

---

## 현재 계획 vs 최적화 후 비용 비교

| 영역 | 현재 계획 | 월 비용 | 최적화 대안 | 월 비용 |
|------|-----------|---------|-------------|---------|
| 영상 생성 | HeyGen | $24 | FFmpeg + MoviePy (Python) | **$0** |
| TTS 음성 | ElevenLabs | $5 | Edge TTS / Google Cloud TTS | **$0** |
| 자동화 | Make.com Core | $9 | n8n 셀프호스팅 / GitHub Actions | **$0** |
| 앱 UI | Glide Pro | $25 | Streamlit / Vercel (Next.js) | **$0** |
| 소셜 업로드 | Make.com 경유 | (포함) | Python 스크립트 / GitHub Actions | **$0** |
| **합계** | | **$39~69/월** | | **$0~5/월** |

---

# A. 영상 생성 대안 (HeyGen $24/월 → $0)

## 추천 순위

### 1순위: FFmpeg + MoviePy + Pillow (Python 파이프라인) -- $0

> 코드로 직접 영상을 조립하는 방식. 가장 유연하고 완전 무료.

```
[대본 텍스트]
     ├──→ [TTS] → 음성 파일 (.mp3)
     ├──→ [Pexels API] → 배경 영상/이미지 (무료)
     ├──→ [Pillow] → 스탯 그래픽 생성
     └──→ [Whisper] → 자막 타임스탬프 (.srt)
              │
              ▼
     [MoviePy: 전부 합성 → MP4 출력]
```

- **비용**: $0 (로컬 PC에서 실행)
- **장점**: 완전한 커스터마이징, 무제한 영상 생성, 워터마크 없음
- **단점**: Python 개발 필요, 초기 세팅에 시간 소요
- **필요 라이브러리**:
  - `moviepy` (v2.0) -- 영상 합성
  - `Pillow` -- 텍스트/이미지 오버레이
  - `faster-whisper` -- 자막 생성
  - `pexels-api` -- 무료 스톡 영상
  - `ffmpeg-python` -- 인코딩

### 2순위: MoneyPrinter (오픈소스 턴키 솔루션) -- $0

- **URL**: https://github.com/FujiwaraChoki/MoneyPrinter
- **설명**: 주제 입력 → 대본 → TTS → 스톡영상 → 자막 → 완성 영상까지 자동화된 파이썬 프로젝트
- **비용**: $0 (Gemini API 무료 티어 + Pexels 무료)
- **장점**: 이미 만들어진 파이프라인, 포크해서 MLB 특화 커스텀 가능
- **단점**: 커뮤니티 유지보수, 비공식 TTS API 사용

### 3순위: Remotion (React 기반 영상 프레임워크) -- $0

- **URL**: https://remotion.dev
- **설명**: React 컴포넌트로 영상을 만드는 프레임워크
- **비용**: 개인/3인 이하 팀 무료 (상업적 사용 포함)
- **장점**: React 개발자에게 최적, 데이터 기반 영상에 강점
- **단점**: React/TypeScript 지식 필요

### 참고: 클라우드 API 옵션 (유료)

| 서비스 | 가격 | 특징 |
|--------|------|------|
| Shotstack | $39/월 | JSON 기반 영상 API, 200크레딧 |
| JSON2Video | $49.95/월 | JSON → 영상, 자막 자동 |
| Creatomate | $54/월 | 템플릿 기반, REST API |

→ 유료 옵션은 현재 HeyGen($24)보다 오히려 비쌈. **Python 파이프라인이 가장 합리적**.

---

# B. TTS 음성 대안 (ElevenLabs $5/월 → $0)

## 추천 순위

### 1순위: Edge TTS (Microsoft) -- $0, 무제한

- **URL**: https://github.com/rany2/edge-tts
- **비용**: 완전 무료, API 키 불필요, 글자수 제한 없음
- **한국어 음성**: `ko-KR-SunHiNeural` (여성), `ko-KR-InJoonNeural` (남성)
- **품질**: 8/10 -- 뉴럴 음성, 자연스러운 억양
- **사용법**: `pip install edge-tts`, 코드 5줄로 구현
- **Make.com 연동**: 셀프호스팅 래퍼를 통해 HTTP 호출 가능

```python
import edge_tts
import asyncio

async def generate_speech(text, output_file):
    communicate = edge_tts.Communicate(text, "ko-KR-SunHiNeural")
    await communicate.save(output_file)

asyncio.run(generate_speech("오타니가 또 해냈습니다!", "output.mp3"))
```

### 2순위: Google Cloud TTS -- $0 (월 100만 자 무료)

- **URL**: https://cloud.google.com/text-to-speech
- **비용**: WaveNet/Neural2 음성 월 100만 자 무료 (초과 시 $16/100만 자)
- **한국어 품질**: 9/10 -- Edge TTS보다 한 단계 위
- **Make.com**: 네이티브 연동 모듈 있음 (가장 쉬운 통합)
- **주의**: Google Cloud 계정 + 카드 등록 필요 (과금은 무료 한도 초과 시만)

### 3순위: Kokoro-82M (로컬 오픈소스) -- $0, 오프라인

- **URL**: https://huggingface.co/hexgrad/Kokoro-82M
- **비용**: 완전 무료, 로컬 실행
- **한국어 품질**: 7.5/10
- **특징**: CPU에서도 실행 가능, 82M 파라미터로 가벼움
- **사용법**: `pip install kokoro`

### 4순위: Naver CLOVA Voice -- 한국어 최고 품질

- **URL**: https://www.ncloud.com/v2/product/aiService/clovaVoice
- **비용**: 기본 100만 자 포함, 이후 종량제
- **한국어 품질**: 9.5/10 -- 한국어 전용 100개 음성, 최고 품질
- **특징**: 한국어에 가장 특화된 서비스

### 비교표

| 서비스 | 비용 | 한국어 품질 | 오프라인 | GPU 필요 | Make.com |
|--------|------|------------|---------|---------|----------|
| **Edge TTS** | $0 무제한 | 8/10 | X | X | HTTP 래퍼 |
| **Google Cloud TTS** | $0 (100만자/월) | 9/10 | X | X | 네이티브 |
| **Kokoro-82M** | $0 로컬 | 7.5/10 | O | X (CPU OK) | 셀프호스팅 |
| **Naver CLOVA** | ~$0 (기본포함) | 9.5/10 | X | X | HTTP |
| ElevenLabs (현재) | $5/월 | 8.5/10 | X | X | 네이티브 |

---

# C. 자동화 도구 대안 (Make.com $9/월 → $0)

## 추천 순위

### 1순위: n8n 셀프호스팅 -- $0

- **URL**: https://n8n.io
- **설명**: Make.com과 동일한 시각적 워크플로우 빌더, 오픈소스
- **비용**: 셀프호스팅 시 $0 (Docker로 로컬 실행)
- **무료 호스팅 옵션**:
  - Railway 무료 티어 (월 $5 크레딧 제공)
  - Render 무료 티어 (슬립 모드 있음)
  - 로컬 PC에서 Docker로 상시 실행
- **장점**: Make.com과 거의 동일한 UI, 400+ 노드, 무제한 워크플로우
- **단점**: 셀프호스팅 관리 필요

### 2순위: GitHub Actions -- $0

- **URL**: https://github.com/features/actions
- **비용**: 퍼블릭 레포 무제한 무료, 프라이빗 월 2,000분 무료
- **사용법**: cron 스케줄로 매일 오전 8시 실행, Python 스크립트 트리거
- **장점**: 코드 기반 자동화, 버전 관리 자동, 무료 한도 넉넉
- **단점**: 시각적 빌더 없음, YAML 작성 필요

```yaml
# .github/workflows/mlb-daily.yml
name: MLB Daily Research
on:
  schedule:
    - cron: '0 23 * * *'  # UTC 23:00 = KST 08:00
jobs:
  research:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/daily_research.py
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

### 3순위: Google Apps Script -- $0

- **URL**: https://script.google.com
- **비용**: 완전 무료
- **장점**: Google Sheets/Gmail과 네이티브 연동, 트리거 설정 간단
- **단점**: JavaScript만 사용, 실행 시간 6분 제한, 외부 API 호출 제한적

### 4순위: Python + Cron (로컬/VPS) -- $0

- 로컬 PC의 Windows 작업 스케줄러로 Python 스크립트 매일 실행
- 또는 Oracle Cloud 무료 VPS(평생 무료)에서 cron 실행

### 비교표

| 서비스 | 비용 | 시각적 빌더 | 설정 난이도 | 무료 한도 |
|--------|------|------------|------------|----------|
| **n8n 셀프호스팅** | $0 | O | 중 | 무제한 |
| **GitHub Actions** | $0 | X | 중 | 월 2,000분 |
| **Google Apps Script** | $0 | X | 하 | 일 90분 실행 |
| **Python + Cron** | $0 | X | 중 | 무제한 |
| Make.com (현재) | $9/월 | O | 하 | 월 10,000 ops |

---

# D. 앱 UI/호스팅 대안 (Glide $25/월 → $0)

## 추천 순위

### 1순위: Streamlit Community Cloud -- $0

- **URL**: https://streamlit.io
- **설명**: Python으로 대시보드/웹앱을 빠르게 만드는 프레임워크
- **비용**: Community Cloud 무료 호스팅
- **장점**: Python만으로 UI 구현, 대시보드에 최적, 무료 배포
- **단점**: 모바일 최적화 제한적, 커스텀 디자인 한계

```python
import streamlit as st

st.title("MLB Daily AI Creator")
st.subheader("2026년 2월 11일 - 오늘의 핵심 뉴스")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### #1 오타니 10호 홈런")
    if st.button("영상 만들기", key="news1"):
        generate_script(news_1)
```

### 2순위: Vercel + Next.js -- $0

- **URL**: https://vercel.com
- **비용**: 취미 플랜 무료 (월 100GB 대역폭)
- **장점**: 프로덕션급 웹앱, 모바일 반응형, 서버리스 함수 포함
- **단점**: React/Next.js 개발 필요

### 3순위: Gradio on Hugging Face Spaces -- $0

- **URL**: https://huggingface.co/spaces
- **설명**: Python으로 AI 데모 앱을 만드는 프레임워크
- **비용**: Hugging Face Spaces 무료 호스팅
- **장점**: AI/ML 앱에 특화, 파일 업/다운로드 기본 지원

### 4순위: Telegram/Discord Bot -- $0

- 앱 대신 봇 인터페이스로 시작
- 매일 아침 뉴스 카드 전송 → 사용자가 선택 → 대본 생성 → 영상 전달
- **장점**: 별도 앱 개발 불필요, 즉시 구현 가능
- **단점**: UI 제약, 알림 기반 경험

### 비교표

| 서비스 | 비용 | 개발 언어 | 모바일 지원 | 배포 난이도 |
|--------|------|----------|------------|------------|
| **Streamlit** | $0 | Python | 제한적 | 매우 쉬움 |
| **Vercel + Next.js** | $0 | React | 우수 | 중 |
| **Gradio + HF Spaces** | $0 | Python | 보통 | 쉬움 |
| **Telegram Bot** | $0 | Python | 우수 | 쉬움 |
| Glide (현재) | $0~25/월 | 노코드 | 우수 | 매우 쉬움 |

---

# E. 소셜 미디어 업로드 (무료 방법)

### YouTube 업로드 -- $0
- **YouTube Data API v3**: 무료 할당량 일 10,000 유닛
- 영상 업로드 = 1,600 유닛 → 하루 6개 영상 업로드 가능
- Python `google-api-python-client` 라이브러리로 구현

### Instagram -- 제한적
- Instagram Graph API: 비즈니스 계정 필요, Reels 업로드 지원
- 무료이지만 Facebook 앱 심사 필요

### Twitter/X -- $0 (Free 티어)
- Free 티어: 월 1,500 트윗 게시 가능
- 미디어 업로드 포함

---

# F. 최종 추천: 3가지 비용 시나리오

## 시나리오 A: "완전 무료" -- $0/월

> 모든 것을 로컬 + 오픈소스로 해결

| 영역 | 도구 | 비용 |
|------|------|------|
| 리서치 | Gemini API 무료 티어 | $0 |
| 대본 생성 | Gemini API 무료 티어 | $0 |
| TTS | Edge TTS | $0 |
| 영상 생성 | MoviePy + FFmpeg | $0 |
| 자막 | faster-whisper | $0 |
| 배경 소재 | Pexels/Unsplash API | $0 |
| 자동화 | GitHub Actions / n8n | $0 |
| 앱 UI | Streamlit Community Cloud | $0 |
| 업로드 | YouTube Data API | $0 |
| **합계** | | **$0/월** |

**적합한 경우**: Python 개발이 가능하거나 학습 의지가 있는 경우
**트레이드오프**: 초기 개발 시간 투자 필요 (2~4주), AI 아바타 없음

## 시나리오 B: "최소 비용" -- ~$5/월

> 핵심만 유료, 나머지 무료

| 영역 | 도구 | 비용 |
|------|------|------|
| 리서치 + 대본 | Gemini API 무료 티어 | $0 |
| TTS | Google Cloud TTS 무료 티어 | $0 |
| 영상 생성 | MoviePy + FFmpeg | $0 |
| 자동화 | n8n on Railway | ~$5 |
| 앱 UI | Streamlit | $0 |
| **합계** | | **~$5/월** |

**적합한 경우**: 시각적 자동화 빌더(n8n)를 클라우드에서 편하게 쓰고 싶은 경우

## 시나리오 C: "균형형" -- ~$15/월

> 편의성과 비용의 균형

| 영역 | 도구 | 비용 |
|------|------|------|
| 리서치 + 대본 | Gemini API | $0 |
| TTS | Naver CLOVA Voice | ~$0 (기본 포함) |
| 영상 생성 | MoviePy + FFmpeg | $0 |
| 자동화 | Make.com 무료 → Core | $0~9 |
| 앱 UI | Glide 무료 플랜 | $0 |
| TTS 보강 | ElevenLabs Starter | $5 |
| **합계** | | **~$5~15/월** |

**적합한 경우**: 노코드 도구를 선호하고, 한국어 TTS 품질이 중요한 경우

---

# G. 핵심 결론

1. **가장 큰 절감**: HeyGen($24) → MoviePy/FFmpeg($0)로 **월 $24 절약**
   - AI 아바타는 포기하지만, 자막 + 배경영상 + TTS 조합으로 충분히 매력적인 숏폼 제작 가능
   - MoneyPrinter 같은 오픈소스 프로젝트를 포크하면 개발 시간도 단축

2. **두 번째 절감**: ElevenLabs($5) → Edge TTS($0)로 **월 $5 절약**
   - Edge TTS의 한국어 뉴럴 음성이 충분히 자연스러움
   - 더 높은 품질이 필요하면 Google Cloud TTS 무료 티어(월 100만 자)

3. **세 번째 절감**: Make.com($9) → GitHub Actions / n8n($0)
   - 개발자라면 GitHub Actions가 가장 깔끔
   - 시각적 빌더를 원하면 n8n 셀프호스팅

4. **앱 UI**: Streamlit이 Python 개발자에게 가장 빠른 선택지
   - 대시보드형 워크플로우에 최적화된 프레임워크

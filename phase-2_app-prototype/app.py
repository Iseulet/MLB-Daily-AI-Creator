"""
MLB Daily AI Creator - Phase 2 대시보드
Streamlit 기반 뉴스 대시보드 + 숏폼 대본 생성기
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# Phase 1 src를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase-1_research-automation" / "src"))

from data_store import get_available_dates, get_news, save_script, get_scripts
from script_generator import generate_script

# Phase 1 리서치 함수 재사용
try:
    from researcher import research_mlb_news
    HAS_RESEARCHER = True
except ImportError:
    HAS_RESEARCHER = False

API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── 페이지 설정 ──
st.set_page_config(
    page_title="MLB Daily AI Creator",
    page_icon="&#9918;",
    layout="wide",
)

# ── 커스텀 CSS ──
st.markdown("""
<style>
.news-card {
    background: #f8f9fb;
    border-radius: 10px;
    padding: 20px;
    border-left: 5px solid #1a2a6c;
    margin-bottom: 12px;
}
.news-rank {
    display: inline-block;
    background: #1a2a6c;
    color: white;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    text-align: center;
    line-height: 28px;
    font-weight: bold;
    font-size: 14px;
    margin-right: 8px;
}
.korean-card {
    background: #fff8f0;
    border-radius: 10px;
    padding: 16px;
    border-left: 5px solid #e67e22;
    margin-bottom: 8px;
}
.shorts-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}
.shorts-high { background: #fde8e8; color: #e74c3c; }
.shorts-medium { background: #fef3e2; color: #f39c12; }
.shorts-low { background: #eee; color: #95a5a6; }
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ──
with st.sidebar:
    st.title("MLB Daily AI Creator")

    # API 키 입력 (환경변수 없으면)
    if not API_KEY:
        API_KEY = st.text_input("Gemini API Key", type="password")

    st.divider()

    # 날짜 선택
    dates = get_available_dates()
    if dates:
        selected_date = st.selectbox("날짜 선택", dates, index=0)
    else:
        selected_date = None
        st.warning("수집된 뉴스가 없습니다.")

    # 수동 리서치 버튼
    if HAS_RESEARCHER and API_KEY:
        if st.button("지금 뉴스 수집", use_container_width=True):
            with st.spinner("Gemini로 뉴스 수집 중..."):
                try:
                    import json
                    from datetime import datetime
                    news_data = research_mlb_news(API_KEY)
                    out_dir = Path(__file__).resolve().parent.parent / "phase-1_research-automation" / "outputs"
                    out_dir.mkdir(exist_ok=True)
                    today = datetime.now().strftime("%Y-%m-%d")
                    with open(out_dir / f"{today}.json", "w", encoding="utf-8") as f:
                        json.dump(news_data, f, ensure_ascii=False, indent=2)
                    st.success(f"뉴스 {len(news_data.get('top_news', []))}건 수집 완료!")
                    st.rerun()
                except Exception as e:
                    st.error(f"수집 실패: {e}")

    st.divider()
    page = st.radio("메뉴", ["뉴스 대시보드", "대본 생성", "저장된 대본"], label_visibility="collapsed")


# ── 페이지 1: 뉴스 대시보드 ──
if page == "뉴스 대시보드":
    if not selected_date:
        st.info("사이드바에서 '지금 뉴스 수집' 버튼을 눌러 시작하세요.")
        st.stop()

    news_data = get_news(selected_date)
    if not news_data:
        st.warning(f"{selected_date} 뉴스 데이터가 없습니다.")
        st.stop()

    st.header(f"{selected_date} MLB 핵심 뉴스")

    # TOP 뉴스 카드
    for news in news_data.get("top_news", []):
        potential = news.get("shorts_potential", "low")
        badge_class = f"shorts-{potential}"

        st.markdown(f"""
        <div class="news-card">
            <span class="news-rank">{news.get('rank', '')}</span>
            <strong style="font-size:16px;">{news.get('headline', '')}</strong>
            <span class="shorts-badge {badge_class}" style="margin-left:8px;">{potential.upper()}</span>
            <p style="margin-top:8px; color:#555; line-height:1.6;">{news.get('summary', '')}</p>
            <p style="font-size:12px; color:#888;">
                선수: {', '.join(news.get('players', [])) or '-'}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 한국 선수 동향
    korean = news_data.get("korean_players", [])
    if korean:
        st.subheader("한국 선수 동향")
        for player in korean:
            st.markdown(f"""
            <div class="korean-card">
                <strong style="color:#e67e22;">{player.get('name', '')}</strong>
                <span style="color:#888; margin-left:6px;">{player.get('team', '')}</span>
                <p style="margin-top:4px; color:#444;">{player.get('result', '')}</p>
                <p style="font-size:12px; color:#e67e22;">{player.get('highlight', '')}</p>
            </div>
            """, unsafe_allow_html=True)

    # 숏폼 추천
    shorts = news_data.get("recommended_shorts_topic", {})
    if shorts:
        st.subheader("숏폼 콘텐츠 추천")
        st.info(f"**{shorts.get('topic', '')}**\n\n{shorts.get('reason', '')}")
        hook = shorts.get("script_hook", "")
        if hook:
            st.caption(f'후킹 멘트: "{hook}"')


# ── 페이지 2: 대본 생성 ──
elif page == "대본 생성":
    st.header("숏폼 대본 생성")

    if not API_KEY:
        st.warning("사이드바에서 Gemini API Key를 입력해주세요.")
        st.stop()

    if not selected_date:
        st.warning("수집된 뉴스가 없습니다. 먼저 뉴스를 수집해주세요.")
        st.stop()

    news_data = get_news(selected_date)
    if not news_data:
        st.warning(f"{selected_date} 뉴스 데이터가 없습니다.")
        st.stop()

    top_news = news_data.get("top_news", [])
    if not top_news:
        st.warning("뉴스가 비어있습니다.")
        st.stop()

    # 뉴스 선택
    news_options = {f"#{n['rank']} {n['headline']}": n for n in top_news}
    selected_headline = st.selectbox("뉴스 선택", list(news_options.keys()))
    selected_news = news_options[selected_headline]

    # 옵션
    col1, col2 = st.columns(2)
    with col1:
        tone = st.radio("말투", ["유머러스", "분석적", "열정적"], horizontal=True)
    with col2:
        duration = st.radio("길이", [30, 45, 60], horizontal=True, format_func=lambda x: f"{x}초")

    # 생성 버튼
    if st.button("대본 생성", type="primary", use_container_width=True):
        with st.spinner("Gemini로 대본 생성 중..."):
            try:
                script = generate_script(API_KEY, selected_news, tone, duration)
                st.session_state["generated_script"] = script
            except Exception as e:
                st.error(f"대본 생성 실패: {e}")

    # 생성 결과 표시
    if "generated_script" in st.session_state:
        script = st.session_state["generated_script"]

        st.divider()
        st.subheader("생성된 대본")

        # Hook
        st.markdown("**훅 (첫 5초)**")
        st.info(script.get("hook", ""))

        # Body
        st.markdown("**본문**")
        st.write(script.get("body", ""))

        # Closing
        st.markdown("**마무리**")
        st.write(script.get("closing", ""))

        st.divider()

        # 전체 대본 (편집 가능)
        st.markdown("**전체 대본 (편집 가능)**")
        edited_script = st.text_area(
            "전체 대본",
            value=script.get("full_script", ""),
            height=200,
            label_visibility="collapsed",
        )

        # 해시태그
        tags = script.get("suggested_hashtags", [])
        if tags:
            st.caption(" ".join(tags))

        # 저장 버튼
        col_save, col_regen = st.columns(2)
        with col_save:
            if st.button("대본 저장", use_container_width=True):
                script["full_script"] = edited_script
                path = save_script(selected_date, selected_news.get("rank", 0), script)
                st.success(f"저장 완료!")
        with col_regen:
            if st.button("다시 생성", use_container_width=True):
                del st.session_state["generated_script"]
                st.rerun()


# ── 페이지 3: 저장된 대본 ──
elif page == "저장된 대본":
    st.header("저장된 대본")

    scripts = get_scripts(selected_date)
    if not scripts:
        st.info("저장된 대본이 없습니다. '대본 생성' 메뉴에서 대본을 만들어보세요.")
        st.stop()

    for i, s in enumerate(scripts):
        meta = s.get("_meta", {})
        with st.expander(f"{meta.get('news_headline', '제목 없음')} | {meta.get('tone', '')} {meta.get('duration', '')}초"):
            st.markdown(f"**훅:** {s.get('hook', '')}")
            st.write(s.get("full_script", ""))
            tags = s.get("suggested_hashtags", [])
            if tags:
                st.caption(" ".join(tags))
            st.caption(f"파일: {s.get('_filename', '')}")

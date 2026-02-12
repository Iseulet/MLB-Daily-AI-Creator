"""
MLB Daily AI Creator - 통합 대시보드
Streamlit 기반 뉴스 대시보드 + 숏폼 대본 생성 + 영상 생성 + YouTube 업로드
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# 각 Phase src를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase-1_research-automation" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase-3_video-pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase-4_integration" / "src"))

# 통합 환경변수 로더 (fallback: 기존 load_dotenv)
try:
    from pipeline_config import load_all_env
    load_all_env()
except ImportError:
    load_dotenv(Path(__file__).resolve().parent / ".env")

from data_store import get_available_dates, get_news, save_script, get_scripts
from script_generator import generate_script

# Phase 1 리서치 함수
try:
    from researcher import research_mlb_news
    HAS_RESEARCHER = True
except ImportError:
    HAS_RESEARCHER = False

# Phase 3 영상 생성
try:
    from video_pipeline import run_pipeline as generate_video
    HAS_VIDEO = True
except ImportError:
    HAS_VIDEO = False

# Phase 4 업로드 + 메타데이터 + 히스토리
try:
    from youtube_uploader import upload_to_youtube
    from metadata_generator import generate_metadata
    from history import save_history, get_history
    HAS_UPLOAD = True
except ImportError:
    HAS_UPLOAD = False

# 전체 파이프라인 (원클릭)
try:
    from full_pipeline import run_full_pipeline, PipelineOptions
    HAS_FULL_PIPELINE = True
except ImportError:
    HAS_FULL_PIPELINE = False

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
.history-card {
    background: #f0f4ff;
    border-radius: 10px;
    padding: 16px;
    border-left: 5px solid #3b82f6;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ──
with st.sidebar:
    st.title("MLB Daily AI Creator")

    if not API_KEY:
        API_KEY = st.text_input("Gemini API Key", type="password")

    st.divider()

    dates = get_available_dates()
    if dates:
        selected_date = st.selectbox("날짜 선택", dates, index=0)
    else:
        selected_date = None
        st.warning("수집된 뉴스가 없습니다.")

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

    menu_items = []
    if HAS_FULL_PIPELINE:
        menu_items.append("원클릭 자동 생성")
    menu_items += ["뉴스 대시보드", "대본 생성", "저장된 대본"]
    if HAS_UPLOAD:
        menu_items.append("히스토리")
    page = st.radio("메뉴", menu_items, label_visibility="collapsed")


# ── 원클릭 자동 생성 ──
if page == "원클릭 자동 생성":
    st.header("원클릭 자동 생성")
    st.caption("리서치 → 대본 → 영상 → 메타데이터 → YouTube 업로드까지 한번에 실행합니다.")

    if not API_KEY:
        st.warning("사이드바에서 Gemini API Key를 입력해주세요.")
        st.stop()

    # 옵션 선택
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        pipe_tone = st.radio("말투", ["유머러스", "분석적", "열정적"], horizontal=True, key="pipe_tone")
        pipe_duration = st.radio("길이", [30, 45, 60], horizontal=True, format_func=lambda x: f"{x}초", key="pipe_dur")
    with col_opt2:
        pipe_voice = st.radio("음성", ["male", "female"], horizontal=True,
                              format_func=lambda x: "남성" if x == "male" else "여성", key="pipe_voice")
        pipe_rank = st.number_input("뉴스 순위", min_value=1, max_value=5, value=1, key="pipe_rank")
    with col_opt3:
        pipe_privacy = st.selectbox(
            "YouTube 공개 설정",
            ["private", "unlisted", "public"],
            format_func=lambda x: {"private": "비공개", "unlisted": "일부 공개", "public": "전체 공개"}[x],
            key="pipe_privacy",
        )
        pipe_skip_upload = st.checkbox("YouTube 업로드 스킵", value=False, key="pipe_skip_upload")

    st.divider()

    if st.button("파이프라인 실행", type="primary", use_container_width=True):
        options = PipelineOptions(
            tone=pipe_tone,
            duration=pipe_duration,
            voice=pipe_voice,
            news_rank=pipe_rank,
            privacy=pipe_privacy,
            skip_upload=pipe_skip_upload,
            skip_email=True,
        )

        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()

        stage_order = ["research", "script", "video", "metadata", "upload", "history"]
        stage_labels = {
            "research": "뉴스 수집",
            "script": "대본 생성",
            "video": "영상 생성",
            "metadata": "메타데이터 생성",
            "upload": "YouTube 업로드",
            "history": "히스토리 저장",
            "config": "설정 확인",
        }

        def streamlit_callback(stage: str, status: str, message: str):
            label = stage_labels.get(stage, stage)
            if status == "start":
                idx = stage_order.index(stage) if stage in stage_order else 0
                progress_bar.progress((idx) / len(stage_order))
                status_text.info(f"**[{label}]** {message}")
            elif status == "done":
                idx = stage_order.index(stage) if stage in stage_order else 0
                progress_bar.progress((idx + 1) / len(stage_order))
                status_text.success(f"**[{label}]** {message}")
            elif status == "error":
                status_text.error(f"**[{label}]** {message}")
            elif status == "skip":
                status_text.warning(f"**[{label}]** {message}")

        result = run_full_pipeline(options, callback=streamlit_callback)
        progress_bar.progress(1.0)
        st.session_state["pipeline_result"] = result

    # 결과 표시
    if "pipeline_result" in st.session_state:
        result = st.session_state["pipeline_result"]
        st.divider()

        if result.success:
            st.success(f"파이프라인 완료! (완료된 단계: {', '.join(result.stages_completed)})")
        else:
            st.error("파이프라인 실패")

        if result.errors:
            with st.expander("에러 목록"):
                for err in result.errors:
                    st.warning(err)

        # 영상 미리보기
        if result.video_path and Path(result.video_path).exists():
            st.subheader("생성된 영상")
            st.video(result.video_path)
            with open(result.video_path, "rb") as f:
                st.download_button(
                    "영상 다운로드 (.mp4)", data=f,
                    file_name=Path(result.video_path).name,
                    mime="video/mp4", use_container_width=True,
                )

        # YouTube URL
        if result.upload_result and result.upload_result.get("url"):
            st.subheader("YouTube")
            url = result.upload_result["url"]
            st.markdown(f"**URL:** [{url}]({url})")

        # 대본
        if result.script:
            with st.expander("생성된 대본"):
                st.markdown(f"**훅:** {result.script.get('hook', '')}")
                st.write(result.script.get("full_script", ""))
                tags = result.script.get("suggested_hashtags", [])
                if tags:
                    st.caption(" ".join(tags))

        # 메타데이터
        if result.metadata:
            with st.expander("생성된 메타데이터"):
                yt = result.metadata.get("youtube", {})
                st.markdown(f"**YouTube 제목:** {yt.get('title', '')}")
                st.markdown(f"**설명:** {yt.get('description', '')}")
                st.markdown(f"**태그:** {', '.join(yt.get('tags', []))}")
                ig = result.metadata.get("instagram", {})
                if ig:
                    st.markdown(f"**Instagram:** {ig.get('caption', '')}")
                tw = result.metadata.get("twitter", {})
                if tw:
                    st.markdown(f"**Twitter:** {tw.get('tweet_text', '')}")


# ── 페이지 1: 뉴스 대시보드 ──
elif page == "뉴스 대시보드":
    if not selected_date:
        st.info("사이드바에서 '지금 뉴스 수집' 버튼을 눌러 시작하세요.")
        st.stop()

    news_data = get_news(selected_date)
    if not news_data:
        st.warning(f"{selected_date} 뉴스 데이터가 없습니다.")
        st.stop()

    st.header(f"{selected_date} MLB 핵심 뉴스")

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

    news_options = {f"#{n['rank']} {n['headline']}": n for n in top_news}
    selected_headline = st.selectbox("뉴스 선택", list(news_options.keys()))
    selected_news = news_options[selected_headline]

    col1, col2 = st.columns(2)
    with col1:
        tone = st.radio("말투", ["유머러스", "분석적", "열정적"], horizontal=True)
    with col2:
        duration = st.radio("길이", [30, 45, 60], horizontal=True, format_func=lambda x: f"{x}초")

    if st.button("대본 생성", type="primary", use_container_width=True):
        with st.spinner("Gemini로 대본 생성 중..."):
            try:
                script = generate_script(API_KEY, selected_news, tone, duration)
                st.session_state["generated_script"] = script
                st.session_state["selected_news"] = selected_news
            except Exception as e:
                st.error(f"대본 생성 실패: {e}")

    if "generated_script" in st.session_state:
        script = st.session_state["generated_script"]

        st.divider()
        st.subheader("생성된 대본")

        st.markdown("**훅 (첫 5초)**")
        st.info(script.get("hook", ""))

        st.markdown("**본문**")
        st.write(script.get("body", ""))

        st.markdown("**마무리**")
        st.write(script.get("closing", ""))

        st.divider()

        st.markdown("**전체 대본 (편집 가능)**")
        edited_script = st.text_area(
            "전체 대본",
            value=script.get("full_script", ""),
            height=200,
            label_visibility="collapsed",
        )

        tags = script.get("suggested_hashtags", [])
        if tags:
            st.caption(" ".join(tags))

        # 버튼 행
        if HAS_VIDEO:
            col_save, col_video, col_regen = st.columns(3)
        else:
            col_save, col_regen = st.columns(2)
            col_video = None

        with col_save:
            if st.button("대본 저장", use_container_width=True):
                script["full_script"] = edited_script
                path = save_script(selected_date, selected_news.get("rank", 0), script)
                st.success("저장 완료!")

        if col_video is not None:
            with col_video:
                voice = st.selectbox("음성", ["male", "female"], format_func=lambda x: "남성" if x == "male" else "여성", label_visibility="collapsed")
                if st.button("영상 만들기", type="primary", use_container_width=True):
                    with st.spinner("영상 생성 중... (1~3분 소요)"):
                        try:
                            players = selected_news.get("players", [])
                            player_name = players[0] if players else None
                            stats = selected_news.get("stats", None)

                            video_path = generate_video(
                                script_text=edited_script,
                                output_dir=None,
                                pexels_api_key=os.environ.get("PEXELS_API_KEY", ""),
                                voice_type=voice,
                                player_name=player_name,
                                stats=stats if isinstance(stats, dict) else None,
                            )
                            st.session_state["video_path"] = video_path
                            st.success("영상 생성 완료!")
                        except Exception as e:
                            st.error(f"영상 생성 실패: {e}")

        with col_regen:
            if st.button("다시 생성", use_container_width=True):
                del st.session_state["generated_script"]
                st.rerun()

        # 영상 미리보기 + 업로드
        if "video_path" in st.session_state:
            video_file = Path(st.session_state["video_path"])
            if video_file.exists():
                st.divider()
                st.subheader("생성된 영상")
                st.video(str(video_file))

                col_dl, col_upload = st.columns(2)

                with col_dl:
                    with open(video_file, "rb") as f:
                        st.download_button(
                            "영상 다운로드 (.mp4)",
                            data=f,
                            file_name=f"mlb_shorts_{selected_date}.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )

                # YouTube 업로드 섹션
                if HAS_UPLOAD:
                    with col_upload:
                        privacy = st.selectbox(
                            "공개 설정",
                            ["private", "unlisted", "public"],
                            format_func=lambda x: {"private": "비공개", "unlisted": "일부 공개", "public": "전체 공개"}[x],
                            label_visibility="collapsed",
                        )
                        if st.button("YouTube 업로드", type="primary", use_container_width=True):
                            # 메타데이터 자동 생성
                            with st.spinner("메타데이터 생성 + YouTube 업로드 중..."):
                                try:
                                    news_for_meta = st.session_state.get("selected_news", {})
                                    meta = generate_metadata(
                                        API_KEY,
                                        edited_script,
                                        headline=news_for_meta.get("headline", ""),
                                    )
                                    st.session_state["upload_metadata"] = meta

                                    yt_meta = meta.get("youtube", {})
                                    result = upload_to_youtube(
                                        video_path=str(video_file),
                                        title=yt_meta.get("title", f"MLB 숏폼 - {selected_date}"),
                                        description=yt_meta.get("description", ""),
                                        tags=yt_meta.get("tags", []),
                                        privacy=privacy,
                                    )
                                    st.session_state["upload_result"] = result

                                    # 히스토리 저장
                                    save_history(
                                        date=selected_date,
                                        headline=news_for_meta.get("headline", ""),
                                        video_path=str(video_file),
                                        upload_result=result,
                                        metadata=meta,
                                        tone=tone,
                                        duration=duration,
                                    )

                                    st.success(f"업로드 완료! {result['url']}")
                                    st.balloons()
                                except FileNotFoundError as e:
                                    st.error(str(e))
                                    st.info(
                                        "YouTube 업로드를 위해 OAuth 설정이 필요합니다:\n\n"
                                        "1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성\n"
                                        "2. client_secret.json 파일을 phase-4_integration/ 에 저장\n"
                                        "3. 다시 업로드 버튼 클릭"
                                    )
                                except Exception as e:
                                    st.error(f"업로드 실패: {e}")

                    # 업로드 결과 표시
                    if "upload_result" in st.session_state:
                        result = st.session_state["upload_result"]
                        st.markdown(f"**YouTube URL:** [{result['url']}]({result['url']})")

                    # 메타데이터 미리보기
                    if "upload_metadata" in st.session_state:
                        meta = st.session_state["upload_metadata"]
                        with st.expander("생성된 메타데이터"):
                            yt = meta.get("youtube", {})
                            st.markdown(f"**YouTube 제목:** {yt.get('title', '')}")
                            st.markdown(f"**설명:** {yt.get('description', '')}")
                            st.markdown(f"**태그:** {', '.join(yt.get('tags', []))}")

                            ig = meta.get("instagram", {})
                            if ig:
                                st.markdown(f"**Instagram:** {ig.get('caption', '')}")

                            tw = meta.get("twitter", {})
                            if tw:
                                st.markdown(f"**Twitter:** {tw.get('tweet_text', '')}")


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


# ── 페이지 4: 히스토리 ──
elif page == "히스토리":
    st.header("영상 히스토리")

    history = get_history(limit=30)
    if not history:
        st.info("생성/업로드된 영상이 없습니다.")
        st.stop()

    for entry in history:
        upload = entry.get("upload")
        upload_badge = ""
        if upload and upload.get("url"):
            upload_badge = f' | <a href="{upload["url"]}" target="_blank">YouTube</a>'

        st.markdown(f"""
        <div class="history-card">
            <strong>{entry.get('date', '')}</strong> - {entry.get('headline', '제목 없음')}
            <span style="color:#888; margin-left:8px;">{entry.get('tone', '')} {entry.get('duration', '')}초</span>
            {upload_badge}
            <p style="font-size:12px; color:#888; margin-top:4px;">
                {entry.get('created_at', '')[:19]}
            </p>
        </div>
        """, unsafe_allow_html=True)

        video_path = entry.get("video_path", "")
        if video_path and Path(video_path).exists():
            col1, col2 = st.columns([3, 1])
            with col2:
                with open(video_path, "rb") as f:
                    st.download_button(
                        "다운로드",
                        data=f,
                        file_name=Path(video_path).name,
                        mime="video/mp4",
                        key=f"dl_{entry.get('_filename', '')}",
                    )

from datetime import datetime, timedelta

def format_email(news_data: dict) -> tuple[str, str]:
    """
    뉴스 데이터를 HTML 이메일 본문으로 변환한다.
    반환값: (제목, HTML본문)
    """
    retrieved_at = news_data.get("retrieved_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 데이터 기준 시간 (Data Reference Time)
    # JSON에 있으면 쓰고, 없으면 계산 (yesterday 7am ~ today 7am)
    ref_time = news_data.get("data_reference_time")
    if not ref_time:
        now = datetime.now()
        today_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
        if now >= today_7am:
            end_time = today_7am
            start_time = end_time - timedelta(days=1)
        else:
            end_time = today_7am
            start_time = end_time - timedelta(days=1)
        ref_time = f"{start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')}"

    # 제목
    subject = f"[MLB Daily] {today_str} 오늘의 핵심 뉴스"

    # HTML 스타일
    style = """
    <style>
        body { font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        h1 { color: #002D62; border-bottom: 2px solid #D31145; padding-bottom: 10px; margin-bottom: 5px; }
        .ref-time { color: #D31145; font-weight: bold; font-size: 13px; margin-bottom: 20px; background-color: #fff0f5; padding: 8px; border-radius: 4px; text-align: center; }
        h2 { color: #D31145; margin-top: 30px; border-left: 5px solid #002D62; padding-left: 10px; }
        .news-item { margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
        .news-title { font-size: 16px; font-weight: bold; color: #1a1a1a; margin-bottom: 5px; }
        .news-summary { font-size: 14px; color: #555; margin-bottom: 5px; }
        .news-meta { font-size: 12px; color: #888; }
        .news-meta a { color: #002D62; text-decoration: none; }
        .no-news { font-style: italic; color: #888; text-align: center; padding: 20px; background: #fafafa; border-radius: 8px; }
    </style>
    """

    # 본문 구성
    body_content = f"<h1>MLB Daily Report ({today_str})</h1>"
    body_content += f"<div class='ref-time'>데이터 기준 시간: {ref_time}</div>"

    # 1. 핵심 뉴스
    body_content += "<h2>🔥 핵심 뉴스 (Main News)</h2>"
    main_news = news_data.get("main_news", [])
    if main_news:
        for idx, item in enumerate(main_news, 1):
            source_link = ""
            if item.get("source_url"):
                source_link = f" | <a href='{item['source_url']}'>원문보기</a>"
            
            body_content += f"""
            <div class="news-item">
                <div class="news-title">{idx}. {item.get('headline')}</div>
                <div class="news-summary">{item.get('summary')}</div>
                <div class="news-meta">
                    {item.get('source', 'Unknown')} | {item.get('published_at', '')} {source_link}
                </div>
            </div>
            """
    else:
        body_content += "<p class='no-news'>해당 범위 내 수집된 정보 없음</p>"

    # 2. 선수 이동
    transactions = news_data.get("transactions", [])
    if transactions:
        body_content += "<h2>⚾ 선수 이동 & 루머 (Transactions)</h2>"
        for item in transactions:
            type_badge = f"[{item.get('type', 'news').upper()}]"
            body_content += f"""
            <div class="news-item">
                <div class="news-title">{type_badge} {item.get('headline')}</div>
                <div class="news-summary">{item.get('summary')}</div>
                <div class="news-meta">{item.get('published_at', '')}</div>
            </div>
            """
    # 3. 유망주
    prospects = news_data.get("prospects", [])
    if prospects:
        body_content += "<h2>🌟 유망주 소식 (Prospects)</h2>"
        for item in prospects:
            body_content += f"""
            <div class="news-item">
                <div class="news-title">[{item.get('team', 'MLB')}] {item.get('player_name')}</div>
                <div class="news-summary">{item.get('summary')}</div>
                <div class="news-meta">{item.get('published_at', '')}</div>
            </div>
            """

    # 최종 HTML 조립
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>{style}</head>
    <body>
        {body_content}
        <div style="margin-top: 40px; font-size: 11px; color: #aaa; text-align: center;">
            MLB Daily AI Creator by Gemini
        </div>
    </body>
    </html>
    """

    return subject, html_body

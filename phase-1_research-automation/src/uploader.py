"""
Supabase에 MLB Daily 뉴스 데이터 업로드
- 테이블: mlb_daily_news
- 컬럼: date, main_news, transactions, prospects
- Unique Key: date
"""

import json
from datetime import datetime

from supabase import create_client


def upload_to_supabase(news_data: dict, supabase_url: str, supabase_key: str) -> None:
    """뉴스 JSON을 Supabase mlb_daily_news 테이블에 upsert한다."""
    client = create_client(supabase_url, supabase_key)

    today = datetime.now().strftime("%Y-%m-%d")
    
    # 데이터 준비
    row = {
        "season": datetime.now().year,
        "date": today,
        "news": json.loads(json.dumps(news_data.get("main_news", []), ensure_ascii=False)),
        "transactions": json.loads(json.dumps(news_data.get("transactions", []), ensure_ascii=False)),
        "prospects": json.loads(json.dumps(news_data.get("prospects", []), ensure_ascii=False)),
        "asian_players": [],
    }

    try:
        result = (
            client.table("mlb_news")
            .upsert(row, on_conflict="season,date")
            .execute()
        )
        print(f"  → Supabase 업로드 완료 (table=mlb_news, date={today})")
    except Exception as e:
        print(f"  [ERROR] Supabase 업로드 중 오류: {e}")
        raise e

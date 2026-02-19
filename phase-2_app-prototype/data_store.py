"""
뉴스/대본 데이터 저장 및 조회
- Supabase 'mlb_news' 테이블에서 뉴스 데이터 조회
- 생성된 대본 로컬에 저장/조회
"""
import json
import os
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Supabase 클라이언트 초기화
# 환경 변수 설정이 필수로 변경됨
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
SCRIPTS_DIR.mkdir(exist_ok=True)


def get_available_dates(limit: int = 14) -> list[str]:
    """Supabase에 뉴스 데이터가 있는 날짜 목록 반환 (최신순)."""
    try:
        response = supabase.table("mlb_news").select("date").order("date", desc=True).limit(limit).execute()
        if response.data:
            return [item['date'] for item in response.data]
        return []
    except Exception as e:
        print(f"Error fetching dates from Supabase: {e}")
        return []


def get_news(date: str) -> dict | None:
    """특정 날짜의 뉴스 데이터를 Supabase에서 반환."""
    try:
        response = supabase.table("mlb_news").select("*").eq("date", date).single().execute()
        if response.data:
            # news(JSONB) 컬럼 외 다른 컬럼도 포함하여 반환
            return response.data
        return None
    except Exception as e:
        print(f"Error fetching news for date {date} from Supabase: {e}")
        return None


def save_script(date: str, news_rank: int, script_data: dict) -> str:
    """생성된 대본 저장. 파일 경로 반환."""
    ts = datetime.now().strftime("%H%M%S")
    filename = f"{date}_news{news_rank}_{ts}.json"
    path = SCRIPTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    return str(path)


def get_scripts(date: str | None = None) -> list[dict]:
    """저장된 대본 목록 반환. date 지정 시 해당 날짜만."""
    scripts = []
    for f in sorted(SCRIPTS_DIR.glob("*.json"), reverse=True):
        if date and not f.stem.startswith(date):
            continue
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            data["_filename"] = f.name
            scripts.append(data)
    return scripts

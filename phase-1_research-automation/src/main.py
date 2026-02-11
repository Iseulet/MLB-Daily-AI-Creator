"""
MLB Daily AI Creator — Phase 1 파이프라인
리서치 → 포맷 → 이메일 전송
"""

import os
import sys
import io
import json
from datetime import datetime
from pathlib import Path

# Windows cp949 인코딩 문제 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from dotenv import load_dotenv

# .env 로드 (로컬 실행용, GitHub Actions에서는 secrets 사용)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from researcher import research_mlb_news
from formatter import format_email
from notifier import send_email


def main():
    print(f"[START] MLB Daily Research - {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # 환경변수 확인
    api_key = os.environ.get("GEMINI_API_KEY")
    gmail_addr = os.environ.get("GMAIL_ADDRESS")
    gmail_pw = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL", gmail_addr)

    if not api_key:
        print("[ERROR] GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    if not gmail_addr or not gmail_pw:
        print("[ERROR] GMAIL_ADDRESS / GMAIL_APP_PASSWORD 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    # 1. 리서치
    print("[1/3] Gemini API로 MLB 뉴스 수집 중...")
    news_data = research_mlb_news(api_key)
    print(f"  → 뉴스 {len(news_data.get('top_news', []))}건 수집 완료")

    # 디버그: JSON 저장
    out_dir = Path(__file__).resolve().parent.parent / "outputs"
    out_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    with open(out_dir / f"{today}.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print(f"  → JSON 저장: outputs/{today}.json")

    # 2. 포맷
    print("[2/3] HTML 이메일 포맷 생성 중...")
    subject, html_body = format_email(news_data)
    print(f"  → 제목: {subject}")

    # 3. 전송
    print(f"[3/3] 이메일 전송 중 → {recipient}")
    send_email(gmail_addr, gmail_pw, recipient, subject, html_body)

    print(f"[DONE] 파이프라인 완료")


if __name__ == "__main__":
    main()

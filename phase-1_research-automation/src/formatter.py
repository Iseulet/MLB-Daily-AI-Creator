"""
리서치 JSON → HTML 이메일 변환
Jinja2 템플릿 사용
"""

import os
from jinja2 import Environment, FileSystemLoader


_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def format_email(news_data: dict) -> tuple[str, str]:
    """뉴스 데이터를 (제목, HTML 본문) 튜플로 변환한다."""
    date = news_data.get("date", "날짜 없음")
    subject = f"[MLB Daily] {date} 오늘의 핵심 뉴스"

    env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR))
    template = env.get_template("email.html")
    html_body = template.render(data=news_data)

    return subject, html_body

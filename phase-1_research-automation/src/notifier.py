"""
Gmail SMTP를 통한 HTML 이메일 전송
- smtplib + Gmail 앱 비밀번호 사용
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


def send_email(
    sender: str,
    password: str,
    recipient: str,
    subject: str,
    html_body: str,
) -> None:
    """Gmail SMTP로 HTML 이메일을 전송한다."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"[OK] 이메일 전송 완료 → {recipient}")

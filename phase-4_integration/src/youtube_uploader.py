"""
YouTube Shorts 업로드 모듈
- YouTube Data API v3
- OAuth 2.0 인증
- 숏폼 영상 업로드 + 메타데이터 설정
"""

import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube"]
TOKEN_FILE = Path(__file__).resolve().parent.parent / "token.json"
CLIENT_SECRET_FILE = Path(__file__).resolve().parent.parent / "client_secret.json"


def get_authenticated_service():
    """OAuth 2.0 인증 후 YouTube API 서비스 객체 반환."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                raise FileNotFoundError(
                    f"client_secret.json이 필요합니다.\n"
                    f"Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고\n"
                    f"{CLIENT_SECRET_FILE} 경로에 저장하세요."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE), SCOPES
            )
            creds = flow.run_local_server(port=8090, open_browser=True)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list[str] | None = None,
    privacy: str = "private",
) -> dict:
    """YouTube에 영상 업로드.

    Args:
        video_path: 업로드할 영상 파일 경로
        title: 영상 제목
        description: 영상 설명
        tags: 태그 리스트
        privacy: "public", "private", "unlisted"

    Returns:
        {"video_id": str, "url": str}
    """
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "17",  # Sports
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024,  # 1MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  업로드 진행: {int(status.progress() * 100)}%")

    video_id = response["id"]
    return {
        "video_id": video_id,
        "url": f"https://youtube.com/shorts/{video_id}",
    }

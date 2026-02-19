"""
통합 파이프라인 환경변수 로더
- 프로젝트 루트 .env → 각 Phase .env 순서로 로드
- 먼저 찾은 값 우선 (override=False)
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# 프로젝트 루트 (MLB-Daily-AI-Creator/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 각 Phase .env 경로 (우선순위순)
ENV_FILES = [
    PROJECT_ROOT / ".env",
    # Phase 1 의존성 제거
    PROJECT_ROOT / "phase-2_app-prototype" / ".env",
    PROJECT_ROOT / "phase-3_video-pipeline" / ".env",
    PROJECT_ROOT / "phase-4_integration" / ".env",
]


def load_all_env() -> None:
    """모든 .env 파일 로드 (override=False: 먼저 찾은 값 우선)."""
    for env_path in ENV_FILES:
        if env_path.exists():
            load_dotenv(env_path, override=False)


def get_config() -> dict:
    """필요한 API 키와 설정값을 딕셔너리로 반환."""
    return {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
        "PEXELS_API_KEY": os.environ.get("PEXELS_API_KEY", ""),
        "SUPABASE_URL": os.environ.get("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_KEY": os.environ.get("SUPABASE_SERVICE_KEY", ""),
    }


def validate_config(config: dict, required_keys: list[str]) -> list[str]:
    """누락된 키 반환.

    Args:
        config: get_config() 결과
        required_keys: 필수 키 목록

    Returns:
        누락된 키 이름 리스트 (빈 리스트면 모두 충족)
    """
    return [key for key in required_keys if not config.get(key)]

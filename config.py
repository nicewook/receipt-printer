"""
보안 설정 및 구성 파일
Security configuration and settings
"""

import os
from typing import List
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로컬 MCP 서버이므로 API 키 인증 불필요

# 허용된 프린터 목록 (보안을 위한 화이트리스트)
ALLOWED_PRINTERS: List[str] = [
    "BIXOLON_SRP_330II",
    "BIXOLON_SRP_330III",
    "BIXOLON_SRP_350II",
    "BIXOLON_SRP_350III",
]

# 최대 출력 줄 수 제한
MAX_LINES = 100

# 최대 텍스트 길이 제한
MAX_TEXT_LENGTH = 4000

# 프린터 기본 설정
DEFAULT_PRINTER = "BIXOLON_SRP_330II"
DEFAULT_WIDTH = 40

# 보안 헤더
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}

# 개발 모드 설정
DEBUG_MODE = os.getenv("PRINTER_DEBUG", "false").lower() == "true"
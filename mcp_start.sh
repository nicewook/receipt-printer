#!/bin/bash

# MCP Receipt Printer 통합 시작 스크립트
# FastAPI 서버를 백그라운드에서 시작하고 MCP wrapper를 실행

PROJECT_DIR="/Users/hyunseokjeong/VibeCodingProject/receipt-printer"
PYTHON_PATH="$PROJECT_DIR/.venv/bin/python3"
SERVER_PID_FILE="/tmp/mcp_receipt_server.pid"

# 프로젝트 디렉터리로 이동
cd "$PROJECT_DIR"

# 기존 서버 프로세스 정리
cleanup() {
    if [ -f "$SERVER_PID_FILE" ]; then
        SERVER_PID=$(cat "$SERVER_PID_FILE")
        if kill -0 "$SERVER_PID" 2>/dev/null; then
            echo "🛑 FastAPI 서버 종료 중... (PID: $SERVER_PID)" >&2
            kill "$SERVER_PID"
            sleep 2
            if kill -0 "$SERVER_PID" 2>/dev/null; then
                kill -9 "$SERVER_PID"
            fi
        fi
        rm -f "$SERVER_PID_FILE"
    fi
}

# 종료 시 정리
trap cleanup EXIT INT TERM

# 기존 프로세스 정리
cleanup

# FastAPI 서버 백그라운드 실행
echo "🚀 FastAPI 서버 시작 중..." >&2
"$PYTHON_PATH" server.py &
SERVER_PID=$!
echo $SERVER_PID > "$SERVER_PID_FILE"

# 서버 시작 대기
sleep 3

# 서버 시작 확인
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "❌ FastAPI 서버 시작 실패" >&2
    exit 1
fi

# 서버 응답 확인
if ! curl -s http://127.0.0.1:8000/ >/dev/null; then
    echo "❌ FastAPI 서버가 응답하지 않습니다" >&2
    cleanup
    exit 1
fi

echo "✅ FastAPI 서버 시작 완료 (PID: $SERVER_PID)" >&2

# MCP wrapper 실행 (포어그라운드)
echo "🔗 MCP wrapper 시작 중..." >&2
exec "$PYTHON_PATH" mcp_wrapper.py
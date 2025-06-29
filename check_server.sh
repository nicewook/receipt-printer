#!/bin/bash

echo "🔍 MCP Receipt Printer 서버 상태 점검"
echo "=================================="

# 1. 포트 8000 확인
echo "1️⃣ 포트 8000 사용 중인지 확인..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ 포트 8000이 사용 중입니다 (서버 실행 중)"
    lsof -i :8000
else
    echo "❌ 포트 8000이 사용되지 않습니다 (서버 미실행)"
fi

echo ""

# 2. 서버 응답 테스트
echo "2️⃣ 서버 응답 테스트..."
if curl -s http://127.0.0.1:8000/ >/dev/null 2>&1; then
    echo "✅ 서버가 응답합니다"
    echo "서버 정보:"
    curl -s http://127.0.0.1:8000/ | python3 -m json.tool 2>/dev/null || echo "JSON 파싱 실패"
else
    echo "❌ 서버가 응답하지 않습니다"
fi

echo ""

# 3. 프린터 목록 테스트
echo "3️⃣ 프린터 목록 테스트..."
if curl -s http://127.0.0.1:8000/printers >/dev/null 2>&1; then
    echo "✅ 프린터 API가 응답합니다"
    echo "프린터 목록:"
    curl -s http://127.0.0.1:8000/printers | python3 -m json.tool 2>/dev/null || echo "JSON 파싱 실패"
else
    echo "❌ 프린터 API가 응답하지 않습니다"
fi

echo ""

# 4. MCP wrapper 테스트
echo "4️⃣ MCP wrapper 테스트..."
cd /Users/hyunseokjeong/VibeCodingProject/receipt-printer
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    if echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | timeout 3s python mcp_wrapper.py 2>/dev/null | grep -q "tools"; then
        echo "✅ MCP wrapper가 정상 작동합니다"
    else
        echo "❌ MCP wrapper 테스트 실패"
    fi
else
    echo "❌ 가상환경을 찾을 수 없습니다"
fi

echo ""
echo "=================================="
echo "🚀 서버 시작 명령:"
echo "cd /Users/hyunseokjeong/VibeCodingProject/receipt-printer"
echo "source .venv/bin/activate"  
echo "python server.py"
# MCP Wrapper 단순화 계획

MCP wrapper에서 FastAPI 서버 의존성을 제거하고 printer_utils.py를 직접 호출하는 구조로 리팩토링하는 계획서

## 현재 아키텍처 문제점

### 복잡한 3계층 구조

```
Claude Desktop → mcp_wrapper.py → HTTP API → server.py → printer_utils.py
```

**문제점**:
1. **불필요한 중간 계층**: FastAPI 서버가 단순히 HTTP → 함수 호출 변환만 수행
2. **네트워크 의존성**: HTTP 통신으로 인한 추가 복잡성과 오류 가능성
3. **리소스 낭비**: 별도 서버 프로세스(포트 8000) 실행 필요
4. **응답 지연**: HTTP 요청/응답 오버헤드
5. **복잡한 배포**: FastAPI 서버 + MCP wrapper 두 프로세스 관리
6. **에러 전파**: HTTP 에러 → MCP 에러 → Claude Desktop 에러 (3단계 변환)

### 현재 코드 의존성

**mcp_wrapper.py**:
- `aiohttp.ClientSession` - HTTP 클라이언트
- `make_api_request()` - HTTP 요청 메서드
- 환경변수 `PRINTER_API_URL` 의존

**server.py** (제거 대상):
- FastAPI, Pydantic 의존성
- HTTP 엔드포인트 정의
- 인증 및 검증 로직

## 새로운 단순화 아키텍처

### 직접 호출 구조

```
Claude Desktop → mcp_wrapper.py → printer_utils.py (직접 호출)
```

**장점**:
1. **단순성**: HTTP 서버 없이 함수 직접 호출
2. **안정성**: 네트워크 의존성 완전 제거
3. **성능**: HTTP 오버헤드 제거로 빠른 응답
4. **배포**: 단일 프로세스로 배포 간소화
5. **메모리**: FastAPI 서버 프로세스 불필요
6. **디버깅**: 단순한 호출 스택으로 문제 추적 용이

### 직접 호출 가능한 함수들

**printer_utils.py**에서 제공하는 핵심 함수들:

```python
# 실제 출력
print_to_cups(text, printer_name="BIXOLON_SRP_330II") → bool

# 프린터 목록
get_available_printers() → List[str]

# 상태 확인  
check_printer_status(printer_name) → str

# 미리보기용 텍스트 처리
prepare_print_content(text, min_lines=6) → List[str]

# ESC/POS 바이너리 생성
create_esc_pos_content(lines) → bytes
```

## 코드 변경 사항

### 1. mcp_wrapper.py 주요 변경

#### 제거할 컴포넌트
```python
# HTTP 관련 의존성 제거
import aiohttp
from typing import Any, Dict, List, Optional, Union

# 환경변수 제거
API_URL = os.getenv("PRINTER_API_URL", "http://127.0.0.1:8000")

# HTTP 클라이언트 제거
class MCPServer:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
    
    async def make_api_request(self, method, endpoint, data=None):
        # 전체 메서드 제거
```

#### 추가할 컴포넌트
```python
# printer_utils 직접 import
import printer_utils
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MCPServer:
    def __init__(self):
        # HTTP 세션 대신 ThreadPoolExecutor for 동기 함수 처리
        self.executor = ThreadPoolExecutor(max_workers=2)
```

### 2. 도구 핸들러 리팩토링

#### _handle_print_receipt 변경

**현재 (HTTP 호출)**:
```python
async def _handle_print_receipt(self, arguments):
    request_data = {"content": content, "preview": preview}
    result = await self.make_api_request("POST", f"/printers/{printer_name}/print", request_data)
```

**새로운 (직접 호출)**:
```python
async def _handle_print_receipt(self, arguments):
    printer_name = arguments.get("printer_name", "BIXOLON_SRP_330II")
    content = arguments.get("content", {})
    preview = arguments.get("preview", False)
    
    # 텍스트 추출
    if "text" in content:
        text = content["text"]
    elif "items" in content:
        text = self._format_receipt_items(content)
    else:
        text = content.get("header", "") + content.get("footer", "")
    
    if preview:
        # 미리보기 생성
        lines = await self._run_sync(printer_utils.prepare_print_content, text)
        preview_text = "\n".join(f"|{line:<40}|" for line in lines)
        return {
            "content": [{
                "type": "text",
                "text": f"📄 출력 미리보기:\n{'=' * 42}\n{preview_text}\n{'=' * 42}\n총 {len(lines)}줄"
            }]
        }
    else:
        # 실제 출력
        success = await self._run_sync(printer_utils.print_to_cups, text, printer_name)
        if success:
            return {
                "content": [{
                    "type": "text", 
                    "text": f"✅ 출력 완료: {printer_name}"
                }]
            }
        else:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❌ 출력 실패: {printer_name}"
                }]
            }

async def _run_sync(self, func, *args):
    """동기 함수를 비동기로 실행"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(self.executor, func, *args)
```

#### _handle_list_printers 변경

**현재**:
```python
async def _handle_list_printers(self, arguments):
    result = await self.make_api_request("GET", "/printers")
    printers = result.get("printers", [])
```

**새로운**:
```python
async def _handle_list_printers(self, arguments):
    printers = await self._run_sync(printer_utils.get_available_printers)
    
    if not printers:
        return {
            "content": [{
                "type": "text",
                "text": "❌ 사용 가능한 프린터가 없습니다."
            }]
        }
    
    printer_list = ["🖨️  사용 가능한 프린터:"]
    for printer in printers:
        status = await self._run_sync(printer_utils.check_printer_status, printer)
        printer_list.append(f"  ✅ {printer}")
        printer_list.append(f"     상태: {status}")
    
    return {
        "content": [{
            "type": "text",
            "text": "\n".join(printer_list)
        }]
    }
```

#### _handle_get_printer_status 변경

**현재**:
```python
async def _handle_get_printer_status(self, arguments):
    result = await self.make_api_request("GET", f"/printers/{printer_name}/status")
```

**새로운**:
```python
async def _handle_get_printer_status(self, arguments):
    printer_name = arguments.get("printer_name", "BIXOLON_SRP_330II")
    status = await self._run_sync(printer_utils.check_printer_status, printer_name)
    
    return {
        "content": [{
            "type": "text",
            "text": f"📊 프린터 상태: {printer_name}\n{status}"
        }]
    }
```

### 3. 영수증 포맷팅 헬퍼 함수

```python
def _format_receipt_items(self, content):
    """영수증 아이템을 텍스트로 포맷팅"""
    lines = []
    
    # 헤더
    if "header" in content:
        lines.append(content["header"])
        lines.append("")
    
    # 아이템들
    if "items" in content:
        for item in content["items"]:
            name = item.get("name", "")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)
            total = item.get("total", price * quantity)
            
            if quantity and price:
                lines.append(f"{name} x{quantity}")
                lines.append(f"  {price:,}원 x {quantity} = {total:,}원")
            else:
                lines.append(name)
        lines.append("")
    
    # 푸터
    if "footer" in content:
        lines.append(content["footer"])
    
    return "\n".join(lines)
```

## 제거될 컴포넌트

### 1. server.py (전체 파일)
- FastAPI 애플리케이션
- Pydantic 스키마
- HTTP 엔드포인트
- 인증 미들웨어

### 2. 관련 의존성
```
# requirements.txt에서 제거
fastapi
uvicorn
pydantic
```

### 3. 설정 파일들
- `config.py` - API 설정 관련
- `schemas.py` - Pydantic 모델들

## 유지될 컴포넌트

### 1. 핵심 로직
- `printer_utils.py` - 프린터 제어 로직 (변경 없음)
- `main.py` - 레거시 CLI 인터페이스 (변경 없음)

### 2. MCP 프로토콜
- JSON-RPC 2.0 메시지 처리
- tools 정의 및 스키마
- stdin/stdout 통신

### 3. 설정
- `claude_desktop_config.json` - MCP 서버 설정 (변경 없음)
- `CLAUDE.md` - 프로젝트 문서 (명령어 업데이트 필요)

## 마이그레이션 단계

### Phase 1: 코드 변경
1. `mcp_wrapper.py`에서 HTTP 관련 코드 제거
2. `printer_utils` 직접 import 및 호출 구현
3. 동기/비동기 변환 로직 추가
4. 에러 처리 로직 업데이트

### Phase 2: 테스트
1. 기존 MCP 도구들 동작 확인
2. 영수증 출력 기능 테스트
3. 프린터 목록/상태 확인 테스트
4. 에러 시나리오 테스트

### Phase 3: 문서 업데이트
1. `CLAUDE.md` 명령어 섹션 업데이트
2. `README.md` 설치 가이드 단순화
3. 아키텍처 다이어그램 업데이트

### Phase 4: 정리
1. `server.py`, `config.py`, `schemas.py` 파일 제거
2. `requirements.txt` 의존성 정리
3. 사용하지 않는 테스트 파일 정리

## 새로운 배포 방식

### 이전 (2단계)
```bash
# 1. FastAPI 서버 시작
python3 server.py

# 2. Claude Desktop 설정에서 mcp_wrapper 실행
# (claude_desktop_config.json에서 자동 실행)
```

### 이후 (1단계)
```bash
# Claude Desktop 설정에서 mcp_wrapper만 실행
# FastAPI 서버 불필요
```

### claude_desktop_config.json 변경 없음
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/path/to/python3",
      "args": ["/path/to/mcp_wrapper.py"]
      // env 섹션의 PRINTER_API_URL 제거 가능
    }
  }
}
```

## 성능 및 리소스 개선

### 메모리 사용량
- **이전**: Python FastAPI 프로세스 + Python MCP wrapper 프로세스
- **이후**: Python MCP wrapper 프로세스만

### 응답 시간
- **이전**: JSON-RPC → HTTP → 함수 호출 (네트워크 오버헤드)
- **이후**: JSON-RPC → 함수 호출 (직접 호출)

### 에러 처리
- **이전**: CUPS 에러 → HTTP 에러 → MCP 에러 → Claude Desktop
- **이후**: CUPS 에러 → MCP 에러 → Claude Desktop

## 테스트 계획

### 1. 단위 테스트
```python
# tests/test_mcp_direct.py
async def test_print_receipt_direct():
    server = MCPServer()
    result = await server._handle_print_receipt({
        "content": {"text": "테스트 출력"},
        "preview": True
    })
    assert "📄 출력 미리보기" in result["content"][0]["text"]
```

### 2. 통합 테스트
```python
# tests/test_mcp_integration.py  
async def test_tools_list():
    server = MCPServer()
    request = {"method": "tools/list", "id": 1}
    response = await server.handle_request(request)
    assert len(response["result"]["tools"]) == 4
```

### 3. MCP 프로토콜 테스트
```bash
# 직접 stdin/stdout 테스트
echo '{"method":"tools/list","id":1}' | python3 mcp_wrapper.py
```

## 예상 문제점 및 해결책

### 1. 동기/비동기 혼합
**문제**: `printer_utils` 함수들이 동기 함수
**해결**: `ThreadPoolExecutor`로 비동기 변환

### 2. 에러 메시지 형식
**문제**: HTTP 에러 형식에서 MCP 에러 형식으로 변경
**해결**: 일관된 에러 응답 포맷 정의

### 3. 복잡한 영수증 구조
**문제**: FastAPI의 Pydantic 검증 로직 제거
**해결**: MCP wrapper 내에서 간단한 검증 로직 구현

## 예상 효과

### 개발자 경험
- **배포 단순화**: 단일 프로세스 실행
- **디버깅 개선**: 단순한 호출 스택
- **의존성 감소**: FastAPI, Pydantic 제거

### 사용자 경험  
- **빠른 응답**: HTTP 오버헤드 제거
- **안정성 향상**: 네트워크 에러 요소 제거
- **설정 단순화**: 포트 관리 불필요

### 유지보수
- **코드 복잡도 감소**: 단일 파일에서 모든 로직 처리
- **테스트 단순화**: HTTP 모킹 불필요
- **문서 간소화**: 설치 가이드 단순화

이 계획을 통해 MCP wrapper를 현재보다 훨씬 단순하고 효율적인 구조로 리팩토링할 수 있습니다.
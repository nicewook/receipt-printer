# MCP stdio 통신 방식

MCP (Model Context Protocol)에서 사용하는 stdin/stdout 기반 통신 메커니즘에 대한 상세 설명

## 개요

MCP는 **JSON-RPC over stdio** 방식을 사용하여 클라이언트와 서버 간 통신을 수행합니다. 이는 HTTP나 소켓 통신 대신 **운영체제의 프로세스 파이프**를 활용하는 방식입니다.

## 프로세스 관계와 파이프 연결

### 부모-자식 프로세스 관계

```
Claude Desktop (부모 프로세스)
    ↓ subprocess.Popen()
mcp_wrapper.py (자식 프로세스)
```

### 파이프 연결

```
Claude Desktop          mcp_wrapper.py
     ↓ stdin pipe           ↑ stdout pipe
[JSON 요청 전송]  ←→  [JSON 응답 수신]
[JSON 응답 수신]  ←→  [JSON 요청 처리]
     ↑ stdout pipe          ↓ stdin pipe
```

## 실제 통신 흐름

### 1. 프로세스 생성 및 초기화

```bash
# Claude Desktop이 실행하는 명령
python3 /path/to/mcp_wrapper.py
```

Claude Desktop의 설정(`claude_desktop_config.json`)에서:
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/path/to/python3",
      "args": ["/path/to/mcp_wrapper.py"]
    }
  }
}
```

### 2. 초기 핸드셰이크

**Claude Desktop → mcp_wrapper (stdin)**:
```json
{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {...}}
```

**mcp_wrapper → Claude Desktop (stdout)**:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", ...}}
```

### 3. 도구 목록 조회

**Claude Desktop → mcp_wrapper**:
```json
{"jsonrpc": "2.0", "method": "tools/list", "id": 2}
```

**mcp_wrapper → Claude Desktop**:
```json
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [...]}}
```

### 4. 도구 호출

**Claude Desktop → mcp_wrapper**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 3,
  "params": {
    "name": "print_receipt",
    "arguments": {"content": {"text": "안녕하세요"}}
  }
}
```

## 코드 구현

### Claude Desktop 측 (의사코드)

```python
import subprocess
import json

# MCP 서버 프로세스 생성
process = subprocess.Popen(
    ["python3", "mcp_wrapper.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# JSON 요청 전송
def send_request(request):
    json_line = json.dumps(request) + "\n"
    process.stdin.write(json_line)
    process.stdin.flush()

# JSON 응답 수신
def receive_response():
    response_line = process.stdout.readline()
    return json.loads(response_line.strip())
```

### mcp_wrapper 측 (실제 구현)

```python
# mcp_wrapper.py:423-436
async def run(self):
    while True:
        # Claude Desktop이 보낸 JSON을 stdin에서 읽기
        line = await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline
        )
        if not line:
            break
        
        line = line.strip()
        if not line:
            continue
        
        try:
            # JSON 파싱 및 요청 처리
            request = json.loads(line)
            response = await self.handle_request(request)
            
            # Claude Desktop으로 응답 전송
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        except Exception as e:
            # 에러 응답 전송
            error_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
```

## 운영체제 레벨 동작

### 파이프 생성

```
OS Kernel
├── Claude Desktop Process (PID: 1234)
│   ├── stdin: keyboard input
│   ├── stdout: terminal output  
│   └── subprocess pipes:
│       ├── pipe_to_child_stdin
│       └── pipe_from_child_stdout
└── mcp_wrapper Process (PID: 5678)
    ├── stdin: pipe_from_parent
    ├── stdout: pipe_to_parent
    └── stderr: error logging
```

### 파일 디스크립터

- **mcp_wrapper 관점**: 
  - `sys.stdin` (fd 0) = Claude Desktop의 출력 파이프
  - `sys.stdout` (fd 1) = Claude Desktop의 입력 파이프
- **Claude Desktop 관점**:
  - `process.stdin` = mcp_wrapper의 표준 입력
  - `process.stdout` = mcp_wrapper의 표준 출력

## MCP가 stdio를 선택한 이유

### 1. 단순성
- HTTP 서버나 소켓 연결보다 훨씬 간단
- 포트 관리나 네트워크 설정 불필요

### 2. 보안성
- 네트워크 포트를 열지 않아 외부 접근 차단
- 부모-자식 프로세스 관계로 권한 상속

### 3. 프로세스 생명주기 관리
- 부모 프로세스 종료 시 자식도 자동 종료
- 좀비 프로세스 방지

### 4. 표준화
- JSON-RPC over stdio는 이미 검증된 패턴
- 언어나 플랫폼에 관계없이 구현 가능

### 5. 동기화
- 한 줄당 하나의 메시지로 명확한 경계
- 버퍼링 제어로 실시간 통신

## 디버깅과 모니터링

### stderr을 통한 로깅

```python
# mcp_wrapper.py:147-149
def log_debug(self, message: str):
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}", file=sys.stderr)
```

- **stdin/stdout**: JSON-RPC 통신 전용
- **stderr**: 디버그 로그 및 에러 메시지 전용

### 통신 흐름 추적

```bash
# mcp_wrapper 실행 시 stderr 로그 확인
python3 mcp_wrapper.py 2> debug.log

# 또는 실시간 모니터링
python3 mcp_wrapper.py 2>&1 | tee debug.log
```

## 관련 파일

- `mcp_wrapper.py`: MCP stdio 서버 구현
- `claude_desktop_config.json`: 클라이언트 설정
- `server.py`: FastAPI 백엔드 (HTTP API)
- `docs/mcp-wrapper-analysis.md`: MCP 구현 상세 분석

## 참고자료

- [MCP 공식 사양](https://spec.modelcontextprotocol.io/)
- [JSON-RPC 2.0 스펙](https://www.jsonrpc.org/specification)
- 프로젝트 README.md의 MCP 설정 가이드
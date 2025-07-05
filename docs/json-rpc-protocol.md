# JSON-RPC 프로토콜 상세 가이드

**Created:** 2025-07-02T02:30:00Z  
**Category:** technical

JSON-RPC(JSON Remote Procedure Call)는 원격 프로시저 호출을 위한 stateless, 경량 프로토콜입니다. 이 문서는 JSON-RPC 2.0 사양을 기반으로 한 상세한 기술 가이드입니다.

## 목차

1. [JSON-RPC란 무엇인가?](#json-rpc란-무엇인가)
2. [핵심 개념](#핵심-개념)
3. [메시지 구조](#메시지-구조)
4. [통신 패턴](#통신-패턴)
5. [에러 처리](#에러-처리)
6. [전송 계층](#전송-계층)
7. [실제 구현 예제](#실제-구현-예제)
8. [보안 고려사항](#보안-고려사항)
9. [성능 최적화](#성능-최적화)
10. [디버깅 가이드](#디버깅-가이드)

## JSON-RPC란 무엇인가?

### 정의와 목적

JSON-RPC는 **경량하고 stateless한 원격 프로시저 호출 프로토콜**입니다. JSON을 데이터 교환 형식으로 사용하여 클라이언트가 서버의 메서드를 원격으로 호출할 수 있게 합니다.

### 주요 특징

- **언어 독립적**: 모든 프로그래밍 언어에서 구현 가능
- **전송 계층 독립적**: HTTP, WebSocket, TCP, stdin/stdout 등 다양한 전송 방식 지원
- **경량성**: 최소한의 오버헤드로 효율적인 통신
- **Stateless**: 서버가 클라이언트 상태를 유지하지 않음
- **양방향 통신**: 서버에서 클라이언트로도 호출 가능

### 역사와 버전

```
JSON-RPC 1.0 (2005) → JSON-RPC 1.1 (미완성) → JSON-RPC 2.0 (2010, 현재 표준)
```

## 핵심 개념

### 1. Remote Procedure Call (RPC)

RPC는 **네트워크를 통해 다른 프로세스의 함수를 호출하는 메커니즘**입니다.

```
클라이언트 프로세스                서버 프로세스
    ↓                              ↑
[함수 호출] ──────────────→ [함수 실행]
[결과 수신] ←────────────── [결과 반환]
    ↓                              ↑
```

### 2. JSON 기반 메시징

모든 메시지는 **유효한 JSON 객체**여야 합니다:

```json
{
  "jsonrpc": "2.0",
  "method": "subtract",
  "params": [42, 23],
  "id": 1
}
```

### 3. Request-Response 패턴

```
요청 (Request) → 처리 (Processing) → 응답 (Response)
```

단, **Notification**의 경우 응답이 없습니다.

## 메시지 구조

### 요청 메시지 (Request)

모든 요청 메시지는 다음 구조를 가집니다:

```json
{
  "jsonrpc": "2.0",          // 프로토콜 버전 (필수)
  "method": "method_name",   // 호출할 메서드명 (필수)
  "params": [...],           // 매개변수 (선택사항)
  "id": unique_id            // 요청 식별자 (선택사항)
}
```

#### 필드 상세 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `jsonrpc` | String | ✓ | 반드시 "2.0" |
| `method` | String | ✓ | 호출할 메서드명 |
| `params` | Array/Object | ✗ | 매개변수 |
| `id` | String/Number/null | ✗ | 요청 식별자 |

#### 매개변수 형식

**배열 형식 (위치 기반)**:
```json
{
  "jsonrpc": "2.0",
  "method": "subtract",
  "params": [42, 23],
  "id": 1
}
```

**객체 형식 (이름 기반)**:
```json
{
  "jsonrpc": "2.0",
  "method": "subtract",
  "params": {"subtrahend": 23, "minuend": 42},
  "id": 2
}
```

### 응답 메시지 (Response)

성공적인 응답:
```json
{
  "jsonrpc": "2.0",
  "result": 19,
  "id": 1
}
```

에러 응답:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found"
  },
  "id": 1
}
```

#### 응답 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `jsonrpc` | String | 반드시 "2.0" |
| `result` | Any | 성공 시 결과값 |
| `error` | Object | 에러 시 에러 정보 |
| `id` | Same as request | 요청의 id와 동일 |

### 알림 메시지 (Notification)

`id` 필드가 없는 요청은 알림으로 간주되며, **응답을 기대하지 않습니다**:

```json
{
  "jsonrpc": "2.0",
  "method": "update",
  "params": [1, 2, 3, 4, 5]
}
```

## 통신 패턴

### 1. 단일 요청-응답

```
클라이언트                    서버
    |                         |
    |-- 요청 (id: 1) -------->|
    |                         | (처리)
    |<------ 응답 (id: 1) ----|
    |                         |
```

### 2. 배치 요청 (Batch Request)

여러 요청을 배열로 묶어서 전송:

```json
[
  {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
  {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
  {"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"}
]
```

배치 응답:
```json
[
  {"jsonrpc": "2.0", "result": 7, "id": "1"},
  {"jsonrpc": "2.0", "result": 19, "id": "2"}
]
```

### 3. 비동기 요청

```
클라이언트                    서버
    |                         |
    |-- 요청 A (id: 1) ------>|
    |-- 요청 B (id: 2) ------>|
    |                         | (A 처리 완료)
    |<------ 응답 A (id: 1) --|
    |                         | (B 처리 완료)
    |<------ 응답 B (id: 2) --|
    |                         |
```

## 에러 처리

### 사전 정의된 에러 코드

| 코드 | 메시지 | 의미 |
|------|--------|------|
| -32700 | Parse error | 잘못된 JSON |
| -32600 | Invalid Request | 잘못된 요청 객체 |
| -32601 | Method not found | 메서드를 찾을 수 없음 |
| -32602 | Invalid params | 잘못된 매개변수 |
| -32603 | Internal error | 내부 JSON-RPC 에러 |
| -32000 ~ -32099 | Server error | 서버 구현별 에러 |

### 에러 객체 구조

```json
{
  "code": -32601,
  "message": "Method not found",
  "data": {                    // 선택사항: 추가 정보
    "method": "unknown_method",
    "available_methods": ["add", "subtract", "multiply"]
  }
}
```

### 에러 처리 베스트 프랙티스

1. **명확한 에러 메시지**: 사용자가 이해할 수 있는 설명
2. **적절한 에러 코드**: 표준 코드 우선, 필요시 사용자 정의
3. **추가 컨텍스트**: `data` 필드로 디버깅 정보 제공
4. **일관성**: 동일한 에러에 대해 일관된 응답

## 전송 계층

JSON-RPC는 다양한 전송 계층에서 동작할 수 있습니다.

### 1. HTTP

**POST 요청**:
```http
POST /jsonrpc HTTP/1.1
Content-Type: application/json
Content-Length: 85

{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
```

**HTTP 응답**:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 43

{"jsonrpc": "2.0", "result": 19, "id": 1}
```

### 2. WebSocket

```javascript
// 클라이언트
ws.send('{"jsonrpc": "2.0", "method": "ping", "id": 1}');

// 서버 응답
ws.send('{"jsonrpc": "2.0", "result": "pong", "id": 1}');
```

### 3. TCP Socket

```
줄 구분자(\n)로 메시지 분리:
{"jsonrpc": "2.0", "method": "echo", "params": ["Hello"], "id": 1}\n
{"jsonrpc": "2.0", "result": "Hello", "id": 1}\n
```

### 4. stdin/stdout (MCP에서 사용)

```bash
# 클라이언트 → 서버 (stdin)
echo '{"jsonrpc": "2.0", "method": "list_tools", "id": 1}' | python server.py

# 서버 → 클라이언트 (stdout)
{"jsonrpc": "2.0", "result": {"tools": [...]}, "id": 1}
```

## 실제 구현 예제

### Python 서버 구현

```python
import json
import sys
from typing import Dict, Any, Optional

class JSONRPCServer:
    def __init__(self):
        self.methods = {}
    
    def register_method(self, name: str, func):
        """메서드 등록"""
        self.methods[name] = func
    
    def handle_request(self, request_str: str) -> str:
        """요청 처리"""
        try:
            request = json.loads(request_str)
        except json.JSONDecodeError:
            return self._error_response(None, -32700, "Parse error")
        
        # 배치 요청 처리
        if isinstance(request, list):
            responses = []
            for req in request:
                response = self._process_single_request(req)
                if response:  # Notification이 아닌 경우만
                    responses.append(response)
            return json.dumps(responses) if responses else ""
        
        # 단일 요청 처리
        response = self._process_single_request(request)
        return json.dumps(response) if response else ""
    
    def _process_single_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """단일 요청 처리"""
        # 기본 검증
        if not isinstance(request, dict):
            return self._error_response(None, -32600, "Invalid Request")
        
        if request.get("jsonrpc") != "2.0":
            return self._error_response(request.get("id"), -32600, "Invalid Request")
        
        method_name = request.get("method")
        if not method_name or not isinstance(method_name, str):
            return self._error_response(request.get("id"), -32600, "Invalid Request")
        
        # Notification 확인 (id가 없으면 응답하지 않음)
        is_notification = "id" not in request
        request_id = request.get("id")
        
        # 메서드 실행
        if method_name not in self.methods:
            if not is_notification:
                return self._error_response(request_id, -32601, "Method not found")
            return None
        
        try:
            params = request.get("params", [])
            if isinstance(params, list):
                result = self.methods[method_name](*params)
            elif isinstance(params, dict):
                result = self.methods[method_name](**params)
            else:
                if not is_notification:
                    return self._error_response(request_id, -32602, "Invalid params")
                return None
            
            if not is_notification:
                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }
            return None
            
        except TypeError as e:
            if not is_notification:
                return self._error_response(request_id, -32602, "Invalid params")
            return None
        except Exception as e:
            if not is_notification:
                return self._error_response(request_id, -32603, f"Internal error: {str(e)}")
            return None
    
    def _error_response(self, request_id, code: int, message: str, data=None) -> Dict[str, Any]:
        """에러 응답 생성"""
        error = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        
        return {
            "jsonrpc": "2.0",
            "error": error,
            "id": request_id
        }

# 사용 예제
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

# 서버 설정
server = JSONRPCServer()
server.register_method("add", add)
server.register_method("subtract", subtract)
server.register_method("multiply", multiply)

# stdin/stdout 통신
if __name__ == "__main__":
    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line:
                break
            
            response = server.handle_request(line)
            if response:
                print(response)
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Server error: {str(e)}"},
                "id": None
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
```

### Python 클라이언트 구현

```python
import json
import subprocess
import uuid
from typing import Any, Optional, Union

class JSONRPCClient:
    def __init__(self, server_command: list):
        self.process = subprocess.Popen(
            server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # 무버퍼링
        )
    
    def call(self, method: str, params: Union[list, dict] = None, notification: bool = False) -> Any:
        """메서드 호출"""
        request = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params is not None:
            request["params"] = params
        
        if not notification:
            request["id"] = str(uuid.uuid4())
        
        # 요청 전송
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        if notification:
            return None
        
        # 응답 수신
        response_str = self.process.stdout.readline().strip()
        if not response_str:
            raise Exception("No response received")
        
        response = json.loads(response_str)
        
        if "error" in response:
            raise Exception(f"JSON-RPC Error {response['error']['code']}: {response['error']['message']}")
        
        return response.get("result")
    
    def batch_call(self, calls: list) -> list:
        """배치 호출"""
        requests = []
        for call_info in calls:
            request = {
                "jsonrpc": "2.0",
                "method": call_info["method"],
                "id": str(uuid.uuid4())
            }
            if "params" in call_info:
                request["params"] = call_info["params"]
            requests.append(request)
        
        # 배치 요청 전송
        batch_str = json.dumps(requests) + "\n"
        self.process.stdin.write(batch_str)
        self.process.stdin.flush()
        
        # 배치 응답 수신
        response_str = self.process.stdout.readline().strip()
        responses = json.loads(response_str)
        
        results = []
        for response in responses:
            if "error" in response:
                raise Exception(f"JSON-RPC Error {response['error']['code']}: {response['error']['message']}")
            results.append(response.get("result"))
        
        return results
    
    def close(self):
        """연결 종료"""
        self.process.terminate()
        self.process.wait()

# 사용 예제
if __name__ == "__main__":
    client = JSONRPCClient(["python", "server.py"])
    
    try:
        # 단일 호출
        result = client.call("add", [5, 3])
        print(f"5 + 3 = {result}")
        
        # 객체 매개변수
        result = client.call("subtract", {"a": 10, "b": 4})
        print(f"10 - 4 = {result}")
        
        # 알림 (응답 없음)
        client.call("log", ["Operation completed"], notification=True)
        
        # 배치 호출
        results = client.batch_call([
            {"method": "add", "params": [1, 2]},
            {"method": "multiply", "params": [3, 4]},
            {"method": "subtract", "params": [10, 5]}
        ])
        print(f"Batch results: {results}")
        
    finally:
        client.close()
```

## 보안 고려사항

### 1. 입력 검증

```python
def validate_method_name(method: str) -> bool:
    """메서드명 검증"""
    # rpc.로 시작하는 메서드는 내부용으로 예약
    if method.startswith("rpc."):
        return False
    
    # 알파벳, 숫자, 언더스코어만 허용
    import re
    return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', method) is not None

def sanitize_params(params):
    """매개변수 정제"""
    if isinstance(params, dict):
        # 위험한 키 제거
        dangerous_keys = ['__class__', '__module__', '__globals__']
        return {k: v for k, v in params.items() if k not in dangerous_keys}
    return params
```

### 2. 접근 제어

```python
class SecureJSONRPCServer(JSONRPCServer):
    def __init__(self, auth_token: str = None):
        super().__init__()
        self.auth_token = auth_token
        self.allowed_methods = set()
    
    def allow_method(self, method: str):
        """허용된 메서드 등록"""
        self.allowed_methods.add(method)
    
    def _process_single_request(self, request):
        # 인증 확인
        if self.auth_token:
            auth = request.get("auth")
            if auth != self.auth_token:
                return self._error_response(
                    request.get("id"), -32000, "Authentication required"
                )
        
        # 메서드 접근 권한 확인
        method = request.get("method")
        if method and method not in self.allowed_methods:
            return self._error_response(
                request.get("id"), -32000, "Method not allowed"
            )
        
        return super()._process_single_request(request)
```

### 3. 속도 제한

```python
import time
from collections import defaultdict

class RateLimitedJSONRPCServer(JSONRPCServer):
    def __init__(self, max_requests_per_minute: int = 60):
        super().__init__()
        self.max_requests = max_requests_per_minute
        self.request_history = defaultdict(list)
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """속도 제한 확인"""
        now = time.time()
        minute_ago = now - 60
        
        # 1분 이전 요청 제거
        self.request_history[client_id] = [
            req_time for req_time in self.request_history[client_id]
            if req_time > minute_ago
        ]
        
        # 현재 요청 추가
        self.request_history[client_id].append(now)
        
        return len(self.request_history[client_id]) <= self.max_requests
```

## 성능 최적화

### 1. 연결 풀링

```python
import queue
import threading

class JSONRPCConnectionPool:
    def __init__(self, server_command: list, pool_size: int = 5):
        self.server_command = server_command
        self.pool = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        
        # 초기 연결 생성
        for _ in range(pool_size):
            client = JSONRPCClient(server_command)
            self.pool.put(client)
    
    def call(self, method: str, params=None):
        """풀에서 연결을 가져와서 호출"""
        client = self.pool.get()
        try:
            return client.call(method, params)
        finally:
            self.pool.put(client)
```

### 2. 비동기 처리

```python
import asyncio
import json

class AsyncJSONRPCClient:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.pending_requests = {}
    
    async def call(self, method: str, params=None) -> Any:
        """비동기 메서드 호출"""
        request_id = str(uuid.uuid4())
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id
        }
        if params is not None:
            request["params"] = params
        
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        # 요청 전송
        request_str = json.dumps(request) + "\n"
        self.writer.write(request_str.encode())
        await self.writer.drain()
        
        return await future
    
    async def _response_handler(self):
        """응답 처리 루프"""
        while True:
            line = await self.reader.readline()
            if not line:
                break
            
            try:
                response = json.loads(line.decode().strip())
                request_id = response.get("id")
                
                if request_id in self.pending_requests:
                    future = self.pending_requests.pop(request_id)
                    
                    if "error" in response:
                        error = response["error"]
                        future.set_exception(
                            Exception(f"JSON-RPC Error {error['code']}: {error['message']}")
                        )
                    else:
                        future.set_result(response.get("result"))
            
            except Exception as e:
                print(f"Response handling error: {e}")
```

### 3. 메시지 압축

```python
import gzip
import json

class CompressedJSONRPCClient(JSONRPCClient):
    def _send_request(self, request):
        """압축된 요청 전송"""
        request_str = json.dumps(request)
        
        # 메시지가 큰 경우 압축
        if len(request_str) > 1024:
            compressed = gzip.compress(request_str.encode())
            # 압축 헤더 추가
            self.process.stdin.write("COMPRESSED\n")
            self.process.stdin.write(f"{len(compressed)}\n")
            self.process.stdin.buffer.write(compressed)
        else:
            self.process.stdin.write(request_str + "\n")
        
        self.process.stdin.flush()
```

## 디버깅 가이드

### 1. 로깅 구현

```python
import logging
import sys

class LoggingJSONRPCServer(JSONRPCServer):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("jsonrpc")
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
    
    def handle_request(self, request_str: str) -> str:
        self.logger.debug(f"Received request: {request_str}")
        
        response = super().handle_request(request_str)
        
        if response:
            self.logger.debug(f"Sending response: {response}")
        else:
            self.logger.debug("No response (notification)")
        
        return response
    
    def _process_single_request(self, request):
        method = request.get("method", "unknown")
        self.logger.info(f"Processing method: {method}")
        
        try:
            response = super()._process_single_request(request)
            if response and "error" in response:
                self.logger.error(f"Method {method} failed: {response['error']}")
            else:
                self.logger.info(f"Method {method} completed successfully")
            return response
        except Exception as e:
            self.logger.exception(f"Unexpected error in method {method}")
            raise
```

### 2. 메시지 추적

```python
import time
from typing import Dict, List

class TracingJSONRPCServer(JSONRPCServer):
    def __init__(self):
        super().__init__()
        self.traces: List[Dict] = []
    
    def _process_single_request(self, request):
        start_time = time.time()
        method = request.get("method")
        request_id = request.get("id")
        
        trace = {
            "timestamp": start_time,
            "method": method,
            "request_id": request_id,
            "request": request.copy(),
            "duration": None,
            "success": None,
            "error": None
        }
        
        try:
            response = super()._process_single_request(request)
            trace["duration"] = time.time() - start_time
            trace["success"] = "error" not in (response or {})
            
            if response and "error" in response:
                trace["error"] = response["error"]
            
            return response
            
        except Exception as e:
            trace["duration"] = time.time() - start_time
            trace["success"] = False
            trace["error"] = {"code": -32603, "message": str(e)}
            raise
        finally:
            self.traces.append(trace)
            
            # 최근 1000개 추적만 유지
            if len(self.traces) > 1000:
                self.traces = self.traces[-1000:]
    
    def get_performance_stats(self):
        """성능 통계 반환"""
        if not self.traces:
            return {}
        
        successful = [t for t in self.traces if t["success"]]
        failed = [t for t in self.traces if not t["success"]]
        
        return {
            "total_requests": len(self.traces),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / len(self.traces) if self.traces else 0,
            "average_duration": sum(t["duration"] for t in successful) / len(successful) if successful else 0,
            "method_stats": self._get_method_stats()
        }
    
    def _get_method_stats(self):
        """메서드별 통계"""
        stats = {}
        for trace in self.traces:
            method = trace["method"]
            if method not in stats:
                stats[method] = {"count": 0, "success": 0, "total_duration": 0}
            
            stats[method]["count"] += 1
            if trace["success"]:
                stats[method]["success"] += 1
            stats[method]["total_duration"] += trace["duration"]
        
        # 평균 계산
        for method, data in stats.items():
            data["success_rate"] = data["success"] / data["count"]
            data["average_duration"] = data["total_duration"] / data["count"]
        
        return stats
```

### 3. 개발용 디버그 도구

```python
import json
import sys

def debug_jsonrpc():
    """대화형 JSON-RPC 디버거"""
    print("JSON-RPC Debug Tool")
    print("Type 'quit' to exit")
    print("Example: {\"jsonrpc\": \"2.0\", \"method\": \"ping\", \"id\": 1}")
    
    server = JSONRPCServer()
    server.register_method("ping", lambda: "pong")
    server.register_method("echo", lambda msg: msg)
    server.register_method("add", lambda a, b: a + b)
    
    while True:
        try:
            request_str = input("\n> ")
            if request_str.lower() == 'quit':
                break
            
            response = server.handle_request(request_str)
            if response:
                # 응답을 예쁘게 출력
                response_obj = json.loads(response)
                print(json.dumps(response_obj, indent=2, ensure_ascii=False))
            else:
                print("(No response - notification)")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_jsonrpc()
```

## 본 프로젝트에서의 활용

이 receipt-printer 프로젝트에서는 JSON-RPC를 다음과 같이 활용합니다:

### MCP(Model Context Protocol)와의 통합

```python
# mcp_wrapper.py의 핵심 구조
class MCPServer:
    async def handle_request(self, request: dict) -> dict:
        """JSON-RPC 요청 처리"""
        method = request.get("method")
        
        if method == "initialize":
            return self._initialize_response(request["id"])
        elif method == "tools/list":
            return self._list_tools_response(request["id"])
        elif method == "tools/call":
            return await self._call_tool_response(request)
        # ...
```

### 프린터 도구 호출

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "print_receipt",
    "arguments": {
      "text": "우유 사오기",
      "preview": false
    }
  },
  "id": 1
}
```

이러한 JSON-RPC 기반 아키텍처를 통해 Claude Desktop과 프린터 유틸리티 간의 효율적이고 안정적인 통신이 가능합니다.

## 참고 자료

- [JSON-RPC 2.0 공식 사양](https://www.jsonrpc.org/specification)
- [MCP 공식 문서](https://spec.modelcontextprotocol.io/)
- [프로젝트 MCP 구현 분석](./mcp-wrapper-analysis.md)
- [MCP stdio 통신 방식](./mcp-stdio.md)

## 결론

JSON-RPC는 그 단순함과 유연성으로 인해 많은 프로젝트에서 채택되고 있는 프로토콜입니다. 특히 MCP와 같은 모델 컨텍스트 프로토콜에서 중요한 역할을 하며, 이 문서에서 다룬 내용들을 바탕으로 효율적이고 안정적인 JSON-RPC 기반 시스템을 구축할 수 있습니다.

핵심은 **명확한 메시지 구조**, **적절한 에러 처리**, **보안 고려사항**을 염두에 두고 구현하는 것입니다. 또한 성능과 디버깅을 위한 적절한 도구들을 함께 구축하는 것이 장기적으로 유지보수 가능한 시스템을 만드는 데 도움이 됩니다.
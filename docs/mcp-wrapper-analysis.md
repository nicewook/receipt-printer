# MCP Wrapper 상세 분석

## 개요

`mcp_wrapper.py`는 Claude Desktop과 FastAPI 서버 간의 브리지 역할을 수행하는 핵심 컴포넌트입니다. Model Context Protocol (MCP)을 구현하여 JSON-RPC 2.0 기반의 통신을 제공합니다.

## 아키텍처

### 통신 흐름
```
Claude Desktop → JSON-RPC → MCP Wrapper → HTTP API → FastAPI Server
                                ↓
Claude Desktop ← JSON-RPC ← MCP Wrapper ← HTTP API ← FastAPI Server
```

### 핵심 구성요소

1. **MCPServer 클래스** (`mcp_wrapper.py:23-476`)
   - 비동기 HTTP 클라이언트 관리
   - JSON-RPC 2.0 프로토콜 구현
   - 도구 정의 및 스키마 관리

2. **프로토콜 변환 계층**
   - MCP JSON-RPC → HTTP REST API
   - 에러 코드 변환 및 전파
   - 응답 형식 표준화

## MCP 프로토콜 구현

### 지원 메서드

| 메서드 | 기능 | 응답 |
|--------|------|------|
| `initialize` | 서버 초기화 | 프로토콜 버전, 서버 정보 |
| `tools/list` | 도구 목록 조회 | 사용 가능한 도구 스키마 |
| `tools/call` | 도구 실행 | 도구별 결과 데이터 |

### 프로토콜 상수
```python
MCP_VERSION = "2024-11-05"
SERVER_NAME = "receipt-printer"
SERVER_VERSION = "1.0.0"
```

## 도구 스키마 분석

### 1. print_receipt
**목적**: 영수증 출력 (미리보기 지원)
**입력 스키마**:
- `printer_name`: 프린터 이름 (기본값: "BIXOLON_SRP_330II")
- `content`: 출력 내용 객체
  - `header`: 헤더 텍스트 (선택)
  - `items`: 영수증 항목 배열 (선택)
    - `name`: 항목명 (필수)
    - `quantity`: 수량 (선택)
    - `price`: 단가 (선택)
    - `total`: 합계 (선택)
  - `footer`: 푸터 텍스트 (선택)
  - `text`: 단순 텍스트 (items 대신 사용)
- `preview`: 미리보기 모드 (기본값: false)

### 2. list_printers
**목적**: 사용 가능한 프린터 목록 조회
**입력 스키마**: 파라미터 없음
**출력**: 프린터 목록과 상태 정보

### 3. get_printer_status
**목적**: 특정 프린터 상태 확인
**입력 스키마**:
- `printer_name`: 상태 확인할 프린터 이름 (필수)

### 4. preview_receipt
**목적**: 영수증 미리보기 전용
**입력 스키마**: print_receipt의 content와 동일

## 비동기 처리 구조

### HTTP 클라이언트 관리
```python
async def __aenter__(self):
    """비동기 컨텍스트 매니저 진입"""
    self.session = aiohttp.ClientSession()
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    """비동기 컨텍스트 매니저 종료"""
    if self.session:
        await self.session.close()
```

### API 요청 처리
- **GET 요청**: 프린터 목록, 상태 조회
- **POST 요청**: 영수증 출력 (미리보기 포함)
- **에러 처리**: HTTP 상태 코드 검증 및 예외 변환

## 에러 처리 메커니즘

### 다층 에러 전파
1. **FastAPI 서버 에러** → HTTP 상태 코드
2. **MCP Wrapper 변환** → JSON-RPC 에러 코드
3. **Claude Desktop** → 사용자 친화적 메시지

### 에러 코드 매핑
| JSON-RPC 코드 | 의미 | 원인 |
|---------------|------|------|
| -32700 | Parse error | JSON 파싱 실패 |
| -32601 | Method not found | 지원하지 않는 메서드 |
| -32602 | Invalid params | 파라미터 오류 |
| -32603 | Internal error | 서버 내부 오류 |

## 설정 관리

### 환경 변수
```python
API_URL = os.getenv("PRINTER_API_URL", "http://127.0.0.1:8000")
```

### 기본 설정
- **API 서버**: `127.0.0.1:8000` (로컬 전용)
- **기본 프린터**: `BIXOLON_SRP_330II`
- **타임아웃**: HTTP 요청별 자동 관리

## 보안 특징

### 로컬 통신 제한
- API 서버는 127.0.0.1에서만 실행
- 외부 네트워크 접근 차단
- CORS 정책으로 Origin 제한

### 입력 검증
- JSON 스키마 기반 타입 검증
- 필수 파라미터 확인
- 데이터 형식 표준화

## 디버깅 지원

### 로그 시스템
```python
def log_debug(self, message: str):
    """디버그 로그 (stderr로 출력)"""
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}", file=sys.stderr)
```

### 디버그 정보
- API 요청/응답 로깅
- 에러 상세 정보 기록
- 타임스탬프 포함

## 사용 예시

### Claude Desktop 통합
1. **설정**: `claude_desktop_config.json`에 MCP 서버 등록
2. **실행**: `python3 mcp_wrapper.py`로 서버 시작
3. **상호작용**: Claude Desktop에서 영수증 출력 도구 사용

### 명령어 예시
```bash
# MCP 서버 직접 실행
python3 mcp_wrapper.py

# 환경 변수로 API URL 변경
PRINTER_API_URL=http://127.0.0.1:8080 python3 mcp_wrapper.py
```

## 확장 가능성

### 새로운 도구 추가
1. `self.tools` 딕셔너리에 스키마 정의
2. `handle_tool_call`에 처리 로직 추가
3. 개별 핸들러 메서드 구현

### API 서버 변경
- 환경 변수 `PRINTER_API_URL` 수정
- 다른 포트나 호스트로 연결 가능
- 인증 헤더 추가 지원

## 성능 특성

### 메모리 사용량
- 비동기 I/O로 메모리 효율성 극대화
- HTTP 연결 재사용으로 오버헤드 최소화

### 응답 시간
- 로컬 API 호출로 지연시간 최소화
- 비동기 처리로 동시 요청 지원

### 확장성
- 단일 MCP 서버가 여러 Claude 세션 지원
- FastAPI 서버와 독립적 확장 가능
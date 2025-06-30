# BIXOLON Receipt Printer MCP Server

한국어를 지원하는 BIXOLON 영수증 프린터 제어를 위한 **단순화된** MCP (Model Context Protocol) 서버입니다.

## 🚀 주요 기능

- **MCP 프로토콜 지원**: Claude Desktop과 직접 통합 (HTTP 서버 불필요)
- **한국어 완벽 지원**: EUC-KR 인코딩 및 ESC/POS 명령어
- **간단한 텍스트 출력**: 200자 이내의 메모, 할일 목록 즉시 출력
- **미리보기 모드**: 실제 출력 전 내용 확인 가능
- **직접 호출 구조**: FastAPI 서버 없이 printer 직접 호출

## 📋 시스템 요구사항

- **Python**: 3.8 이상
- **운영체제**: macOS 또는 Linux (CUPS 지원)
- **프린터**: ESC/POS 호환 영수증 프린터 (BIXOLON SRP-330II 시리즈 권장)
- **CUPS**: 프린터 서비스가 설치되고 실행 중이어야 함
- **텍스트 제한**: 200자 이내 (한글/영문 혼용 가능)

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. CUPS 프린터 설정

```bash
# 프린터 목록 확인
lpstat -p

# CUPS 서비스 상태 확인 (macOS)
brew services list | grep cups

# CUPS 서비스 시작 (필요시)
brew services start cups
```

## 🔧 Claude Desktop 설정

### 1. 설정 파일 위치
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Python 환경 확인

먼저 사용할 Python 환경을 확인하세요:

```bash
# 현재 Python 경로 확인
which python3

# 가상환경 사용 시
source /path/to/venv/bin/activate
which python3  # 가상환경의 python 경로 확인
```

### 3. 설정 파일 내용

#### 기본 설정 (시스템 Python)
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "python3",
      "args": ["/절대경로/receipt-printer/mcp_wrapper.py"]
    }
  }
}
```

#### 권장 설정 (전체 경로 지정)
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/usr/bin/python3",
      "args": ["/Users/username/receipt-printer/mcp_wrapper.py"]
    }
  }
}
```

#### 가상환경 사용 시
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/Users/username/receipt-printer/.venv/bin/python3",
      "args": ["/Users/username/receipt-printer/mcp_wrapper.py"]
    }
  }
}
```

**중요**: 
- 절대경로를 정확히 입력해야 합니다!
- 가상환경 사용 시 가상환경의 python 경로를 지정하세요!

### 4. 설정 검증

설정이 올바른지 터미널에서 확인:

```bash
# 설정한 Python으로 MCP wrapper가 실행되는지 테스트
/usr/bin/python3 /Users/username/receipt-printer/mcp_wrapper.py
# 또는 가상환경 사용 시
/Users/username/receipt-printer/.venv/bin/python3 /Users/username/receipt-printer/mcp_wrapper.py

# Ctrl+C로 종료 후 다음 단계 진행
```

### 5. 설정 완료 후

1. **Claude Desktop 완전 재시작** (중요!)
2. 새 대화 시작
3. MCP 도구가 자동으로 연결됨

## 🚀 사용 방법

### 1. Claude Desktop에서 간단한 텍스트 출력

#### ">" 트리거 패턴 (추천)
```
> 우유 사오기
> 회의 준비사항: 프레젠테이션 자료 준비
> 오늘 할일: 운동, 장보기, 청소
```

#### 직접 요청
```
"테스트 메모"를 영수증으로 출력해줘
영수증에 "점심약속 1시"라고 출력해줘
```

### 2. 프린터 관리

#### 프린터 목록 조회
```
프린터 목록을 보여줘
사용 가능한 프린터가 뭐가 있어?
```

#### 프린터 상태 확인
```
프린터 상태 확인해줘
BIXOLON 프린터 상태는 어때?
```

### 3. 미리보기 기능
```
"장보기 목록"을 미리보기로 보여줘
다음 내용을 출력 전에 미리보기 해줘: "회의 안건"
```

## 📖 MCP 도구 상세

### print_receipt
- **기능**: 200자 이내의 간단한 텍스트를 영수증으로 출력
- **매개변수**:
  - `text` (필수): 출력할 텍스트 (200자 이내)
  - `printer_name` (선택): 프린터 이름 (기본값: BIXOLON_SRP_330II)
  - `preview` (선택): 미리보기 모드 (기본값: false)

### list_printers
- **기능**: 사용 가능한 프린터 목록과 상태 조회
- **매개변수**: 없음

### get_printer_status
- **기능**: 특정 프린터의 상태 확인
- **매개변수**:
  - `printer_name` (선택): 프린터 이름 (기본값: BIXOLON_SRP_330II)

## 🧪 테스트 실행

### MCP 서버 직접 테스트

```bash
# MCP 서버 시작 테스트
python3 mcp_wrapper.py

# 도구 목록 조회
echo '{"method":"tools/list","id":1}' | python3 mcp_wrapper.py

# 텍스트 출력 테스트 (미리보기)
echo '{"method":"tools/call","id":2,"params":{"name":"print_receipt","arguments":{"text":"테스트","preview":true}}}' | python3 mcp_wrapper.py

# 프린터 목록 조회
echo '{"method":"tools/call","id":3,"params":{"name":"list_printers","arguments":{}}}' | python3 mcp_wrapper.py
```

### 단위 테스트

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_printer.py -v

# 커버리지 포함 실행
pytest --cov=. --cov-report=html
```

## 🛠️ 개발 가이드

### 단순화된 프로젝트 구조

```
receipt-printer/
├── printer.py     # 핵심 프린터 기능
├── mcp_wrapper.py       # MCP 프로토콜 인터페이스
├── requirements.txt     # 최소 의존성 목록
├── CLAUDE.md           # AI 개발 가이드
├── claude_desktop_config.json  # 설정 예시
└── tests/              # 테스트 스위트
    ├── test_printer.py
    └── test_mcp_integration.py
```

### 아키텍처

```
Claude Desktop → JSON-RPC → mcp_wrapper.py → printer.py → CUPS → 프린터
```

- **단순함**: HTTP 서버 없이 직접 함수 호출
- **빠름**: 네트워크 오버헤드 제거
- **안정함**: 의존성 최소화

## 🐛 문제 해결

### 일반적인 문제

1. **프린터가 인식되지 않음**
   ```bash
   lpstat -p  # 프린터 목록 확인
   ```

2. **CUPS 서비스 오류**
   ```bash
   brew services restart cups  # macOS
   sudo service cups restart   # Linux
   ```

3. **Claude Desktop에 MCP 서버가 나타나지 않음**
   - 설정 파일 경로 확인
   - 절대경로 정확히 입력했는지 확인
   - Claude Desktop 완전 재시작
   - 새 대화 시작

4. **텍스트가 너무 김**
   - 200자 이내로 제한
   - 여러 번에 나누어 출력

5. **한글 출력 문제**
   - 프린터가 EUC-KR 인코딩을 지원하는지 확인
   - ESC/POS 호환성 확인

### 디버그 모드

```bash
# MCP 서버 로그 확인 (stderr)
python3 mcp_wrapper.py 2> debug.log

# 실시간 로그 모니터링
python3 mcp_wrapper.py 2>&1 | tee debug.log
```

## 📚 추가 문서

- **상세 문서**: `docs/` 디렉토리 참조
- **MCP 통신 방식**: `docs/mcp-stdio.md`
- **단순화 계획**: `docs/mcp-simplification-plan.md`
- **개발자 가이드**: `CLAUDE.md`

## 💡 사용 팁

1. **빠른 메모**: `> 텍스트` 형식으로 즉시 출력
2. **긴 텍스트**: 200자를 넘으면 자동으로 오류 메시지 표시
3. **미리보기**: 실제 출력 전 내용 확인 가능
4. **여러 프린터**: 프린터 이름 지정으로 다른 프린터 사용 가능

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📞 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues를 통해 문의해주세요.
# Claude Desktop MCP 설정 가이드

Claude Desktop에서 영수증 프린터 MCP 서버를 사용하기 위한 단계별 설정 가이드입니다.

## 🚀 빠른 설정 (5분)

### 1단계: 설정 파일 위치 찾기

운영체제별 Claude Desktop 설정 파일 위치:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2단계: 현재 프로젝트 경로 확인

터미널에서 프로젝트 경로를 확인합니다:

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/receipt-printer

# 절대 경로 확인
pwd
# 출력 예시: /Users/username/receipt-printer
```

### 3단계: Python 경로 확인

```bash
# Python3 경로 확인
which python3
# 출력 예시: /usr/bin/python3 또는 /opt/homebrew/bin/python3
```

### 4단계: 설정 파일 편집

`claude_desktop_config.json` 파일을 열고 다음과 같이 설정:

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

**⚠️ 중요**: 
- `command`에는 실제 python3 경로를 입력
- `args`에는 mcp_wrapper.py의 절대 경로를 입력

### 5단계: Claude Desktop 재시작

1. Claude Desktop 완전 종료
2. Claude Desktop 다시 시작
3. 새 대화 시작

## ✅ 설정 확인

### 연결 상태 확인

Claude Desktop에서 다음 중 하나를 입력해 확인:

```
프린터 목록을 보여줘
```

또는

```
> 테스트
```

성공하면 프린터 목록이나 출력 결과가 표시됩니다.

### 문제 해결

연결되지 않는 경우:

1. **경로 재확인**
   ```bash
   # mcp_wrapper.py 파일이 존재하는지 확인
   ls -la /Users/username/receipt-printer/mcp_wrapper.py
   
   # 실행 권한 확인
   chmod +x /Users/username/receipt-printer/mcp_wrapper.py
   ```

2. **수동 테스트**
   ```bash
   # MCP 서버가 정상 작동하는지 테스트
   python3 /Users/username/receipt-printer/mcp_wrapper.py
   ```

3. **Claude Desktop 로그 확인**
   - Claude Desktop 개발자 콘솔 열기
   - MCP 관련 오류 메시지 확인

## 📝 설정 예시

### macOS 설정 예시

```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["/Users/john/Projects/receipt-printer/mcp_wrapper.py"]
    }
  }
}
```

### Windows 설정 예시

```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "C:\\Python39\\python.exe",
      "args": ["C:\\Users\\john\\receipt-printer\\mcp_wrapper.py"]
    }
  }
}
```

### Linux 설정 예시

```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/usr/bin/python3",
      "args": ["/home/john/receipt-printer/mcp_wrapper.py"]
    }
  }
}
```

## 🎯 사용법

### 기본 사용

```
> 우유 사오기
> 회의 준비: 자료 준비, 회의실 예약
```

### 미리보기

```
"장보기 목록"을 미리보기로 보여줘
```

### 프린터 관리

```
프린터 목록 보여줘
프린터 상태 확인해줘
```

## 🔧 고급 설정

### 가상환경 사용 시

가상환경의 Python을 사용하는 경우:

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

### 여러 프린터 설정

서로 다른 프린터를 위한 여러 MCP 서버:

```json
{
  "mcpServers": {
    "receipt-printer-office": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/receipt-printer/mcp_wrapper.py"],
      "env": {
        "DEFAULT_PRINTER": "OFFICE_PRINTER"
      }
    },
    "receipt-printer-home": {
      "command": "/usr/bin/python3", 
      "args": ["/path/to/receipt-printer/mcp_wrapper.py"],
      "env": {
        "DEFAULT_PRINTER": "HOME_PRINTER"
      }
    }
  }
}
```

## 📊 상태 모니터링

### 디버그 로그 활성화

```bash
# 로그 파일로 저장
python3 mcp_wrapper.py 2> debug.log

# 실시간 로그 확인
python3 mcp_wrapper.py 2>&1 | tee debug.log
```

### 연결 상태 확인

Claude Desktop에서:

```
연결된 MCP 서버 상태를 알려줘
```

## 🆘 문제 해결 체크리스트

- [ ] Python3 경로가 올바른가?
- [ ] mcp_wrapper.py 파일이 존재하는가?
- [ ] 파일에 실행 권한이 있는가?
- [ ] 절대 경로를 사용했는가?
- [ ] Claude Desktop을 완전 재시작했는가?
- [ ] 새 대화를 시작했는가?
- [ ] CUPS 서비스가 실행 중인가?
- [ ] 프린터가 연결되어 있는가?

모든 항목을 확인했는데도 문제가 있다면 GitHub Issues를 통해 문의하세요.
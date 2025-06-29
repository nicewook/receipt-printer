# MCP Receipt Printer 실제 구동 가이드

Claude Desktop에서 영수증 프린터를 사용하는 완전한 단계별 가이드입니다.

## ✅ 0단계: 현재 상태 확인

먼저 현재 상태를 확인하고 필요한 것들이 준비되어 있는지 체크해보겠습니다.

### 프로젝트 파일 확인
```bash
# 프로젝트 디렉터리로 이동
cd /Users/hyunseokjeong/VibeCodingProject/receipt-printer

# 필수 파일들이 존재하는지 확인
ls -la

# 다음 파일들이 있어야 합니다:
# server.py, mcp_wrapper.py, config.py, schemas.py, requirements.txt
```

### Python 및 시스템 환경 확인
```bash
# Python 3 버전 확인
python3 --version

# 현재 디렉터리 확인
pwd

# 가상환경이 이미 있는지 확인
ls -la .venv/
```

**✅ 체크리스트:**
- [ ] 프로젝트 디렉터리에 있음 (`/Users/hyunseokjeong/VibeCodingProject/receipt-printer`)
- [ ] Python 3.8+ 설치됨
- [ ] 필수 파일들 존재 (server.py, mcp_wrapper.py 등)
- [ ] .venv 폴더 존재 여부 확인

## 🚀 1단계: 시스템 준비

### CUPS 프린터 서비스 확인
```bash
# macOS에서 CUPS 상태 확인
brew services list | grep cups

# CUPS 서비스가 실행 중이 아니라면 시작
brew services start cups

# 프린터가 시스템에 등록되어 있는지 확인
lpstat -p
```

예상 출력:
```
printer BIXOLON_SRP_330II is idle. enabled since Mon 01 Jan 2024 12:00:00 KST
```

### Python 환경 설정
프로젝트 전용 **가상환경(virtual environment)** 사용을 권장합니다. 

#### 🔄 Case A: 가상환경이 이미 있는 경우
```bash
# 가상환경 활성화
source .venv/bin/activate

# 프롬프트가 (.venv)로 바뀌면 성공
# (.venv) user@macbook receipt-printer %

# 의존성 설치 상태 확인
pip list | grep fastapi

# 의존성이 없거나 오래된 경우 재설치
pip install --upgrade pip
pip install -r requirements.txt
```

#### 🆕 Case B: 가상환경이 없는 경우
```bash
# 1) 가상환경 생성 (.venv 폴더)
python3 -m venv .venv

# 2) 가상환경 활성화 (zsh/bash)
source .venv/bin/activate
# fish → source .venv/bin/activate.fish
# PowerShell → .venv\Scripts\Activate.ps1

# 3) 최신 pip 업그레이드 및 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

#### ✅ 설치 확인
```bash
# 필수 패키지 설치 확인
which uvicorn          # .venv/bin/uvicorn 경로가 출력되면 성공
which python           # .venv/bin/python 경로가 출력되면 성공
pip list | grep -E "(fastapi|uvicorn|pydantic)"
```

> 💡 **TIP**: 
> - 프롬프트 앞에 `(.venv)`가 표시되면 가상환경이 활성화된 상태입니다
> - VS Code/Cursor에서 Python 인터프리터를 `.venv/bin/python`으로 설정하세요
> - 터미널을 새로 열 때마다 `source .venv/bin/activate` 실행 필요

## 🔧 2단계: 서버 구성 및 실행

### 🎯 터미널 세션 준비
앞으로 **2개의 터미널**을 사용합니다:
- **터미널 1**: FastAPI 서버 실행 (계속 실행 상태 유지)
- **터미널 2**: 테스트 및 Claude Desktop 설정

### 📡 터미널 1: FastAPI 서버 실행

```bash
# 1) 프로젝트 디렉터리로 이동 
cd /Users/hyunseokjeong/VibeCodingProject/receipt-printer

# 2) 가상환경 활성화 (중요!)
source .venv/bin/activate

# 3) 프롬프트에 (.venv)가 표시되는지 확인
# (.venv) user@macbook receipt-printer %

# 4) 서버 실행 (방법 1: 직접 실행)
python server.py

# 또는 방법 2: uvicorn 사용 (더 상세한 로그)
# uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

**✅ 성공 시 출력:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

> ⚠️ **중요**: 이 터미널은 서버가 실행되는 동안 계속 열어두세요!

### 🧪 터미널 2: 서버 테스트

**새 터미널을 열고** 다음 명령으로 서버가 정상 작동하는지 확인:

```bash
# 서버 응답 확인
curl http://127.0.0.1:8000/

# 프린터 목록 조회 테스트
curl http://127.0.0.1:8000/printers
```

**✅ 예상 응답:**
```json
{
  "printers": [
    {
      "name": "BIXOLON_SRP_330II",
      "status": "printer BIXOLON_SRP_330II is idle. enabled",
      "available": true
    }
  ],
  "total_count": 1
}
```

### ❌ 문제 발생 시 체크사항
```bash
# 포트 8000이 이미 사용 중인지 확인
lsof -i :8000

# 가상환경이 활성화되어 있는지 확인
which python  # .venv/bin/python이 출력되어야 함

# 의존성이 올바르게 설치되었는지 확인
pip list | grep fastapi
```

## 🖥️ 3단계: Claude Desktop 설정

### 📋 사전 확인
Claude Desktop 설정 전에 다음을 확인하세요:
- [ ] **터미널 1**에서 FastAPI 서버가 실행 중
- [ ] **터미널 2**에서 `curl http://127.0.0.1:8000/printers` 테스트 성공
- [ ] 가상환경 경로 확인: `/Users/hyunseokjeong/VibeCodingProject/receipt-printer/.venv/bin/python3`

### 🔧 MCP 서버 구성 파일 수정

```bash
# 설정 파일 열기 (macOS)
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 또는 터미널에서 직접 편집
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**설정 파일 내용:**
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/Users/hyunseokjeong/VibeCodingProject/receipt-printer/.venv/bin/python3",
      "args": ["/Users/hyunseokjeong/VibeCodingProject/receipt-printer/mcp_wrapper.py"],
      "env": {
        "PRINTER_API_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

### ✅ 설정 검증
설정 파일 저장 후 다음을 확인:

```bash
# 1) 가상환경 Python 경로가 올바른지 확인
ls -la /Users/hyunseokjeong/VibeCodingProject/receipt-printer/.venv/bin/python3

# 2) MCP wrapper 파일이 존재하는지 확인
ls -la /Users/hyunseokjeong/VibeCodingProject/receipt-printer/mcp_wrapper.py

# 3) MCP wrapper가 실행 가능한지 테스트
cd /Users/hyunseokjeong/VibeCodingProject/receipt-printer
source .venv/bin/activate
python mcp_wrapper.py
# Ctrl+C로 종료
```

### 🔄 Claude Desktop 재시작
1. **Claude Desktop 완전 종료** (⌘+Q)
2. **모든 백그라운드 프로세스 확인**
   ```bash
   # Claude 프로세스가 완전히 종료되었는지 확인
   ps aux | grep -i claude
   ```
3. **Claude Desktop 재실행**
4. **새 대화 시작**

### 🎯 MCP 연결 확인
새 Claude Desktop 대화에서 다음 명령 시도:
```
프린터 목록을 보여주세요.
```

정상 연결 시 Claude가 MCP 도구를 사용하여 프린터 목록을 조회합니다.

## 🎯 4단계: 실제 사용 예시

### 기본 텍스트 출력
Claude Desktop에서 다음과 같이 요청:

```
안녕하세요! 영수증에 "테스트 출력입니다"라고 출력해주세요.
```

Claude의 응답:
```
영수증에 텍스트를 출력하겠습니다.

[print_receipt 도구 실행]

✅ 출력 완료: 5줄 → BIXOLON_SRP_330II
📝 작업 ID: BIXOLON_SRP_330II-67890
📊 출력 라인 수: 5
```

### 구조화된 영수증 출력
```
다음 내용으로 영수증을 출력해주세요:
- 헤더: "카페 하우스"
- 항목: 아메리카노 2잔, 각 4500원, 총 9000원
- 항목: 카페라떼 1잔, 5000원
- 푸터: "감사합니다. 또 오세요!"
```

Claude의 응답:
```
구조화된 영수증을 출력하겠습니다.

[print_receipt 도구 실행]

✅ 출력 완료: 8줄 → BIXOLON_SRP_330II
📝 작업 ID: BIXOLON_SRP_330II-67891
📊 출력 라인 수: 8
```

실제 프린터 출력:
```
========================================
              카페 하우스
========================================

아메리카노 x2                      9,000원
카페라떼                          5,000원

========================================
         감사합니다. 또 오세요!
========================================
```

### 미리보기 기능
```
영수증을 실제로 출력하기 전에 "주문 확인서"라는 내용으로 미리보기를 보여주세요.
```

Claude의 응답:
```
영수증 미리보기를 생성하겠습니다.

[preview_receipt 도구 실행]

📄 영수증 미리보기:
==========================================
|                                        |
|              주문 확인서                |
|                                        |
|                                        |
==========================================
총 4줄
```

### 프린터 상태 확인
```
프린터 상태를 확인해주세요.
```

Claude의 응답:
```
프린터 상태를 확인하겠습니다.

[get_printer_status 도구 실행]

📊 프린터 상태: BIXOLON_SRP_330II
✅ printer BIXOLON_SRP_330II is idle. enabled since Mon 01 Jan 2024
🕒 확인 시각: 2024-01-01T12:30:45.123456
```

### 프린터 목록 조회
```
사용 가능한 프린터 목록을 보여주세요.
```

Claude의 응답:
```
사용 가능한 프린터 목록을 조회하겠습니다.

[list_printers 도구 실행]

🖨️  사용 가능한 프린터:
  ✅ BIXOLON_SRP_330II
     상태: printer BIXOLON_SRP_330II is idle. enabled since Mon 01 Jan 2024

총 1개 프린터
```

## 🔧 5단계: 고급 사용법

### 복잡한 영수증 작성
```
다음과 같은 상세한 영수증을 출력해주세요:

매장: 스타벅스 강남점
날짜: 2024-01-01
주문번호: #1234

메뉴:
- 아메리카노 (톨) 2잔 × 4,500원 = 9,000원
- 카페라떼 (그란데) 1잔 × 5,500원 = 5,500원  
- 블루베리 머핀 1개 × 3,500원 = 3,500원

소계: 18,000원
할인: -1,000원 (멤버십 할인)
최종 금액: 17,000원

결제수단: 카드
감사합니다!
```

### 여러 작업 순차 실행
```
1. 먼저 프린터 상태를 확인하고
2. 그 다음에 "매장 개점 알림"이라는 내용으로 미리보기를 본 후
3. 문제없으면 실제로 출력해주세요
```

## ❗ 6단계: 문제 해결

### 일반적인 오류와 해결책

#### "Connection refused" 오류
```
오류 발생: Connection refused
```

**해결책:**
1. FastAPI 서버가 실행 중인지 확인
2. 포트 8000이 사용 가능한지 확인
```bash
lsof -i :8000
python3 server.py
```

#### "Module not found" 오류
```
오류 발생: ModuleNotFoundError: No module named 'fastapi'
```

**해결책:**
1. 가상환경이 활성화되어 있는지 확인
2. 의존성 재설치
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

#### "Service Unavailable" 오류
```
오류 발생: HTTP 503: 출력 실패
```

**해결책:**
1. 프린터가 켜져 있고 연결되어 있는지 확인
2. CUPS 서비스 상태 확인
```bash
lpstat -p BIXOLON_SRP_330II
brew services restart cups
```

#### 한글 출력 문제
출력된 영수증에서 한글이 깨져 보이는 경우:

1. 프린터가 EUC-KR 인코딩을 지원하는지 확인
2. 프린터 설정에서 문자 인코딩 확인
3. 필요시 UTF-8 폴백 사용

### 디버깅 모드 활성화
```bash
# 디버그 모드로 서버 실행
export PRINTER_DEBUG=true
python3 server.py
```

디버그 모드에서는 상세한 로그가 출력됩니다:
```
[DEBUG] 2024-01-01T12:30:45.123456 - MCP Receipt Printer Server starting...
[DEBUG] 2024-01-01T12:30:45.234567 - API request failed: Connection timeout
```

## 🎉 성공 확인

모든 것이 정상적으로 작동한다면:

1. ✅ FastAPI 서버가 http://127.0.0.1:8000에서 실행 중
2. ✅ Claude Desktop이 MCP 서버를 인식
3. ✅ 영수증 출력 명령이 실제 프린터에서 작동
4. ✅ 한글과 영문이 모두 올바르게 출력

축하합니다! 이제 Claude Desktop을 통해 자연어로 영수증 프린터를 제어할 수 있습니다. 🎊

## 💡 팁과 권장사항

### 효율적인 사용법
- **미리보기 먼저**: 실제 출력 전에 항상 미리보기로 확인
- **구조화된 요청**: 헤더, 항목, 푸터를 명확히 구분하여 요청
- **상태 확인**: 출력 실패 시 프린터 상태부터 확인

### 보안 고려사항
- **로컬 전용**: 서버는 127.0.0.1에서만 실행 (외부 접근 불가)
- **프린터 화이트리스트**: 허용된 프린터만 사용 가능
- **가상환경 격리**: 시스템 Python과 분리된 환경에서 실행

### 성능 최적화
- 서버는 개발 모드(--reload) 대신 프로덕션 모드로 실행
- 대량 출력 시 배치 처리 고려
- 네트워크 지연 시간 모니터링

이제 Claude Desktop과 영수증 프린터가 완벽하게 연동되어 자연어로 프린터를 제어할 수 있습니다! 🚀

---

## 🚀 빠른 시작 가이드 (요약)

**현재 서버가 실행되지 않은 상태에서 빠르게 시작하는 방법:**

### 1️⃣ 터미널 1 (서버 실행)
```bash
cd /Users/hyunseokjeong/VibeCodingProject/receipt-printer
source .venv/bin/activate
python server.py
# 서버 실행 상태 유지
```

### 2️⃣ 터미널 2 (테스트)
```bash
curl http://127.0.0.1:8000/printers
# 응답이 오면 서버 정상 작동
```

### 3️⃣ Claude Desktop 설정
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "/Users/hyunseokjeong/VibeCodingProject/receipt-printer/.venv/bin/python3",
      "args": ["/Users/hyunseokjeong/VibeCodingProject/receipt-printer/mcp_wrapper.py"],
      "env": {
        "PRINTER_API_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

### 4️⃣ Claude Desktop 재시작 → 테스트
```
프린터 목록을 보여주세요.
```

**완료! 🎉**
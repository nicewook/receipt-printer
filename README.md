# BIXOLON Receipt Printer MCP Server

한국어를 지원하는 BIXOLON 영수증 프린터 제어를 위한 MCP (Model Context Protocol) 서버입니다.

## 🚀 주요 기능

- **MCP 프로토콜 지원**: Claude Desktop과 직접 통합
- **한국어 완벽 지원**: EUC-KR 인코딩 및 ESC/POS 명령어
- **구조화된 영수증**: 헤더, 항목, 푸터가 포함된 영수증 출력
- **보안 기능**: API 키 인증 및 프린터 화이트리스트
- **미리보기 모드**: 실제 출력 전 내용 확인 가능

## 📋 시스템 요구사항

- **Python**: 3.8 이상
- **운영체제**: macOS 또는 Linux (CUPS 지원)
- **프린터**: ESC/POS 호환 영수증 프린터 (BIXOLON SRP-330II 시리즈 권장)
- **CUPS**: 프린터 서비스가 설치되고 실행 중이어야 함

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# API 키 생성 (선택사항, 자동 생성됨)
export PRINTER_API_KEY="your-secure-api-key"

# 디버그 모드 (개발 시에만)
export PRINTER_DEBUG="true"
```

### 3. CUPS 프린터 설정

```bash
# 프린터 목록 확인
lpstat -p

# CUPS 서비스 상태 확인 (macOS)
brew services list | grep cups

# CUPS 서비스 시작 (필요시)
brew services start cups
```

## 🔧 Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일을 수정:

```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "python3",
      "args": ["/path/to/receipt-printer/mcp_wrapper.py"],
      "env": {
        "PRINTER_API_URL": "http://127.0.0.1:8000",
        "API_KEY": "your-generated-api-key"
      }
    }
  }
}
```

## 🚀 사용 방법

### 1. FastAPI 서버 시작

```bash
# 개발 모드
python server.py

# 또는 uvicorn 직접 실행
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Claude Desktop에서 사용

Claude Desktop에서 다음과 같은 명령을 사용할 수 있습니다:

#### 영수증 출력
```
영수증을 출력해줘:
- 헤더: "카페 영수증"
- 항목: 아메리카노 2잔, 각 4,500원
- 항목: 카페라떼 1잔, 5,000원
- 푸터: "감사합니다"
```

#### 프린터 상태 확인
```
프린터 목록을 보여줘
```

#### 미리보기
```
다음 내용으로 영수증 미리보기를 보여줘: "테스트 출력"
```

### 3. 직접 API 사용

```bash
# 프린터 목록 조회
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://127.0.0.1:8000/printers

# 영수증 출력
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "content": {
         "header": "테스트 영수증",
         "items": [
           {"name": "아메리카노", "quantity": 2, "price": 4500, "total": 9000}
         ],
         "footer": "감사합니다"
       },
       "preview": false
     }' \
     http://127.0.0.1:8000/printers/BIXOLON_SRP_330II/print
```

## 📖 API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🧪 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_printer_utils.py -v

# 커버리지 포함 실행
pytest --cov=. --cov-report=html
```

## 🔒 보안 기능

### API 키 인증
모든 API 엔드포인트는 Bearer 토큰 인증이 필요합니다.

### 프린터 화이트리스트
`config.py`에서 허용된 프린터만 사용 가능합니다:

```python
ALLOWED_PRINTERS = [
    "BIXOLON_SRP_330II",
    "BIXOLON_SRP_330III",
    # 추가 허용 프린터...
]
```

### 입력 검증
Pydantic을 사용한 엄격한 입력 데이터 검증이 적용됩니다.

## 🛠️ 개발 가이드

### 프로젝트 구조

```
receipt-printer/
├── main.py              # 기존 스크립트 (호환성 유지)
├── printer_utils.py     # 핵심 프린터 기능
├── server.py           # FastAPI 서버
├── mcp_wrapper.py      # MCP 프로토콜 래퍼
├── schemas.py          # Pydantic 데이터 모델
├── config.py           # 설정 및 보안
├── requirements.txt    # 의존성 목록
└── tests/              # 테스트 스위트
    ├── test_printer_utils.py
    ├── test_api.py
    └── test_mcp_integration.py
```

### 새 기능 추가

1. **프린터 기능**: `printer_utils.py` 수정
2. **API 엔드포인트**: `server.py`에 새 엔드포인트 추가
3. **데이터 모델**: `schemas.py`에 Pydantic 모델 추가
4. **MCP 도구**: `mcp_wrapper.py`에 새 도구 추가
5. **테스트**: 해당 테스트 파일에 테스트 케이스 추가

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

3. **권한 오류**
   ```bash
   # 사용자를 lpadmin 그룹에 추가
   sudo usermod -a -G lpadmin $USER
   ```

4. **한글 출력 문제**
   - 프린터가 EUC-KR 인코딩을 지원하는지 확인
   - ESC/POS 호환성 확인

### 로그 확인

```bash
# FastAPI 서버 로그
python server.py

# MCP 래퍼 디버그 로그 (stderr)
tail -f /path/to/mcp/logs
```

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
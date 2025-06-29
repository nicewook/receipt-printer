# 📚 BIXOLON Receipt Printer - 문서 센터

## 🌐 웹 인터페이스로 문서 보기

**추천**: 브라우저에서 아래 파일을 열어 네비게이션 가능한 문서 센터를 이용하세요!

```bash
# 웹브라우저에서 열기
open docs/index.html
# 또는
start docs/index.html    # Windows
xdg-open docs/index.html # Linux
```

## 📋 문서 목록

### 🏗️ [시스템 아키텍처 개요](./architecture-overview.md)
- 전체 시스템 구조 분석
- Legacy CLI vs Modern MCP 병렬 시스템
- 데이터 플로우 및 컴포넌트 관계
- Mermaid 다이어그램으로 시각화

### ⚙️ [Core Printer Utils 분석](./core-printer-utils-analysis.md)
- MCP 시스템의 핵심 엔진 (242줄)
- 한국어 텍스트 처리 마스터피스
- 적응형 레이아웃 시스템
- ESC/POS 명령어 생성

### 🖨️ [ESC/POS 명령어 심층분석](./escpos-commands-deep-dive.md)
- BIXOLON 프린터 프로토콜 완전 분석
- FS & → FS . 시퀀스의 비밀
- 한글 모드 설정과 버그 우회
- 이중 정렬 문제 발견 및 해결방안

### 🌐 [FastAPI Server 분석](./fastapi-server-analysis.md)
- MCP 시스템의 백엔드 심장부 (337줄)
- 엔터프라이즈급 보안 체계
- 자체 진단 에러 처리 시스템
- 구조화된 데이터 처리 알고리즘

## 🎯 빠른 탐색

| 관심사 | 추천 문서 |
|--------|-----------|
| **전체 시스템 이해** | → [아키텍처 개요](./architecture-overview.md) |
| **한국어 텍스트 처리** | → [Core Utils](./core-printer-utils-analysis.md) |
| **프린터 프로토콜** | → [ESC/POS 분석](./escpos-commands-deep-dive.md) |
| **API 서버 구조** | → [FastAPI 분석](./fastapi-server-analysis.md) |

## 📊 프로젝트 통계

- **📝 총 분석 문서**: 4개
- **🔍 분석된 코드 라인**: 579줄 (FastAPI 337 + Core Utils 242)
- **🖨️ ESC/POS 명령어**: 7개 상세 분석
- **🌐 API 엔드포인트**: 3개 완전 분석
- **🔒 보안 레이어**: 4층 구조 분석

## 🚀 사용법

### 📖 **일반 읽기**
각 markdown 파일을 직접 열어서 읽으세요.

### 🌐 **웹 인터페이스** (추천)
```bash
# 웹브라우저에서 네비게이션 가능한 문서 센터 열기
open docs/index.html
```

### 🔗 **링크 탐색**
각 문서는 서로 연결되어 있어 관련 내용을 쉽게 찾을 수 있습니다.

---

**💡 팁**: `index.html`로 시작하면 프로젝트 전체를 체계적으로 이해할 수 있습니다!
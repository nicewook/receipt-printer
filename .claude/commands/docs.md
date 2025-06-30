# 문서 인덱스 업데이트 명령어

docs/ 디렉터리의 마크다운 파일들을 스캔하여 index.html을 자동 생성/업데이트합니다.

## 실행할 작업:

$ARGUMENTS가 "all"인 경우:
- docs/ 디렉터리의 모든 .md 파일을 스캔
- index.html을 완전히 새로 생성
- 기존 index.html은 timestamp와 함께 백업

$ARGUMENTS가 비어있거나 다른 값인 경우:
- git status로 변경된 .md 파일 확인
- 변경사항이 있으면 전체 문서를 다시 스캔하여 index.html 업데이트
- 변경사항이 없으면 현재 상태 그대로 index.html 업데이트

## 구체적 실행 단계:

1. **Git 상태 확인** (all이 아닌 경우만):
   - `git status --porcelain`로 변경된 .md 파일 찾기
   - docs/ 디렉터리 내 파일만 필터링

2. **마크다운 파일 스캔**:
   - 각 .md 파일에서 메타데이터 추출:
     - 제목: 첫 번째 # 헤더
     - 설명: 첫 번째 문단 (150자 제한)
     - 태그: 파일명과 내용 기반 자동 생성

3. **카드 데이터 생성**:
   - architecture-overview.md → 🏗️ overview 타입
   - core-printer-utils-analysis.md → ⚙️ core 타입  
   - escpos-commands-deep-dive.md → 🖨️ escpos 타입
   - fastapi-server-analysis.md → 🌐 fastapi 타입
   - mcp-wrapper-analysis.md → 🔗 mcp 타입
   - 기타 파일들 → 📄 default 타입

4. **통계 계산**:
   - 문서 개수: docs/*.md 파일 개수
   - FastAPI 라인: server.py 라인 수
   - 핵심 유틸 라인: printer_utils.py 라인 수  
   - 기타: 하드코딩된 값들 (ESC/POS 명령어: 7개, API 엔드포인트: 3개, 한글:영문 비율: 2:1)

5. **HTML 생성**:
   - 기존 index.html 백업 (timestamp 포함)
   - 새로운 index.html 생성 with:
     - 라이브러리: marked, prismjs@1.29.0, mermaid@10.9.0
     - 반응형 카드 그리드 레이아웃
     - GitHub 스타일 마크다운 렌더링
     - Mermaid 다이어그램 지원
     - 문법 강조 (Python, JavaScript, Bash)
     - 동적 통계 애니메이션
     - SPA 형태의 마크다운 뷰어

6. **결과 보고**:
   - 처리된 문서 수
   - 생성된 카드 수  
   - 백업 파일 경로
   - 브라우저에서 확인할 수 있는 파일 경로

## HTML 구조 가이드:

### 필수 라이브러리 (CDN):
```html
<!-- 마크다운 및 문법 강조 -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-javascript.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-bash.min.js"></script>
<link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">

<!-- Mermaid 다이어그램 -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js"></script>
```

### 카드 스타일 클래스:
- `.doc-card.overview` → 파란색 테두리 (#3498db)
- `.doc-card.core` → 빨간색 테두리 (#e74c3c)  
- `.doc-card.escpos` → 주황색 테두리 (#f39c12)
- `.doc-card.fastapi` → 초록색 테두리 (#2ecc71)
- `.doc-card.mcp` → 보라색 테두리 (#9b59b6)
- `.doc-card.default` → 회색 테두리 (#95a5a6)

### JavaScript 기능:
- SPA 네비게이션 (뒤로가기/앞으로가기 지원)
- 마크다운 → HTML 변환 (marked.js)
- 코드 문법 강조 (Prism.js)
- Mermaid 다이어그램 렌더링
- 통계 숫자 카운터 애니메이션
- 카드 호버 효과

이제 실행해주세요!
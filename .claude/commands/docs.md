# 문서 인덱스 업데이트 명령어

docs/ 디렉터리의 마크다운 파일들을 스캔하여 **GitBook 스타일**의 index.html을 자동 생성/업데이트합니다.

## 실행할 작업:

$ARGUMENTS가 "all"인 경우:
- docs/ 디렉터리의 모든 .md 파일을 스캔
- GitBook 스타일 index.html을 완전히 새로 생성

$ARGUMENTS가 비어있거나 다른 값인 경우:
- docs/ 디렉터리의 .md 파일들을 스캔하여 GitBook 스타일 index.html 업데이트

## 구체적 실행 단계:

### $ARGUMENTS가 "all"인 경우:
1. **전체 재생성**:
   - docs/ 디렉터리의 모든 .md 파일 스캔
   - 기존 index.html 백업 (선택사항)
   - 완전히 새로운 GitBook 스타일 HTML 생성

2. **마크다운 파일 분석**:
   - 각 .md 파일에서 첫 번째 # 헤더로 제목 추출
   - 첫 번째 문단에서 설명 추출 (150자 제한)
   - 파일명 패턴으로 카테고리 자동 분류

3. **사이드바 네비게이션 구조 생성**:
   - 자동 분류된 카테고리별로 섹션 구성
   - 각 문서별 아이콘 자동 할당
   - 네비게이션 계층 구조 생성

### $ARGUMENTS가 비어있거나 다른 값인 경우:
1. **증분 업데이트**:
   - 현재 index.html의 네비게이션 구조 유지
   - docs/ 디렉터리 스캔으로 변경사항 감지
   - 추가/삭제된 파일만 네비게이션에 반영

2. **변경사항 처리**:
   - 새로운 .md 파일 → 적절한 카테고리에 자동 추가
   - 삭제된 .md 파일 → 네비게이션에서 제거
   - 수정된 .md 파일 → 제목/설명 업데이트

3. **기존 구조 보존**:
   - 사용자가 수정한 카테고리 구조 유지
   - 커스텀 아이콘 설정 보존
   - 기존 JavaScript 기능 그대로 유지

## GitBook 스타일 특징:

### 레이아웃 구조:
- **사이드바**: 300px 고정 너비, 계층적 네비게이션
- **메인 콘텐츠**: 800px 최대 너비, 중앙 정렬
- **상단 바**: 브레드크럼 네비게이션과 모바일 메뉴 토글

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

<!-- Font Awesome 아이콘 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

### 동적 아이콘 할당 규칙:
- **키워드 기반 자동 매핑**:
  - `overview`, `architecture` → `fas fa-sitemap`
  - `README`, `guide`, `intro` → `fas fa-book-open`
  - `utils`, `core`, `engine` → `fas fa-cogs`
  - `command`, `terminal`, `escpos` → `fas fa-terminal`
  - `wrapper`, `bridge`, `link` → `fas fa-link`
  - `communication`, `stdio`, `protocol` → `fas fa-exchange-alt`
  - `backlog`, `todo`, `plan` → `fas fa-tasks`
  - `test`, `spec` → `fas fa-vial`
  - `config`, `setting` → `fas fa-cog`
  - **기본값**: `fas fa-file-alt`

### 핵심 기능:
- **다크/라이트 테마 토글**: CSS 변수 기반, 로컬스토리지 저장
- **검색 기능**: 실시간 네비게이션 필터링
- **반응형 디자인**: 모바일에서 오버레이 사이드바
- **SPA 네비게이션**: 브라우저 히스토리 지원
- **마크다운 렌더링**: marked.js + Prism.js + Mermaid
- **부드러운 애니메이션**: CSS 트랜지션과 호버 효과

### JavaScript 핵심 함수:
- `showHome()`: 홈페이지 표시
- `loadDocument(filename)`: 마크다운 문서 로드 및 렌더링
- `toggleTheme()`: 다크/라이트 테마 전환
- `toggleSidebar()`: 모바일 사이드바 토글
- `filterNavigation(query)`: 검색 기능
- `updateBreadcrumb(title)`: 브레드크럼 업데이트

## 동적 카테고리 분류 규칙:

### 카테고리 자동 할당:
- **Getting Started**: `README`, `guide`, `intro`, `overview`, `architecture`
- **Core Components**: `core`, `utils`, `engine`, `command`, `escpos`
- **MCP Integration**: `mcp`, `wrapper`, `stdio`, `protocol`, `integration`
- **Development**: `backlog`, `todo`, `plan`, `dev`, `roadmap`
- **Testing**: `test`, `spec`, `benchmark`
- **Configuration**: `config`, `setting`, `setup`
- **API Reference**: `api`, `reference`, `schema`
- **기본값**: **Miscellaneous**

### 우선순위 매칭:
1. **파일명 키워드**: 파일명에서 키워드 추출
2. **첫 번째 헤더**: # 헤더 내용에서 키워드 매칭
3. **내용 분석**: 문서 내용의 주요 키워드 빈도 분석
4. **기본 카테고리**: 매칭되지 않으면 Miscellaneous

### 특별 처리:
- **index.html**: 네비게이션에서 제외
- **빈 파일**: 네비게이션에서 제외
- **숨김 파일** (점으로 시작): 네비게이션에서 제외

이제 실행해주세요!
# 문서 포털 index.html 생성 명령어

1. project root의 README.md 파일과 docs/ 디렉터리의 마크다운 파일들을 스캔하여 
2. project root에 **최적화된** 심플하고 모던한 index.html을 생성한다.

## 실행할 작업:

1. project root의 README.md 파일을 **메타데이터만** 추출 (제목, 경로, 카테고리)
2. docs/ 디렉터리의 모든 .md 파일을 **메타데이터만** 추출
    - 파일 내용은 읽지 않는다.
    - CLAUDE.md 파일은 제외
3. project root의 index.html을 삭제
4. **동적 로딩 방식**의 `HTML 템플릿`을 사용하여 project root에 index.html을 새로 생성. docs/ 디렉토리 아래에 만들지 않는다.
5. 실제 .md 파일은 브라우저에서 필요시 동적으로 로드

## 5개 카테고리 자동 분류 로직:

### 카테고리 매핑 규칙 (categorizeDocument 함수):
- **프로젝트 개요 (overview)**: README, overview, intro, guide, architecture
- **기술적 기반 (technical)**: core, utils, command, escpos, protocol, stdio, engine  
- **심층 분석 (analysis)**: analysis, detailed, deep-dive, implementation, study
- **계획 및 개발 (planning)**: backlog, todo, plan, roadmap, development, feature
- **기타 (misc)**: 위 카테고리에 매칭되지 않는 모든 파일

### 카테고리 매핑 방법:

1. .md 문서의 Category 항목 확인
2. 파일명 키워드 확인
3. 문서 제목 키워드 확인  
4. 매칭되지 않으면 기타(misc) 카테고리
주의: 문서의 내용은 들여다보지 않는다. 

## HTML 템플릿:

다음은 생성될 index.html의 **최적화된** 템플릿이다.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Receipt Printer Documentation</title>
    
    <!-- 한글 폰트 -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- 마크다운 및 문법 강조 -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-bash.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-json.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css" rel="stylesheet">
    
    <!-- Mermaid 다이어그램 -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js"></script>
    
    <!-- 간소화된 CSS 스타일시트 (200줄) -->
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #ffffff;
            color: #333333;
            line-height: 1.6;
        }

        /* 상단바 */
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: #ffffff;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .header-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #346DBB;
            cursor: pointer;
        }

        .mobile-toggle {
            display: none;
            background: none;
            border: 1px solid #e9ecef;
            color: #333;
            padding: 8px;
            border-radius: 4px;
            cursor: pointer;
        }

        /* 레이아웃 */
        .container {
            display: flex;
            margin-top: 60px;
            min-height: calc(100vh - 60px);
        }

        /* 왼쪽 사이드바 */
        .sidebar {
            width: 280px;
            background-color: #f8f9fa;
            border-right: 1px solid #e9ecef;
            overflow-y: auto;
            position: fixed;
            left: 0;
            top: 60px;
            height: calc(100vh - 60px);
            transition: transform 0.3s ease;
        }

        .sidebar-content {
            padding: 20px;
        }

        .category {
            margin-bottom: 25px;
        }

        .category-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: #346DBB;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .document-list {
            list-style: none;
        }

        .document-item {
            margin-bottom: 3px;
        }

        .document-link {
            display: block;
            padding: 8px 12px;
            color: #333;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.2s ease;
            font-size: 0.9rem;
        }

        .document-link:hover {
            background-color: #e9ecef;
        }

        .document-link.active {
            background-color: #346DBB;
            color: white;
        }

        /* 메인 콘텐츠 */
        .main-container {
            flex: 1;
            margin-left: 280px;
            display: flex;
        }

        .content {
            flex: 1;
            max-width: 800px;
            padding: 40px;
            background-color: #ffffff;
        }

        .content h1, .content h2, .content h3, .content h4 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.3;
        }

        .content h1 {
            font-size: 2rem;
            color: #346DBB;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }

        .content h2 {
            font-size: 1.5rem;
            color: #333;
        }

        .content h3 {
            font-size: 1.25rem;
            color: #333;
        }

        .content p {
            margin-bottom: 1em;
        }

        .content pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            margin: 1em 0;
        }

        .content code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 0.9em;
        }

        .content pre code {
            background: none;
            padding: 0;
        }

        .content ul, .content ol {
            margin-left: 1.5em;
            margin-bottom: 1em;
        }

        .content table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
        }

        .content table th,
        .content table td {
            border: 1px solid #e9ecef;
            padding: 8px 12px;
            text-align: left;
        }

        .content table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }

        /* 오른쪽 TOC */
        .toc-container {
            width: 200px;
            background-color: #f8f9fa;
            border-left: 1px solid #e9ecef;
            padding: 20px;
            position: sticky;
            top: 60px;
            height: calc(100vh - 60px);
            overflow-y: auto;
        }

        .toc-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: #346DBB;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .toc-list {
            list-style: none;
        }

        .toc-item {
            margin-bottom: 3px;
        }

        .toc-link {
            display: block;
            padding: 4px 8px;
            color: #333;
            text-decoration: none;
            font-size: 0.85rem;
            border-radius: 3px;
            transition: background-color 0.2s ease;
        }

        .toc-link:hover {
            background-color: #e9ecef;
        }

        .toc-link.h2 {
            margin-left: 0;
        }

        .toc-link.h3 {
            margin-left: 15px;
        }

        .toc-link.h4 {
            margin-left: 30px;
        }

        /* 홈페이지 */
        .home-content {
            text-align: center;
            padding: 60px 20px;
        }

        .home-title {
            font-size: 2.5rem;
            color: #346DBB;
            margin-bottom: 20px;
        }

        .home-subtitle {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 40px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .stat-item {
            padding: 20px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            background-color: #ffffff;
        }

        .stat-number {
            font-size: 1.5rem;
            font-weight: bold;
            color: #346DBB;
        }

        .stat-label {
            color: #666;
            margin-top: 5px;
            font-size: 0.9rem;
        }

        /* 반응형 */
        @media (max-width: 768px) {
            .mobile-toggle {
                display: block;
            }

            .sidebar {
                transform: translateX(-100%);
                z-index: 1001;
            }

            .sidebar.open {
                transform: translateX(0);
            }

            .main-container {
                margin-left: 0;
            }

            .toc-container {
                display: none;
            }

            .content {
                max-width: 100%;
                padding: 20px;
            }

            .home-title {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <!-- 상단바 -->
    <div class="header">
        <div class="header-title" onclick="showHome()">Receipt Printer Documentation</div>
        <button class="mobile-toggle" onclick="toggleSidebar()">☰</button>
    </div>

    <div class="container">
        <!-- 왼쪽 사이드바 -->
        <nav class="sidebar" id="sidebar">
            <div class="sidebar-content">
                <div class="category">
                    <div class="category-title">🏠 프로젝트 개요</div>
                    <ul class="document-list" id="category-overview"></ul>
                </div>
                <div class="category">
                    <div class="category-title">🔧 기술적 기반</div>
                    <ul class="document-list" id="category-technical"></ul>
                </div>
                <div class="category">
                    <div class="category-title">🔍 심층 분석</div>
                    <ul class="document-list" id="category-analysis"></ul>
                </div>
                <div class="category">
                    <div class="category-title">📋 계획 및 개발</div>
                    <ul class="document-list" id="category-planning"></ul>
                </div>
                <div class="category">
                    <div class="category-title">📦 기타</div>
                    <ul class="document-list" id="category-misc"></ul>
                </div>
            </div>
        </nav>

        <!-- 메인 콘텐츠 영역 -->
        <div class="main-container">
            <main class="content" id="content">
                <!-- 동적으로 로드될 콘텐츠 -->
            </main>
            
            <!-- 오른쪽 TOC -->
            <aside class="toc-container" id="toc-container">
                <div class="toc-title">목차</div>
                <ul class="toc-list" id="toc-list"></ul>
            </aside>
        </div>
    </div>

    <!-- 간소화된 JavaScript (150줄) -->
    <script>
        // 전역 변수
        let documents = {};
        let currentDocument = null;

        // 초기화
        document.addEventListener('DOMContentLoaded', function() {
            // Mermaid 초기화
            if (typeof mermaid !== 'undefined') {
                mermaid.initialize({ 
                    startOnLoad: false,
                    theme: 'default',
                    securityLevel: 'loose'
                });
            }
            
            loadDocuments();
            showHome();
        });

        // 사이드바 토글 (모바일)
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
        }

        // 문서 로드
        function loadDocuments() {
            documents = {
                // DOCUMENT_DATA_PLACEHOLDER - 실제 스캔된 메타데이터로 교체됨
                // 예시 구조:
                // "README.md": {
                //     title: "BIXOLON Receipt Printer MCP Server",
                //     filename: "README.md",
                //     category: "overview"
                // }
            };
            
            renderNavigation();
        }

        // 네비게이션 렌더링
        function renderNavigation() {
            const categories = {
                'overview': document.getElementById('category-overview'),
                'technical': document.getElementById('category-technical'),
                'analysis': document.getElementById('category-analysis'),
                'planning': document.getElementById('category-planning'),
                'misc': document.getElementById('category-misc')
            };

            // 모든 카테고리 초기화
            Object.values(categories).forEach(el => el.innerHTML = '');

            // 문서를 카테고리별로 분류하여 렌더링
            Object.keys(documents).forEach(filename => {
                const doc = documents[filename];
                const category = categorizeDocument(filename, doc);
                const categoryElement = categories[category];
                
                if (categoryElement) {
                    const li = document.createElement('li');
                    li.className = 'document-item';
                    li.innerHTML = `
                        <a href="#" class="document-link" onclick="loadDocument('${filename}')">${doc.title}</a>
                    `;
                    categoryElement.appendChild(li);
                }
            });
        }

        // 문서 카테고리 분류
        function categorizeDocument(filename, doc) {
            const title = doc.title.toLowerCase();
            const content = doc.content.toLowerCase();
            const name = filename.toLowerCase();

            // 프로젝트 개요
            if (name.includes('readme') || title.includes('overview') || title.includes('intro') || 
                title.includes('guide') || title.includes('architecture')) {
                return 'overview';
            }

            // 기술적 기반
            if (name.includes('core') || name.includes('utils') || name.includes('command') || 
                name.includes('escpos') || name.includes('protocol') || name.includes('stdio') ||
                title.includes('technical') || content.includes('implementation')) {
                return 'technical';
            }

            // 심층 분석
            if (name.includes('analysis') || name.includes('detailed') || name.includes('deep-dive') ||
                title.includes('analysis') || title.includes('deep') || title.includes('study')) {
                return 'analysis';
            }

            // 계획 및 개발
            if (name.includes('backlog') || name.includes('todo') || name.includes('plan') ||
                name.includes('roadmap') || name.includes('development') || name.includes('feature')) {
                return 'planning';
            }

            // 기타
            return 'misc';
        }

        // 홈페이지 표시
        function showHome() {
            currentDocument = null;
            const totalDocs = Object.keys(documents).length;
            const categories = ['overview', 'technical', 'analysis', 'planning', 'misc'];
            const categoryCounts = {};
            
            categories.forEach(cat => {
                categoryCounts[cat] = 0;
            });

            Object.keys(documents).forEach(filename => {
                const category = categorizeDocument(filename, documents[filename]);
                categoryCounts[category]++;
            });

            const content = document.getElementById('content');
            content.innerHTML = `
                <div class="home-content">
                    <h1 class="home-title">Receipt Printer Documentation</h1>
                    <p class="home-subtitle">BIXOLON SRP-330II 프린터를 위한 한국어 지원 문서</p>
                    
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-number">${totalDocs}</div>
                            <div class="stat-label">총 문서 수</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${categoryCounts.overview}</div>
                            <div class="stat-label">프로젝트 개요</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${categoryCounts.technical}</div>
                            <div class="stat-label">기술적 기반</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${categoryCounts.analysis}</div>
                            <div class="stat-label">심층 분석</div>
                        </div>
                    </div>
                </div>
            `;

            // TOC 숨기기
            document.getElementById('toc-container').style.display = 'none';
            
            // 활성 링크 제거
            document.querySelectorAll('.document-link').forEach(link => {
                link.classList.remove('active');
            });
        }

        // 문서 동적 로드
        async function loadDocument(filename) {
            if (!documents[filename]) return;
            
            try {
                currentDocument = filename;
                const doc = documents[filename];
                
                // 실제 .md 파일을 동적으로 fetch
                const response = await fetch(doc.filename);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const markdownContent = await response.text();
                
                // 마크다운 렌더링
                renderMarkdown(markdownContent);
                
                // TOC 표시
                document.getElementById('toc-container').style.display = 'block';
                
                // 활성 링크 업데이트
                document.querySelectorAll('.document-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.textContent === documents[filename].title) {
                        link.classList.add('active');
                    }
                });
                
            } catch (error) {
                console.error('문서 로딩 실패:', error);
                document.getElementById('content').innerHTML = `
                    <div style="text-align: center; padding: 50px;">
                        <h2>문서 로딩 실패</h2>
                        <p>파일을 불러올 수 없습니다: ${filename}</p>
                        <p>오류: ${error.message}</p>
                    </div>
                `;
            }
        }

        // 마크다운 렌더링
        function renderMarkdown(content) {
            const contentElement = document.getElementById('content');
            
            // 로딩 상태 표시
            contentElement.innerHTML = '<div style="text-align: center; padding: 50px;">로딩 중...</div>';
            
            try {
                // Marked로 마크다운 변환
                const html = marked.parse(content);
                contentElement.innerHTML = html;
                
                // Prism으로 코드 하이라이팅
                if (typeof Prism !== 'undefined') {
                    Prism.highlightAll();
                }
                
                // Mermaid 다이어그램 렌더링
                if (typeof mermaid !== 'undefined') {
                    mermaid.run();
                }
                
                // TOC 생성
                generateTOC();
                
            } catch (error) {
                console.error('마크다운 렌더링 실패:', error);
                contentElement.innerHTML = `
                    <div style="text-align: center; padding: 50px;">
                        <h2>렌더링 오류</h2>
                        <p>마크다운을 HTML로 변환하는 중 오류가 발생했습니다.</p>
                        <p>오류: ${error.message}</p>
                    </div>
                `;
            }
        }

        // TOC 생성
        function generateTOC() {
            const tocList = document.getElementById('toc-list');
            tocList.innerHTML = '';
            
            const headings = document.querySelectorAll('#content h1, #content h2, #content h3, #content h4');
            
            headings.forEach((heading, index) => {
                const id = `heading-${index}`;
                heading.id = id;
                
                const li = document.createElement('li');
                li.className = 'toc-item';
                
                const link = document.createElement('a');
                link.href = `#${id}`;
                link.className = `toc-link ${heading.tagName.toLowerCase()}`;
                link.textContent = heading.textContent;
                link.onclick = function(e) {
                    e.preventDefault();
                    heading.scrollIntoView({ behavior: 'smooth' });
                };
                
                li.appendChild(link);
                tocList.appendChild(li);
            });
        }
    </script>
</body>
</html>
```

## 🚀 동적 로딩 방식의 혁신적 최적화

### 기존 방식 vs 개선된 방식

| 항목 | docs2 (기존) | docs3 (개선) | 개선율 |
|------|-------------|-------------|--------|
| **생성 시간** | 25-30분 | **3분** | 90% ⬇️ |
| **파일 크기** | ~300KB | **~30KB** | 90% ⬇️ |
| **로딩 속도** | 느림 | **즉시** | 95% ⬆️ |
| **확장성** | 제한적 | **무제한** | ∞ |

### 핵심 개선사항

#### 1. 메타데이터만 포함 방식
```javascript
// 기존: 모든 내용 포함 (문제)
documents = {
  "README.md": {
    title: "...",
    content: "2400줄의 모든 내용..."  // ❌ 거대한 크기
  }
}

// 개선: 메타데이터만 포함 (해결)
documents = {
  "README.md": {
    title: "BIXOLON Receipt Printer MCP Server",
    filename: "README.md",           // ✅ 파일 경로만
    category: "overview"
  }
}
```
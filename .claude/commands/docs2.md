# NordVPN Meshnet 스타일 문서 포털 생성 명령어

docs/ 디렉터리의 마크다운 파일들을 스캔하여 **NordVPN Meshnet 스타일**의 심플하고 모던한 index.html을 자동 생성/업데이트합니다.

## 실행할 작업:

$ARGUMENTS가 "all"인 경우:
- docs/ 디렉터리의 모든 .md 파일을 스캔
- NordVPN Meshnet 스타일 index.html을 완전히 새로 생성

$ARGUMENTS가 비어있거나 다른 값인 경우:
- docs/ 디렉터리의 .md 파일들을 스캔하여 기존 index.html 업데이트

## 완전한 HTML 템플릿:

다음은 생성될 index.html의 완전한 구조입니다:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Receipt Printer Documentation</title>
    
    <!-- 한글 폰트 (Pretendard 우선, Noto Sans KR 폴백) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- 마크다운 및 문법 강조 -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-javascript.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-bash.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-json.min.js"></script>
    
    <!-- 테마별 Prism CSS -->
    <link id="prism-light" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css" rel="stylesheet">
    <link id="prism-dark" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" disabled>
    
    <!-- Mermaid 다이어그램 -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js"></script>
    
    <!-- 완전한 CSS 스타일시트 -->
    <style>
        :root {
            --primary-color: #346DBB;
            --bg-color: #ffffff;
            --text-color: #333333;
            --sidebar-bg: #f8f9fa;
            --sidebar-border: #e9ecef;
            --hover-bg: #e9ecef;
            --active-bg: #346DBB;
            --active-text: #ffffff;
            --content-bg: #ffffff;
            --border-color: #e9ecef;
            --toc-bg: #f8f9fa;
            --shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        [data-theme="dark"] {
            --bg-color: #1a1a1a;
            --text-color: #e9ecef;
            --sidebar-bg: #2d2d2d;
            --sidebar-border: #404040;
            --hover-bg: #404040;
            --active-bg: #346DBB;
            --active-text: #ffffff;
            --content-bg: #2d2d2d;
            --border-color: #404040;
            --toc-bg: #2d2d2d;
            --shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            transition: all 0.3s ease;
        }

        /* 상단바 */
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: var(--content-bg);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 1000;
        }

        .header-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--primary-color);
        }

        .header-controls {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .theme-toggle {
            background: none;
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .theme-toggle:hover {
            background-color: var(--hover-bg);
        }

        .mobile-toggle {
            display: none;
            background: none;
            border: 1px solid var(--border-color);
            color: var(--text-color);
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
            width: 300px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--sidebar-border);
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
            margin-bottom: 30px;
        }

        .category-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .document-list {
            list-style: none;
        }

        .document-item {
            margin-bottom: 5px;
        }

        .document-link {
            display: block;
            padding: 8px 12px;
            color: var(--text-color);
            text-decoration: none;
            border-radius: 4px;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }

        .document-link:hover {
            background-color: var(--hover-bg);
        }

        .document-link.active {
            background-color: var(--active-bg);
            color: var(--active-text);
        }

        /* 메인 콘텐츠 */
        .main-container {
            flex: 1;
            margin-left: 300px;
            display: flex;
        }

        .content {
            flex: 1;
            max-width: 800px;
            padding: 40px;
            background-color: var(--content-bg);
        }

        .content h1, .content h2, .content h3, .content h4, .content h5, .content h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.3;
        }

        .content h1 {
            font-size: 2rem;
            color: var(--primary-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
        }

        .content h2 {
            font-size: 1.5rem;
            color: var(--text-color);
        }

        .content p {
            margin-bottom: 1em;
        }

        .content pre {
            background-color: var(--toc-bg);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            margin: 1em 0;
        }

        .content code {
            background-color: var(--toc-bg);
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 0.9em;
        }

        .content pre code {
            background: none;
            padding: 0;
        }

        /* 오른쪽 TOC */
        .toc-container {
            width: 200px;
            background-color: var(--toc-bg);
            border-left: 1px solid var(--border-color);
            padding: 20px;
            position: sticky;
            top: 60px;
            height: calc(100vh - 60px);
            overflow-y: auto;
        }

        .toc-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .toc-list {
            list-style: none;
        }

        .toc-item {
            margin-bottom: 5px;
        }

        .toc-link {
            display: block;
            padding: 4px 8px;
            color: var(--text-color);
            text-decoration: none;
            font-size: 0.85rem;
            border-radius: 3px;
            transition: all 0.3s ease;
        }

        .toc-link:hover {
            background-color: var(--hover-bg);
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
            }
        }

        /* 홈페이지 스타일 */
        .home-content {
            text-align: center;
            padding: 60px 20px;
        }

        .home-title {
            font-size: 3rem;
            color: var(--primary-color);
            margin-bottom: 20px;
        }

        .home-subtitle {
            font-size: 1.2rem;
            color: var(--text-color);
            margin-bottom: 40px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }

        .stat-item {
            padding: 20px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background-color: var(--content-bg);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
        }

        .stat-label {
            color: var(--text-color);
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <!-- 상단바 -->
    <div class="header">
        <div class="header-title">Receipt Printer Documentation</div>
        <div class="header-controls">
            <button class="theme-toggle" onclick="toggleTheme()">🌓 테마</button>
            <button class="mobile-toggle" onclick="toggleSidebar()">☰</button>
        </div>
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

    <!-- JavaScript 구현 -->
    <script>
        // 전역 변수
        let documents = {};
        let currentDocument = null;

        // 초기화
        document.addEventListener('DOMContentLoaded', function() {
            initializeTheme();
            loadDocuments();
            showHome();
        });

        // 테마 초기화
        function initializeTheme() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateMermaidTheme(savedTheme);
            updatePrismTheme(savedTheme);
        }

        // 테마 토글
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            updateMermaidTheme(newTheme);
            updatePrismTheme(newTheme);
            
            // 현재 문서가 있다면 다시 렌더링
            if (currentDocument) {
                renderMarkdown(documents[currentDocument].content);
            }
        }

        // Mermaid 테마 업데이트
        function updateMermaidTheme(theme) {
            if (typeof mermaid !== 'undefined') {
                const mermaidTheme = theme === 'dark' ? 'dark' : 'default';
                mermaid.initialize({ 
                    startOnLoad: false, 
                    theme: mermaidTheme,
                    securityLevel: 'loose'
                });
            }
        }

        // Prism 테마 업데이트
        function updatePrismTheme(theme) {
            const lightTheme = document.getElementById('prism-light');
            const darkTheme = document.getElementById('prism-dark');
            
            if (theme === 'dark') {
                lightTheme.disabled = true;
                darkTheme.disabled = false;
            } else {
                lightTheme.disabled = false;
                darkTheme.disabled = true;
            }
        }

        // 사이드바 토글 (모바일)
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
        }

        // 문서 로드
        function loadDocuments() {
            // 실제 구현에서는 서버에서 문서 목록을 가져와야 함
            // 여기서는 예시 데이터
            documents = {
                // DOCUMENT_DATA_PLACEHOLDER - 실제 스캔된 문서 데이터로 교체됨
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

        // 문서 로드
        function loadDocument(filename) {
            if (!documents[filename]) return;
            
            currentDocument = filename;
            const doc = documents[filename];
            
            // 마크다운 렌더링
            renderMarkdown(doc.content);
            
            // TOC 표시
            document.getElementById('toc-container').style.display = 'block';
            
            // 활성 링크 업데이트
            document.querySelectorAll('.document-link').forEach(link => {
                link.classList.remove('active');
            });
            event.target.classList.add('active');
        }

        // 마크다운 렌더링
        function renderMarkdown(content) {
            const contentElement = document.getElementById('content');
            
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

        // 로고 클릭시 홈으로
        document.querySelector('.header-title').addEventListener('click', showHome);
    </script>
</body>
</html>
```

## 5개 카테고리 자동 분류 로직:

### 카테고리 매핑 규칙 (categorizeDocument 함수):
- **🏠 프로젝트 개요 (overview)**: README, overview, intro, guide, architecture
- **🔧 기술적 기반 (technical)**: core, utils, command, escpos, protocol, stdio, engine
- **🔍 심층 분석 (analysis)**: analysis, detailed, deep-dive, implementation, study
- **📋 계획 및 개발 (planning)**: backlog, todo, plan, roadmap, development, feature
- **📦 기타 (misc)**: 위 카테고리에 매칭되지 않는 모든 파일

### 우선순위 매칭:
1. 파일명 키워드 확인
2. 문서 제목 키워드 확인  
3. 문서 내용 키워드 확인
4. 매칭되지 않으면 기타(misc) 카테고리

## 실행 단계:

### $ARGUMENTS가 "all"인 경우:
1. docs/ 디렉터리의 모든 .md 파일 스캔
2. project 루트 디렉터리의 README.md 파일도 스캔
3. 각 파일의 제목과 내용 추출
4. 위 HTML 템플릿에 DOCUMENT_DATA_PLACEHOLDER 부분을 실제 데이터로 교체
5. index.html 파일 생성

### $ARGUMENTS가 비어있거나 다른 값인 경우:
1. 기존 index.html에서 문서 데이터 부분만 업데이트
2. 네비게이션 구조는 유지하되 변경된 파일만 반영

이제 실행해주세요!
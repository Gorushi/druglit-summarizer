document.addEventListener('DOMContentLoaded', () => {

    // HTML 요소 선택
    const drugInput = document.getElementById('drug-input');
    const searchButton = document.getElementById('search-button');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    const recentSearchesContainer = document.getElementById('recent-searches');
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const themeIcon = document.getElementById('theme-icon');
    const themeModeText = document.getElementById('theme-mode-text');
    const exportContainer = document.getElementById('export-container'); 
    const exportPdfBtn = document.getElementById('export-pdf-btn');
    const API_BASE_URL = 'http://127.0.0.1:8080';

    // 화면 갱신을 기다리는 Promise 기반 헬퍼 함수
    function waitForRepaint() {
        // requestAnimationFrame을 두 번 호출하여 스타일 변경이 확실히 적용되도록 보장
        return new Promise(resolve => {
            requestAnimationFrame(() => {
                requestAnimationFrame(resolve);
            });
        });
    }

    // --- 사이드바 토글 기능 ---
    function toggleSidebar() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }
    menuToggle.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);

    // --- 다크 모드 기능 ---
    function updateThemeUI() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        if (isDarkMode) {
            themeIcon.textContent = '🌙';
            themeModeText.textContent = 'Dark Mode';
        } else {
            themeIcon.textContent = '☀️';
            themeModeText.textContent = 'Light Mode';
        }
    }

    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
    }
    updateThemeUI();

    themeToggleButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        updateThemeUI();
    });

    // --- 이벤트 리스너 설정 ---
    displayRecentSearches();
    searchButton.addEventListener('click', handleSearch);
    drugInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') handleSearch();
    });

    // PDF 저장 버튼 로직 (화면 갱신 대기 기능 포함)
    exportPdfBtn.addEventListener('click', async () => {
        const isDarkMode = document.body.classList.contains('dark-mode');

        try {
            if (isDarkMode) {
                document.body.classList.remove('dark-mode');
                // 스타일 변경이 화면에 완전히 반영될 때까지 대기
                await waitForRepaint(); 
            }
            
            // preload를 통해 노출된 API 호출
            await window.electronAPI.printToPDF();

        } catch (error) {
            console.error("PDF 생성 중 오류가 발생했습니다:", error);
        } finally {
            // PDF 저장 후에는 대기 없이 즉시 원래 테마로 복구
            if (isDarkMode) {
                document.body.classList.add('dark-mode');
            }
        }
    });

    // --- 검색 처리 함수 ---
    async function handleSearch() {
        if (sidebar.classList.contains('open')) toggleSidebar();
        const drugName = drugInput.value.trim();
        if (!drugName) {
            resultsContainer.innerHTML = `<p class="error">약물 이름을 입력해주세요.</p>`;
            return;
        }
        saveSearchTerm(drugName);
        performSearch(drugName);
    }

    async function performSearch(drugName) {
        resultsContainer.innerHTML = '';
        loadingIndicator.style.display = 'block';
        exportContainer.style.display = 'none';

        try {
            const response = await fetch(`${API_BASE_URL}/search?drug=${encodeURIComponent(drugName)}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `서버 에러: ${response.status}`);
            }
            const data = await response.json();
            displayResults(data);
        } catch (error) {
            console.error('Error fetching search results:', error);
            resultsContainer.innerHTML = `<p class="error">오류가 발생했습니다: ${error.message}</p>`;
            exportContainer.style.display = 'none';
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    // --- 결과 표시 함수 ---
    function displayResults(data) {
        resultsContainer.innerHTML = '';
        const resultHeader = document.createElement('h2');
        resultHeader.textContent = `'${data.drug}' 검색 결과`;
        resultsContainer.appendChild(resultHeader);

        if (!data.papers || data.papers.length === 0) {
            resultsContainer.innerHTML += '<p>해당 약물에 대한 논문 요약 정보를 찾을 수 없습니다.</p>';
            exportContainer.style.display = 'none';
            return;
        }
        
        exportContainer.style.display = 'block';

        data.papers.forEach(paper => {
            const card = document.createElement('div');
            card.className = 'paper-card';
            const title = paper.title || '제목 없음';
            const pubmedLink = `https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`;
            const pubdate = paper.pubdate || '날짜 정보 없음';
            const summary = paper.summary || '요약 정보가 없습니다.';
            card.innerHTML = `
                <h3><a href="${pubmedLink}" target="_blank" rel="noopener noreferrer">${title}</a></h3>
                <div class="meta"><span><strong>PMID:</strong> ${paper.pmid}</span> | <span><strong>게시일:</strong> ${pubdate}</span></div>
                <p>${summary}</p>
            `;
            resultsContainer.appendChild(card);
        });
    }

    // --- 최근 검색어 관련 함수 ---
    function saveSearchTerm(term) {
        let recentSearches = JSON.parse(localStorage.getItem('recentSearches')) || [];
        recentSearches = recentSearches.filter(item => item.toLowerCase() !== term.toLowerCase());
        recentSearches.unshift(term);
        localStorage.setItem('recentSearches', JSON.stringify(recentSearches.slice(0, 3)));
        displayRecentSearches();
    }

    function displayRecentSearches() {
        const recentSearches = JSON.parse(localStorage.getItem('recentSearches')) || [];
        recentSearchesContainer.innerHTML = '<h3>최근 검색어</h3>';
        if (recentSearches.length > 0) {
            const ul = document.createElement('ul');
            recentSearches.forEach(term => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '#';
                a.textContent = term;
                a.addEventListener('click', (e) => {
                    e.preventDefault();
                    drugInput.value = term;
                    handleSearch();
                });
                li.appendChild(a);
                ul.appendChild(li);
            });
            recentSearchesContainer.appendChild(ul);
        } else {
            recentSearchesContainer.innerHTML += '<p>검색 기록이 없습니다.</p>';
        }
    }
});

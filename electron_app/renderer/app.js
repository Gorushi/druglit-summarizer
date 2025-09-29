document.addEventListener('DOMContentLoaded', () => {

    // HTML에서 필요한 요소들을 가져옴
    const drugInput = document.getElementById('drug-input');
    const searchButton = document.getElementById('search-button');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    const recentSearchesContainer = document.getElementById('recent-searches');
    const themeToggle = document.getElementById('checkbox');

    // --- 신규: 사이드바 관련 요소 ---
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    // FastAPI 서버 주소
    const API_BASE_URL = 'http://127.0.0.1:8080';

    // --- 신규: 사이드바 토글 기능 ---
    function toggleSidebar() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }

    menuToggle.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);

    // --- 다크 모드 기능 구현 ---

    // 1. 페이지 로드 시, localStorage에 저장된 테마 설정을 확인하고 적용
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.checked = true; // 토글 스위치 상태를 동기화
    }

    // 2. 토글 스위치를 클릭할 때마다 테마를 변경하고 선택을 저장
    themeToggle.addEventListener('change', () => {
        if (themeToggle.checked) {
            // 다크 모드로 변경
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            // 라이트 모드로 변경
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });
    
    // --- 기존 검색 기능 ---

    // 페이지가 로드되면 제일 먼저 최근 검색어 목록을 화면에 표시
    displayRecentSearches();

    // '논문 요약 검색' 버튼 클릭 시 handleSearch 함수를 실행
    searchButton.addEventListener('click', handleSearch);

    // Enter 키를 눌러도 검색이 되도록 설정
    drugInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    });

    /**
     * 검색 버튼을 누르거나 Enter 키를 입력했을 때 실행되는 메인 함수
     */
    async function handleSearch() {
        // 검색 실행 시 사이드바가 열려있으면 닫기
        if (sidebar.classList.contains('open')) {
            toggleSidebar();
        }

        const drugName = drugInput.value.trim();

        if (!drugName) {
            resultsContainer.innerHTML = `<p class="error">약물 이름을 입력해주세요.</p>`;
            return;
        }

        saveSearchTerm(drugName);
        performSearch(drugName);
    }

    /**
     * 검색어를 기반으로 실제 논문 검색 및 요약 로직을 수행하는 함수
     * @param {string} drugName - 검색할 약물 이름
     */
    async function performSearch(drugName) {
        resultsContainer.innerHTML = '';
        loadingIndicator.style.display = 'block';

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
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    /**
     * API로부터 받은 결과를 화면에 표시하는 함수
     * @param {object} data - 서버로부터 받은 JSON 데이터
     */
    function displayResults(data) {
        resultsContainer.innerHTML = '';

        const resultHeader = document.createElement('h2');
        resultHeader.textContent = `'${data.drug}' 검색 결과`;
        resultsContainer.appendChild(resultHeader);

        if (!data.papers || data.papers.length === 0) {
            resultsContainer.innerHTML += '<p>해당 약물에 대한 논문 요약 정보를 찾을 수 없습니다.</p>';
            return;
        }

        data.papers.forEach(paper => {
            const card = document.createElement('div');
            card.className = 'paper-card';

            const title = paper.title || '제목 없음';
            const pubmedLink = `https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`;
            const pubdate = paper.pubdate || '날짜 정보 없음';
            const summary = paper.summary || '요약 정보가 없습니다.';

            card.innerHTML = `
                <h3><a href="${pubmedLink}" target="_blank" rel="noopener noreferrer">${title}</a></h3>
                <div class="meta">
                    <span><strong>PMID:</strong> ${paper.pmid}</span> |
                    <span><strong>게시일:</strong> ${pubdate}</span>
                </div>
                <p>${summary}</p>
            `;
            resultsContainer.appendChild(card);
        });
    }

    /**
     * 검색어를 로컬 스토리지에 저장하는 함수
     * @param {string} term - 저장할 검색어
     */
    function saveSearchTerm(term) {
        let recentSearches = JSON.parse(localStorage.getItem('recentSearches')) || [];
        
        recentSearches = recentSearches.filter(item => item.toLowerCase() !== term.toLowerCase());
        
        recentSearches.unshift(term);
        
        const limitedSearches = recentSearches.slice(0, 3);
        
        localStorage.setItem('recentSearches', JSON.stringify(limitedSearches));
        
        displayRecentSearches();
    }

    /**
     * 로컬 스토리지의 검색어 목록을 가져와 화면에 표시하는 함수
     */
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
                    handleSearch(); // 검색 실행
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

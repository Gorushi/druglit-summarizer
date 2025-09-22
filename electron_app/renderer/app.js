// 페이지의 모든 HTML 요소가 로드된 후에 스크립트를 실행
document.addEventListener('DOMContentLoaded', () => {

    // HTML에서 필요한 요소들을 가져옴
    const drugInput = document.getElementById('drug-input');
    const searchButton = document.getElementById('search-button');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    const recentSearchesContainer = document.getElementById('recent-searches');

    // FastAPI 서버 주소
    const API_BASE_URL = 'http://127.0.0.1:8000';

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
        const drugName = drugInput.value.trim(); // 입력값의 양쪽 공백 제거

        if (!drugName) {
            alert('약물 이름을 입력해주세요.');
            return; // 함수 종료
        }

        // 1. 사용자가 입력한 검색어를 저장
        saveSearchTerm(drugName);
        
        // 2. 실제 검색 및 요약 로직을 실행
        performSearch(drugName);
    }

    /**
     * 검색어를 기반으로 실제 논문 검색 및 요약 로직을 수행하는 함수
     * @param {string} drugName - 검색할 약물 이름
     */
    async function performSearch(drugName) {
        // 검색 시작 전, 이전 결과 초기화 및 로딩 표시
        resultsContainer.innerHTML = '';
        loadingIndicator.style.display = 'block';

        try {
            // FastAPI 서버에 검색 요청
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
            // 성공/실패 여부와 관계없이 로딩 숨기기
            loadingIndicator.style.display = 'none';
        }
    }

    /**
     * API로부터 받은 결과를 화면에 표시하는 함수
     * @param {object} data - 서버로부터 받은 JSON 데이터
     */
    function displayResults(data) {
        resultsContainer.innerHTML = ''; // 컨테이너 초기화

        const resultHeader = document.createElement('h2');
        resultHeader.textContent = `'${data.drug}' 검색 결과`;
        resultsContainer.appendChild(resultHeader);

        if (!data.papers || data.papers.length === 0) {
            resultsContainer.innerHTML += '<p>해당 약물에 대한 논문 요약 정보를 찾을 수 없습니다.</p>';
            return;
        }

        // 각 논문 정보를 카드로 만들어 추가
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
        // 1. 로컬 스토리지에서 기존 목록을 가져옴 (없으면 빈 배열로 시작)
        let recentSearches = JSON.parse(localStorage.getItem('recentSearches')) || [];
        
        // 2. 현재 검색어가 목록에 이미 있다면, 기존 항목을 제거
        recentSearches = recentSearches.filter(item => item.toLowerCase() !== term.toLowerCase());
        
        // 3. 새로운 검색어를 목록의 맨 앞에 추가
        recentSearches.unshift(term);
        
        // 4. 목록의 길이를 3개로 제한
        const limitedSearches = recentSearches.slice(0, 3);
        
        // 5. 업데이트된 목록을 다시 로컬 스토리지에 저장
        localStorage.setItem('recentSearches', JSON.stringify(limitedSearches));
        
        // 6. 화면의 최근 검색어 목록을 즉시 갱신
        displayRecentSearches();
    }

    /**
     * 로컬 스토리지의 검색어 목록을 가져와 화면에 표시하는 함수
     */
    function displayRecentSearches() {
        const recentSearches = JSON.parse(localStorage.getItem('recentSearches')) || [];
        
        // 항상 제목을 먼저 표시
        recentSearchesContainer.innerHTML = '<h3>최근 검색어</h3>';

        if (recentSearches.length > 0) {
            const ul = document.createElement('ul');
            recentSearches.forEach(term => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '#';
                a.textContent = term;
                
                // 각 검색어를 클릭했을 때의 동작 설정
                a.addEventListener('click', (e) => {
                    e.preventDefault(); // 링크의 기본 동작(페이지 이동) 방지
                    drugInput.value = term; // 검색창에 해당 단어 입력
                    handleSearch(); // 바로 검색 실행
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

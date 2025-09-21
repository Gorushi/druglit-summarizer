document.addEventListener('DOMContentLoaded', () => {
    // DOM 요소 가져오기
    const drugInput = document.getElementById('drug-input');
    const searchButton = document.getElementById('search-button');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');

    const API_BASE_URL = 'http://127.0.0.1:8000';

    // 검색 버튼 클릭 이벤트 처리
    searchButton.addEventListener('click', handleSearch);

    // 엔터 키로 검색 실행
    drugInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    });

    async function handleSearch() {
        const drugName = drugInput.value.trim();

        if (!drugName) {
            alert('약물 이름을 입력해주세요.');
            return;
        }

        // 이전 결과 초기화 및 로딩 표시
        resultsContainer.innerHTML = '';
        loadingIndicator.style.display = 'block';

        try {
            // FastAPI 서버에 검색 요청 (변경된 엔드포인트와 파라미터 사용)
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
});


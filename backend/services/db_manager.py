import sqlite3
from pathlib import Path

DB_PATH = Path("papers.db")

def _get_conn():
    """DB 연결 객체를 반환."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """DB를 초기화하고, 필요 시 테이블과 인덱스를 생성."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                pmid TEXT PRIMARY KEY,
                drug TEXT,
                title TEXT,
                abstract TEXT,
                summary TEXT,
                pubdate TEXT
            )
        """)
        # 대소문자 무시 검색을 위한 인덱스 생성
        conn.execute("CREATE INDEX IF NOT EXISTS idx_drug ON papers(LOWER(drug))")

def get_paper(pmid: str):
    """PMID로 특정 논문 한 개를 가져옴."""
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM papers WHERE pmid=?", (pmid,)).fetchone()
        return dict(row) if row else None

def save_paper(paper: dict):
    """논문 정보를 DB에 저장하거나 갱신 (INSERT OR REPLACE)."""
    with _get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO papers (pmid, drug, title, abstract, summary, pubdate)
            VALUES (:pmid, :drug, :title, :abstract, :summary, :pubdate)
        """, paper)

def get_papers_by_pmids(pmid_list: list[str]):
    """pmid 리스트를 받아 존재하는 논문들을 한 번의 쿼리로 조회"""
    if not pmid_list:
        return {}
    
    # (?,?,?) 형태의 플레이스홀더 문자열 생성
    placeholders = ','.join('?' for _ in pmid_list)
    query = f"SELECT * FROM papers WHERE pmid IN ({placeholders})"
    
    with _get_conn() as conn:
        rows = conn.execute(query, pmid_list).fetchall()
        # pmid를 key로 하는 딕셔너리로 변환하여 반환 (빠른 조회를 위해)
        return {dict(row)['pmid']: dict(row) for row in rows}

def get_papers_by_drug(drug: str):
    """특정 약물에 대한 논문들을 최신순으로 15개 가져옴 (대소문자 무시)."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM papers WHERE LOWER(drug) = LOWER(?) ORDER BY pubdate DESC LIMIT 15",
            (drug,)
        ).fetchall()
        return [dict(row) for row in rows]


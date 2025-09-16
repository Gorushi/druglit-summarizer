import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search_pubmed(query: str, retmax: int = 20):
    """
    PubMed에서 PMID 리스트 검색
    """
    url = f"{BASE_URL}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "sort": "date",
        "retmode": "json",
        "retmax": retmax
    }
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return []
    data = r.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_pubmed_abstract(pmid: str):
    """
    PubMed에서 논문 상세정보 가져오기 (title, abstract, pubdate)
    pubdate는 Year, Month, Day → 없으면 MedlineDate 사용
    abstract 없는 논문은 None 반환 (필터링)
    """
    url = f"{BASE_URL}/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return None

    root = ET.fromstring(r.text)
    article = root.find(".//PubmedArticle")
    if article is None:
        return None

    title = article.findtext(".//ArticleTitle", default="").strip()

    # Abstract
    abstract_parts = [a.text.strip() for a in article.findall(".//AbstractText") if a.text]
    abstract = " ".join(abstract_parts)
    if not abstract:
        return None  # abstract 없는 논문은 스킵

    # PubDate (Year, Month, Day 조합)
    pub_date = article.find(".//PubDate")
    pubdate_str = "1900"
    if pub_date is not None:
        year = pub_date.findtext("Year")
        month = pub_date.findtext("Month")
        day = pub_date.findtext("Day")
        if year:
            parts = [year]
            if month:
                parts.append(month)
            if day:
                parts.append(day)
            pubdate_str = " ".join(parts)
        else:
            # Year가 없을 경우 MedlineDate 시도
            medline_date = pub_date.findtext("MedlineDate")
            if medline_date:
                pubdate_str = medline_date

    return {"title": title, "abstract": abstract, "pubdate": pubdate_str}


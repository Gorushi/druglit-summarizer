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

    title = article.findtext(".//ArticleTitle", default="")
    abstract = " ".join(
        [a.text for a in article.findall(".//AbstractText") if a.text]
    )
    pubdate = article.findtext(".//PubDate/Year", default="1900")

    return {"title": title, "abstract": abstract, "pubdate": pubdate}


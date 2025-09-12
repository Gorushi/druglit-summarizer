import requests
from xml.etree import ElementTree

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def fetch_pubmed_articles(drug_name: str, max_results: int = 15):
    # Step 1: PMID 검색
    search_url = f"{BASE_URL}esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": drug_name,
        "retmax": max_results,
        "retmode": "json"
    }
    search_resp = requests.get(search_url, params=params)
    id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return []

    # Step 2: PMID로 상세 정보 가져오기
    fetch_url = f"{BASE_URL}efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }
    fetch_resp = requests.get(fetch_url, params=params)

    # XML 파싱
    root = ElementTree.fromstring(fetch_resp.content)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        abstract = " ".join([abst.text for abst in article.findall(".//AbstractText") if abst.text])

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract
        })

    return articles


import requests
from bs4 import BeautifulSoup

BASE_URL = "https://xsw.gachon.ac.kr/cms/"
SOURCE = "SW중심대학"
EMOJI = "💻"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GachonNotifyBot/1.0)"
}


def fetch():
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[{SOURCE}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    # 워드프레스 기반 — 최신 글 목록 셀렉터 (실제 사이트 구조에 맞게 조정)
    for a_tag in soup.select("article h2 a, .entry-title a, .post-title a"):
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        if not href:
            continue
        uid = href

        items.append({
            "id": uid,
            "title": title,
            "url": href,
            "date": "",
            "source": SOURCE,
            "emoji": EMOJI,
        })

    return items

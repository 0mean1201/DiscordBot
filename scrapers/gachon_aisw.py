import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.gachon.ac.kr/sites/aisw/index.do"
PARAMS = {"fnctId": "recentBbs", "fnctNo": "447"}
SOURCE = "AI학과공지"
EMOJI = "🤖"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GachonNotifyBot/1.0)"
}


def fetch():
    try:
        resp = requests.get(BASE_URL, params=PARAMS, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[{SOURCE}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    # 학과 사이트의 최근 게시글 위젯 구조 — 실제 셀렉터는 사이트 확인 후 조정 필요
    for a_tag in soup.select(".bbs-latest-list li a, .recent-board li a"):
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = "https://www.gachon.ac.kr" + href
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

from bs4 import BeautifulSoup
from .utils import get

BASE_URL = "https://www.gachon.ac.kr/sites/aisw/index.do"
PARAMS = {"fnctId": "recentBbs", "fnctNo": "447"}
SOURCE = "AI학과공지"
EMOJI = "🤖"


def fetch():
    try:
        resp = get(BASE_URL, params=PARAMS)
        resp.raise_for_status()
    except Exception as e:
        print(f"[{SOURCE}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    for a_tag in soup.select(".bbs-latest-list li a, .recent-board li a"):
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = "https://www.gachon.ac.kr" + href
        uid = href

        items.append({"id": uid, "title": title, "url": href, "date": "", "source": SOURCE, "emoji": EMOJI})

    return items

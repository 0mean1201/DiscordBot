from bs4 import BeautifulSoup
from .utils import get

BASE_URL = "https://www.gachon.ac.kr/kor/3104/subview.do"
PARAMS = {"fnctId": "bbs", "fnctNo": "475"}
SOURCE = "학사공지"
EMOJI = "📌"


def fetch():
    try:
        resp = get(BASE_URL, params=PARAMS)
        resp.raise_for_status()
    except Exception as e:
        print(f"[{SOURCE}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    for row in soup.select("table.board-table tbody tr"):
        title_tag = row.select_one("td.td-subject a")
        date_tag = row.select_one("td.td-date")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        if href.startswith("/"):
            href = "https://www.gachon.ac.kr" + href
        date = date_tag.get_text(strip=True) if date_tag else ""
        uid = href

        items.append({"id": uid, "title": title, "url": href, "date": date, "source": SOURCE, "emoji": EMOJI})

    return items

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.gachon.ac.kr/kor/3104/subview.do"
PARAMS = {"fnctId": "bbs", "fnctNo": "475"}
SOURCE = "학사공지"
EMOJI = "📌"

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

        # 고유 ID: URL 그대로 사용
        uid = href

        items.append({
            "id": uid,
            "title": title,
            "url": href,
            "date": date,
            "source": SOURCE,
            "emoji": EMOJI,
        })

    return items

from bs4 import BeautifulSoup
from .utils import get

BASE_URL = "https://wind.gachon.ac.kr/ko/program/all"
SOURCE = "비교과"
EMOJI = "🧩"

KEYWORDS = ["AI", "인공지능", "SW", "소프트웨어", "전공", "IT", "데이터", "머신러닝", "딥러닝", "코딩"]


def _is_relevant(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in KEYWORDS)


def fetch():
    try:
        resp = get(BASE_URL)
        resp.raise_for_status()
    except Exception as e:
        print(f"[{SOURCE}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    for card in soup.select(".program-item, .program-card, li.program"):
        title_tag = card.select_one("a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = "https://wind.gachon.ac.kr" + href

        if not _is_relevant(title):
            continue

        uid = href
        items.append({"id": uid, "title": title, "url": href, "date": "", "source": SOURCE, "emoji": EMOJI})

    return items

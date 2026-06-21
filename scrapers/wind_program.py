import requests
from bs4 import BeautifulSoup

BASE_URL = "https://wind.gachon.ac.kr/ko/program/all"
SOURCE = "비교과"
EMOJI = "🧩"

# 관련 키워드 필터 — 이 중 하나라도 포함되면 수집
KEYWORDS = ["AI", "인공지능", "SW", "소프트웨어", "전공", "IT", "데이터", "머신러닝", "딥러닝", "코딩"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GachonNotifyBot/1.0)"
}


def _is_relevant(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in KEYWORDS)


def fetch():
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
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

        items.append({
            "id": uid,
            "title": title,
            "url": href,
            "date": "",
            "source": SOURCE,
            "emoji": EMOJI,
        })

    return items

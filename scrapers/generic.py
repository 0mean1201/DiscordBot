"""
사이트 타입별 제네릭 스크레이퍼.
config.json의 sites 항목을 받아 아이템 리스트를 반환한다.

지원 타입:
  gachon_board  - gachon.ac.kr 표준 게시판 (table.board-table)
  gachon_widget - gachon.ac.kr 학과 사이트 최근글 위젯
  wordpress     - 워드프레스 기반 사이트
  wind          - wind.gachon.ac.kr 비교과 프로그램
"""

from bs4 import BeautifulSoup
from .utils import get

BASE_GACHON = "https://www.gachon.ac.kr"
BASE_WIND = "https://wind.gachon.ac.kr"


def _make_item(site: dict, title: str, href: str, date: str = "") -> dict:
    return {
        "id": href,
        "title": title,
        "url": href,
        "date": date,
        "source": site["source"],
        "emoji": site["emoji"],
    }


def fetch_gachon_board(site: dict) -> list:
    try:
        resp = get(site["url"], params=site.get("params"))
        resp.raise_for_status()
    except Exception as e:
        print(f"[{site['source']}] fetch 실패: {e}")
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
            href = BASE_GACHON + href
        date = date_tag.get_text(strip=True) if date_tag else ""
        items.append(_make_item(site, title, href, date))
    return items


def fetch_gachon_widget(site: dict) -> list:
    try:
        resp = get(site["url"], params=site.get("params"))
        resp.raise_for_status()
    except Exception as e:
        print(f"[{site['source']}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a_tag in soup.select(".bbs-latest-list li a, .recent-board li a"):
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = BASE_GACHON + href
        items.append(_make_item(site, title, href))
    return items


def fetch_wordpress(site: dict) -> list:
    try:
        resp = get(site["url"])
        resp.raise_for_status()
    except Exception as e:
        print(f"[{site['source']}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a_tag in soup.select("article h2 a, .entry-title a, .post-title a"):
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        if not href:
            continue
        items.append(_make_item(site, title, href))
    return items


def fetch_wind(site: dict) -> list:
    try:
        resp = get(site["url"])
        resp.raise_for_status()
    except Exception as e:
        print(f"[{site['source']}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for li in soup.select("ul[data-role='list'] li"):
        a_tag = li.select_one("a[href]")
        if not a_tag:
            continue
        href = a_tag.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = BASE_WIND + href
        content = li.select_one("div.content")
        title = content.get_text(strip=True) if content else a_tag.get_text(strip=True)
        if not title:
            continue
        items.append(_make_item(site, title, href))
    return items


FETCHERS = {
    "gachon_board": fetch_gachon_board,
    "gachon_widget": fetch_gachon_widget,
    "wordpress": fetch_wordpress,
    "wind": fetch_wind,
}


def fetch(site: dict) -> list:
    fetcher = FETCHERS.get(site["type"])
    if not fetcher:
        print(f"[{site['source']}] 알 수 없는 타입: {site['type']}")
        return []
    return fetcher(site)

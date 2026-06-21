from bs4 import BeautifulSoup
from .utils import get

BASE_URL = "https://xsw.gachon.ac.kr/"
SOURCE = "SW중심대학"
EMOJI = "💻"


def fetch():
    try:
        resp = get(BASE_URL)
        resp.raise_for_status()
    except Exception as e:
        print(f"[{SOURCE}] fetch 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    for a_tag in soup.select("article h2 a, .entry-title a, .post-title a"):
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        if not href:
            continue
        uid = href

        items.append({"id": uid, "title": title, "url": href, "date": "", "source": SOURCE, "emoji": EMOJI})

    return items

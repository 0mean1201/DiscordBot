import json
import os
from datetime import date
from pathlib import Path

import requests

from scrapers import generic

SEEN_IDS_PATH = Path(__file__).parent / "data" / "seen_ids.json"
CONFIG_PATH = Path(__file__).parent / "config.json"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_seen(seen: dict):
    SEEN_IDS_PATH.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")


def is_filtered(title: str, config: dict) -> bool:
    """True면 전송 안 함."""
    includes = config.get("include_keywords", [])
    excludes = config.get("exclude_keywords", [])
    if any(kw in title for kw in excludes):
        return True
    if includes and not any(kw in title for kw in includes):
        return True
    return False


def is_before_since(item_date: str, since: date | None) -> bool:
    """기준일보다 오래된 글이면 True."""
    if not since or not item_date:
        return False
    try:
        # gachon 날짜 형식: YYYY.MM.DD 또는 YYYY-MM-DD
        normalized = item_date.replace(".", "-")
        return date.fromisoformat(normalized) < since
    except ValueError:
        return False


def send_discord(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("[경고] DISCORD_WEBHOOK_URL 환경변수가 없습니다.")
        return
    resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
    if not resp.ok:
        print(f"[Discord] 전송 실패: {resp.status_code} {resp.text}")


def main():
    config = load_json(CONFIG_PATH)
    seen = load_json(SEEN_IDS_PATH)

    since_str = config.get("since_date", "")
    since = date.fromisoformat(since_str) if since_str else None

    enabled_sites = [s for s in config.get("sites", []) if s.get("enabled", True)]

    print(f"[설정] 기준일: {since or '없음'}")
    print(f"[설정] 포함 키워드: {config.get('include_keywords')}")
    print(f"[설정] 제외 키워드: {config.get('exclude_keywords')}")
    print(f"[설정] 활성 사이트: {[s['source'] for s in enabled_sites]}\n")

    new_count = 0

    for site in enabled_sites:
        items = generic.fetch(site)
        source = site["source"]
        seen_set = set(seen.get(source, []))
        new_items = [item for item in items if item["id"] not in seen_set]

        for item in new_items:
            seen_set.add(item["id"])

            if is_before_since(item["date"], since):
                print(f"[기준일 이전] {item['title']} ({item['date']})")
                continue

            if is_filtered(item["title"], config):
                print(f"[필터] {item['title']}")
                continue

            message = f"{item['emoji']} **[{item['source']}]** {item['title']}\n{item['url']}"
            print(f"[전송] {message}")
            send_discord(message)
            new_count += 1

        seen[source] = list(seen_set)

    save_seen(seen)
    print(f"\n완료: 새 글 {new_count}개 전송됨.")


if __name__ == "__main__":
    main()

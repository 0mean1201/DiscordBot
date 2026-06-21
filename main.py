import json
import os
from pathlib import Path

import requests

from scrapers import gachon_academic, gachon_scholarship, gachon_aisw, xsw_notice, wind_program

SEEN_IDS_PATH = Path(__file__).parent / "data" / "seen_ids.json"
CONFIG_PATH = Path(__file__).parent / "config.json"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

SCRAPERS = [
    gachon_academic,
    gachon_scholarship,
    gachon_aisw,
    xsw_notice,
    wind_program,
]


def load_seen() -> dict:
    if SEEN_IDS_PATH.exists():
        return json.loads(SEEN_IDS_PATH.read_text(encoding="utf-8"))
    return {}


def save_seen(seen: dict):
    SEEN_IDS_PATH.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"include_keywords": [], "exclude_keywords": []}


def is_filtered(title: str, config: dict) -> bool:
    """True면 전송 안 함."""
    includes = config.get("include_keywords", [])
    excludes = config.get("exclude_keywords", [])

    # 제외 키워드가 하나라도 포함되면 스킵
    if any(kw in title for kw in excludes):
        return True

    # 포함 키워드가 설정된 경우, 하나도 없으면 스킵
    if includes and not any(kw in title for kw in includes):
        return True

    return False


def send_discord(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("[경고] DISCORD_WEBHOOK_URL 환경변수가 없습니다. 메시지 전송을 건너뜁니다.")
        return
    resp = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=10,
    )
    if not resp.ok:
        print(f"[Discord] 전송 실패: {resp.status_code} {resp.text}")


def main():
    if not DISCORD_WEBHOOK_URL:
        print("[경고] DISCORD_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")

    config = load_config()
    print(f"[설정] 포함 키워드: {config.get('include_keywords')}")
    print(f"[설정] 제외 키워드: {config.get('exclude_keywords')}")

    seen = load_seen()
    new_count = 0

    for scraper in SCRAPERS:
        items = scraper.fetch()
        source = scraper.SOURCE

        seen_set = set(seen.get(source, []))
        new_items = [item for item in items if item["id"] not in seen_set]

        for item in new_items:
            seen_set.add(item["id"])  # seen에는 필터 여부 무관하게 등록 (재전송 방지)

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

    if new_count == 0:
        print("새 공지 없음.")


if __name__ == "__main__":
    main()

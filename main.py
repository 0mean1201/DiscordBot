import json
import os
import sys
from pathlib import Path

import requests

from scrapers import gachon_academic, gachon_scholarship, gachon_aisw, xsw_notice, wind_program

SEEN_IDS_PATH = Path(__file__).parent / "data" / "seen_ids.json"
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

    seen = load_seen()
    new_count = 0

    for scraper in SCRAPERS:
        items = scraper.fetch()
        source = scraper.SOURCE

        seen_set = set(seen.get(source, []))
        new_items = [item for item in items if item["id"] not in seen_set]

        for item in new_items:
            message = f"{item['emoji']} **[{item['source']}]** {item['title']}\n{item['url']}"
            print(f"[전송] {message}")
            send_discord(message)
            seen_set.add(item["id"])
            new_count += 1

        seen[source] = list(seen_set)

    save_seen(seen)
    print(f"\n완료: 새 글 {new_count}개 전송됨.")

    if new_count == 0:
        print("새 공지 없음.")


if __name__ == "__main__":
    main()

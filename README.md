# 가천대 공지 디스코드 알림 봇

가천대학교 관련 공지사항을 매일 자동으로 크롤링해서 Discord 채널에 전송하는 봇입니다.

## 동작 방식

```
GitHub Actions (매일 오전 11시 자동 실행)
        │
        ▼
config.json에서 활성화된 사이트 목록 로드
        │
        ▼
각 사이트 크롤링
        │
        ▼
기준일(since_date) 필터 → 키워드 필터 → seen_ids.json 중복 제거
        │
        ▼
새 글만 Discord Webhook으로 전송
        │
        ▼
seen_ids.json 업데이트 후 레포에 자동 커밋
```

## config.json 설정

모든 설정은 레포 루트의 `config.json` 하나로 관리합니다.  
수정 후 GitHub에 push하면 다음 실행부터 자동 반영됩니다.

```json
{
  "since_date": "2026-06-01",
  "include_keywords": [],
  "exclude_keywords": [],
  "sites": [ ... ]
}
```

---

### since_date (기준일)

이 날짜 이후에 올라온 글만 전송합니다.  
처음 봇을 설정할 때 오래된 공지가 한꺼번에 쏟아지는 것을 방지합니다.

```json
"since_date": "2026-06-01"
```

- 형식: `YYYY-MM-DD`
- 비워두면(`""`) 날짜 필터 없이 전체 전송

---

### sites (사이트 목록)

크롤링할 사이트를 추가하거나 `enabled`로 켜고 끌 수 있습니다.

```json
"sites": [
  {
    "id": "gachon_academic",
    "enabled": true,
    "source": "학사공지",
    "emoji": "📌",
    "type": "gachon_board",
    "url": "https://www.gachon.ac.kr/kor/3104/subview.do",
    "params": {"fnctId": "bbs", "fnctNo": "475"}
  }
]
```

| 필드 | 설명 |
|---|---|
| `id` | 고유 식별자 (임의 문자열) |
| `enabled` | `true`/`false` — false이면 해당 사이트 크롤링 안 함 |
| `source` | 디스코드 메시지에 표시될 출처 이름 |
| `emoji` | 메시지 앞에 붙는 이모지 |
| `type` | 사이트 종류 (아래 타입 목록 참고) |
| `url` | 크롤링할 URL |
| `params` | URL 쿼리 파라미터 (없으면 `{}`) |

#### 지원 타입

| type | 설명 |
|---|---|
| `gachon_board` | gachon.ac.kr 표준 게시판 |
| `gachon_widget` | gachon.ac.kr 학과 사이트 최근글 위젯 |
| `wordpress` | 워드프레스 기반 사이트 |
| `wind` | wind.gachon.ac.kr 비교과 프로그램 |

#### 특정 학과 공지 추가 예시

가천대 다른 학과 게시판은 `gachon_board` 타입으로 URL과 파라미터만 바꿔서 추가할 수 있습니다.

```json
{
  "id": "gachon_sw",
  "enabled": true,
  "source": "소프트웨어학과",
  "emoji": "🖥️",
  "type": "gachon_board",
  "url": "https://www.gachon.ac.kr/sites/sw/index.do",
  "params": {"fnctId": "bbs", "fnctNo": "123"}
}
```

#### 사이트 비활성화 예시

삭제하지 않고 `enabled: false`로 끌 수 있습니다.

```json
{
  "id": "wind_program",
  "enabled": false,
  ...
}
```

---

### include_keywords / exclude_keywords (키워드 필터)

```json
"include_keywords": ["장학", "AI", "특강"],
"exclude_keywords": ["교직원", "채용"]
```

| 설정 | 동작 |
|---|---|
| `include_keywords` 비어있음 | 전체 공지 전송 |
| `include_keywords` 설정됨 | 해당 키워드 포함된 공지만 전송 |
| `exclude_keywords` 설정됨 | 해당 키워드 포함된 공지는 전송 안 함 |

제외 키워드가 포함 키워드보다 먼저 적용됩니다.

---

## 메시지 형식

```
📌 [학사공지] 2026-1학기 수강신청 안내
https://www.gachon.ac.kr/...

🎓 [장학공지] 교내장학금 신청기간 안내
https://www.gachon.ac.kr/...
```

---

## 초기 설정 방법

### 1. Discord Webhook 생성
1. 알림 받을 채널 우클릭 → **채널 편집**
2. **연동** 탭 → **웹후크 → 새 웹후크**
3. **웹후크 URL 복사**

### 2. GitHub Secrets 등록
1. 레포 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
3. Name: `DISCORD_WEBHOOK_URL` / Value: 복사한 URL

### 3. 수동 실행 (테스트)
Actions 탭 → **Gachon Notify** → **Run workflow**

---

## 파일 구조

```
DiscordBot/
├── scrapers/
│   ├── generic.py   # 타입별 제네릭 스크레이퍼
│   └── utils.py     # 공통 HTTP 유틸
├── main.py          # 메인 실행 파일
├── config.json      # 사이트 목록 + 키워드 필터 + 기준일 설정
├── data/
│   └── seen_ids.json  # 전송된 공지 ID 저장 (중복 방지)
└── .github/workflows/notify.yml
```

# 가천대 공지 디스코드 알림 봇

가천대학교 관련 공지사항을 매일 자동으로 크롤링해서 Discord 채널에 전송하는 봇입니다.

## 동작 방식

```
GitHub Actions (매일 오전 11시 자동 실행)
        │
        ▼
각 사이트 크롤링 (학사공지 / 장학공지 / AI학과 / SW중심대학 / 비교과)
        │
        ▼
config.json 키워드 필터 적용
        │
        ▼
seen_ids.json과 비교 → 새 글만 Discord Webhook으로 전송
        │
        ▼
seen_ids.json 업데이트 후 레포에 자동 커밋 (중복 방지)
```

## 정보 소스

| 분류 | 출처 |
|---|---|
| 학사공지 | gachon.ac.kr 학사공지 게시판 |
| 장학공지 | gachon.ac.kr 장학공지 게시판 |
| AI학과공지 | gachon.ac.kr 인공지능학과 사이트 |
| SW중심대학 | xsw.gachon.ac.kr |
| 비교과 프로그램 | wind.gachon.ac.kr |

## 메시지 형식

```
📌 [학사공지] 2026-1학기 수강신청 안내
https://www.gachon.ac.kr/...

🎓 [장학공지] 교내장학금 신청기간 안내
https://www.gachon.ac.kr/...

🤖 [AI학과공지] 학과 세미나 안내
https://www.gachon.ac.kr/...

💻 [SW중심대학] AI 교수 특별초빙
https://xsw.gachon.ac.kr/...

🧩 [비교과] AI 컴퓨팅 기술 특강
https://wind.gachon.ac.kr/...
```

## 키워드 필터 설정 (config.json)

레포 루트의 `config.json`을 수정해서 원하는 공지만 받을 수 있습니다.
수정 후 GitHub에 push하면 다음 실행부터 자동 반영됩니다.

```json
{
  "include_keywords": [],
  "exclude_keywords": []
}
```

### include_keywords (포함 키워드)
- 설정된 키워드 중 하나라도 제목에 포함된 공지만 전송
- **비어있으면 전체 공지 전송**

```json
{
  "include_keywords": ["장학", "AI", "특강"],
  "exclude_keywords": []
}
```

### exclude_keywords (제외 키워드)
- 설정된 키워드가 제목에 포함된 공지는 전송하지 않음

```json
{
  "include_keywords": [],
  "exclude_keywords": ["교직원", "채용", "주차"]
}
```

### 동시 사용
- 제외 키워드가 먼저 적용되고, 이후 포함 키워드로 필터링

```json
{
  "include_keywords": ["장학", "AI"],
  "exclude_keywords": ["교직원"]
}
```

## 초기 설정 방법

### 1. Discord Webhook 생성
1. 알림 받을 채널 우클릭 → **채널 편집**
2. **연동** 탭 → **웹후크 → 새 웹후크**
3. **웹후크 URL 복사**

### 2. GitHub Secrets 등록
1. 레포 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
3. Name: `DISCORD_WEBHOOK_URL` / Value: 복사한 URL 붙여넣기

### 3. 수동 실행 (테스트)
Actions 탭 → **Gachon Notify** → **Run workflow**

## 파일 구조

```
DiscordBot/
├── scrapers/
│   ├── gachon_academic.py    # 학사공지
│   ├── gachon_scholarship.py # 장학공지
│   ├── gachon_aisw.py        # AI학과공지
│   ├── xsw_notice.py         # SW중심대학
│   ├── wind_program.py       # 비교과 프로그램
│   └── utils.py              # 공통 HTTP 유틸
├── main.py                   # 메인 실행 파일
├── config.json               # 키워드 필터 설정
├── data/seen_ids.json        # 전송된 공지 ID 저장 (중복 방지)
└── .github/workflows/notify.yml  # GitHub Actions 스케줄
```

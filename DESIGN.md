# 가천대 알림 디스코드 봇 - 설계 문서

## 1. 목표

가천대학교(인공지능학과 재학)와 관련된 새 공지/프로그램을 매일 한 번 자동으로 확인해서,
디스코드 채널에 새 글만 제목+링크 형태로 올려준다.

## 2. 정보 소스

공식 API는 없음. 모두 HTML 크롤링으로 수집.

| 분류 | 출처 | URL | 접근 특이사항 |
|---|---|---|---|
| 학사공지 | gachon.ac.kr 학사공지 게시판 | https://www.gachon.ac.kr/kor/3104/subview.do (fnctId=bbs, fnctNo=475) | gachon.ac.kr은 robots.txt로 자동화 접근을 막아둠. 법적 강제는 아니지만, 짧은 간격 반복 요청 시 차단 위험 있음 → 하루 1회 정도면 안전 |
| 장학공지 | gachon.ac.kr 장학공지 게시판 | https://www.gachon.ac.kr/kor/1146/subview.do | 위와 동일 |
| 인공지능학과 자체 공지 | gachon.ac.kr 학과 사이트 | https://www.gachon.ac.kr/sites/aisw/index.do (fnctId=recentBbs, fnctNo=447) | 위와 동일 |
| SW중심대학(AI중심대학) 공지 | xsw.gachon.ac.kr (워드프레스 기반) | https://xsw.gachon.ac.kr/cms/ | 별도 도메인, 접근 제한 없음. 채용공고/장학/특강 등 활발히 올라옴 |
| 비교과 프로그램 | WIND 비교과통합관리시스템 | https://wind.gachon.ac.kr/ko/program/all | 로그인 없이 전체 목록 열람 가능(meta-robots: all). "운영기관" 필터로 IT융합대학 등 선택 가능, "전공기반"/"AI"/"SW" 등 태그로 전공 관련 프로그램만 추출 가능 |

> 주의: 위 URL과 게시판 구조(fnctNo, HTML 셀렉터 등)는 검색 결과 기반으로 확인한 것이며,
> 실제 셀렉터(class명, DOM 구조)는 Claude Code에서 직접 페이지를 열어 확인 후 작성 필요.
> gachon.ac.kr 계열은 현재 환경에서 직접 fetch가 막혀 있어 검증하지 못함.

## 3. 전체 아키텍처

```
[소스별 스크레이퍼 함수] (gachon_academic.py, gachon_scholarship.py,
                          gachon_aisw.py, xsw_notice.py, wind_program.py)
        │  각자 (제목, 날짜, URL, 출처) 형태의 공통 객체 리스트 반환
        ▼
[정규화 + 통합] → 하나의 리스트로 합침
        ▼
[중복 체크] seen_ids.json (레포에 커�밋되어 있는 파일)과 비교해서 새 글만 필터링
        ▼
[디스코드 전송] Webhook으로 새 글마다 메시지 전송 (제목 + 출처 + 링크)
        ▼
[seen_ids.json 갱신 후 레포에 다시 커밋] (다음 실행 때 중복 방지용)
```

## 4. 기술 스택

- 언어: Python (requests, BeautifulSoup4)
- 디스코드 전송: Discord Webhook (discord.py 불필요, 단순 POST 요청)
- 실행 환경: GitHub Actions scheduled workflow (cron)
  - 매일 KST 11:00 = UTC 02:00 에 실행 (`cron: '0 2 * * *'`)
  - 워크플로우 마지막 단계에서 seen_ids.json 변경분을 `git commit && git push`로 레포에 반영
  - Discord Webhook URL은 GitHub Secrets에 저장 (코드에 하드코딩 금지)
- 중복 방지 저장소: 레포 내 `data/seen_ids.json` (소스별로 이미 보낸 글의 고유 ID 또는 URL 목록)

## 5. 메시지 포맷 (예시)

```
📌 [학사공지] 2026-1학기 수강신청 안내
https://www.gachon.ac.kr/bbs/kor/475/116985/artclView.do

🎓 [장학공지] 2026-1학기 교내장학금 신청기간 안내
https://www.gachon.ac.kr/...

💻 [SW중심대학] AI소프트웨어학부 정년트랙교수 특별초빙
https://xsw.gachon.ac.kr/...

🧩 [비교과-전공기반] AI 컴퓨팅 기술 특강
https://wind.gachon.ac.kr/ko/program/all/view/6943
```

소스별로 이모지/태그를 다르게 붙여서 한눈에 구분되게 한다.

## 6. 향후 확장 가능 옵션 (현재 범위 아님)

- discord.py 기반 봇으로 전환해서 `!장학공지` 같은 명령어로 즉시 조회
- 비교과 프로그램 신청 마감 임박(D-1, D-2 등) 알림 별도 발송
- 학과/카테고리별로 디스코드 채널 분리

## 7. 결정된 사항 요약

- 알림 대상: 학사공지, 장학공지(공식 + 인공지능학과/SW중심대학), 비교과 프로그램(전공 관련 필터 포함)
- 언어: Python
- 전송 방식: Discord Webhook, 새 글만, 링크 첨부
- 실행 주기: 하루 1회, 오전 11시
- 호스팅: GitHub Actions (무료, 상시 서버 불필요)

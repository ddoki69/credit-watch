# CREDIT WATCH — 인수인계 브리프 (Cowork 이어받기용)

> 이 문서 1개 + 파일 3개만 있으면 처음부터 설명 없이 이어서 진행할 수 있습니다.

## 1. 무엇을 만들고 있나
빅테크의 **부채 기반 AI capex 붐**이 꺾이는 변곡점을, 돈을 대주는 **신용시장의 공급 의지가 약해지는 신호**로 먼저 포착하기 위한 **모바일 일일 대시보드**.
- 핵심 가설: 채권시장 가격(크레딧 스프레드)이 선행 변수, 주가가 후행 변수. 스프레드가 벌어지는데 주가가 아직 오르는 **괴리**가 핵심 매도 트리거.
- 최우선 선행 신호: **HY OAS (FRED: BAMLH0A0HYM2)** — 1997년 이후 8번의 주가 급락에 모두 1~13개월 선행.

## 2. 확정된 아키텍처 (이유 포함)
**GitHub Actions + GitHub Pages.** n8n·상시 서버 없이, 무료로, 내 장비가 꺼져 있어도 매일 동작.
- 매일 06:00 KST cron → GitHub Actions가 **서버단에서 FRED API 호출**(CORS 없음, 키는 Secret) → `data.json` 생성 → Pages에 대시보드 + JSON 배포.
- 브라우저는 **같은 출처의 data.json만 read** → CORS 프록시 불필요 → 안정적.

## 3. 파일 인벤토리 & repo 배치
```
credit-watch/                 ← 새 GitHub repo (public 권장: 출력은 공개 FRED 숫자뿐, 키는 Secret)
├─ index.html                 ← 대시보드 (data.json을 같은 출처에서 fetch)
├─ fetch_fred.py              ← FRED 수집기 (stdlib만, pip 불필요)
├─ data.json                  ← Action이 생성 (수동 커밋 X)
└─ .github/workflows/update.yml   ← 워크플로 (※ update.yml을 이 경로로 이동)
```
> 주의: `update.yml`은 반드시 `.github/workflows/` 아래에 있어야 인식됩니다.

## 4. 남은 설치 단계 (Cowork에서 진행)
1. **FRED 무료 API 키 발급** — fred.stlouisfed.org → My Account → API Keys (즉시).
2. **새 repo 생성** (예: `credit-watch`, public).
3. **파일 3개 업로드** — `index.html`, `fetch_fred.py`를 루트에, `update.yml`을 `.github/workflows/`에.
4. **Secret 등록** — repo Settings → Secrets and variables → Actions → New repository secret → 이름 `FRED_API_KEY`, 값=발급키.
5. **Pages 소스 설정** — Settings → Pages → Source = **GitHub Actions**.
6. **최초 1회 수동 실행** — Actions 탭 → "Update Credit Watch" → Run workflow (cron 첫 발동 전까지 비어있으므로 필수).
7. **폰에서 열기** — `https://<user>.github.io/credit-watch/` → 홈 화면에 추가(아이콘처럼 사용).

## 5. 알아둘 한계
- GitHub 예약작업은 부하 시 수십 분 지연될 수 있음. cron 시간은 `update.yml`의 `cron:` 한 줄로 변경.
- **repo가 60일간 활동 없으면 예약 워크플로가 자동 중지** → 가끔 수동 Run 또는 커밋으로 깨어있게.
- MOVE는 Yahoo 비공식 API로 보조 시도(실패해도 무방, 스냅샷 표시). 개별 CDS(Oracle·CoreWeave)·BDC 할인·SLOOS는 무료 실시간 소스가 없어 수동/주기 확인.
- ICE BofA OAS는 2026년 4월부터 3년 롤링 윈도우만 제공 → 장기 이력은 별도 보관 필요.
- 종합 점수는 임의 가중치 휴리스틱. 투자 자문 아님.

## 6. Cowork에서 해볼 다음 단계 (선택)
- repo 생성·파일 푸시·배포 검증까지 자동 수행, 첫 Pages URL 확인.
- **텔레그램/이메일 푸시** 추가: Action 끝에 점수가 임계값(예: 50↑) 넘으면 알림 보내는 스텝.
- **분기 SLOOS(DRTSCILM)·BDC 할인(ARCC/OBDC/BXSL)** 패널 추가 — fetch_fred.py에 시리즈/소스 확장.
- HY OAS 저점 대비 +75bp 같은 **룰 기반 단계 자동 판정** 강화(현재는 점수→단계 매핑).
- 한국 시장 연계: 본인 Korean 스크리너/대시보드와 신호 동기화(SK하이닉스·삼성 등 반도체 신용 민감도).

## 7. 종합 권고 (현 시점 요약)
현재 모든 종합 지표는 **평온**(보유 유지) 구간. 이 도구는 확신 도구가 아니라 "변곡점을 먼저 보는 망원경". 매일 봐야 할 단 하나는 **HY 스프레드의 저점 대비 반전 + 주가와의 괴리**. 반대 의견(Mag-7 현금창출력·저레버리지로 부채 채널 통제 가능, IMF·Goldman 주식팀)도 함께 염두에 둘 것.

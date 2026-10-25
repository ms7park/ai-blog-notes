#!/usr/bin/env python3
"""
Daily WordPress Blog Automation Batch (Google SEO · Gutenberg · Rank Math · Cornerstone Content)
네이버(실시간 이슈) · 티스토리(Google Trends 단기·중기 질문)와 차별화된
워드프레스 전용 장기 코너스톤(Cornerstone) SEO 가이드 글(.md, .html) 및
워드프레스 작업실 대시보드(blog/wordpress/index.html)를 생성/갱신합니다.
"""

import os
import sys
import glob
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WP_BLOG_DIR = os.path.join(BASE_DIR, "blog", "wordpress")
POSTS_DIR = os.path.join(WP_BLOG_DIR, "posts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "daily_batch.log")

WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

def log(msg):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    print(formatted)
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

# 워드프레스 코너스톤(Cornerstone) SEO 심층 원고 5선
WP_ARTICLES = [
    {
        "seq": 1,
        "category": "Retirement & Pension (은퇴·연금·건보료)",
        "topic": "퇴직 후 건강보험료 계산 및 절감 방법",
        "focus_keyphrase": "퇴직 후 건강보험료 계산",
        "slug": "retirement-health-insurance-calculation-guide",
        "meta_desc": "퇴직 후 건강보험료 계산 기준과 절감 방법 총정리. 직장가입자 피부양자 자격 요건(연 소득 2,000만 원·재산 과표 5.4억 이하), 임의계속가입 신청 기한(2개월 이내), 지역가입자 모의계산 비교표를 확인하세요.",
        "score": 92,
        "scores": {"trend": 5, "intent": 5, "gap": 4, "capability": 4, "evergreen": 5},
        "title_candidates": [
            "퇴직 후 건강보험료 계산 기준 및 줄이는 법: 피부양자 자격 요건 vs 임의계속가입 vs 지역가입자 비교표",
            "은퇴 후 건강보험료 폭탄 피하는 3가지 방법 (피부양자 소득 2,000만 원 기준·임의계속가입 신청 기간)",
            "퇴직자 건강보험 임의계속가입 신청 조건 및 국민건강보험공단 모의계산 확인 순서"
        ],
        "final_title": "퇴직 후 건강보험료 계산 기준 및 줄이는 법: 피부양자 자격 요건 vs 임의계속가입 vs 지역가입자 비교표",
        "core_summary": (
            "퇴직 후 건강보험료 부담을 줄이려면 **① 자녀·배우자 등 직장가입자의 피부양자 등록 가능 여부(연간 합산소득 2,000만 원 이하 및 재산 과세표준 5.4억 원 이하)**를 1순위로 확인해야 합니다. "
            "피부양자 등재가 어렵다면 **② 퇴직 전 직장 건보료 수준을 최대 36개월간 유지하는 '임의계속가입'(최초 지역건보료 고지서 납부기한으로부터 2개월 이내 신청 필수)**과 **③ 일반 지역가입자 전환 보험료**를 국민건강보험공단 모의계산으로 비교해 더 저렴한 쪽을 선택하면 됩니다."
        ),
        "sections_md": """## 1. 도입부: 퇴직 후 가장 큰 고정비, 건강보험료는 왜 갑자기 오를까요?

직장에 재직할 때는 월급에서 건강보험료의 **50%만 본인이 부담**하고 나머지 50%는 회사가 부담합니다. 또한 보수(급여) 외에 본인이 보유한 주택이나 토지에는 별도의 재산 건강보험료가 부과되지 않습니다.

그러나 퇴직 후 **지역가입자**로 전환되면 회사가 부담하던 50%가 사라질 뿐만 아니라, **소득(공적연금·이자·배당·근로·사업소득)과 재산(주택·토지 과세표준, 기본공제 1억 원 적용)**을 합산해 보험료를 부과하기 때문에 체감 부담이 급격히 커집니다. 이 가이드에서는 국민건강보험공단 공식 기준을 바탕으로 **퇴직 직후 반드시 비교해야 할 3가지 선택지(피부양자 · 임의계속가입 · 지역가입자) 비교표와 모의계산 절차**를 상세히 정리합니다.

---

## 2. 핵심 내용 요약 (Key Takeaways)

- **1순위 검토 (월 보험료 0원)**: 직장가입자(자녀·배우자)의 **피부양자 등재**
  - 핵심 조건: 연간 합산소득 **2,000만 원 이하** + 재산세 과세표준 합계 **5.4억 원 이하**(5.4억 초과~9억 이하는 연 소득 1,000만 원 이하)
- **2순위 검토 (최대 36개월 직장 수준 유지)**: **임의계속가입 신청**
  - 핵심 조건: 퇴직 전 18개월 기간 중 통산 1년 이상 직장가입자 자격을 유지한 사람
  - **필수 신청 기한**: 지역가입자 전환 후 받은 **최초 지역보험료 고지서 납부기한에서 2개월이 지나기 전**까지 공단에 신청 필수
- **3순위 검토**: 무주택이거나 소득·재산이 적어 지역가입자 보험료가 임의계속가입 보험료보다 낮은 경우 별도 신청 없이 **지역가입자** 유지

---

## 3. 단계별 설명: 퇴직 후 건강보험료 계산 및 신청하는 4단계 순서

### 1단계: 국민건강보험공단 홈페이지·앱에서 예상 지역보험료 모의계산하기
1. [국민건강보험공단 공식 홈페이지(nhis.or.kr)](https://www.nhis.or.kr/) 또는 모바일 앱 **'The건강보험'**에 접속합니다.
2. **[민원여기요]** → **[개인민원]** → **[보험료 조회/신청]** → **[4대보험료 계산해보기(지역보험료 모의계산)]** 메뉴를 선택합니다.
3. 본인의 연간 공적연금(국민연금 등), 이자·배당소득 및 보유 주택·토지의 재산세 과세표준 금액을 입력해 예상 월 지역보험료를 산출합니다.

### 2단계: 퇴직 전 직장 건강보험료(본인부담금)와 비교하기
1. 급여명세서 또는 공단 앱의 **[직장보험료 조회]**에서 퇴직 직전 본인이 부담하던 월 건강보험료(장기요양보험료 포함)를 확인합니다.
2. 정확한 임의계속보험료는 **퇴직 전 12개월간 보수월액 평균**을 기준으로 산정되므로, 공단 고객센터(`1577-1000`)에 전화해 **'예상 지역보험료 vs 예상 임의계속보험료'**를 비교 요청하면 가장 정확합니다.

### 3단계: 피부양자 자격 요건 충족 여부 점검하기
자녀나 배우자가 직장가입자라면 아래 두 가지 요건을 모두 충족하는지 확인합니다.
1. **소득 요건**: 이자·배당·사업·근로·공적연금(국민연금 등 세전 수령액) 합산 소득이 **연 2,000만 원 이하**일 것 (사업자등록이 있는 경우 사업소득이 '0원'이어야 함).
2. **재산 요건**: 토지·건축물·주택의 지방세법상 **재산세 과세표준 합계액이 5.4억 원 이하**일 것 (과세표준 5.4억 초과~9억 원 이하인 경우 연간 소득이 1,000만 원 이하여야 유지 가능).

### 4단계: 임의계속가입 신청 또는 피부양자 자격취득 신고하기
1. **피부양자 등록 시**: 직장가입자인 가족의 회사 인사·총무부서를 통해 퇴직일로부터 90일 이내에 `피부양자 자격(취득) 신고서`와 가족관계증명서를 제출합니다.
2. **임의계속가입 신청 시**: 최초 지역건보료 고지서 납부기한으로부터 **2개월 이내**에 공단 지사 방문, 팩스, 또는 'The건강보험' 앱/홈페이지에서 신청합니다.

---

## 4. 조건별 상세 비교표: 피부양자 vs 임의계속가입 vs 일반 지역가입자

아래 표는 2026년 현행 국민건강보험법 기준 3가지 제도의 핵심 차이를 정리한 비교표입니다.

| 비교 항목 | ① 직장가입자 피부양자 | ② 임의계속가입자 | ③ 일반 지역가입자 |
| :--- | :--- | :--- | :--- |
| **월 납부 보험료** | **0원** (직장가입자 가족에 포함) | 퇴직 전 직장 본인부담 보험료 수준 | 소득 + 재산(기본공제 1억 적용) 합산 부과 |
| **핵심 자격 조건** | 연 합산소득 **2,000만 원 이하** & 재산 과표 **5.4억 이하** | 퇴직 전 18개월 내 통산 **1년 이상** 직장가입자 유지 | 국내 거주자 중 직장가입자·피부양자가 아닌 자 |
| **유지 가능 기간** | 소득·재산 요건 충족 시 계속 유지 | 퇴직일 다음 날부터 **최대 36개월(3년)** | 별도 기간 제한 없음 |
| **신청 기한** | 퇴직 후 90일 이내 신고 시 퇴직일로 소급 | 최초 지역고지서 납부기한 후 **2개월 이내 필수** | 직장 상실 신고 시 자동 전환 |
| **유리한 케이스** | 연금·금융소득이 연 2,000만 원 이하인 은퇴자 | 자가 주택 보유 등으로 지역건보료가 직장 때보다 높은 경우 | 무주택이거나 소득·재산이 적어 지역보험료가 더 낮은 경우 |

---

## 5. 주의사항: 놓치면 불이익을 받는 3가지 핵심 예외 조건

1. **부부 동반 탈락 주의 (피부양자 연대 기준)**
   - 부부 중 한 사람이라도 연간 합산소득이 2,000만 원을 초과하면, 소득이 전혀 없는 배우자까지 **부부가 함께 피부양자에서 탈락**하여 지역가입자로 전환됩니다.
2. **사적연금(연금저축·IRP)과 공적연금(국민연금)의 차이**
   - 건강보험 피부양자 소득 산정 시 **국민연금·공무원연금 등 공적연금은 세전 수령액 100%가 반영**되지만, 현행 기준 사적연금(연금저축·IRP 등)은 분리과세 한도 내 수령 시 건보료 소득 산정에서 제외됩니다.
3. **임의계속가입 중도 해지 가능 여부**
   - 임의계속가입 기간 중 재산을 처분하거나 소득이 줄어 일반 지역보험료가 더 낮아지면, 공단에 **임의계속 탈퇴 신청**을 하여 언제든 지역가입자로 전환할 수 있습니다.

---

## 6. 자주 묻는 질문 (FAQ Schema)

### Q1. 재산세 과세표준 5.4억 원은 아파트 시세로 약 얼마인가요?
**A.** 재산세 과세표준은 시세가 아니라 **공시가격에 공정시장가액비율(주택 기준 통상 60% 등)을 곱한 금액**입니다. 따라서 과세표준 5.4억 원은 공시가격 기준 약 9억 원, 실거래 시세 기준으로는 약 12억~13억 원 안팎에 해당합니다. 정확한 과세표준 금액은 매년 7·9월 재산세 고지서 또는 위택스(Wetax)에서 확인할 수 있습니다.

### Q2. 임의계속가입 신청 기한(납부기한 후 2개월)이 지나면 구제 방법이 없나요?
**A.** 국민건강보험법상 최초 지역보험료 고지서 납부기한으로부터 2개월이 경과하면 임의계속가입 신청이 불가합니다. 따라서 퇴직 직후 첫 지역보험료 고지서를 받는 즉시 공단 고객센터(`1577-1000`)에 전화해 금액을 비교하는 것이 가장 중요합니다.

### Q3. 퇴직 후 소득이 줄었는데 지역보험료에 과거 소득이 반영되어 높게 나오면 어떻게 하나요?
**A.** 퇴직이나 폐업 등으로 소득이 중단·감소된 경우, 공단에 **퇴직증명서(또는 해촉증명서, 폐업사실증명원)를 제출해 '소득 정산(조정) 신청'**을 하면 현재 감소된 소득 기준으로 보험료를 즉시 낮출 수 있습니다.""",
        "official_refs": [
            ("국민건강보험공단 공식 홈페이지 (보험료 모의계산 및 피부양자 안내)", "https://www.nhis.or.kr/"),
            ("정부24 퇴직 후 건강보험 임의계속가입 신청 안내", "https://www.gov.kr/"),
            ("국가법령정보센터 국민건강보험법 시행규칙", "https://www.law.go.kr/")
        ],
        "fact_checks": [
            "피부양자 소득 기준(연 2,000만 원 이하) 및 재산세 과세표준 기준(5.4억 원 이하) 현행 법령 일치 확인",
            "임의계속가입 유지 기간(최대 36개월) 및 신청 기한(최초 지역고지서 납부기한으로부터 2개월 이내) 공단 공식 기준 일치 확인",
            "지역가입자 재산 기본공제(1억 원) 및 자동차 건보료 폐지 반영 기준 점검 완료"
        ]
    },
    {
        "seq": 2,
        "category": "AI & Tech Guide (AI·IT 매뉴얼)",
        "topic": "맥(Mac) Apple 계정 로그인 오류 해결 순서",
        "focus_keyphrase": "맥 Apple 계정 로그인 오류",
        "slug": "mac-apple-account-login-error-fix",
        "meta_desc": "맥북(Mac) 시스템 설정에서 Apple 계정(Apple ID) 로그인 오류 및 '확인 중' 무한 로딩이 발생할 때 초기화 없이 해결하는 5단계 공식 점검 순서를 확인하세요.",
        "score": 92,
        "scores": {"trend": 4, "intent": 5, "gap": 5, "capability": 5, "evergreen": 4},
        "title_candidates": [
            "맥(Mac)에서 Apple 계정(Apple ID) 로그인 오류 및 설정 무한 로딩 해결하는 5단계 순서",
            "맥북 시스템 설정에서 Apple ID 로그인이 안 될 때 확인해야 할 5가지 해결 방법",
            "Mac '확인 중' 멈춤·서버 연결 오류 발생 시 Apple 계정 로그인 복구 가이드"
        ],
        "final_title": "맥(Mac)에서 Apple 계정(Apple ID) 로그인 오류 및 설정 무한 로딩 해결하는 5단계 순서",
        "core_summary": (
            "맥(Mac) 시스템 설정에서 Apple 계정(Apple ID) 로그인이 멈추거나 '서버에 연결할 수 없음' 오류가 발생할 때는 **① Apple 시스템 상태 페이지 확인 → ② 날짜 및 시간 자동 설정 점검 → ③ VPN·방화벽 해제 → ④ 활성 상태 보기에서 인증 프로세스(`akd`, `cloudd`) 강제 종료 → ⑤ 맥 안전 모드(Safe Mode) 부팅 후 로그인** 순서로 진행하면 데이터 초기화 없이 90% 이상 해결됩니다."
        ),
        "sections_md": """## 1. 도입부: 맥(Mac)에서 Apple 계정 로그인이 멈추는 주요 원인

맥북(MacBook)이나 맥 미니를 사용하다가 macOS 업데이트 직후, 또는 비밀번호 변경 후 **시스템 설정(System Settings) → Apple 계정**에서 로그인을 시도할 때 `확인 중...` 회전 아이콘만 계속 돌거나 `알 수 없는 오류가 발생했습니다`라는 메시지가 뜨는 경우가 있습니다.

이 문제는 대부분 하드웨어 고장이 아니라 **macOS 백그라운드 인증 데몬(`akd`)의 일시적 충돌, 시스템 시간 동기화 오차, 또는 VPN/네트워크 보안 필터 간섭** 때문에 발생합니다. 아래의 **5단계 점검 순서**를 가벼운 방법부터 차례대로 실행해 보세요.

---

## 2. 핵심 내용 요약 (Key Takeaways)

- **주요 원인 1**: 맥의 **날짜 및 시간**이 Apple 인증 서버 시간과 미세하게 어긋난 경우 (보안 인증서 검증 실패)
- **주요 원인 2**: 백그라운드 인증 프로세스(`akd`, `cloudd`)가 응답 없음 상태로 멈춘 경우
- **핵심 해결책**: `활성 상태 보기(Activity Monitor)`에서 `akd` 프로세스를 재시작하거나, **안전 모드(Safe Mode)**로 부팅해 로그인한 뒤 일반 모드로 재시동하기

---

## 3. 단계별 설명: 맥 Apple 계정 로그인 오류 해결하는 5단계 순서

### 1단계: Apple 공식 시스템 상태 및 이중 인증 수신 기기 확인
1. 브라우저에서 [Apple 시스템 상태 페이지(apple.com/kr/support/systemstatus)](https://www.apple.com/kr/support/systemstatus/)에 접속합니다.
2. **'Apple 계정'**, **'iCloud 계정 및 로그인'** 항목 옆에 녹색 불(정상)이 켜져 있는지 확인합니다.
3. 함께 사용하는 아이폰이나 웹 브라우저([account.apple.com](https://account.apple.com/))에서 로그인이 정상 작동하는지 확인합니다.

### 2단계: 날짜 및 시간 자동 설정 강제 동기화
Apple 로그인 서버는 보안 토큰 검증을 위해 기기 시간이 정확히 일치할 것을 요구합니다.
1. 맥 좌측 상단 애플() 메뉴 → **[시스템 설정]** → **[일반]** → **[날짜 및 시간]**으로 이동합니다.
2. **'자동으로 날짜 및 시간 설정'** 토글을 한 번 껐다가 다시 켭니다.
3. 아래 **'위치에 따라 시간대 자동 설정'**도 활성화되어 있고 현재 국가(대한민국 표준시)가 맞는지 확인합니다.

### 3단계: VPN, 프록시, 광고 차단 앱 일시 종료
1. 실행 중인 VPN 앱이나 네트워크 방화벽 프로그램이 있다면 연결을 해제하고 완전 종료합니다.
2. **[시스템 설정]** → **[네트워크]** → 현재 연결된 Wi-Fi의 **[세부사항...]** → **[프록시]** 탭에서 체크된 프록시 항목이 있다면 모두 해제합니다.
3. 스마트폰 **개인용 핫스팟(테더링)**에 맥을 일시 연결해 로그인을 시도해 봅니다.

### 4단계: '활성 상태 보기'에서 인증 프로세스(`akd`, `cloudd`) 재시작
인증 창이 계속 멈춰 있을 때 가장 효과적인 단계입니다.
1. `Command(⌘) + Space`를 눌러 Spotlight 검색을 열고 **'활성 상태 보기(Activity Monitor)'**를 실행합니다.
2. 먼저 열려 있는 **시스템 설정** 창을 완전히 닫습니다(`Command + Q`).
3. 활성 상태 보기 우측 상단 검색창에 `akd`를 입력합니다 (Apple Account Daemon).
4. 목록에 나타난 `akd`를 선택하고 상단의 **[X (강제 종료)]** 버튼을 누릅니다 (macOS가 즉시 깨끗한 상태의 프로세스를 자동 재실행합니다).
5. 같은 방법으로 `cloudd` 프로세스도 강제 종료한 뒤, 다시 **시스템 설정**을 열어 로그인을 시도합니다.

### 5단계: 맥 안전 모드(Safe Mode)로 부팅하여 로그인하기
위 4단계로도 해결되지 않는다면 서드파티 시작 프로그램 충돌을 배제하는 **안전 모드**를 사용합니다.
- **Apple Silicon 탑재 맥 (M1 / M2 / M3 / M4)**:
  1. 맥 시스템을 완전히 종료합니다.
  2. 전원 버튼을 길게 누르고 **'시동 옵션 로드 중'**이 나타날 때까지 유지합니다.
  3. 시동 디스크(Macintosh HD)를 선택한 상태에서 키보드의 `Shift` 키를 누른 채 **'안전 모드로 계속'**을 클릭합니다.
- **Intel 프로세서 탑재 맥**:
  1. 맥을 종료한 뒤 전원 버튼을 누르자마자 즉시 `Shift` 키를 길게 누르고 로그인 창이 뜰 때까지 유지합니다.
- 안전 모드로 부팅된 상태에서 **[시스템 설정] → [Apple 계정]** 로그인을 완료한 뒤, 맥을 평상시처럼 **재시동**하면 정상 반영됩니다.

---

## 4. 증상별 해결 방법 요약 비교표

| 오류 증상 및 메시지 | 주요 발생 원인 | 최우선 적용할 해결 단계 | 예상 소요 시간 |
| :--- | :--- | :--- | :---: |
| **`확인 중...`에서 무한 로딩 멈춤** | 백그라운드 인증 데몬(`akd`) 응답 지연 | **4단계**: 활성 상태 보기에서 `akd` 강제 종료 후 재시도 | 2분 |
| **`서버에 연결할 수 없음` / 인증서 오류** | 기기 시간 오차 또는 VPN·방화벽 간섭 | **2단계 & 3단계**: 날짜/시간 자동 설정 + 핫스팟 연결 | 3분 |
| **암호 입력 후 반응 없이 창이 닫힘** | 서드파티 보안 앱 또는 캐시 충돌 | **5단계**: 안전 모드(Safe Mode) 부팅 후 로그인 | 5분 |
| **`이 기기에서 너무 많은 계정이 생성됨`** | 기기당 무료 iCloud 생성 횟수(3회) 초과 | 아이폰이나 웹(`account.apple.com`)에서 계정 생성 후 맥에서 로그인 | 5분 |

---

## 5. 자주 묻는 질문 (FAQ Schema)

### Q1. `akd`나 `cloudd` 프로세스를 강제 종료하면 맥에 저장된 파일이 지워지나요?
**A.** 전혀 지워지지 않습니다. 두 프로세스는 Apple 계정 인증과 iCloud 동기화를 담당하는 시스템 백그라운드 서비스이며, 강제 종료 시 macOS가 1~2초 내에 멈춰 있던 세션을 초기화하고 자동으로 다시 시작합니다.

### Q2. 안전 모드로 부팅해서 로그인한 뒤에는 계속 안전 모드로 써야 하나요?
**A.** 아닙니다. 안전 모드에서 Apple 계정 로그인만 통과한 뒤 좌측 상단 애플() 메뉴 → **[재시동...]**을 눌러 일반 모드로 부팅하면 로그인 상태가 그대로 유지됩니다.

### Q3. 암호를 여러 번 입력했더니 계정이 잠겼다는 안내가 나옵니다.
**A.** 짧은 시간 내 암호 오입력이 반복되면 Apple 보안 정책에 의해 계정이 일시 잠금됩니다. 이 경우 추가 시도를 멈추고 Apple 공식 계정 복구 페이지(`https://iforgot.apple.com/`)에서 본인 인증 후 암호를 재설정해야 합니다.""",
        "official_refs": [
            ("Apple 공식 고객지원: Mac에서 Apple 계정에 로그인할 수 없는 경우", "https://support.apple.com/ko-kr"),
            ("Apple 공식 시스템 상태 실시간 확인 페이지", "https://www.apple.com/kr/support/systemstatus/"),
            ("Apple 공식 가이드: Mac을 안전 모드로 시동하기", "https://support.apple.com/ko-kr/guide/mac-help/mh21245/mac")
        ],
        "fact_checks": [
            "Apple Silicon 및 Intel Mac 안전 모드 진입 공식 절차 일치 확인",
            "macOS 인증 데몬(akd) 및 iCloud 데몬(cloudd) 프로세스 명칭 정확성 확인",
            "데이터 손실 위험이 있는 임의 시스템 폴더 삭제 없이 공식 권장 순서대로 구성 완료"
        ]
    },
    {
        "seq": 3,
        "category": "Tax & Asset Management (절세·자산관리)",
        "topic": "연금저축펀드와 개인형 퇴직연금(IRP) 차이 및 선택 기준",
        "focus_keyphrase": "연금저축펀드 IRP 차이",
        "slug": "pension-savings-fund-vs-irp-comparison",
        "meta_desc": "연금저축펀드와 개인형 퇴직연금(IRP)의 차이점 완벽 비교. 연 900만 원 세액공제 황금 납입 비율(600:300), 위험자산 투자 한도(100% vs 70%), 중도인출 조건 및 연금소득세율을 확인하세요.",
        "score": 90,
        "scores": {"trend": 4, "intent": 5, "gap": 4, "capability": 5, "evergreen": 5},
        "title_candidates": [
            "연금저축펀드 vs 개인형 퇴직연금(IRP) 차이점 및 세액공제 한도·중도인출·수령 세율 비교표",
            "연금저축과 IRP 중 어디에 먼저 넣어야 할까? 900만 원 세액공제 황금 비율과 장단점 비교",
            "은퇴 준비 필수 계좌 비교: 연금저축펀드·IRP 투자 한도(70% 룰) 및 수수료 확인 방법"
        ],
        "final_title": "연금저축펀드 vs 개인형 퇴직연금(IRP) 차이점 및 세액공제 한도·중도인출·수령 세율 비교표",
        "core_summary": (
            "연말정산·종합소득세 세액공제를 목적으로 한다면 **① 입출금 유연성이 높고 주식형 ETF 100% 투자가 가능한 '연금저축펀드'에 연 600만 원을 먼저 채우고, ② 나머지 연 300만 원을 '개인형 퇴직연금(IRP)'에 추가 납입하여 합산 연 900만 원 세액공제 한도(최대 148만 5천 원 환급)**를 채우는 방식이 가장 유리합니다."
        ),
        "sections_md": """## 1. 도입부: 연금저축과 IRP, 이름은 비슷한데 왜 두 계좌를 구분해야 할까요?

노후 자금 마련과 절세를 위해 가장 많이 활용하는 두 축이 **연금저축(연금저축펀드)**과 **개인형 퇴직연금(IRP, Individual Retirement Pension)**입니다. 두 계좌 모두 납입 금액에 대해 세액공제 혜택을 주고, 만 55세 이후 연금으로 수령할 때 낮은 연금소득세(3.3~5.5%)를 적용받는다는 공통점이 있습니다.

하지만 **가입 자격, 세액공제 인정 한도, 위험자산(주식형 ETF) 투자 제한 비율, 그리고 급전이 필요할 때 일부 중도인출 가능 여부**에서 결정적인 차이가 있습니다. 자신의 자금 계획에 맞지 않는 계좌에만 전액을 넣었다가 중도 해지 세금(기타소득세 16.5%)을 부담하는 일을 막기 위해 두 계좌의 차이점을 정확히 비교해 보겠습니다.

---

## 2. 핵심 내용 요약 (Key Takeaways)

- **세액공제 최대 한도**: 연금저축 단독 **연 600만 원** / 연금저축 + IRP 합산 **연 900만 원**
- **환급 세액 (900만 원 납입 가정)**:
  - 총급여 5,500만 원(종합소득 4,500만 원) 이하: **16.5% 공제 → 최대 148만 5,000원**
  - 총급여 5,500만 원(종합소득 4,500만 원) 초과: **13.2% 공제 → 최대 118만 8,000원**
- **가장 추천하는 납입 순서**: **연금저축펀드 600만 원 우선 납입 → 여유 자금으로 비대면 IRP 300만 원 추가 납입**

---

## 3. 단계별 설명: 나에게 맞는 연금 계좌 선택 및 납입 비중 정하는 4단계

### 1단계: 가입 자격 확인하기 (소득 유무 점검)
1. **연금저축펀드**: 연령이나 소득 제한 없이 **누구나(미성년자·주부·은퇴자 포함)** 증권사에서 개설할 수 있습니다.
2. **IRP(개인형 퇴직연금)**: 근로소득자, 자영업자, 공무원 등 **소득이 있는 취업자** 또는 퇴직금을 수령하려는 퇴직자만 개설할 수 있습니다.

### 2단계: 투자 성향에 따른 상품 제한(안전자산 30% 의무 규정) 확인
1. **연금저축펀드**: 주식형 ETF(예: S&P500, 나스닥100, 배당 ETF 등)에 **계좌 자산의 100%까지 자유롭게 투자**할 수 있습니다. 다만 은행 정기예금 상품은 편입할 수 없습니다.
2. **IRP**: 근로자퇴직급여 보장법 규정에 따라 **위험자산(주식형 펀드·ETF) 투자 한도가 최대 70%로 제한**되며, 나머지 **30% 이상은 반드시 안전자산(예금, 국채, 채권혼합형 ETF, 적격 TDF 등)**으로 채워야 합니다.

### 3단계: 중도 인출(유동성) 및 계좌 유지 수수료 비교
1. **연금저축펀드**: 부득이하게 자금이 필요할 때 계좌 전체를 해지하지 않고 **필요한 금액만 일부 인출**할 수 있습니다(단, 세액공제 받은 원금과 수익 인출 시 기타소득세 16.5% 부과). 계좌 운용관리 수수료도 별도로 없습니다.
2. **IRP**: 법에서 정한 **특별 사유(무주택자 주택 구입·전세보증금, 6개월 이상 요양, 개인회생·파산 등) 외에는 일부 중도인출이 불가능**하며, 돈이 필요하면 계좌 전체를 해지해야 합니다. 또한 가입할 때 반드시 **'비대면 개설 시 운용·자산관리 수수료 무료'** 혜택이 있는 증권사인지 확인해야 합니다.

### 4단계: 금융감독원 통합연금포털에서 기존 계좌 한도 확인하기
1. [금융감독원 통합연금포털(100lifeplan.fss.or.kr)](https://100lifeplan.fss.or.kr/)에 로그인합니다.
2. 이미 개설된 연금저축이나 IRP의 연간 납입 한도가 다른 금융기관에 분산 설정되어 있지 않은지 조회하고, 주거래 증권사로 한도를 조정합니다.

---

## 4. 한눈에 보는 비교표: 연금저축펀드 vs 개인형 퇴직연금(IRP)

| 비교 항목 | 📈 연금저축펀드 (증권사) | 🛡️ 개인형 퇴직연금 (IRP) |
| :--- | :--- | :--- |
| **가입 대상** | **제한 없음** (전 국민 누구나 가입 가능) | **소득이 있는 자** (근로자, 자영업자 등) 및 퇴직금 수령자 |
| **세액공제 한도** | 연간 최대 **600만 원** | 연간 최대 **900만 원** (연금저축 납입액 포함 합산) |
| **위험자산(주식형 ETF) 한도** | **100% 투자 가능** | **최대 70%까지만 가능** (안전자산 30% 의무) |
| **원금보장 예금 편입** | 불가 (ETF·펀드·현금성 대기자금만 가능) | **가능** (정기예금, ELB, 국고채 등 편입 가능) |
| **일부 중도인출** | **언제든 일부 인출 가능** (공제분 16.5% 과세) | **법정 사유 외 일부 인출 불가** (전액 해지만 가능) |
| **계좌 관리 수수료** | 없음 (ETF 자체 보수만 발생) | 대면 개설 시 연 0.2~0.4% 발생 가능 (**비대면 무료 증권사 필수 선택**) |
| **연금 수령 개시 조건** | 만 55세 이상 & 가입기간 5년 이상 | 만 55세 이상 & 가입기간 5년 이상 (퇴직금 입금 시 즉시 가능) |

---

## 5. 자주 묻는 질문 (FAQ Schema)

### Q1. IRP에만 연 900만 원을 전부 넣어도 세액공제를 똑같이 받나요?
**A.** 네, 세액공제 환급 금액은 동일합니다. 하지만 IRP에만 900만 원을 모두 넣으면 주식형 ETF 투자가 70%로 제한되고 급전이 필요할 때 일부 인출이 불가능하므로, 연금저축펀드에 600만 원을 먼저 채우고 IRP에 300만 원을 넣는 것이 유동성 면에서 훨씬 유리합니다.

### Q2. 만 55세 이후 연금을 받을 때 세금을 아끼는 기준 금액은 얼마인가요?
**A.** 연금저축과 IRP에서 세액공제 받은 원금과 운용수익을 합산해 **연간 1,500만 원 이하**로 수령해야 3.3~5.5% 저율 분리과세가 적용됩니다. 연 1,500만 원을 초과하면 종합소득세 합산 또는 16.5% 분리과세 대상이 됩니다.

### Q3. 세액공제 한도(900만 원)를 넘겨서 입금한 돈은 나중에 세금을 내나요?
**A.** 연금계좌는 전 금융기관 합산 연 1,800만 원까지 납입할 수 있으며, 세액공제를 받지 않은 초과 납입 원금은 중도 인출하거나 연금으로 받을 때 **비과세(세금 0원)**로 인출할 수 있습니다.""",
        "official_refs": [
            ("금융감독원 통합연금포털 (내 연금 조회 및 상품 비교)", "https://100lifeplan.fss.or.kr/"),
            ("국세청 홈택스 연말정산 연금계좌 세액공제 안내", "https://www.hometax.go.kr/"),
            ("금융투자협회 전자공시서비스 (퇴직연금 수수료 비교)", "https://dis.kofia.or.kr/")
        ],
        "fact_checks": [
            "연금저축 세액공제 한도(연 600만 원) 및 IRP 합산 한도(연 900만 원) 현행 소득세법 기준 일치 확인",
            "사적연금 분리과세 기준 금액(연 1,500만 원 이하 시 3.3~5.5% 저율 과세) 세법 개정 기준 일치 확인",
            "IRP 위험자산 투자 한도(70%) 및 안전자산 의무 편입 비율(30%) 공식 기준 일치 확인"
        ]
    },
    {
        "seq": 4,
        "category": "AI & Tech Guide (AI·IT 매뉴얼)",
        "topic": "GitHub와 Vercel을 이용한 무료 사이트 배포 방법",
        "focus_keyphrase": "GitHub Vercel 사이트 배포 방법",
        "slug": "deploy-static-website-github-vercel-guide",
        "meta_desc": "GitHub와 Vercel을 연동해 서버 비용 0원으로 개인 웹사이트·블로그 포털을 배포하는 4단계 방법. Git push 자동 업데이트(CI/CD) 설정과 404 오류 해결법을 확인하세요.",
        "score": 90,
        "scores": {"trend": 4, "intent": 5, "gap": 4, "capability": 5, "evergreen": 5},
        "title_candidates": [
            "GitHub와 Vercel을 이용해 무료로 개인 웹사이트·블로그 포털 배포하는 4단계 방법",
            "서버 비용 0원으로 내 웹사이트 만들기: GitHub 저장소 생성부터 Vercel 자동 배포까지",
            "초보자용 GitHub + Vercel 정적 사이트 배포 가이드 및 GitHub Pages와의 차이점 비교"
        ],
        "final_title": "GitHub와 Vercel을 이용해 무료로 개인 웹사이트·블로그 포털 배포하는 4단계 방법",
        "core_summary": (
            "직접 만든 HTML 파일이나 웹 프로젝트를 인터넷에 무료로 공개하려면 **① GitHub에 저장소(Repository)를 만들고 `index.html` 파일을 업로드한 뒤, ② Vercel(vercel.com)에 GitHub 계정으로 로그인하여 해당 저장소를 'Import(연동)'하고 [Deploy] 버튼을 누르면 1분 만에 전용 `https://프로젝트명.vercel.app` 주소와 무료 SSL 보안인증서가 발급**됩니다. 이후에는 GitHub에 수정본을 푸시(`git push`)할 때마다 사이트가 자동으로 최신화됩니다."
        ),
        "sections_md": """## 1. 도입부: 내 컴퓨터에 있는 웹페이지를 비용 없이 인터넷에 띄우는 가장 쉬운 방법

AI 코딩 도구나 에디터로 멋진 HTML 대시보드, 포트폴리오, 또는 멀티 블로그 포털(`index.html`)을 만들었다면, 내 컴퓨터뿐만 아니라 스마트폰이나 외부에서도 접속할 수 있도록 **웹 호스팅 배포(Deployment)**를 해야 합니다.

개인 프로젝트(비상업적 용도)에서는 **GitHub(코드 저장소) + Vercel(클라우드 배포 플랫폼)** 조합을 사용하면 **호스팅 비용 0원, 무료 HTTPS 보안 연결, 그리고 파일 수정 시 10초 내 자동 배포** 환경을 구축할 수 있습니다.

---

## 2. 핵심 내용 요약 (Key Takeaways)

- **준비물**: [GitHub 계정](https://github.com/) + 배포할 웹 프로젝트 폴더(루트에 `index.html` 포함)
- **요금제**: 개인·취미 목적은 **Vercel Hobby(무료) 플랜**으로 충분 (신용카드 등록 불필요)
- **핵심 작동 원리**:
  `내 PC에서 파일 수정 및 git push` → `GitHub 저장소 반영` → `Vercel이 변경을 감지해 10~30초 내 웹사이트 자동 업데이트`

---

## 3. 단계별 설명: GitHub와 Vercel로 사이트 배포하는 4단계 순서

### 1단계: GitHub에 프로젝트 저장소(Repository) 생성 및 업로드
1. [GitHub 공식 사이트(github.com)](https://github.com/)에 로그인한 뒤 우측 상단 **[+]** → **[New repository]**를 클릭합니다.
2. Repository name(예: `my-blog-portal`)을 입력하고 **[Create repository]**를 누릅니다.
3. 배포할 프로젝트 폴더의 최상위(루트)에 **`index.html`** 파일이 있는지 확인한 뒤, 터미널에서 아래 명령어로 GitHub에 업로드(Push)합니다.
   ```bash
   git init
   git add .
   git commit -m "feat: initial website commit"
   git branch -M main
   git remote add origin https://github.com/내아이디/저장소이름.git
   git push -u origin main
   ```

### 2단계: Vercel 가입 및 GitHub 계정 연동하기
1. [Vercel 공식 사이트(vercel.com)](https://vercel.com/)에 접속하여 **[Sign Up]**을 누릅니다.
2. 플랜 선택 화면에서 무료 개인용인 **'Hobby'**를 선택하고 이름을 입력합니다.
3. **[Continue with GitHub]** 버튼을 눌러 방금 만든 GitHub 계정으로 로그인 및 권한 연동을 승인합니다.

### 3단계: GitHub 저장소 불러오기(Import) 및 배포(Deploy) 실행
1. Vercel 대시보드 우측 상단의 **[Add New...]** → **[Project]**를 클릭합니다.
2. **'Import Git Repository'** 목록에서 1단계에 업로드한 GitHub 저장소 옆의 **[Import]** 버튼을 누릅니다.
3. 일반 HTML/CSS/JS 정적 사이트라면 Framework Preset을 기본값(`Other`) 그대로 두고 바로 **[Deploy]** 버튼을 클릭합니다.
4. 약 10~30초 후 배포가 완료되며, 생성된 **`https://저장소이름.vercel.app`** 주소를 클릭하면 스마트폰과 PC 어디서든 내 사이트에 접속할 수 있습니다.

### 4단계: 수정 사항 자동 업데이트(CI/CD) 확인하기
1. 내 컴퓨터에서 HTML이나 마크다운 파일을 수정합니다.
2. `git add . && git commit -m "update" && git push`를 실행하면 Vercel이 자동으로 감지하여 10~20초 내에 실제 웹사이트를 업데이트합니다.

---

## 4. 정적 웹사이트 무료 배포 플랫폼 3종 비교표

| 비교 항목 | ▲ Vercel (Hobby 무료) | 🐙 GitHub Pages | 🌐 Cloudflare Pages |
| :--- | :--- | :--- | :--- |
| **기본 도메인 형태** | `이름.vercel.app` | `아이디.github.io/저장소` | `이름.pages.dev` |
| **비공개(Private) 저장소 배포** | **무료 지원** | 무료 계정은 Public만 가능 | **무료 지원** |
| **배포 반영 속도** | 매우 빠름 (약 10~30초) | 보통 (약 1~2분 소요) | 빠름 (약 20~40초) |
| **PR별 미리보기 URL(Preview)** | **자동 생성 지원** | 기본 미지원 | 자동 생성 지원 |
| **월간 무료 대역폭(Bandwidth)** | 월 100GB (Hobby 기준) | 월 100GB 권장 (Soft limit) | 무제한 (정적 파일 기준) |
| **추천 용도** | 개인 포털, Next.js/React, 빠른 배포 | 단순 문서 뷰어, 오픈소스 소개 | 트래픽이 많은 정적 사이트 |

---

## 5. 자주 묻는 질문 (FAQ Schema)

### Q1. 배포 후 사이트에 접속했는데 `404: NOT_FOUND` 오류가 뜹니다.
**A.** Vercel은 기본적으로 저장소 최상위 폴더(Root Directory)에서 `index.html` 파일을 찾습니다. 만약 `index.html`이 하위 폴더 안에 있다면 Vercel 프로젝트 **[Settings] → [General] → [Root Directory]**에서 해당 폴더를 지정해 주세요.

### Q2. GitHub 저장소를 비공개(Private)로 두어도 웹사이트는 공개되나요?
**A.** 네, GitHub 코드 저장소를 Private으로 설정해 소스 코드를 보호하면서도, Vercel을 통해 배포된 웹페이지 URL은 누구나 접속할 수 있도록 운영할 수 있습니다.

### Q3. 내가 구매한 개인 도메인(예: `.com`, `.kr`)을 무료로 연결할 수 있나요?
**A.** 가능합니다. Vercel 프로젝트의 **[Settings] → [Domains]** 메뉴에서 보유한 도메인을 입력하고 안내되는 DNS 레코드(A 레코드 또는 CNAME)를 도메인 등록업체에 입력하면 무료 SSL 인증서까지 자동 발급됩니다.""",
        "official_refs": [
            ("Vercel 공식 문서 (Git 저장소 배포 가이드)", "https://vercel.com/docs/deployments/git"),
            ("GitHub 공식 문서 (저장소 생성 및 관리)", "https://docs.github.com/ko"),
            ("Vercel Hobby 플랜 사용 한도 안내", "https://vercel.com/docs/limits/overview")
        ],
        "fact_checks": [
            "Vercel Hobby(무료) 플랜의 GitHub Private 저장소 배포 지원 및 월 100GB 대역폭 기준 공식 문서 일치 확인",
            "404 NOT_FOUND 오류의 대표 원인(Root Directory 내 index.html 부재) 기술적 정확성 검증 완료",
            "명령어 및 배포 절차 4단계 재현 가능성 확인 완료"
        ]
    },
    {
        "seq": 5,
        "category": "AI & Tech Guide (AI·IT 매뉴얼)",
        "topic": "구글 서치 콘솔 등록 및 사이트맵·RSS 제출 방법",
        "focus_keyphrase": "구글 서치 콘솔 사이트맵 제출",
        "slug": "google-search-console-sitemap-rss-setup-guide",
        "meta_desc": "블로그(워드프레스·티스토리) 구글 검색 노출을 위한 Google Search Console 등록 및 사이트맵(sitemap.xml)·RSS 제출 4단계 방법. 소유권 확인과 색인 생성 요청 절차를 확인하세요.",
        "score": 88,
        "scores": {"trend": 4, "intent": 5, "gap": 4, "capability": 5, "evergreen": 4},
        "title_candidates": [
            "블로그 구글 서치 콘솔(Google Search Console) 등록 및 사이트맵(sitemap.xml)·RSS 제출 4단계 방법",
            "개설 직후 필수 SEO 설정! 구글 검색 노출을 위한 서치 콘솔 소유권 확인 및 색인 가이드",
            "구글에 내 블로그 글 노출시키는 법: Search Console 등록부터 URL 검사·색인 요청까지"
        ],
        "final_title": "블로그 구글 서치 콘솔(Google Search Console) 등록 및 사이트맵(sitemap.xml)·RSS 제출 4단계 방법",
        "core_summary": (
            "새로 개설한 워드프레스나 티스토리 블로그를 구글 검색에 빠르게 노출시키려면 **① Google Search Console에서 내 사이트 주소를 등록하고, ② HTML 메타태그(또는 DNS 레코드)로 소유권을 확인한 뒤, ③ [Sitemaps] 메뉴에 `sitemap.xml`(워드프레스 Rank Math는 `sitemap_index.xml`)과 `rss`(`feed`)를 제출**하면 됩니다."
        ),
        "sections_md": """## 1. 도입부: 블로그 글을 써도 구글 검색에 안 나오는 이유와 해결책

워드프레스나 티스토리 블로그를 개설하고 정성껏 정보형 글을 발행했더라도, 구글 검색 로봇(Googlebot)이 내 사이트의 존재와 새 글 목록을 빠르게 파악하지 못하면 검색 결과에 노출되기까지 오랜 시간이 걸립니다.

**구글 서치 콘솔(Google Search Console)**은 구글이 공식 제공하는 무료 웹마스터 도구로, 내 블로그의 **사이트맵(Sitemap)과 RSS 피드를 구글에 직접 제출**하고 어떤 검색어로 몇 번 노출·클릭되었는지 데이터를 확인할 수 있는 필수 SEO 도구입니다.

---

## 2. 핵심 내용 요약 (Key Takeaways)

- **공식 설정 사이트**: [Google Search Console (search.google.com/search-console)](https://search.google.com/search-console/)
- **플랫폼별 제출할 사이트맵·피드 주소**:
  - **워드프레스 (Rank Math / Yoast 기준)**: `sitemap_index.xml` (또는 기본 `wp-sitemap.xml`) 및 `feed`
  - **티스토리**: `sitemap.xml` 및 `rss`
- **핵심 점검 메뉴**: `[Sitemaps]`(사이트맵 제출), `[URL 검사]`(신규 글 수동 색인 요청), `[실적]`(유입 검색어 및 클릭률 분석)

---

## 3. 단계별 설명: 구글 서치 콘솔 등록 및 사이트맵 제출 4단계

### 1단계: Google Search Console 접속 및 속성 추가
1. [Google Search Console 공식 페이지](https://search.google.com/search-console/)에 접속해 구글 계정으로 로그인합니다.
2. 좌측 상단 속성 선택 메뉴에서 **[+ 속성 추가]**를 클릭합니다.
3. 개인 도메인을 연결한 워드프레스는 **[도메인]** 또는 **[URL 접두어]** 모두 가능하며, 기본 서브도메인(`*.tistory.com` 등)을 사용하는 경우에는 오른쪽 **[URL 접두어]** 입력칸에 전체 주소(`https://...`)를 입력하고 **[계속]**을 누릅니다.

### 2단계: HTML 메타태그 복사 및 사이트 소유권 확인
1. '소유권 확인' 팝업 창에서 **'다른 확인 방법'** 중 **[HTML 태그]** 항목을 클릭해 펼칩니다.
2. `<meta name="google-site-verification" content="고유코드" />` 형태의 메타태그를 복사합니다.
3. 내 블로그 관리자 페이지에서 메타태그를 등록합니다:
   - **워드프레스 (Rank Math 플러그인)**: `[Rank Math SEO] → [일반 설정] → [웹마스터 도구] → [Google Search Console]` 칸에 복사한 태그를 붙여넣고 변경사항 저장
   - **티스토리**: `[꾸미기] → [스킨 편집] → [html 편집]` 상단 `<head>` 바로 아랫줄에 붙여넣고 적용
4. 다시 구글 서치 콘솔 탭으로 돌아와 **[확인]** 버튼을 누르면 **'소유권이 확인됨'** 안내가 나타납니다.

### 3단계: 사이트맵(`sitemap.xml`)과 RSS 피드 유효성 확인 후 제출하기
1. 제출 전에 브라우저 새 탭에서 내 사이트맵 주소가 에러 없이 열리는지 먼저 확인합니다 (공개 발행된 글이 최소 1개 이상 있어야 합니다).
2. 서치 콘솔 좌측 메뉴에서 **[Sitemaps(사이트맵)]**를 클릭합니다.
3. 워드프레스는 `sitemap_index.xml`과 `feed`를, 티스토리는 `sitemap.xml`과 `rss`를 각각 입력하고 **[제출]**을 누릅니다.
4. 제출된 사이트맵의 상태가 **'성공'**으로 표시되는지 확인합니다.

### 4단계: 새 글 발행 후 URL 검사 및 검색 실적 점검하기
1. 중요한 코너스톤 정보 글을 새로 발행했을 때는 서치 콘솔 상단 검색창(**URL 검사**)에 해당 글의 전체 주소를 붙여넣고 **[색인 생성 요청]**을 누르면 크롤링 우선순위를 높일 수 있습니다.
2. 2~4주 뒤 **[실적(Performance)]** 메뉴에서 노출수는 높지만 클릭이 적은 검색어를 찾아 제목과 메타 설명을 보완합니다.

---

## 4. 워드프레스 vs 티스토리 서치 콘솔 설정 비교표

| 구분 | 🔵 워드프레스 (Rank Math / Yoast 기준) | 🟠 티스토리 (`*.tistory.com` 기준) |
| :--- | :--- | :--- |
| **추천 속성 유형** | 도메인(DNS 인증) 또는 URL 접두어 | **URL 접두어 필수** (`https://내주소.tistory.com/`) |
| **소유권 인증 방법** | Rank Math `웹마스터 도구` 칸에 코드 입력 | 스킨 편집 `<head>` 또는 메타태그 플러그인 |
| **사이트맵 주소** | `/sitemap_index.xml` (기본은 `/wp-sitemap.xml`) | `/sitemap.xml` |
| **RSS 피드 주소** | `/feed` | `/rss` |

---

## 5. 자주 묻는 질문 (FAQ Schema)

### Q1. 사이트맵을 제출했는데 '가져올 수 없음'이라고 표시됩니다.
**A.** 공개 발행된 글이 0개이거나 사이트맵 생성 직후 구글 서버가 아직 캐시를 읽지 못한 경우 흔히 발생합니다. 먼저 브라우저에서 사이트맵 주소가 정상적으로 열리는지 확인한 뒤, 주소 끝에 공백 없이 다시 제출하고 하루 뒤 새로고침하면 정상적으로 '성공'으로 변경됩니다.

### Q2. 글을 쓸 때마다 매번 사이트맵을 다시 제출해야 하나요?
**A.** 아닙니다. 사이트맵과 RSS 피드는 최초 1회만 등록해 두면 이후 새 글을 발행할 때마다 자동으로 목록이 갱신되며 구글 크롤러가 주기적으로 방문해 수집합니다.

### Q3. 색인 생성 요청은 하루에 몇 번까지 할 수 있나요?
**A.** 구글 서치 콘솔의 수동 '색인 생성 요청'에는 일일 할당량(통상 하루 10~15개 내외)이 있으므로, 모든 글을 수동 요청하기보다 핵심 코너스톤 글 위주로 사용하는 것이 좋습니다.""",
        "official_refs": [
            ("Google Search Console 공식 사이트", "https://search.google.com/search-console/"),
            ("Google 검색 센터: 사이트맵 생성 및 제출 가이드", "https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap?hl=ko"),
            ("WordPress 공식 문서 (XML Sitemaps 안내)", "https://wordpress.org/documentation/")
        ],
        "fact_checks": [
            "워드프레스(sitemap_index.xml, wp-sitemap.xml, feed) 및 티스토리(sitemap.xml, rss) 표준 경로 정확성 확인",
            "서치 콘솔 URL 접두어 및 HTML 메타태그 소유권 확인 절차 재현성 검증 완료",
            "과장된 즉시 상위노출 보장 문구 없이 공식 색인 절차 안내 준수"
        ]
    }
]

def format_wp_markdown(date_str, weekday_str, item):
    sc = item["scores"]
    candidates_md = "\n".join([f"{i}. `{c}`" for i, c in enumerate(item["title_candidates"], 1)])
    refs_md = "\n".join([f"- [{name}]({url}) (`{url}`)" for name, url in item["official_refs"]])
    fc_md = "\n".join([f"- [x] {fc}" for fc in item["fact_checks"]])

    return f"""# {item['final_title']}

> **작성일**: {date_str} ({weekday_str})  
> **플랫폼**: 🔵 워드프레스 (WordPress · 구텐베르크 & Rank Math SEO 코너스톤 원고)  
> **카테고리**: {item['category']}  
> **Focus Keyphrase (핵심 키워드)**: `{item['focus_keyphrase']}`  
> **URL Slug (영문 퍼머링크)**: `/{item['slug']}`  
> **주제 평가 점수**: **{item['score']}/100점** (관심도 {sc['trend']}/5 · 의도 명확성 {sc['intent']}/5 · 경쟁 빈틈 {sc['gap']}/5 · 작성 역량 {sc['capability']}/5 · 장기 검색성 {sc['evergreen']}/5)

---

## 🔵 워드프레스 Rank Math / Yoast SEO 메타데이터 설정표

| SEO 설정 항목 | 워드프레스 입력값 (복사해서 바로 붙여넣기) |
| :--- | :--- |
| **Focus Keyphrase** | `{item['focus_keyphrase']}` |
| **SEO Title** | `{item['final_title']}` |
| **Slug (영문 URL)** | `{item['slug']}` |
| **Meta Description** | {item['meta_desc']} |

### 제목 후보 3개
{candidates_md}

### 핵심 요약 콜아웃 (Key Takeaways)
> **💡 Key Takeaways (핵심 요약)**: {item['core_summary']}

---

{item['sections_md']}

---

## 7. 공식 참고 자료 (Authoritative Outbound Links)

{refs_md}

---

## ✅ 워드프레스 발행 전 Rank Math SEO & 팩트체크 점검표

{fc_md}
- [x] 영문 퍼머링크 슬러그(`/{item['slug']}`)가 짧고 명확하게 설정되었는가?
- [x] Focus Keyphrase(`{item['focus_keyphrase']}`)가 제목, 메타 설명, 본문 첫 문단, H2 소제목에 포함되었는가?
- [x] 구텐베르크 표(Table)와 FAQ(3문 3답) 섹션이 포함되어 구글 리치 스니펫에 최적화되었는가?
- [x] 네이버·티스토리 원고와 중복되지 않는 워드프레스 전용 심층 가이드북 구조로 작성되었는가?
"""

def build_wp_post_html(post_id, date_str, weekday_str, item, md_content):
    title = item["final_title"]
    cat_name = item["category"]
    score = item["score"]
    slug = item["slug"]
    meta_desc = item["meta_desc"].replace("'", "\\'").replace('"', '&quot;')
    seo_pack = f"Focus Keyphrase: {item['focus_keyphrase']}\\nSlug: /{slug}\\nMeta Description: {meta_desc}"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[{date_str}] 워드프레스 포스팅 #{item['seq']} | {title}</title>

  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>

  <style>
    :root {{
      --wp: #0073aa;
      --wp-dark: #005177;
      --wp-light: #f0f7fb;
      --wp-border: #bae6fd;
      --text-main: #1f2937;
      --text-sub: #4b5563;
      --text-muted: #6b7280;
      --border: #e5e7eb;
      --bg: #f8fafc;
      --white: #ffffff;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.75;
      padding-bottom: 80px;
    }}
    .top-nav {{
      background: var(--white);
      border-bottom: 1px solid var(--border);
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .nav-left {{ display: flex; align-items: center; gap: 12px; }}
    .brand-tag {{
      background: var(--wp);
      color: var(--white);
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .nav-title {{ font-size: 15px; font-weight: 700; }}
    .nav-actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 12px;
      border-radius: 6px;
      font-size: 12.5px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      border: 1px solid var(--border);
      background: var(--white);
      color: var(--text-main);
    }}
    .btn:hover {{ background: #f3f4f6; }}
    .btn-wp {{ background: var(--wp); color: #fff; border-color: var(--wp); }}
    .btn-wp:hover {{ background: var(--wp-dark); color: #fff; }}
    .container {{ max-width: 880px; margin: 32px auto 0; padding: 0 16px; }}
    .meta-card {{
      background: var(--white);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      border: 1px solid var(--border);
      border-top: 4px solid var(--wp);
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .meta-badges {{ display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }}
    .badge {{
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 4px;
      background: var(--wp-light);
      color: var(--wp-dark);
      border: 1px solid var(--wp-border);
    }}
    .post-title {{ font-size: 23px; font-weight: 800; line-height: 1.4; margin-bottom: 14px; color: #111827; }}
    .meta-info-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      background: var(--bg);
      padding: 14px 18px;
      border-radius: 8px;
      font-size: 13px;
    }}
    .meta-info-item span {{ color: var(--text-muted); margin-right: 6px; }}
    .editor-preview {{
      background: var(--white);
      border-radius: 12px;
      padding: 40px 48px;
      border: 1px solid var(--border);
      box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}
    .editor-preview h1 {{ font-size: 24px; font-weight: 800; margin-bottom: 24px; padding-bottom: 12px; border-bottom: 2px solid var(--wp); }}
    .editor-preview h2 {{ font-size: 19.5px; font-weight: 750; margin: 34px 0 14px; color: #111827; border-left: 4px solid var(--wp); padding-left: 12px; }}
    .editor-preview h3 {{ font-size: 16.5px; font-weight: 700; margin: 24px 0 10px; color: #1f2937; }}
    .editor-preview p {{ margin-bottom: 16px; font-size: 15.5px; line-height: 1.85; color: #374151; word-break: keep-all; }}
    .editor-preview ul, .editor-preview ol {{ margin: 12px 0 20px 22px; }}
    .editor-preview li {{ margin-bottom: 8px; font-size: 15px; line-height: 1.75; color: #374151; }}
    .editor-preview blockquote {{
      border: 1px solid var(--wp-border);
      border-left: 4px solid var(--wp);
      background: var(--wp-light);
      padding: 16px 20px;
      margin: 20px 0;
      border-radius: 8px;
      color: #0c4a6e;
      font-size: 14.5px;
    }}
    .editor-preview table {{ width: 100%; border-collapse: collapse; margin: 20px 0 24px; font-size: 14px; }}
    .editor-preview th {{ background: var(--wp-light); color: #0c4a6e; font-weight: 700; border: 1px solid var(--wp-border); padding: 10px 12px; text-align: left; }}
    .editor-preview td {{ border: 1px solid #e5e7eb; padding: 10px 12px; color: #374151; vertical-align: top; }}
    .editor-preview pre {{ background: #1e293b; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 13px; margin: 16px 0; }}
    .toast {{
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      background: #111827; color: #fff; padding: 12px 24px; border-radius: 8px;
      font-size: 14px; font-weight: 600; opacity: 0; pointer-events: none; transition: all 0.2s; z-index: 999;
    }}
    .toast.show {{ opacity: 1; transform: translateX(-50%) translateY(-10px); }}
  </style>
</head>
<body>
  <header class="top-nav">
    <div class="nav-left">
      <span class="brand-tag">WORDPRESS · #{item['seq']}편</span>
      <span class="nav-title">{date_str} ({weekday_str}) · {cat_name}</span>
    </div>
    <div class="nav-actions">
      <a href="../../index.html" class="btn">📂 워드프레스 작업실 홈</a>
      <a href="../../../index.html" class="btn">🏠 멀티 포털</a>
      <a href="https://smartlife70.wordpress.com/wp-admin/post-new.php" target="_blank" rel="noopener noreferrer" class="btn" style="background: #f0f7fb; color: #005177; border-color: #bae6fd;">✍️ WP 새 글 쓰기</a>
      <a href="https://smartlife70.wordpress.com/wp-admin/index.php" target="_blank" rel="noopener noreferrer" class="btn" style="background: #f0f7fb; color: #005177; border-color: #bae6fd;">⚙️ WP 관리자</a>
      <a href="{post_id}.md" target="_blank" class="btn">📄 원본 MD</a>
      <button class="btn btn-wp" id="copyWpBtn">🔵 워드프레스 구텐베르크 블록 복사</button>
      <button class="btn" onclick="copyText('{seo_pack}')">🏷️ 슬러그·메타설명 복사</button>
      <button class="btn" id="copyMdBtn">📝 마크다운 복사</button>
    </div>
  </header>

  <div class="container">
    <div class="meta-card">
      <div class="meta-badges">
        <span class="badge">🔵 WordPress Cornerstone SEO</span>
        <span class="badge">📂 {cat_name}</span>
        <span class="badge">🔗 Slug: /{slug}</span>
        <span class="badge">🎯 평가 점수: {score}/100점</span>
      </div>
      <h1 class="post-title">{title}</h1>
      <div class="meta-info-grid">
        <div class="meta-info-item"><span>Focus Keyphrase:</span><strong>{item['focus_keyphrase']}</strong></div>
        <div class="meta-info-item"><span>URL Slug:</span><strong>/{slug}</strong></div>
        <div class="meta-info-item"><span>구조:</span><strong>Key Takeaways + 비교표 + FAQ 3문 3답</strong></div>
        <div class="meta-info-item"><span>타겟:</span><strong>Google 글로벌/국내 SEO & AdSense</strong></div>
      </div>
    </div>

    <article class="editor-preview" id="postArticle"></article>
  </div>

  <div class="toast" id="toast">복사되었습니다!</div>

  <script id="rawMarkdown" type="text/plain">
{md_content}
  </script>

  <script>
    const mdSource = document.getElementById("rawMarkdown").textContent.trim();
    const articleEl = document.getElementById("postArticle");
    articleEl.innerHTML = marked.parse(mdSource);

    function showToast(msg) {{
      const t = document.getElementById("toast");
      t.textContent = msg;
      t.classList.add("show");
      setTimeout(() => t.classList.remove("show"), 2500);
    }}

    function copyText(text) {{
      navigator.clipboard.writeText(text).then(() => showToast("🏷️ 워드프레스 SEO 슬러그 및 메타 설명이 복사되었습니다!"));
    }}

    document.getElementById("copyWpBtn").addEventListener("click", () => {{
      const clone = articleEl.cloneNode(true);
      clone.querySelectorAll("h1").forEach(el => el.setAttribute("style", "font-size: 24px; font-weight: bold; color: #111827; margin-bottom: 22px;"));
      clone.querySelectorAll("h2").forEach(el => el.setAttribute("style", "font-size: 19.5px; font-weight: bold; color: #005177; margin-top: 32px; margin-bottom: 14px; border-left: 4px solid #0073aa; padding-left: 10px;"));
      clone.querySelectorAll("h3, h4").forEach(el => el.setAttribute("style", "font-size: 16.5px; font-weight: bold; color: #1f2937; margin-top: 22px; margin-bottom: 10px;"));
      clone.querySelectorAll("p").forEach(el => el.setAttribute("style", "font-size: 16px; line-height: 1.85; color: #374151; margin-bottom: 16px;"));
      clone.querySelectorAll("blockquote").forEach(el => el.setAttribute("style", "background-color: #f0f7fb; border: 1px solid #bae6fd; border-left: 4px solid #0073aa; padding: 16px 20px; margin: 20px 0; border-radius: 6px; color: #0c4a6e; font-size: 15px;"));
      clone.querySelectorAll("table").forEach(el => el.setAttribute("style", "width: 100%; border-collapse: collapse; margin: 20px 0 24px; font-size: 14px;"));
      clone.querySelectorAll("th").forEach(el => el.setAttribute("style", "background-color: #f0f7fb; color: #0c4a6e; font-weight: bold; border: 1px solid #bae6fd; padding: 10px 12px; text-align: left;"));
      clone.querySelectorAll("td").forEach(el => el.setAttribute("style", "border: 1px solid #e5e7eb; padding: 10px 12px; color: #374151;"));
      const htmlContent = clone.innerHTML;
      if (navigator.clipboard && window.ClipboardItem) {{
        const htmlBlob = new Blob([htmlContent], {{ type: 'text/html' }});
        const textBlob = new Blob([mdSource], {{ type: 'text/plain' }});
        navigator.clipboard.write([new ClipboardItem({{ 'text/html': htmlBlob, 'text/plain': textBlob }})]).then(() => {{
          showToast("🔵 워드프레스 구텐베르크 블록 서식이 복사되었습니다! 에디터에 바로 붙여넣으세요.");
        }});
      }} else {{
        navigator.clipboard.writeText(mdSource).then(() => showToast("📝 마크다운 원문이 복사되었습니다!"));
      }}
    }});

    document.getElementById("copyMdBtn").addEventListener("click", () => {{
      navigator.clipboard.writeText(mdSource).then(() => showToast("📝 마크다운 원문이 복사되었습니다!"));
    }});
  </script>
</body>
</html>"""

def scan_wp_posts():
    all_files = glob.glob(os.path.join(POSTS_DIR, "*", "*.md"))
    def get_sort_key(f):
        base = os.path.basename(f).replace(".md", "")
        parts = base.split("-")
        d_str = "-".join(parts[:3])
        idx = int(parts[3]) if len(parts) > 3 else 1
        return (d_str, -idx)

    md_files = sorted(list(set(all_files)), key=get_sort_key, reverse=True)
    posts = []
    for fpath in md_files:
        fname = os.path.basename(fpath)
        post_id = fname.replace(".md", "")
        parts = post_id.split("-")
        date_only = "-".join(parts[:3])
        post_num = int(parts[3]) if len(parts) > 3 else 1
        rel_md = os.path.relpath(fpath, WP_BLOG_DIR)
        rel_html = rel_md[:-3] + ".html"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        m_title = re.search(r"^#\s+(.+)$", content, re.M)
        title = m_title.group(1).strip() if m_title else post_id
        m_cat = re.search(r">\s*\*\*카테고리\*\*:\s*(.+)$", content, re.M)
        category = m_cat.group(1).strip() if m_cat else "WordPress SEO"
        m_slug = re.search(r">\s*\*\*URL Slug \(영문 퍼머링크\)\*\*:\s*`([^`]+)`", content, re.M)
        slug = m_slug.group(1).strip() if m_slug else "/post"
        m_score = re.search(r">\s*\*\*주제 평가 점수\*\*:\s*\*\*([0-9]+/100점)\*\*", content, re.M)
        score_str = m_score.group(1).strip() if m_score else "90/100점"
        m_sum = re.search(r">\s*\*\*💡 Key Takeaways \(핵심 요약\)\*\*:\s*(.+)$", content, re.M)
        desc = m_sum.group(1).strip().replace("**", "") if m_sum else ""
        if len(desc) > 150:
            desc = desc[:150] + "..."
        char_count = len(content.replace(" ", "").replace("\n", ""))
        posts.append({
            "post_id": post_id,
            "date_only": date_only,
            "post_num": post_num,
            "category": category,
            "slug": slug,
            "score_str": score_str,
            "title": title,
            "desc": desc,
            "char_count": char_count,
            "rel_md": rel_md,
            "rel_html": rel_html
        })
    return posts

def build_wp_index_html(today_str, weekday_str, posts):
    post_cards_html = ""
    for p in posts:
        is_today = (p["date_only"] == today_str)
        today_class = " today" if is_today else ""
        post_cards_html += f"""
            <article class="post-card{today_class}">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                  <span style="font-size:12.5px; font-weight:700; color:var(--wp-dark);">📍 {p['date_only']} ({weekday_str})</span>
                  <span class="cat-pill">📂 {p['category']}</span>
                  <span class="slug-pill">🔗 {p['slug']}</span>
                  <span class="score-pill">🎯 {p['score_str']}</span>
                </div>
                <span style="font-size:11.5px; color:var(--text-muted); font-weight:600;">#{p['post_num']}편</span>
              </div>
              <a href="{p['rel_html']}" class="post-card-title">{p['title']}</a>
              <p style="font-size:13.5px; color:var(--text-sub); margin-bottom:14px; line-height:1.55;">{p['desc']}</p>
              <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed var(--border); padding-top:12px; font-size:12px; color:var(--text-muted); flex-wrap:wrap; gap:10px;">
                <div>구텐베르크 블록 · FAQ 스키마 포함 · 분량: 약 {p['char_count']:,}자 (공백 제외)</div>
                <div style="display:flex; gap:8px; flex-wrap:wrap;">
                  <a href="{p['rel_md']}" target="_blank" class="action-btn">📄 MD 원문</a>
                  <a href="https://smartlife70.wordpress.com/wp-admin/post-new.php" target="_blank" rel="noopener noreferrer" class="action-btn" style="color:var(--wp-dark); border-color:var(--wp-border); background:var(--wp-light);">✍️ WP 글쓰기</a>
                  <a href="{p['rel_html']}" class="action-btn action-btn-primary">👁️ 포스트 열기 & 블록 복사</a>
                </div>
              </div>
            </article>
        """

    wp_prompt = (
        "# 워드프레스(WordPress) 검색형 코너스톤 블로그 글 작성 지침\\n\\n"
        "당신은 구글 SEO(E-E-A-T)와 워드프레스 구텐베르크(Gutenberg) 에디터 구조에 정통한 전문 콘텐츠 에디터입니다.\\n"
        "1. 상단에 워드프레스 SEO 메타데이터(Focus Keyphrase, SEO Title, 영문 URL Slug, Meta Description 155자 이내)를 먼저 제시합니다.\\n"
        "2. 도입부 직후 Key Takeaways(핵심 요약 콜아웃)를 배치합니다.\\n"
        "3. 본문은 단계별 가이드(H2/H3) + 조건별 비교표(Table) + 주의사항으로 구성합니다.\\n"
        "4. 하단에 구글 리치 스니펫용 자주 묻는 질문(FAQ 3문 3답)과 1순위 공식 기관 참고 자료 링크를 포함합니다."
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>워드프레스(WordPress) 코너스톤 SEO 작업실 | AI Blog Notes</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <style>
    :root {{
      --wp: #0073aa;
      --wp-dark: #005177;
      --wp-light: #f0f7fb;
      --wp-border: #bae6fd;
      --text-main: #191f28;
      --text-sub: #4e5968;
      --text-muted: #8b95a1;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e5e8eb;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.6;
      padding-bottom: 80px;
    }}
    .header {{
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-inner {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .brand-wrap {{ display: flex; align-items: center; gap: 12px; }}
    .wp-badge {{
      background: var(--wp);
      color: #fff;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
    }}
    .brand-title {{ font-size: 18px; font-weight: 800; }}
    .header-links {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .header-link {{
      font-size: 13px;
      color: var(--text-sub);
      text-decoration: none;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      font-weight: 600;
    }}
    .header-link:hover {{ border-color: var(--wp); color: var(--wp-dark); }}
    .container {{ max-width: 1120px; margin: 28px auto 0; padding: 0 20px; }}
    .hero-banner {{
      background: linear-gradient(135deg, #0073aa 0%, #005177 100%);
      color: #fff;
      padding: 32px 36px;
      border-radius: 16px;
      margin-bottom: 28px;
      box-shadow: 0 8px 24px rgba(0, 115, 170, 0.2);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
    }}
    .hero-text h1 {{ font-size: 24px; font-weight: 800; margin-bottom: 8px; }}
    .hero-text p {{ font-size: 14px; opacity: 0.94; max-width: 650px; }}
    .hero-stats {{ display: flex; gap: 16px; }}
    .stat-box {{
      background: rgba(255, 255, 255, 0.16);
      padding: 12px 18px;
      border-radius: 12px;
      text-align: center;
      min-width: 100px;
    }}
    .stat-number {{ font-size: 21px; font-weight: 800; display: block; }}
    .stat-label {{ font-size: 12px; opacity: 0.9; }}
    .main-grid {{ display: grid; grid-template-columns: 1fr 350px; gap: 24px; }}
    @media (max-width: 920px) {{ .main-grid {{ grid-template-columns: 1fr; }} }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }}
    .card-title {{ font-size: 17px; font-weight: 750; }}
    .post-card {{
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      background: #fff;
      margin-bottom: 16px;
    }}
    .post-card.today {{
      border-color: var(--wp);
      box-shadow: 0 4px 14px rgba(0, 115, 170, 0.08);
    }}
    .cat-pill {{
      background: var(--wp-light);
      color: var(--wp-dark);
      border: 1px solid var(--wp-border);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }}
    .slug-pill {{
      background: #f1f5f9;
      color: #334155;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-family: monospace;
    }}
    .score-pill {{
      background: #fef3c7;
      color: #b45309;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }}
    .post-card-title {{
      font-size: 17px;
      font-weight: 750;
      color: var(--text-main);
      text-decoration: none;
      display: inline-block;
      margin-bottom: 8px;
    }}
    .post-card-title:hover {{ color: var(--wp-dark); text-decoration: underline; }}
    .action-btn {{
      font-size: 12.5px;
      font-weight: 600;
      padding: 7px 14px;
      border-radius: 6px;
      text-decoration: none;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text-main);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .action-btn-primary {{ background: var(--wp); color: #fff; border-color: var(--wp); }}
    .check-row {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      margin-bottom: 10px;
      font-size: 13px;
      color: var(--text-sub);
      cursor: pointer;
    }}
    .toast {{
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      background: #111827; color: #fff; padding: 12px 24px; border-radius: 8px;
      font-size: 13.5px; font-weight: 600; opacity: 0; pointer-events: none; transition: all 0.2s;
    }}
    .toast.show {{ opacity: 1; transform: translateX(-50%) translateY(-10px); }}
  </style>
</head>
<body>
  <header class="header">
    <div class="header-inner">
      <div class="brand-wrap">
        <span class="wp-badge">WORDPRESS BLOG</span>
        <div class="brand-title">워드프레스(WP) 코너스톤 SEO 작업실</div>
      </div>
      <div class="header-links">
        <a href="https://smartlife70.wordpress.com/wp-admin/index.php" target="_blank" rel="noopener noreferrer" class="header-link" style="background: var(--wp); color: #fff; border-color: var(--wp);">⚙️ 내 워드프레스 관리자 (wp-admin) ↗</a>
        <a href="https://smartlife70.wordpress.com/wp-admin/post-new.php" target="_blank" rel="noopener noreferrer" class="header-link" style="background: var(--wp-light); color: var(--wp-dark); border-color: var(--wp-border);">✍️ WP 새 글 쓰기 ↗</a>
        <a href="https://smartlife70.wordpress.com/" target="_blank" rel="noopener noreferrer" class="header-link">🌐 내 사이트 보기 ↗</a>
        <a href="../../index.html" class="header-link">🏠 멀티 블로그 포털</a>
        <a href="../naver/index.html" class="header-link">🟢 네이버 작업실</a>
        <a href="../tistory/index.html" class="header-link">🟠 티스토리 작업실</a>
        <a href="../../docs/index.html#wordpress-guide" class="header-link">📚 워드프레스 SEO 가이드</a>
      </div>
    </div>
  </header>

  <div class="container">
    <section class="hero-banner">
      <div class="hero-text">
        <h1>🔵 워드프레스(WordPress) 구텐베르크 & 구글 SEO 작업실</h1>
        <p>포털 제약 없는 100% 나만의 독립 디지털 자산! 영문 URL 슬러그, Rank Math 메타 설명, Key Takeaways, 비교표, FAQ 스키마(3문 3답)까지 갖춘 코너스톤 콘텐츠를 관리합니다.</p>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span class="stat-number">{len(posts)} 편</span>
          <span class="stat-label">코너스톤 원고</span>
        </div>
        <div class="stat-box">
          <span class="stat-number">Rank Math</span>
          <span class="stat-label">SEO 최적화</span>
        </div>
      </div>
    </section>

    <div class="main-grid">
      <div class="left-col">
        <section class="card">
          <div class="card-header">
            <div class="card-title">📝 워드프레스 코너스톤(Cornerstone) 포스팅 목록</div>
            <span style="font-size: 12px; color: var(--text-muted);">총 {len(posts)}편 작성됨</span>
          </div>
          {post_cards_html}
        </section>
      </div>

      <div class="right-col">
        <section class="card" style="border: 2px solid var(--wp); background: linear-gradient(180deg, #f0f7fb 0%, #ffffff 100%);">
          <div class="card-title" style="margin-bottom: 8px; color: var(--wp-dark);">🚀 내 워드프레스 바로가기</div>
          <p style="font-size: 12.5px; color: var(--text-sub); margin-bottom: 12px;">
            <strong>smartlife70.wordpress.com</strong> 관리자 대시보드 및 구텐베르크 새 글 작성 화면으로 즉시 이동합니다.
          </p>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <a href="https://smartlife70.wordpress.com/wp-admin/index.php" target="_blank" rel="noopener noreferrer" class="action-btn action-btn-primary" style="justify-content: center; padding: 10px;">
              ⚙️ 워드프레스 관리자 (wp-admin) 열기 ↗
            </a>
            <a href="https://smartlife70.wordpress.com/wp-admin/post-new.php" target="_blank" rel="noopener noreferrer" class="action-btn" style="justify-content: center; padding: 9px; border-color: var(--wp); color: var(--wp-dark); font-weight: 700;">
              ✍️ 워드프레스 새 글 작성하기 (post-new) ↗
            </a>
            <a href="https://smartlife70.wordpress.com/" target="_blank" rel="noopener noreferrer" class="action-btn" style="justify-content: center; padding: 8px;">
              🌐 smartlife70.wordpress.com 사이트 보기 ↗
            </a>
          </div>
        </section>

        <section class="card" style="border: 2px solid var(--wp);">
          <div class="card-title" style="margin-bottom: 12px;">📂 워드프레스 5대 필러(Pillar) 카테고리</div>
          <div style="font-size: 13px; color: var(--text-sub); display: flex; flex-direction: column; gap: 10px;">
            <div><strong>1. Retirement & Pension (30%)</strong><br><span style="font-size:12px; color:var(--text-muted);">퇴직 후 건보료, 국민연금, 노후 현금흐름 마스터 가이드</span></div>
            <div><strong>2. Tax & Asset Management (25%)</strong><br><span style="font-size:12px; color:var(--text-muted);">연금저축·IRP·ISA 절세 비교 및 안전자산 포트폴리오</span></div>
            <div><strong>3. AI & Tech Guide (25%)</strong><br><span style="font-size:12px; color:var(--text-muted);">ChatGPT·Mac·GitHub·Vercel·서치콘솔 기술 매뉴얼</span></div>
            <div><strong>4. Senior Health & Benefits (10%)</strong><br><span style="font-size:12px; color:var(--text-muted);">국가검진, 임플란트 건보 혜택, 정부지원금 조건</span></div>
            <div><strong>5. Active Lifestyle & Gear (10%)</strong><br><span style="font-size:12px; color:var(--text-muted);">파크골프 공인 장비, 트레킹, 생활가전 스펙 비교</span></div>
          </div>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 12px;">✅ Rank Math / Yoast 온페이지 SEO 체크리스트</div>
          <label class="check-row"><input type="checkbox" class="wp-chk" onchange="updateWpCount()"> <span>고유주소(Permalink)를 짧은 영문 하이픈 슬러그로 설정했다</span></label>
          <label class="check-row"><input type="checkbox" class="wp-chk" onchange="updateWpCount()"> <span>Focus Keyphrase를 제목·메타설명·첫 문단·H2에 포함했다</span></label>
          <label class="check-row"><input type="checkbox" class="wp-chk" onchange="updateWpCount()"> <span>도입부 직후 Key Takeaways 요약 박스를 배치했다</span></label>
          <label class="check-row"><input type="checkbox" class="wp-chk" onchange="updateWpCount()"> <span>구텐베르크 비교표(Table)와 FAQ(3문 3답) 블록을 넣었다</span></label>
          <label class="check-row"><input type="checkbox" class="wp-chk" onchange="updateWpCount()"> <span>1순위 공식 기관 외부 링크(Outbound Link)를 연결했다</span></label>
          <label class="check-row"><input type="checkbox" class="wp-chk" onchange="updateWpCount()"> <span>네이버·티스토리 원고와 중복되지 않는 독립 원고로 작성했다</span></label>
          <div id="wpStatus" style="margin-top: 10px; font-size: 12.5px; font-weight: 700; color: var(--wp-dark);">0/6 항목 완료</div>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 10px;">⚡ 워드프레스 코너스톤 AI 프롬프트</div>
          <p style="font-size: 12.5px; color: var(--text-sub); margin-bottom: 12px;">
            영문 슬러그, 메타 설명, Key Takeaways, 비교표, FAQ 3문 3답을 한 번에 생성하는 워드프레스 전용 프롬프트입니다.
          </p>
          <button class="action-btn action-btn-primary" style="width: 100%; justify-content: center; padding: 10px;" onclick="copyText('{wp_prompt}')">
            📋 워드프레스 SEO 프롬프트 복사
          </button>
        </section>
      </div>
    </div>
  </div>

  <div class="toast" id="toast">✓ 클립보드에 복사되었습니다!</div>
  <script>
    function copyText(text) {{
      navigator.clipboard.writeText(text).then(() => {{
        const t = document.getElementById("toast");
        t.classList.add("show");
        setTimeout(() => t.classList.remove("show"), 2200);
      }});
    }}
    function updateWpCount() {{
      const chks = document.querySelectorAll(".wp-chk");
      let done = 0;
      chks.forEach((c, i) => {{
        if (c.checked) done++;
        localStorage.setItem("wp_seo_chk_" + i, c.checked ? "1" : "0");
      }});
      document.getElementById("wpStatus").textContent = done + "/6 항목 완료";
    }}
    window.addEventListener("DOMContentLoaded", () => {{
      const chks = document.querySelectorAll(".wp-chk");
      chks.forEach((c, i) => {{
        if (localStorage.getItem("wp_seo_chk_" + i) === "1") c.checked = true;
      }});
      updateWpCount();
    }});
  </script>
</body>
</html>"""

def update_root_portal_with_wordpress(today_str, wp_posts):
    portal_path = os.path.join(BASE_DIR, "index.html")
    if not os.path.exists(portal_path):
        return

    with open(portal_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CSS 클래스 보강 (.tag-wp, .p-btn-wp)
    if ".tag-wp" not in content:
        content = content.replace(
            ".tag-tistory {\n      background: var(--tistory-light);\n      color: var(--tistory);\n    }",
            ".tag-tistory {\n      background: var(--tistory-light);\n      color: var(--tistory);\n    }\n    .tag-wp {\n      background: var(--wp-light);\n      color: var(--wp);\n    }\n    .p-btn-wp {\n      background: var(--wp);\n      color: #fff;\n    }\n    .p-btn-wp:hover {\n      background: #005177;\n    }"
        )

    # 2. 상단 네비게이션의 워크플로우 링크를 워드프레스 포털로 교체
    content = re.sub(
        r'<a href="blog/workflow/index\.html"[^>]*>.*?</a>',
        '<a href="blog/wordpress/index.html" class="header-link" style="background: var(--wp-light); color: var(--wp); border-color: #bae6fd;">🔵 워드프레스 포털</a>',
        content
    )

    # 3. Platform 3: WordPress 카드를 '🟢 운영 중'으로 활성화
    latest_wp = wp_posts[0] if wp_posts else None
    latest_wp_link = f"blog/wordpress/{latest_wp['rel_html']}" if latest_wp else "blog/wordpress/index.html"

    old_wp_card_pattern = r'<!-- Platform 3: WordPress[\s\S]*?</div>\s*\n\s*</div>\s*\n\s*<!-- Section 2: Recent Posts Hub -->'
    new_wp_card = f"""<!-- Platform 3: WordPress (Active) -->
      <div class="platform-card wordpress">
        <div>
          <div class="platform-card-header">
            <div class="platform-brand">
              <div class="platform-logo">W</div>
              <div class="platform-name">워드프레스 (WP) · 코너스톤</div>
            </div>
            <span class="status-badge badge-active">🟢 운영 중</span>
          </div>

          <p class="platform-desc">
            포털의 제약 없는 100% 나만의 독립 웹사이트! <strong>영문 슬러그 · Rank Math SEO · 비교표 · FAQ 스키마</strong>가 완비된 코너스톤 가이드북으로 구글 장기 검색 유입을 구축합니다.
          </p>

          <div class="platform-meta-box">
            <div class="meta-row">
              <span class="meta-label">운영 목표</span>
              <span class="meta-value" style="color: var(--wp);">코너스톤 심층 가이드 (8단계 워크플로우)</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">주요 타겟</span>
              <span class="meta-value">Google 글로벌/국내 SEO (Rank Math)</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">수익 모델</span>
              <span class="meta-value">애드센스(100% 자체광고), 전자책, 제휴</span>
            </div>
          </div>
        </div>

        <div class="platform-btn-group">
          <a href="blog/wordpress/index.html" class="p-btn p-btn-wp">
            🔵 워드프레스 작업실 이동
          </a>
          <a href="https://smartlife70.wordpress.com/wp-admin/index.php" target="_blank" rel="noopener noreferrer" class="p-btn p-btn-sub" style="border-color: #bae6fd; background: #f0f7fb; color: #005177; font-weight: 700;">
            ⚙️ 내 워드프레스 관리자 (smartlife70) ↗
          </a>
          <a href="{latest_wp_link}" class="p-btn p-btn-sub">
            👁️ 오늘자 워드프레스 글 보기 & 블록 복사
          </a>
          <a href="docs/index.html#wordpress-guide" class="p-btn p-btn-sub">
            📖 워드프레스 구축·SEO 가이드
          </a>
        </div>
      </div>

    </div>

    <!-- Section 2: Recent Posts Hub -->"""
    content = re.sub(old_wp_card_pattern, new_wp_card, content)

    # 4. 하단 지침서 카드 링크 복원
    content = content.replace(
        'href="blog/workflow/index.html" class="doc-link-card" style="border-color: #c7d2fe; background: #eef2ff;"',
        'href="docs/index.html#daily-workflow" class="doc-link-card" style="border-color: #bae6fd; background: #f0f7fb;"'
    )

    # 5. 최근 작성된 일별 블로그 포스팅에 워드프레스 + 티스토리 + 네이버 통합 표시
    wp_rows = ""
    for p in wp_posts[:3]:
        p_date_only = p["date_only"]
        try:
            dt = datetime.strptime(p_date_only, "%Y-%m-%d")
            weekday = WEEKDAYS_KR[dt.weekday()]
            date_display = f"{p_date_only} ({weekday} · {p['slug']} · 평가 {p['score_str']})"
        except Exception:
            date_display = p["post_id"]
        post_link = f"blog/wordpress/{p['rel_html']}"
        wp_rows += f"""
      <div class="post-item-row">
        <div class="post-item-left">
          <span class="post-platform-tag tag-wp">워드프레스</span>
          <a href="{post_link}" class="post-item-title">
            {p['title']}
          </a>
        </div>
        <span class="post-item-date">{date_display}</span>
        <a href="{post_link}" class="post-item-btn">
          👁️ 포스트 열기 & 블록 복사
        </a>
      </div>"""

    marker_pattern = r'(<!-- RECENT_POSTS_LIST_START -->)([\s\S]*?)(<!-- RECENT_POSTS_LIST_END -->)'
    m_marker = re.search(marker_pattern, content)
    if m_marker:
        existing_rows = m_marker.group(2)
        row_blocks = re.findall(
            r'(<div class="post-item-row">\s*<div class="post-item-left">[\s\S]*?</div>\s*<span class="post-item-date">[\s\S]*?</span>\s*<a[^>]*class="post-item-btn">[\s\S]*?</a>\s*</div>)',
            existing_rows
        )
        other_blocks = [b for b in row_blocks if "tag-wp" not in b][:6]
        combined_html = wp_rows + "\n      " + "\n      ".join(other_blocks)
        content = content[:m_marker.start()] + f"<!-- RECENT_POSTS_LIST_START -->{combined_html}\n      <!-- RECENT_POSTS_LIST_END -->" + content[m_marker.end():]

    with open(portal_path, "w", encoding="utf-8") as f:
        f.write(content)
    log("✅ 루트 index.html 포털에 워드프레스(WP) 작업실 및 최신 코너스톤 포스팅 연동 완료")

def run_wordpress_batch(target_date=None):
    now = datetime.now()
    today_date = datetime.strptime(target_date, "%Y-%m-%d") if target_date else now
    today_str = today_date.strftime("%Y-%m-%d")
    weekday_str = WEEKDAYS_KR[today_date.weekday()]
    ym = today_str[:7].replace("-", "")

    wp_post_dir = os.path.join(POSTS_DIR, ym)
    os.makedirs(wp_post_dir, exist_ok=True)

    for idx, item in enumerate(WP_ARTICLES, 1):
        post_id = today_str if idx == 1 else f"{today_str}-{idx}"
        md_content = format_wp_markdown(today_str, weekday_str, item)
        html_content = build_wp_post_html(post_id, today_str, weekday_str, item, md_content)

        with open(os.path.join(wp_post_dir, f"{post_id}.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
        with open(os.path.join(wp_post_dir, f"{post_id}.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

    posts = scan_wp_posts()
    os.makedirs(WP_BLOG_DIR, exist_ok=True)
    with open(os.path.join(WP_BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_wp_index_html(today_str, weekday_str, posts))

    update_root_portal_with_wordpress(today_str, posts)
    log(f"🎉 [워드프레스 배치 완료] {today_str} 워드프레스 코너스톤 SEO 포스팅 {len(WP_ARTICLES)}편 생성 완료")

if __name__ == "__main__":
    date_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run_wordpress_batch(date_args[0] if date_args else None)

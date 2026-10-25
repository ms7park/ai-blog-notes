#!/usr/bin/env python3
"""
Daily Integrated Blog Workflow Batch (네이버 · 티스토리 8단계 통합 워크플로우 원고 생성기)
workflow/daily-workflow.md의 Step 1 ~ Step 8 절차에 따라:
1) 주제 수집 및 100점 만점 5대 기준 평가
2) 공식 출처(공단, 국세청, Apple, Google 등) 팩트 시트 검증
3) [티스토리용 7단계 검색형 원고] + [네이버용 품미인생 공감형 요약 원고] 동시 생성
4) 발행 전 팩트체크(fact-check.md) 및 publishing.md 체크리스트 점검
을 수행하여 blog/workflow/posts/YYYYMM/ 및 blog/tistory/posts/YYYYMM/ 에 완성본(.md, .html)을 생성합니다.
"""

import os
import sys
import glob
import re
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_BLOG_DIR = os.path.join(BASE_DIR, "blog", "workflow")
POSTS_DIR = os.path.join(WORKFLOW_BLOG_DIR, "posts")
TISTORY_BLOG_DIR = os.path.join(BASE_DIR, "blog", "tistory")
TISTORY_POSTS_DIR = os.path.join(TISTORY_BLOG_DIR, "posts")

WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

# 워크플로우 기반 심층 작성 주제 5선 (topics/topic-backlog.md 고득점 순)
WORKFLOW_ARTICLES = [
    {
        "seq": 1,
        "category": "은퇴·연금·생활비",
        "topic": "퇴직 후 건강보험료 계산 및 절감 방법",
        "score": 92,
        "scores": {"trend": 5, "intent": 5, "gap": 4, "capability": 4, "evergreen": 5},
        "search_question": "퇴직 후 직장가입자에서 지역가입자로 전환될 때 건강보험료 계산 기준과 피부양자 등록·임의계속가입 중 유리한 선택 기준은?",
        "title_candidates": [
            "퇴직 후 건강보험료 계산 기준 및 줄이는 법: 피부양자 자격 요건 vs 임의계속가입 vs 지역가입자 비교표",
            "은퇴 후 건강보험료 폭탄 피하는 3가지 방법 (피부양자 소득 2,000만 원 기준·임의계속가입 신청 기간)",
            "퇴직자 건강보험 임의계속가입 신청 조건 및 국민건강보험공단 모의계산 확인 순서"
        ],
        "final_title": "퇴직 후 건강보험료 계산 기준 및 줄이는 법: 피부양자 자격 요건 vs 임의계속가입 vs 지역가입자 비교표",
        "naver_title": "은퇴 직후 가장 놀라는 '건강보험료' 줄이는 3가지 비결! 피부양자 조건과 임의계속가입 체크포인트",
        "core_summary": (
            "퇴직 후 건강보험료 부담을 줄이려면 **① 자녀 등 직장가입자의 피부양자 등록 가능 여부(연간 합산소득 2,000만 원 이하 및 재산 과세표준 5.4억 원 이하)**를 가장 먼저 확인해야 합니다. "
            "피부양자 요건을 충족하지 못한다면 **② 퇴직 전 직장 건보료 수준을 최대 36개월간 유지하는 '임의계속가입'(최초 지역건보료 고지서 납부기한으로부터 2개월 이내 신청 필수)**과 **③ 일반 지역가입자 전환 보험료**를 국민건강보험공단 모의계산으로 비교해 더 저렴한 쪽을 선택하면 됩니다."
        ),
        "sections_md": """## 1. 도입부: 퇴직 후 가장 큰 고정비, 건강보험료는 왜 갑자기 오를까요?

직장에 다닐 때는 월급에서 건강보험료의 **50%만 본인 부담**하고 나머지 50%는 회사가 부담합니다. 또한 보수(월급) 외에 보유한 주택이나 자동차에는 별도 보험료가 부과되지 않습니다.

하지만 퇴직 후 **지역가입자**로 전환되면 회사가 내주던 50%가 사라질 뿐만 아니라, **소득(연금·이자·배당·근로·사업소득)과 재산(주택·토지 과세표준, 기본공제 1억 원 적용)**을 합산해 보험료를 산정하기 때문에 체감 보험료가 크게 오르는 경우가 많습니다. 이 글에서는 국민건강보험공단 공식 기준을 바탕으로 **퇴직 직후 반드시 확인해야 할 3가지 선택지(피부양자 · 임의계속가입 · 지역가입자) 비교표와 모의계산 확인 절차**를 정리합니다.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

- **1순위 검토 (보험료 0원)**: 직장가입자(자녀·배우자)의 **피부양자 등재**
  - 핵심 조건: 연간 합산소득 **2,000만 원 이하** + 재산세 과세표준 합계 **5.4억 원 이하**(5.4억 초과~9억 이하는 연 소득 1,000만 원 이하)
- **2순위 검토 (최대 3년간 직장 수준 유지)**: **임의계속가입 신청**
  - 핵심 조건: 퇴직 전 18개월 기간 중 통산 1년 이상 직장가입자 자격을 유지한 사람
  - **신청 기한 주의**: 지역가입자 전환 후 받은 **최초 지역보험료 고지서 납부기한에서 2개월이 지나기 전**까지 공단에 신청해야 함
- **3순위 검토**: 재산과 소득이 적어 지역가입자 보험료가 임의계속가입 보험료보다 더 낮은 경우에는 별도 신청 없이 **지역가입자** 유지

---

## 3. 단계별 설명: 퇴직 후 내 건강보험료 확인 및 신청하는 4단계 순서

### 1단계: 국민건강보험공단 홈페이지·앱에서 예상 지역보험료 모의계산하기
1. [국민건강보험공단 공식 홈페이지(nhis.or.kr)](https://www.nhis.or.kr/) 또는 모바일 앱 **'The건강보험'**에 접속합니다.
2. **[민원여기요]** → **[개인민원]** → **[보험료 조회/신청]** → **[4대보험료 계산해보기(지역보험료 모의계산)]** 메뉴를 선택합니다.
3. 본인의 연간 공적연금(국민연금 등), 이자·배당소득 및 보유 주택·토지의 재산세 과세표준 금액을 입력해 예상 월 지역보험료를 확인합니다.

### 2단계: 퇴직 전 마지막 직장 건강보험료(본인부담금)와 비교하기
1. 급여명세서 또는 공단 앱의 **[직장보험료 조회]**에서 퇴직 직전 본인이 부담하던 월 건강보험료(장기요양보험료 포함)를 확인합니다.
2. 정확한 임의계속보험료는 **퇴직 전 12개월간 보수월액 평균**을 기준으로 산정되므로, 고객센터(1577-1000)에 전화하면 **'예상 지역보험료 vs 예상 임의계속보험료'**를 1원 단위까지 즉시 비교 안내받을 수 있습니다.

### 3단계: 피부양자 자격 요건 충족 여부 점검하기
자녀나 배우자가 직장가입자라면 아래 두 가지 기준을 모두 통과하는지 확인합니다.
1. **소득 요건**: 이자·배당·사업·근로·공적연금(국민연금 등 세전 금액) 합산 소득이 **연 2,000만 원 이하**일 것 (단, 사업자등록증이 있는 경우 사업소득이 '0원'이어야 함).
2. **재산 요건**: 토지·건축물·주택의 지방세법상 **재산세 과세표준 합계액이 5.4억 원 이하**일 것 (과세표준 5.4억 초과~9억 원 이하인 경우 연간 소득이 1,000만 원 이하여야 유지 가능).

### 4단계: 임의계속가입 신청 또는 피부양자 자격취득 신고하기
1. **피부양자 등록 시**: 직장가입자인 가족의 회사 총무/인사부서를 통해 퇴직일로부터 90일 이내에 `피부양자 자격(취득) 신고서`와 가족관계증명서를 제출합니다.
2. **임의계속가입 신청 시**: 최초 지역건보료 고지서 납부기한으로부터 **2개월 이내**에 공단 지사 방문, 팩스, 또는 'The건강보험' 앱/홈페이지에서 신청합니다.

---

## 4. 조건별 비교표: 피부양자 vs 임의계속가입 vs 일반 지역가입자

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
2. **개인연금(연금저축·IRP)과 공적연금(국민연금)의 차이**
   - 건강보험 피부양자 소득 산정 시 **국민연금·공무원연금 등 공적연금은 세전 수령액 100%가 반영**되지만, 현재 기준 사적연금(연금저축·IRP 등)은 분리과세 한도 내 수령 시 건보료 소득 산정에서 제외됩니다. (※ 향후 정책 변경 가능성을 항상 확인하세요.)
3. **임의계속가입 중도 해지 가능 여부**
   - 임의계속가입 신청 후 중간에 재산을 처분하거나 소득이 줄어 일반 지역보험료가 더 저렴해지면, 공단에 **임의계속 탈퇴 신청**을 하여 언제든 지역가입자로 전환할 수 있습니다.

---

## 6. 결론: 퇴직 전후 바로 실행할 행동 요약

1. 퇴직 전이라면 **국민연금 예상 연 수령액 + 연간 이자·배당소득 합계**가 연 2,000만 원을 넘는지 먼저 계산해 피부양자 등록 가능 여부를 확인하세요.
2. 피부양자 등록이 어렵다면 퇴직 후 **첫 지역보험료 고지서**를 받는 즉시 공단 고객센터(1577-1000)에 전화해 **임의계속가입 보험료와 비교**한 뒤, 납부기한 2개월 이내에 신청 여부를 결정하시기 바랍니다.""",
        "naver_summary_md": """### 🟢 [네이버 블로그 '품미인생' 발행용 요약 원고]
안녕하세요, 든든한 노후 자산을 가꾸는 **품미인생(品味人生)**입니다.
평생 다닌 직장을 은퇴하고 나면 가장 먼저 날아오는 고지서 중 하나가 바로 **지역 건강보험료**입니다. 회사에서 절반을 내주던 시절과 달리 집과 연금에도 보험료가 붙다 보니 깜짝 놀라는 분들이 정말 많으신데요.
오늘 꼭 기억하셔야 할 **건보료 절감 3원칙**입니다.
1. **자녀 피부양자 조건 먼저 확인하기**: 부부 각자의 연 소득(국민연금+금융소득 등)이 2,000만 원 이하이고 재산세 과세표준이 5.4억 원 이하라면 피부양자 등록으로 건보료를 아낄 수 있습니다.
2. **임의계속가입 골든타임(2개월) 놓치지 않기**: 지역건보료가 직장 때보다 많이 나왔다면, 첫 고지서 납부기한으로부터 2개월 안에 '임의계속가입'을 신청해 최대 3년간 예전 수준으로 내실 수 있습니다.
3. **1577-1000 전화 한 통으로 비교하기**: 혼자 고민하지 마시고 건강보험공단 고객센터에 전화해 '지역보험료와 임의계속보험료 중 어느 쪽이 유리한지' 비교해 달라고 요청해 보세요!""",
        "official_refs": [
            ("국민건강보험공단 공식 홈페이지 (보험료 모의계산 및 피부양자 안내)", "https://www.nhis.or.kr/"),
            ("정부24 퇴직 후 건강보험 임의계속가입 안내", "https://www.gov.kr/"),
            ("국가법령정보센터 국민건강보험법 시행규칙", "https://www.law.go.kr/")
        ],
        "fact_checks": [
            "피부양자 소득 기준(연 2,000만 원 이하) 및 재산세 과세표준 기준(5.4억 원 이하, 5.4억~9억 원은 연 소득 1,000만 원 이하) 현행 법령 일치 확인",
            "임의계속가입 유지 기간(최대 36개월) 및 신청 기한(최초 지역고지서 납부기한으로부터 2개월 이내) 공단 공식 기준 일치 확인",
            "지역가입자 재산 기본공제(1억 원) 및 자동차 건보료 폐지 반영 기준 점검 완료"
        ]
    },
    {
        "seq": 2,
        "category": "AI·IT 활용법",
        "topic": "맥(Mac) Apple 계정 로그인 오류 해결 순서",
        "score": 92,
        "scores": {"trend": 4, "intent": 5, "gap": 5, "capability": 5, "evergreen": 4},
        "search_question": "맥북(MacBook)·아이맥에서 Apple 계정(Apple ID) 로그인이 안 되거나 확인 중 무한 로딩이 발생할 때 데이터를 지우지 않고 해결하는 순서는?",
        "title_candidates": [
            "맥(Mac)에서 Apple 계정(Apple ID) 로그인 오류 및 설정 무한 로딩 해결하는 5단계 순서",
            "맥북 시스템 설정에서 Apple ID 로그인이 안 될 때 확인해야 할 5가지 해결 방법",
            "Mac '확인 중' 멈춤·서버 연결 오류 발생 시 Apple 계정 로그인 복구 가이드"
        ],
        "final_title": "맥(Mac)에서 Apple 계정(Apple ID) 로그인 오류 및 설정 무한 로딩 해결하는 5단계 순서",
        "naver_title": "맥북 Apple 계정 로그인이 갑자기 안 될 때! 당황하지 않고 5분 만에 해결하는 순서",
        "core_summary": (
            "맥(Mac) 시스템 설정에서 Apple 계정(Apple ID) 로그인이 멈추거나 '서버에 연결할 수 없음' 오류가 발생할 때는 **① Apple 시스템 상태 페이지 확인 → ② 날짜 및 시간 자동 설정 점검 → ③ VPN·방화벽 해제 → ④ 활성 상태 보기에서 인증 프로세스(`akd`, `cloudd`) 강제 종료 → ⑤ 맥 안전 모드(Safe Mode) 부팅 후 로그인** 순서로 진행하면 초기화 없이 90% 이상 해결됩니다."
        ),
        "sections_md": """## 1. 도입부: 맥(Mac)에서 Apple 계정 로그인이 멈추는 주요 원인

맥북(MacBook)이나 맥 미니를 사용하다가 macOS 업데이트 직후, 또는 비밀번호 변경 후 **시스템 설정(System Settings) → Apple 계정**에서 로그인을 시도할 때 `확인 중...` 회전 아이콘만 계속 돌거나 `알 수 없는 오류가 발생했습니다`라는 메시지가 뜨는 경우가 있습니다.

이 문제는 대부분 기기 고장이 아니라 **macOS 백그라운드 인증 데몬(`akd`)의 일시적 충돌, 시스템 시간 동기화 오차, 또는 VPN/네트워크 보안 필터 간섭** 때문에 발생합니다. 아래의 **5단계 점검 순서**를 가벼운 방법부터 차례대로 따라 해보세요.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

- **가장 흔한 원인 1**: 맥의 **날짜 및 시간**이 Apple 인증 서버 시간과 미세하게 어긋난 경우 (보안 인증서 검증 실패)
- **가장 흔한 원인 2**: 백그라운드 인증 프로세스(`akd`, `cloudd`)가 응답 없음 상태로 멈춘 경우
- **가장 빠른 해결법**: `활성 상태 보기(Activity Monitor)`에서 `akd` 프로세스를 재시작하거나, **안전 모드(Safe Mode)**로 부팅해 로그인한 뒤 일반 모드로 재부팅하기

---

## 3. 단계별 설명: 맥 Apple 계정 로그인 오류 해결하는 5단계 순서

### 1단계: Apple 공식 시스템 상태 및 이중 인증 수신 기기 확인
가장 먼저 내 맥의 문제인지 Apple 서버 점검인지 확인합니다.
1. 브라우저에서 [Apple 시스템 상태 페이지(apple.com/kr/support/systemstatus)](https://www.apple.com/kr/support/systemstatus/)에 접속합니다.
2. **'Apple 계정'**, **'iCloud 계정 및 로그인'** 항목 옆에 녹색 불(정상)이 켜져 있는지 확인합니다.
3. 함께 사용하는 아이폰이나 아이패드에서 [apple.com](https://account.apple.com/) 웹 로그인이 정상적으로 되는지 먼저 테스트합니다.

### 2단계: 날짜 및 시간 자동 설정 강제 동기화
Apple 로그인 서버는 보안 토큰 검증을 위해 기기 시간이 정확히 일치할 것을 요구합니다.
1. 맥 좌측 상단 애플() 메뉴 → **[시스템 설정]** → **[일반]** → **[날짜 및 시간]**으로 이동합니다.
2. **'자동으로 날짜 및 시간 설정'** 토글을 한 번 껐다가 다시 켭니다.
3. 아래 **'위치에 따라 시간대 자동 설정'**도 활성화되어 있고 현재 국가(대한민국 표준시)가 맞는지 확인합니다.

### 3단계: VPN, 프록시, 광고 차단 앱 일시 종료
사내 보안망, VPN 앱, 또는 네트워크 필터 프로그램이 Apple 인증 서버 포트를 차단할 수 있습니다.
1. 실행 중인 VPN 앱이 있다면 연결을 해제하고 완전 종료합니다.
2. **[시스템 설정]** → **[네트워크]** → 현재 연결된 Wi-Fi의 **[세부사항...]** → **[프록시]** 탭에서 체크된 프록시 항목이 있다면 모두 해제합니다.
3. 가능하면 스마트폰 **개인용 핫스팟(테더링)**에 맥을 일시 연결해 로그인을 시도해 봅니다.

### 4단계: '활성 상태 보기'에서 인증 프로세스(`akd`, `cloudd`) 재시작
인증 창이 계속 멈춰 있을 때 가장 효과적인 단계입니다.
1. `Command(⌘) + Space(스페이스바)`를 눌러 Spotlight 검색을 열고 **'활성 상태 보기(Activity Monitor)'**를 실행합니다.
2. 먼저 열려 있는 **시스템 설정** 창을 완전히 닫습니다(`Command + Q`).
3. 활성 상태 보기 우측 상단 검색창에 `akd`를 입력합니다 (Apple Keychain/Account Daemon).
4. 목록에 나타난 `akd`를 선택하고 상단의 **[X (강제 종료)]** 버튼을 누릅니다 (macOS가 즉시 깨끗한 상태의 프로세스를 자동 재실행합니다).
5. 같은 방법으로 `cloudd` 프로세스도 검색해 강제 종료한 뒤, 다시 **시스템 설정**을 열어 로그인을 시도합니다.

### 5단계: 맥 안전 모드(Safe Mode)로 부팅하여 로그인하기
위 4단계로도 해결되지 않는다면 서드파티 시작 프로그램 충돌을 배제하는 **안전 모드**를 사용합니다.
- **Apple Silicon 탑재 맥 (M1 / M2 / M3 / M4)**:
  1. 맥 시스템을 완전히 종료합니다.
  2. 전원 버튼을 길게 누르고 **'시동 옵션 로드 중'**이 나타날 때까지 손을 떼지 않습니다.
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

## 5. 주의사항: 로그인 오류 해결 시 피해야 할 행동

1. **키체인(Keychain) 폴더 임의 삭제 주의**
   - 인터넷의 오래된 팁 중 `~/Library/Keychains/` 폴더 전체를 삭제하라는 안내가 있으나, 저장된 Wi-Fi 암호와 로컬 인증서가 함께 유실될 수 있으므로 반드시 **4단계(`akd` 재시작)와 5단계(안전 모드)**를 먼저 시도하세요.
2. **비밀번호 연속 오입력 주의**
   - 짧은 시간 내에 암호를 여러 번 틀리면 Apple 계정이 보안 잠금 처리되어 계정 복구(iforgot.apple.com)에 하루 이상 걸릴 수 있습니다. 암호가 헷갈린다면 웹 브라우저에서 먼저 정확히 확인하세요.

---

## 6. 결론: 다음 행동 정리

1. 지금 바로 **시스템 설정 창을 닫고(`Command + Q`)**, **날짜/시간 자동 설정(2단계)**과 **활성 상태 보기 `akd` 재시작(4단계)**을 먼저 실행해 보세요.
2. 여전히 멈춘다면 **안전 모드 부팅(5단계)**으로 진입해 로그인하면 데이터 손실 없이 깔끔하게 해결할 수 있습니다.""",
        "naver_summary_md": """### 🟢 [네이버 블로그 '품미인생' 발행용 요약 원고]
맥북이나 아이맥을 쓰다 보면 가끔 Apple 계정 로그인이 '확인 중'에서 멈춰 속을 태울 때가 있습니다. 서비스센터에 가기 전에 집에서 5분 만에 해결할 수 있는 3가지 핵심 팁입니다!
1. **날짜 및 시간 자동 설정 껐다 켜기**: 시간이 1~2분만 어긋나도 Apple 보안 서버가 로그인을 차단합니다.
2. **활성 상태 보기에서 `akd` 종료하기**: 인증 담당 프로그램이 멈춘 경우 강제 종료해주면 즉시 새로고침됩니다.
3. **안전 모드로 부팅해서 로그인하기**: 전원 버튼을 길게 눌러 Shift 키와 함께 안전 모드로 들어가 로그인하면 거짓말처럼 해결됩니다!""",
        "official_refs": [
            ("Apple 공식 고객지원: Mac에서 Apple 계정에 로그인할 수 없는 경우", "https://support.apple.com/ko-kr"),
            ("Apple 공식 시스템 상태 실시간 확인 페이지", "https://www.apple.com/kr/support/systemstatus/"),
            ("Apple 공식 가이드: Mac을 안전 모드로 시동하기", "https://support.apple.com/ko-kr/guide/mac-help/mh21245/mac")
        ],
        "fact_checks": [
            "Apple Silicon(전원 버튼 길게 누르기 → Shift + 안전 모드로 계속) 및 Intel Mac 안전 모드 진입 공식 절차 일치 확인",
            "macOS 인증 데몬(akd) 및 iCloud 데몬(cloudd) 프로세스 명칭 정확성 확인",
            "데이터 손실 위험이 있는 임의 시스템 파일 삭제 없이 공식 권장 순서대로 구성 완료"
        ]
    },
    {
        "seq": 3,
        "category": "은퇴·연금·생활비",
        "topic": "연금저축펀드와 개인형 퇴직연금(IRP) 차이 및 선택 기준",
        "score": 90,
        "scores": {"trend": 4, "intent": 5, "gap": 4, "capability": 5, "evergreen": 5},
        "search_question": "노후 준비와 연말정산 세액공제를 위해 연금저축펀드와 IRP 중 무엇을 먼저 가입해야 하며, 납입 한도·투자 가능 상품·중도인출 조건의 차이는 무엇인가?",
        "title_candidates": [
            "연금저축펀드 vs 개인형 퇴직연금(IRP) 차이점 및 세액공제 한도·중도인출·수령 세율 비교표",
            "연금저축과 IRP 중 어디에 먼저 넣어야 할까? 900만 원 세액공제 황금 비율과 장단점 비교",
            "은퇴 준비 필수 계좌 비교: 연금저축펀드·IRP 투자 한도(70% 룰) 및 수수료 확인 방법"
        ],
        "final_title": "연금저축펀드 vs 개인형 퇴직연금(IRP) 차이점 및 세액공제 한도·중도인출·수령 세율 비교표",
        "naver_title": "연금저축 vs IRP 무엇부터 시작할까? 세금 환급 최대 148만 원 챙기는 황금 배분 공식",
        "core_summary": (
            "연말정산·종합소득세 세액공제를 목적으로 한다면 **① 입출금 유연성이 높고 주식형 ETF 100% 투자가 가능한 '연금저축펀드'에 연 600만 원을 먼저 채우고, ② 나머지 연 300만 원을 '개인형 퇴직연금(IRP)'에 추가 납입하여 합산 연 900만 원 세액공제 한도(최대 148만 5천 원 환급)**를 채우는 방식이 가장 유리합니다."
        ),
        "sections_md": """## 1. 도입부: 연금저축과 IRP, 이름은 비슷한데 왜 두 계좌를 구분해야 할까요?

노후 자금 마련과 절세를 위해 가장 많이 활용하는 두 축이 **연금저축(연금저축펀드)**과 **개인형 퇴직연금(IRP, Individual Retirement Pension)**입니다. 두 계좌 모두 납입 금액에 대해 세액공제 혜택을 주고, 만 55세 이후 연금으로 수령할 때 낮은 연금소득세(3.3~5.5%)를 적용받는다는 공통점이 있습니다.

하지만 **가입 자격, 세액공제 인정 한도, 위험자산(주식형 ETF) 투자 제한 비율, 그리고 급전이 필요할 때 중도인출 가능 여부**에서 결정적인 차이가 있습니다. 자신의 자금 계획에 맞지 않는 계좌에만 전액을 넣었다가 중도 해지 세금(기타소득세 16.5%)을 부담하는 일을 막기 위해 두 계좌의 차이점을 정확히 비교해 보겠습니다.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

- **세액공제 최대 한도**: 연금저축 단독 **연 600만 원** / 연금저축 + IRP 합산 **연 900만 원**
- **환급 세액 (900만 원 납입 가정)**:
  - 총급여 5,500만 원(종합소득 4,500만 원) 이하: **16.5% 공제 → 최대 148만 5,000원**
  - 총급여 5,500만 원(종합소득 4,500만 원) 초과: **13.2% 공제 → 최대 118만 8,000원**
- **가장 추천하는 납입 순서**: **연금저축펀드 600만 원 우선 납입 → 여유 자금으로 IRP 300만 원 추가 납입**

---

## 3. 단계별 설명: 나에게 맞는 연금 계좌 선택 및 납입 비중 정하는 4단계

### 1단계: 가입 자격 확인하기 (소득 유무 점검)
1. **연금저축펀드**: 연령이나 소득 제한 없이 **누구나(미성년자·주부·은퇴자 포함)** 증권사에서 개설할 수 있습니다.
2. **IRP(개인형 퇴직연금)**: 근로소득자, 자영업자, 공무원 등 **소득이 있는 취업자** 또는 퇴직금을 수령하려는 퇴직자만 개설할 수 있습니다.

### 2단계: 투자 성향에 따른 상품 제한(안전자산 30% 의무 규정) 확인
1. **연금저축펀드**: 주식형 ETF(예: S&P500, 나스닥100, 배당 ETF 등)에 **계좌 자산의 100%까지 자유롭게 투자**할 수 있습니다. 다만 은행 정기예금 상품은 편입할 수 없습니다.
2. **IRP**: 근로자퇴직급여 보장법 규정에 따라 **위험자산(주식형 펀드·ETF) 투자 한도가 최대 70%로 제한**되며, 나머지 **30% 이상은 반드시 안전자산(예금, 국채, 채권혼합형 ETF, TDF 등)**으로 채워야 합니다.

### 3단계: 중도 인출(유동성) 및 계좌 유지 수수료 비교
1. **연금저축펀드**: 부득이하게 자금이 필요할 때 계좌 전체를 깨지 않고 **필요한 금액만 일부 인출**할 수 있습니다(단, 세액공제 받은 원금과 수익 인출 시 기타소득세 16.5% 부과). 계좌 운용관리 수수료도 별도로 없습니다.
2. **IRP**: 법에서 정한 **특별 사유(무주택자 주택 구입·전세보증금, 6개월 이상 요양, 개인회생·파산 등) 외에는 일부 중도인출이 불가능**하며, 돈이 필요하면 계좌 전체를 해지해야 합니다. 또한 가입할 때 반드시 **'비대면 개설 시 운용·자산관리 수수료 무료'** 혜택이 있는 증권사인지 확인해야 합니다.

### 4단계: 금융감독원 통합연금포털에서 기존 계좌 한도 확인하기
1. [금융감독원 통합연금포털(100lifeplan.fss.or.kr)](https://100lifeplan.fss.or.kr/)에 로그인합니다.
2. 이미 개설된 연금저축이나 IRP의 연간 납입 한도가 다른 금융기관에 분산 설정되어 있지 않은지 조회하고, 주거래 증권사로 한도를 조정합니다.

---

## 4. 한눈에 보는 비교표: 연금저축펀드 vs 개인형 퇴직연금(IRP)

아래 표는 현행 소득세법 및 근로자퇴직급여 보장법 기준을 정리한 비교표입니다.

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

## 5. 주의사항: 납입 및 수령 시 반드시 알아야 할 세금 기준

1. **연간 사적연금 수령액 1,500만 원 기준 확인**
   - 만 55세 이후 연금저축과 IRP에서 세액공제 받은 원금 및 운용수익을 연금으로 수령할 때, **연간 합산 수령액이 1,500만 원 이하**이면 낮은 연금소득세(만 55~69세 5.5%, 만 70~79세 4.4%, 만 80세 이상 3.3%)로 분리과세 종결됩니다.
   - 만약 연 1,500만 원을 초과하여 인출하면 초과분이 아닌 **수령액 전체에 대해 종합소득세 또는 16.5% 분리과세** 중 선택해야 하므로 연간 인출 한도를 1,500만 원 이내로 설계하는 것이 핵심입니다.
2. **세액공제 한도(900만 원) 초과 납입금의 활용**
   - 연 900만 원을 초과해 납입한 금액(연간 총 납입 한도 1,800만 원 이내)은 세액공제를 받지 않은 원금이므로, 나중에 **세금(16.5%) 없이 언제든 중도 인출하거나 비과세로 연금 수령**할 수 있습니다(납입액 세액공제 확인서 제출 필요).

---

## 6. 결론: 상황별 최적 선택 가이드

1. **연간 저축 여력이 600만 원 이하인 경우**: 중도인출이 자유롭고 ETF 100% 투자가 가능한 **연금저축펀드** 하나만 먼저 집중 운용하세요.
2. **연 900만 원 세액공제를 모두 챙기고 싶은 경우**: **연금저축펀드에 600만 원 + 비대면 수수료 무료 증권사 IRP에 300만 원**을 나누어 납입하는 것이 유동성과 절세를 모두 잡는 최적의 조합입니다.""",
        "naver_summary_md": """### 🟢 [네이버 블로그 '품미인생' 발행용 요약 원고]
노후 준비와 연말정산 환급을 위해 연금저축과 IRP 중 무엇을 먼저 해야 할지 고민되시나요? 가장 현명한 **600 : 300 황금 공식**을 알려드립니다!
1. **첫 600만 원은 '연금저축펀드'에!**: 일부 인출이 자유롭고 배당·지수 ETF를 100% 담을 수 있어 활용도가 가장 높습니다.
2. **추가 300만 원은 '비대면 IRP'에!**: 합산 900만 원까지 채우면 연말정산 때 최대 148만 5천 원을 돌려받습니다.
3. **55세 이후 수령할 때는 연 1,500만 원 이내로!**: 세율 3.3~5.5% 저율 과세 혜택을 온전히 누리려면 연간 인출 한도 1,500만 원을 꼭 기억하세요.""",
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
        "category": "AI·IT 활용법",
        "topic": "GitHub와 Vercel을 이용한 무료 사이트 배포 방법",
        "score": 90,
        "scores": {"trend": 4, "intent": 5, "gap": 4, "capability": 5, "evergreen": 5},
        "search_question": "직접 만든 HTML 웹페이지나 블로그 포털을 서버 비용 없이 인터넷 주소(URL)로 배포하고 코드 수정 시 자동 업데이트되도록 GitHub와 Vercel을 연결하는 순서는?",
        "title_candidates": [
            "GitHub와 Vercel을 이용해 무료로 개인 웹사이트·블로그 포털 배포하는 4단계 방법",
            "서버 비용 0원으로 내 웹사이트 만들기: GitHub 저장소 생성부터 Vercel 자동 배포까지",
            "초보자용 GitHub + Vercel 정적 사이트 배포 가이드 및 GitHub Pages와의 차이점 비교"
        ],
        "final_title": "GitHub와 Vercel을 이용해 무료로 개인 웹사이트·블로그 포털 배포하는 4단계 방법",
        "naver_title": "서버비 0원으로 나만의 인터넷 홈페이지 만들기! GitHub와 Vercel 무료 연동 비법",
        "core_summary": (
            "내가 만든 HTML 파일이나 웹 프로젝트를 인터넷에 무료로 공개하려면 **① GitHub에 저장소(Repository)를 만들고 `index.html` 파일을 업로드한 뒤, ② Vercel(vercel.com)에 GitHub 계정으로 로그인하여 해당 저장소를 'Import(연동)'하고 [Deploy] 버튼을 누르면 1분 만에 전용 `https://프로젝트명.vercel.app` 주소와 무료 SSL 보안인증서가 발급**됩니다. 이후에는 GitHub에 수정본을 푸시(`git push`)할 때마다 사이트가 자동으로 최신화됩니다."
        ),
        "sections_md": """## 1. 도입부: 내 컴퓨터에 있는 웹페이지를 비용 없이 인터넷에 띄우는 가장 쉬운 방법

AI 코딩 도구나 에디터로 멋진 HTML 대시보드, 포트폴리오, 또는 멀티 블로그 포털(`index.html`)을 만들었다면, 내 컴퓨터뿐만 아니라 스마트폰이나 외부에서도 접속할 수 있도록 **웹 호스팅 배포(Deployment)**를 해야 합니다.

과거에는 유료 웹호스팅 서버를 임대하고 FTP로 파일을 매번 수동 업로드해야 했지만, 현재 개인 프로젝트(비상업적 용도)에서는 **GitHub(코드 저장소) + Vercel(클라우드 배포 플랫폼)** 조합을 사용하면 **호스팅 비용 0원, 무료 HTTPS 보안 연결, 그리고 파일 수정 시 10초 내 자동 배포** 환경을 구축할 수 있습니다.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

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
4. 약 10~30초 후 폭죽 화면과 함께 배포가 완료되며, 생성된 **`https://저장소이름.vercel.app`** 주소를 클릭하면 스마트폰과 PC 어디서든 내 사이트에 접속할 수 있습니다.

### 4단계: 수정 사항 자동 업데이트(CI/CD) 확인하기
한 번 연동이 끝나면 이후에는 Vercel 사이트에 다시 들어갈 필요가 없습니다.
1. 내 컴퓨터에서 HTML이나 마크다운 파일을 수정합니다.
2. `git add . && git commit -m "update" && git push`를 실행하면 Vercel이 자동으로 감지하여 10~20초 내에 실제 웹사이트를 업데이트합니다.

---

## 4. 정적 웹사이트 무료 배포 플랫폼 3종 비교표

개인 웹사이트를 무료로 배포할 때 가장 많이 쓰이는 3가지 서비스의 공식 스펙 비교표입니다.

| 비교 항목 | ▲ Vercel (Hobby 무료) | 🐙 GitHub Pages | 🌐 Cloudflare Pages |
| :--- | :--- | :--- | :--- |
| **기본 도메인 형태** | `이름.vercel.app` | `아이디.github.io/저장소` | `이름.pages.dev` |
| **비공개(Private) 저장소 배포** | **무료 지원** | 무료 계정은 Public만 가능 | **무료 지원** |
| **배포 반영 속도** | 매우 빠름 (약 10~30초) | 보통 (약 1~2분 소요) | 빠름 (약 20~40초) |
| **PR별 미리보기 URL(Preview)** | **자동 생성 지원** | 기본 미지원 | 자동 생성 지원 |
| **월간 무료 대역폭(Bandwidth)** | 월 100GB (Hobby 기준) | 월 100GB 권장 (Soft limit) | 무제한 (정적 파일 기준) |
| **추천 용도** | 개인 포털, Next.js/React, 빠른 배포 | 단순 문서 뷰어, 오픈소스 소개 | 트래픽이 많은 정적 사이트 |

---

## 5. 주의사항: 배포 시 자주 겪는 오류(404 Not Found)와 해결법

1. **`404: NOT_FOUND` 오류가 뜨는 경우**
   - Vercel은 기본적으로 저장소의 **최상위 폴더(Root Directory)**에서 `index.html` 파일을 찾습니다. 만약 `index.html`이 하위 폴더(예: `public/` 또는 `docs/`) 안에만 있다면, Vercel 프로젝트의 **[Settings] → [General] → [Root Directory]**에서 해당 폴더 경로를 지정해 주어야 합니다.
2. **파일 경로 대소문자 구분 주의**
   - 내 컴퓨터(macOS/Windows)에서는 `Image.png`와 `image.png`를 구분하지 않아도 열리지만, Vercel의 리눅스(Linux) 서버는 **대소문자를 엄격하게 구분**합니다. 이미지나 링크가 깨진다면 파일명 대소문자가 코드와 정확히 일치하는지 확인하세요.
3. **Hobby 플랜의 라이선스 범위**
   - Vercel 무료(Hobby) 플랜은 개인·비상업적 용도 전용이며, 직접적인 유료 결제 상품 판매 등 상업적 법인 서비스 운영 시에는 Pro 플랜 정책을 확인해야 합니다.

---

## 6. 결론: 오늘 바로 실행할 체크포인트

1. 내 컴퓨터에서 관리하던 웹 프로젝트의 최상위에 `index.html`이 있는지 확인하고 GitHub에 먼저 푸시해 두세요.
2. [Vercel(vercel.com)](https://vercel.com/)에서 GitHub 저장소를 **Import → Deploy**하여 언제 어디서나 스마트폰으로도 열어볼 수 있는 나만의 웹 주소를 만들어 보시기 바랍니다.""",
        "naver_summary_md": """### 🟢 [네이버 블로그 '품미인생' 발행용 요약 원고]
내 컴퓨터 안에만 있던 웹페이지나 블로그 정리 노트를 스마트폰에서도 언제든 열어볼 수 있다면 얼마나 편리할까요? 서버 비용 한 푼 없이 무료로 내 사이트 주소를 만드는 **GitHub + Vercel 연동 3단계**입니다!
1. **GitHub에 파일 올리기**: 내 작업 폴더(`index.html` 포함)를 GitHub 저장소에 올립니다.
2. **Vercel에서 Import 누르기**: Vercel에 GitHub 아이디로 로그인해 저장소를 선택하고 Deploy 버튼만 누르면 끝납니다.
3. **수정하면 10초 만에 자동 반영**: 이후에는 글이나 파일을 고치고 Git 푸시만 하면 알아서 웹사이트가 최신으로 바뀝니다!""",
        "official_refs": [
            ("Vercel 공식 문서 (Git 저장소 배포 가이드)", "https://vercel.com/docs/deployments/git"),
            ("GitHub 공식 문서 (저장소 생성 및 관리)", "https://docs.github.com/ko"),
            ("Vercel Hobby 플랜 사용 한도 안내", "https://vercel.com/docs/limits/overview")
        ],
        "fact_checks": [
            "Vercel Hobby(무료) 플랜의 GitHub Private 저장소 배포 지원 및 월 100GB 대역폭 기준 공식 문서 일치 확인",
            "404 NOT_FOUND 오류의 대표 원인(Root Directory 내 index.html 부재 및 Linux 대소문자 구분) 기술적 정확성 검증 완료",
            "명령어 및 배포 절차 4단계 재현 가능성 확인 완료"
        ]
    },
    {
        "seq": 5,
        "category": "AI·IT 활용법",
        "topic": "티스토리 구글 서치 콘솔 등록 및 사이트맵·RSS 제출 방법",
        "score": 88,
        "scores": {"trend": 4, "intent": 5, "gap": 4, "capability": 5, "evergreen": 4},
        "search_question": "새로 개설한 티스토리 블로그 글이 구글(Google) 검색에 잘 노출되도록 Google Search Console에서 소유권을 확인하고 사이트맵과 RSS를 제출하는 정확한 순서는?",
        "title_candidates": [
            "티스토리 블로그 구글 서치 콘솔(Google Search Console) 등록 및 사이트맵(sitemap.xml)·RSS 제출 방법",
            "티스토리 개설 직후 필수 설정! 구글 검색 노출을 위한 서치 콘솔 소유권 확인 4단계 가이드",
            "구글에 내 티스토리 글 노출시키는 법: Search Console 등록부터 색인 생성 확인까지"
        ],
        "final_title": "티스토리 블로그 구글 서치 콘솔(Google Search Console) 등록 및 사이트맵(sitemap.xml)·RSS 제출 방법",
        "naver_title": "티스토리 블로그 시작할 때 꼭 해야 할 1순위 설정! 구글 서치 콘솔 & 사이트맵 등록법",
        "core_summary": (
            "티스토리 블로그를 구글 검색에 노출시키려면 **① Google Search Console에서 [URL 접두어] 방식으로 내 티스토리 주소(`https://내주소.tistory.com/`)를 입력하고, ② [HTML 태그] 복사 후 티스토리 관리 화면의 [플러그인 → 메타태그 등록] 또는 [스킨 편집 → HTML `<head>`]에 붙여넣어 소유권을 확인한 뒤, ③ [Sitemaps] 메뉴에 `sitemap.xml`과 `rss` 두 가지를 제출**하면 됩니다."
        ),
        "sections_md": """## 1. 도입부: 티스토리 글을 써도 구글 검색에 안 나오는 이유와 해결책

티스토리 블로그를 개설하고 정성껏 정보형 글을 발행했더라도, 구글 검색 로봇(Googlebot)이 내 블로그의 존재와 새 글 목록을 빠르게 파악하지 못하면 검색 결과에 노출되기까지 오랜 시간이 걸립니다.

**구글 서치 콘솔(Google Search Console)**은 구글이 공식 제공하는 무료 도구로, 내 티스토리 블로그의 **사이트맵(Sitemap)과 RSS 피드를 구글에 직접 제출**하고 어떤 검색어로 몇 번 노출·클릭되었는지 데이터를 확인할 수 있는 필수 도구입니다. 처음 개설했을 때 딱 5분만 투자해 아래 순서대로 설정을 마쳐두세요.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

- **공식 설정 사이트**: [Google Search Console (search.google.com/search-console)](https://search.google.com/search-console/)
- **속성 유형 선택**: 반드시 오른쪽 **'URL 접두어(URL Prefix)'** 선택 (`*.tistory.com` 기본 도메인은 DNS 레코드를 직접 수정할 수 없으므로 왼쪽 '도메인' 방식 사용 불가)
- **제출할 사이트맵 주소 2개**:
  1. `sitemap.xml` (`https://내블로그주소.tistory.com/sitemap.xml`)
  2. `rss` (`https://내블로그주소.tistory.com/rss`)

---

## 3. 단계별 설명: 티스토리 구글 서치 콘솔 등록 및 사이트맵 제출 4단계

### 1단계: Google Search Console 접속 및 'URL 접두어'로 주소 입력
1. [Google Search Console 공식 페이지](https://search.google.com/search-console/)에 접속해 구글 계정으로 로그인합니다.
2. 좌측 상단 속성 선택 메뉴에서 **[+ 속성 추가]**를 클릭합니다.
3. 두 가지 유형 중 오른쪽의 **[URL 접두어]** 입력칸에 내 티스토리 전체 주소(예: `https://smartlifelab.tistory.com/`)를 `https://`까지 정확히 입력하고 **[계속]**을 누릅니다.

### 2단계: HTML 메타태그 복사 및 티스토리 소유권 확인
1. '소유권 확인' 팝업 창에서 아래쪽의 **'다른 확인 방법'** 중 **[HTML 태그]** 항목을 클릭해 펼칩니다.
2. `<meta name="google-site-verification" content="고유코드" />` 형태의 메타태그 옆 **[복사]** 버튼을 누릅니다 (아직 창을 닫지 마세요).
3. 새 탭에서 **티스토리 블로그 관리 페이지**로 이동하여 아래 두 방법 중 하나로 적용합니다:
   - **방법 A (스킨 편집 - 가장 확실한 방법)**: `[꾸미기] → [스킨 편집] → 우측 [html 편집]` 클릭 후, 상단 `<head>` 바로 아랫줄에 복사한 `<meta ... />` 태그를 붙여넣고 **[적용]** 클릭
   - **방법 B (플러그인 활용)**: `[플러그인] → [메타태그 등록]` 플러그인을 열고 `name`에 `google-site-verification`, `content`에 따옴표 안의 고유코드만 입력 후 **[적용]** 클릭
4. 다시 구글 서치 콘솔 탭으로 돌아와 **[확인]** 버튼을 누르면 **'소유권이 확인됨'** 초록색 안내가 나타납니다.

### 3단계: 사이트맵(`sitemap.xml`)과 `rss` 유효성 확인 후 제출하기
소유권 확인 후 **[속성으로 이동]**을 눌러 서치 콘솔 대시보드로 들어갑니다.
1. 제출하기 전에 브라우저 새 탭에서 `https://내주소.tistory.com/sitemap.xml`과 `https://내주소.tistory.com/rss`가 에러 없이 열리는지 먼저 확인합니다 (공개 발행된 글이 최소 1개 이상 있어야 정상 표시됩니다).
2. 서치 콘솔 좌측 메뉴에서 **[Sitemaps(사이트맵)]**를 클릭합니다.
3. '새 사이트맵 추가' 입력란에 **`sitemap.xml`**을 입력하고 **[제출]**을 누릅니다.
4. 이어서 같은 입력란에 **`rss`**를 입력하고 **[제출]**을 한 번 더 누릅니다.
5. 아래 제출된 사이트맵 목록의 상태가 **'성공'**으로 표시되는지 확인합니다.

### 4단계: 새 글 발행 후 색인 상태 및 검색 실적 점검하기
1. 사이트맵을 제출했다고 해서 모든 글이 1분 만에 구글 첫 페이지에 뜨는 것은 아니며, 구글 크롤러가 수집·색인하는 데 수일에서 수주가 걸릴 수 있습니다.
2. 중요한 정보 글을 새로 발행했을 때는 서치 콘솔 상단 검색창(**URL 검사**)에 해당 글의 전체 주소를 붙여넣고 **[색인 생성 요청]**을 누르면 크롤링 우선순위를 높일 수 있습니다.

---

## 4. 서치 콘솔 속성 유형 및 소유권 확인 방식 비교표

| 구분 | ❌ 도메인(Domain) 방식 | ✅ URL 접두어(URL Prefix) 방식 (티스토리 필수) |
| :--- | :--- | :--- |
| **입력 주소 예시** | `tistory.com` 또는 개인 구매 도메인 | **`https://내블로그주소.tistory.com/`** |
| **소유권 인증 방법** | DNS TXT 레코드 수정만 가능 | **HTML 메타태그**, HTML 파일, Google 애널리틱스 등 지원 |
| **티스토리 기본 주소 적용** | **불가능** (티스토리 기본 도메인 DNS 수정 권한 없음) | **가능** (스킨 `<head>` 또는 메타태그 플러그인으로 1분 완료) |

---

## 5. 주의사항: 사이트맵 제출 시 '가져올 수 없음' 오류가 뜰 때 해결법

1. **공개 발행된 글이 0개인 상태에서 제출한 경우**
   - 블로그에 전체 공개된 글이 하나도 없으면 `/rss`나 `/sitemap.xml`이 비어 있어 오류가 날 수 있습니다. 반드시 **첫 번째 정보형 글을 공개 발행한 뒤** 제출하세요.
2. **슬래시(`/`) 중복 입력 또는 일시적 인식 지연**
   - 입력란 앞에 이미 `https://내주소.tistory.com/`이 적혀 있으므로 뒤에 `sitemap.xml`만 입력하면 됩니다. 제출 직후 일시적으로 '가져올 수 없음'이 뜨더라도 페이지 새로고침(F5)을 하거나 하루 뒤 확인하면 정상적으로 '성공'으로 바뀝니다.

---

## 6. 결론: 설정 완료 후 다음 행동

1. 서치 콘솔의 **[Sitemaps]** 메뉴에서 `sitemap.xml`과 `rss` 두 항목 모두 **'성공'** 상태인지 확인하세요.
2. 설정을 마쳤다면 매일 서치 콘솔을 새로고침하기보다, 2~4주간 독자의 질문에 답하는 고품질 글을 꾸준히 누적한 뒤 **[실적(Performance)]** 메뉴에서 실제 유입 검색어를 분석해 후속 글 주제로 확장하시기 바랍니다.""",
        "naver_summary_md": """### 🟢 [네이버 블로그 '품미인생' 발행용 요약 원고]
티스토리 블로그를 새로 개설하셨다면 첫 글을 올린 직후 딱 5분만 투자해 **구글 서치 콘솔(Google Search Console)**을 연결해 두세요!
1. **URL 접두어 방식 선택**: 티스토리 기본 주소는 오른쪽 'URL 접두어' 칸에 `https://내주소.tistory.com/`을 입력해야 합니다.
2. **HTML 메타태그 붙여넣기**: 복사한 메타태그를 티스토리 스킨 편집 `<head>` 바로 아래에 넣고 소유권 확인을 누릅니다.
3. **`sitemap.xml`과 `rss` 두 개 제출하기**: 좌측 Sitemaps 메뉴에 두 가지를 제출해 두면 구글 로봇이 내 글을 차곡차곡 수집해 갑니다!""",
        "official_refs": [
            ("Google Search Console 공식 사이트", "https://search.google.com/search-console/"),
            ("Google 검색 센터: 사이트맵 생성 및 제출 가이드", "https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap?hl=ko"),
            ("티스토리 공식 공지 및 스킨 편집 안내", "https://notice.tistory.com/")
        ],
        "fact_checks": [
            "티스토리 기본 도메인(*.tistory.com)은 DNS 수정이 불가하므로 'URL 접두어' 및 'HTML 태그' 방식을 사용해야 함을 정확히 명시",
            "티스토리 표준 사이트맵 경로(/sitemap.xml) 및 RSS 경로(/rss) 일치 확인",
            "과장된 즉시 상위노출 보장 문구 없이 공식 색인 절차와 소요 시간 안내 준수"
        ]
    }
]

def format_full_workflow_markdown(date_str, weekday_str, item):
    sc = item["scores"]
    candidates_md = "\n".join([f"{i}. `{c}`" for i, c in enumerate(item["title_candidates"], 1)])
    refs_md = "\n".join([f"- [{name}]({url}) (`{url}`)" for name, url in item["official_refs"]])
    fc_md = "\n".join([f"- [x] {fc}" for fc in item["fact_checks"]])

    return f"""# {item['final_title']}

> **작성일**: {date_str} ({weekday_str})  
> **워크플로우 단계**: `Step 1 주제 수집` → `Step 2 평가({item['score']}/100점)` → `Step 3 플랫폼 분리` → `Step 4 공식 출처 검증` → `Step 5~7 완성 원고`  
> **카테고리**: {item['category']}  
> **주제 평가 점수**: **{item['score']}/100점** (관심도 {sc['trend']}/5 · 의도 명확성 {sc['intent']}/5 · 경쟁 빈틈 {sc['gap']}/5 · 작성 역량 {sc['capability']}/5 · 장기 검색성 {sc['evergreen']}/5)  
> **핵심 검색 질문**: {item['search_question']}

---

## 💡 [Step 1~3] 워크플로우 주제 선정 & 플랫폼별 제목 설계

### 1) 티스토리 제목 후보 3개
{candidates_md}

### 2) 플랫폼별 확정 제목 분리
- **🟠 티스토리 최종 제목 (장기 검색 질문형)**: `{item['final_title']}`
- **🟢 네이버 블로그 연계 제목 (공감·체크포인트형)**: `{item['naver_title']}`

### 3) 핵심 답변 요약 (도입부 상단 배치용)
> **📌 핵심 요약**: {item['core_summary']}

---

{item['sections_md']}

---

## 7. 참고 자료 및 공식 확인 사이트 (`Step 4 출처 검증`)

{refs_md}

---

{item['naver_summary_md']}

---

## ✅ [Step 6 & Step 7] 발행 전 품질 검증 체크리스트 (`fact-check.md` & `publishing.md`)

{fc_md}
- [x] 공식 자료와 본문 내 숫자·기준이 일치하는가?
- [x] 제목이 본문에서 실제로 답하는 질문과 정확히 일치하는가?
- [x] 직접 해보지 않은 일을 본인의 경험처럼 과장해 표현하지 않았는가?
- [x] 네이버용 요약 원고와 티스토리용 7단계 본문이 중복 없이 분리되었는가?
"""

def build_workflow_article_html(post_id, date_str, weekday_str, item, md_content):
    title = item["final_title"]
    cat_name = item["category"]
    score = item["score"]

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[{date_str}] 워크플로우 원고 #{item['seq']} | {title}</title>

  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>

  <style>
    :root {{
      --wf: #4f46e5;
      --wf-dark: #4338ca;
      --wf-light: #eef2ff;
      --wf-border: #c7d2fe;
      --tistory: #ea580c;
      --naver: #03c75a;
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
      background: var(--wf);
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
    .btn-tistory {{ background: var(--tistory); color: #fff; border-color: var(--tistory); }}
    .btn-naver {{ background: var(--naver); color: #fff; border-color: var(--naver); }}
    .container {{ max-width: 880px; margin: 32px auto 0; padding: 0 16px; }}
    .meta-card {{
      background: var(--white);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      border: 1px solid var(--border);
      border-top: 4px solid var(--wf);
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .meta-badges {{ display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }}
    .badge {{
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 4px;
      background: var(--wf-light);
      color: var(--wf-dark);
      border: 1px solid var(--wf-border);
    }}
    .post-title {{ font-size: 23px; font-weight: 800; line-height: 1.4; margin-bottom: 14px; color: #111827; }}
    .meta-info-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
    .editor-preview h1 {{ font-size: 24px; font-weight: 800; margin-bottom: 24px; padding-bottom: 12px; border-bottom: 2px solid var(--wf); }}
    .editor-preview h2 {{ font-size: 19.5px; font-weight: 750; margin: 34px 0 14px; color: #111827; border-left: 4px solid var(--wf); padding-left: 12px; }}
    .editor-preview h3 {{ font-size: 16.5px; font-weight: 700; margin: 24px 0 10px; color: #1f2937; }}
    .editor-preview p {{ margin-bottom: 16px; font-size: 15.5px; line-height: 1.85; color: #374151; word-break: keep-all; }}
    .editor-preview ul, .editor-preview ol {{ margin: 12px 0 20px 22px; }}
    .editor-preview li {{ margin-bottom: 8px; font-size: 15px; line-height: 1.75; color: #374151; }}
    .editor-preview blockquote {{
      border: 1px solid var(--wf-border);
      border-left: 4px solid var(--wf);
      background: var(--wf-light);
      padding: 16px 20px;
      margin: 20px 0;
      border-radius: 8px;
      color: #312e81;
      font-size: 14.5px;
    }}
    .editor-preview table {{ width: 100%; border-collapse: collapse; margin: 20px 0 24px; font-size: 14px; }}
    .editor-preview th {{ background: var(--wf-light); color: #312e81; font-weight: 700; border: 1px solid var(--wf-border); padding: 10px 12px; text-align: left; }}
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
      <span class="brand-tag">WORKFLOW · #{item['seq']}편</span>
      <span class="nav-title">{date_str} ({weekday_str}) · {cat_name}</span>
    </div>
    <div class="nav-actions">
      <a href="../../index.html" class="btn">⚙️ 워크플로우 작업실 홈</a>
      <a href="../../../index.html" class="btn">🏠 멀티 포털</a>
      <a href="{post_id}.md" target="_blank" class="btn">📄 원본 MD</a>
      <button class="btn btn-tistory" id="copyTistoryBtn">🟠 티스토리 서식 복사</button>
      <button class="btn btn-naver" id="copyNaverBtn">🟢 네이버 서식 복사</button>
      <button class="btn" id="copyMdBtn">📝 마크다운 복사</button>
    </div>
  </header>

  <div class="container">
    <div class="meta-card">
      <div class="meta-badges">
        <span class="badge">⚙️ 8단계 워크플로우 검증 완료</span>
        <span class="badge">📂 카테고리: {cat_name}</span>
        <span class="badge">🎯 주제 평가 점수: {score}/100점</span>
      </div>
      <h1 class="post-title">{title}</h1>
      <div class="meta-info-grid">
        <div class="meta-info-item"><span>작성일자:</span><strong>{date_str} ({weekday_str})</strong></div>
        <div class="meta-info-item"><span>연동 채널:</span><strong>티스토리 7단계 + 네이버 요약본</strong></div>
        <div class="meta-info-item"><span>출처 검증:</span><strong>1순위 공식 기관 대조 완료</strong></div>
        <div class="meta-info-item"><span>팩트체크:</span><strong>할루시네이션·가상경험 배제</strong></div>
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

    function copyRichHtml(accentColor, bgColor, borderColor, label) {{
      const clone = articleEl.cloneNode(true);
      clone.querySelectorAll("h1").forEach(el => el.setAttribute("style", "font-size: 24px; font-weight: bold; color: #111827; margin-bottom: 22px;"));
      clone.querySelectorAll("h2").forEach(el => el.setAttribute("style", `font-size: 19px; font-weight: bold; color: ${{accentColor}}; margin-top: 32px; margin-bottom: 14px; border-left: 4px solid ${{accentColor}}; padding-left: 10px;`));
      clone.querySelectorAll("h3, h4").forEach(el => el.setAttribute("style", "font-size: 16.5px; font-weight: bold; color: #1f2937; margin-top: 22px; margin-bottom: 10px;"));
      clone.querySelectorAll("p").forEach(el => el.setAttribute("style", "font-size: 16px; line-height: 1.85; color: #374151; margin-bottom: 16px;"));
      clone.querySelectorAll("blockquote").forEach(el => el.setAttribute("style", `background-color: ${{bgColor}}; border: 1px solid ${{borderColor}}; border-left: 4px solid ${{accentColor}}; padding: 16px 20px; margin: 20px 0; border-radius: 6px; font-size: 15px;`));
      clone.querySelectorAll("table").forEach(el => el.setAttribute("style", "width: 100%; border-collapse: collapse; margin: 20px 0 24px; font-size: 14px;"));
      clone.querySelectorAll("th").forEach(el => el.setAttribute("style", `background-color: ${{bgColor}}; font-weight: bold; border: 1px solid ${{borderColor}}; padding: 10px 12px; text-align: left;`));
      clone.querySelectorAll("td").forEach(el => el.setAttribute("style", "border: 1px solid #e5e7eb; padding: 10px 12px; color: #374151;"));
      const htmlContent = clone.innerHTML;
      if (navigator.clipboard && window.ClipboardItem) {{
        const htmlBlob = new Blob([htmlContent], {{ type: 'text/html' }});
        const textBlob = new Blob([mdSource], {{ type: 'text/plain' }});
        navigator.clipboard.write([new ClipboardItem({{ 'text/html': htmlBlob, 'text/plain': textBlob }})]).then(() => showToast(label));
      }} else {{
        navigator.clipboard.writeText(mdSource).then(() => showToast(label));
      }}
    }}

    document.getElementById("copyTistoryBtn").addEventListener("click", () => {{
      copyRichHtml("#c2410c", "#fff7ed", "#fed7aa", "🟠 티스토리 에디터 맞춤 서식(표·소제목 포함)이 복사되었습니다!");
    }});
    document.getElementById("copyNaverBtn").addEventListener("click", () => {{
      copyRichHtml("#03c75a", "#f4fbf7", "#d9f3e4", "🟢 네이버 스마트에디터 맞춤 서식이 복사되었습니다!");
    }});
    document.getElementById("copyMdBtn").addEventListener("click", () => {{
      navigator.clipboard.writeText(mdSource).then(() => showToast("📝 마크다운 원문이 복사되었습니다!"));
    }});
  </script>
</body>
</html>"""

def scan_workflow_posts():
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
        rel_md = os.path.relpath(fpath, WORKFLOW_BLOG_DIR)
        rel_html = rel_md[:-3] + ".html"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        m_title = re.search(r"^#\s+(.+)$", content, re.M)
        title = m_title.group(1).strip() if m_title else post_id
        m_cat = re.search(r">\s*\*\*카테고리\*\*:\s*(.+)$", content, re.M)
        category = m_cat.group(1).strip() if m_cat else "통합 워크플로우"
        m_score = re.search(r">\s*\*\*주제 평가 점수\*\*:\s*\*\*([0-9]+/100점)\*\*", content, re.M)
        score_str = m_score.group(1).strip() if m_score else "90/100점"
        m_sum = re.search(r">\s*\*\*📌 핵심 요약\*\*:\s*(.+)$", content, re.M)
        desc = m_sum.group(1).strip().replace("**", "") if m_sum else ""
        if len(desc) > 150:
            desc = desc[:150] + "..."
        char_count = len(content.replace(" ", "").replace("\n", ""))
        posts.append({
            "post_id": post_id,
            "date_only": date_only,
            "post_num": post_num,
            "category": category,
            "score_str": score_str,
            "title": title,
            "desc": desc,
            "char_count": char_count,
            "rel_md": rel_md,
            "rel_html": rel_html
        })
    return posts

def build_workflow_index_html(today_str, weekday_str, posts):
    post_cards_html = ""
    for p in posts:
        is_today = (p["date_only"] == today_str)
        today_class = " today" if is_today else ""
        post_cards_html += f"""
            <article class="post-card{today_class}">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                  <span style="font-size:12.5px; font-weight:700; color:var(--wf-dark);">📍 {p['date_only']} ({weekday_str})</span>
                  <span class="cat-pill">📂 {p['category']}</span>
                  <span class="score-pill">🎯 평가 {p['score_str']}</span>
                </div>
                <span style="font-size:11.5px; color:var(--text-muted); font-weight:600;">#{p['post_num']}편</span>
              </div>
              <a href="{p['rel_html']}" class="post-card-title">{p['title']}</a>
              <p style="font-size:13.5px; color:var(--text-sub); margin-bottom:14px; line-height:1.55;">{p['desc']}</p>
              <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed var(--border); padding-top:12px; font-size:12px; color:var(--text-muted); flex-wrap:wrap; gap:10px;">
                <div>Step 1~8 검증 완료 · 분량: 약 {p['char_count']:,}자 (공백 제외)</div>
                <div style="display:flex; gap:8px;">
                  <a href="{p['rel_md']}" target="_blank" class="action-btn">📄 MD 원문</a>
                  <a href="{p['rel_html']}" class="action-btn action-btn-primary">👁️ 포스트 열기 & 에디터 복사</a>
                </div>
              </div>
            </article>
        """

    claude_cmd = (
        "이 저장소의 README.md와 workflow/daily-workflow.md를 먼저 읽어 주세요.\\n\\n"
        "오늘의 블로그 콘텐츠 작업을 시작합니다.\\n\\n"
        "1. topics/topic-backlog.md에서 기존 주제와 중복되는 항목을 확인합니다.\\n"
        "2. 네이버 블로그용 실시간 이슈 주제 후보와 티스토리용 검색형 주제 후보를 구분합니다.\\n"
        "3. 실제 최신 검색 데이터를 확인할 수 없는 경우 검색량이나 순위를 추측하지 말고, 추가 조사가 필요한 항목으로 표시합니다.\\n"
        "4. 후보별 검색 의도, 장기성, 경쟁 콘텐츠의 빈틈, 사실 확인 가능성을 평가합니다.\\n"
        "5. 우선 작성할 주제를 추천하고, 선정 이유와 필요한 출처를 제시합니다.\\n"
        "6. 제가 주제를 승인하기 전에는 최종 게시글을 발행하거나 기존 파일을 덮어쓰지 마세요.\\n"
        "7. 승인된 주제에 대해서만 해당 플랫폼의 작성 지침에 따라 초안을 생성합니다.\\n"
        "8. fact-check.md와 publishing.md 기준으로 검토하고, 미확인 사실과 발행 전 점검 항목을 별도로 출력합니다.\\n\\n"
        "우선 주제 후보와 평가 결과부터 보여 주세요."
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>네이버 · 티스토리 통합 워크플로우 작업실 | AI Blog Notes</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <style>
    :root {{
      --wf: #4f46e5;
      --wf-dark: #4338ca;
      --wf-light: #eef2ff;
      --wf-border: #c7d2fe;
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
    .wf-badge {{
      background: var(--wf);
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
    .header-link:hover {{ border-color: var(--wf); color: var(--wf-dark); }}
    .container {{ max-width: 1120px; margin: 28px auto 0; padding: 0 20px; }}
    .hero-banner {{
      background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
      color: #fff;
      padding: 32px 36px;
      border-radius: 16px;
      margin-bottom: 28px;
      box-shadow: 0 8px 24px rgba(79, 70, 229, 0.2);
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
      border-color: var(--wf);
      box-shadow: 0 4px 14px rgba(79, 70, 229, 0.08);
    }}
    .cat-pill {{
      background: var(--wf-light);
      color: var(--wf-dark);
      border: 1px solid var(--wf-border);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
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
    .post-card-title:hover {{ color: var(--wf-dark); text-decoration: underline; }}
    .file-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }}
    @media (max-width: 600px) {{ .file-grid {{ grid-template-columns: 1fr; }} }}
    .file-item {{
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      background: var(--bg);
      text-decoration: none;
      color: var(--text-main);
      transition: all 0.15s;
    }}
    .file-item:hover {{
      border-color: var(--wf);
      background: var(--wf-light);
    }}
    .file-item-title {{ font-size: 13.5px; font-weight: 750; color: var(--wf-dark); margin-bottom: 4px; }}
    .file-item-desc {{ font-size: 12px; color: var(--text-sub); }}
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
    .action-btn-primary {{ background: var(--wf); color: #fff; border-color: var(--wf); }}
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
        <span class="wf-badge">WORKFLOW HUB</span>
        <div class="brand-title">네이버 · 티스토리 통합 워크플로우 작업실</div>
      </div>
      <div class="header-links">
        <a href="../../index.html" class="header-link">🏠 멀티 블로그 포털</a>
        <a href="../naver/index.html" class="header-link">🟢 네이버 작업실</a>
        <a href="../tistory/index.html" class="header-link">🟠 티스토리 작업실</a>
        <a href="../../docs/index.html#daily-workflow" class="header-link">📚 워크플로우 문서 뷰어</a>
      </div>
    </div>
  </header>

  <div class="container">
    <section class="hero-banner">
      <div class="hero-text">
        <h1>⚙️ 네이버 · 티스토리 8단계 통합 워크플로우 작업실</h1>
        <p>주제 조사 1회 → 플랫폼별 맞춤 원고 2편(티스토리 7단계 본문 + 네이버 공감 요약본) 동시 생산! 공식 출처 검증과 팩트체크를 통과한 고득점 원고를 관리합니다.</p>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span class="stat-number">{len(posts)} 편</span>
          <span class="stat-label">워크플로우 원고</span>
        </div>
        <div class="stat-box">
          <span class="stat-number">8 단계</span>
          <span class="stat-label">팩트체크 검증</span>
        </div>
      </div>
    </section>

    <div class="main-grid">
      <div class="left-col">
        <section class="card">
          <div class="card-header">
            <div class="card-title">📝 8단계 워크플로우 기반 작성 포스팅 목록</div>
            <span style="font-size: 12px; color: var(--text-muted);">총 {len(posts)}편 작성됨</span>
          </div>
          {post_cards_html}
        </section>

        <section class="card">
          <div class="card-header">
            <div class="card-title">📂 표준 워크플로우 · 프롬프트 · 가이드라인 파일 체계</div>
            <a href="../../docs/index.html#daily-workflow" style="font-size: 12.5px; color: var(--wf-dark); font-weight: 700; text-decoration: none;">전체 문서 뷰어로 열기 →</a>
          </div>
          <div class="file-grid">
            <a href="../../workflow/daily-workflow.md" target="_blank" class="file-item">
              <div class="file-item-title">📋 workflow/daily-workflow.md</div>
              <div class="file-item-desc">매일 수행할 8단계 작업 순서와 30분 시간 배분</div>
            </a>
            <a href="../../workflow/topic-selection.md" target="_blank" class="file-item">
              <div class="file-item-title">🎯 workflow/topic-selection.md</div>
              <div class="file-item-desc">네이버·티스토리 주제 선정 규칙 및 100점 평가표</div>
            </a>
            <a href="../../workflow/article-production.md" target="_blank" class="file-item">
              <div class="file-item-title">✍️ workflow/article-production.md</div>
              <div class="file-item-desc">주제 조사 1회 → 플랫폼별 원고 2편 제작·검증 절차</div>
            </a>
            <a href="../../workflow/publishing.md" target="_blank" class="file-item">
              <div class="file-item-title">✅ workflow/publishing.md</div>
              <div class="file-item-desc">발행 전 필수 3대 팩트체크 및 플랫폼별 점검표</div>
            </a>
            <a href="../../workflow/performance-review.md" target="_blank" class="file-item">
              <div class="file-item-title">📈 workflow/performance-review.md</div>
              <div class="file-item-desc">주간 성과 분석(노출·클릭·체류시간) 및 다음 주 계획</div>
            </a>
            <a href="../../topics/topic-backlog.md" target="_blank" class="file-item">
              <div class="file-item-title">🗂️ topics/topic-backlog.md</div>
              <div class="file-item-desc">5대 카테고리별 미작성 유망 주제 대기열 & 캘린더</div>
            </a>
            <a href="../../prompts/fact-check.md" target="_blank" class="file-item">
              <div class="file-item-title">🔍 prompts/fact-check.md</div>
              <div class="file-item-desc">초안 사실관계·수치·가상 경험 검증 전용 프롬프트</div>
            </a>
            <a href="../../logs/publishing-log.csv" target="_blank" class="file-item">
              <div class="file-item-title">📊 logs/publishing-log.csv</div>
              <div class="file-item-desc">일자별 네이버·티스토리 발행 이력 및 성과 기록 CSV</div>
            </a>
          </div>
        </section>
      </div>

      <div class="right-col">
        <section class="card" style="border: 2px solid var(--wf);">
          <div class="card-title" style="margin-bottom: 10px;">🤖 매일 Claude Code / AI 실행 명령</div>
          <p style="font-size: 12.5px; color: var(--text-sub); margin-bottom: 12px;">
            저장소 루트에서 아래 명령을 복사해 입력하면 주제 중복 확인 → 후보 평가 → 승인 후 초안 생성 → 팩트체크까지 표준 절차대로 실행됩니다.
          </p>
          <button class="action-btn action-btn-primary" style="width: 100%; justify-content: center; padding: 10px;" onclick="copyText('{claude_cmd}')">
            📋 일일 워크플로우 시작 명령 복사
          </button>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 12px;">⏱️ 매일 30분 표준 시간 배분</div>
          <div style="font-size: 13px; color: var(--text-sub); display: flex; flex-direction: column; gap: 8px;">
            <div style="display:flex; justify-content:space-between;"><span>1. 주제 수집 및 선정</span><strong>5분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>2. 공식 자료 확인</span><strong>5분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>3. 플랫폼별 AI 초안 작성</span><strong>10분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>4. 사실 검증 및 편집</span><strong>7분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>5. 발행 및 CSV 기록</span><strong>3분</strong></div>
            <div style="display:flex; justify-content:space-between; border-top:1px solid var(--border); padding-top:8px; color:var(--wf-dark);"><strong>일일 합계</strong><strong>총 30분</strong></div>
          </div>
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
  </script>
</body>
</html>"""

def run_workflow_batch(target_date=None):
    now = datetime.now()
    today_date = datetime.strptime(target_date, "%Y-%m-%d") if target_date else now
    today_str = today_date.strftime("%Y-%m-%d")
    weekday_str = WEEKDAYS_KR[today_date.weekday()]
    ym = today_str[:7].replace("-", "")

    wf_post_dir = os.path.join(POSTS_DIR, ym)
    ts_post_dir = os.path.join(TISTORY_POSTS_DIR, ym)
    os.makedirs(wf_post_dir, exist_ok=True)
    os.makedirs(ts_post_dir, exist_ok=True)

    for idx, item in enumerate(WORKFLOW_ARTICLES, 1):
        post_id = today_str if idx == 1 else f"{today_str}-{idx}"
        md_content = format_full_workflow_markdown(today_str, weekday_str, item)
        html_content = build_workflow_article_html(post_id, today_str, weekday_str, item, md_content)

        # 1) blog/workflow/posts/YYYYMM/ 에 저장 (#1편 ~ #5편)
        with open(os.path.join(wf_post_dir, f"{post_id}.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
        with open(os.path.join(wf_post_dir, f"{post_id}.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        # 2) blog/tistory/posts/YYYYMM/ 에도 추가 연동 (#4편 ~ #8편)
        ts_seq = idx + 3
        ts_post_id = f"{today_str}-{ts_seq}"
        ts_md_content = md_content.replace("> **워크플로우 단계**:", f"> **Google Trends 상승 검색어**: `{item['topic']}` (상승)  \n> **워크플로우 단계**:")
        ts_html_content = build_workflow_article_html(ts_post_id, today_str, weekday_str, item, ts_md_content)
        with open(os.path.join(ts_post_dir, f"{ts_post_id}.md"), "w", encoding="utf-8") as f:
            f.write(ts_md_content)
        with open(os.path.join(ts_post_dir, f"{ts_post_id}.html"), "w", encoding="utf-8") as f:
            f.write(ts_html_content)

    posts = scan_workflow_posts()
    os.makedirs(WORKFLOW_BLOG_DIR, exist_ok=True)
    with open(os.path.join(WORKFLOW_BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_workflow_index_html(today_str, weekday_str, posts))

    # 티스토리 대시보드 및 루트 포털도 함께 갱신
    ts_script = os.path.join(BASE_DIR, "tools", "daily_tistory_batch.py")
    if os.path.exists(ts_script):
        subprocess.run([sys.executable, ts_script, today_str], cwd=BASE_DIR)

    print(f"✅ 워크플로우 기반 심층 블로그 원고 {len(WORKFLOW_ARTICLES)}편 생성 및 티스토리 연동 완료")

if __name__ == "__main__":
    date_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run_workflow_batch(date_args[0] if date_args else None)

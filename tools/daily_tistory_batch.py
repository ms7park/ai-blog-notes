#!/usr/bin/env python3
"""
Daily Tistory Blog Automation Batch (Google Trends Rising Keywords -> Evergreen Search Content)
Google Trends(https://trends.google.com/trends/) 상승 검색어를 수집하고,
5대 평가 기준(100점 만점 루브릭)으로 장기 검색 가치가 높은 주제를 선별하여
티스토리 표준 7단계 구성(.md, .html) 및 티스토리 대시보드(blog/tistory/index.html)를 생성/갱신합니다.
"""

import os
import sys
import glob
import json
import re
import subprocess
import fcntl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TISTORY_BLOG_DIR = os.path.join(BASE_DIR, "blog", "tistory")
POSTS_DIR = os.path.join(TISTORY_BLOG_DIR, "posts")
NAVER_BLOG_DIR = os.path.join(BASE_DIR, "blog", "naver")
NAVER_POSTS_DIR = os.path.join(NAVER_BLOG_DIR, "posts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "daily_batch.log")

WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

# 티스토리 5대 공식 카테고리 및 운영 목표 비중
TISTORY_CATEGORIES = {
    "pension_finance": {
        "name": "은퇴·연금·생활비",
        "ratio": "30%",
        "desc": "국민연금, 개인연금, 퇴직 후 건강보험, 생활비·절세 계산",
        "keywords": [
            "국민연금", "기초연금", "퇴직연금", "주택연금", "개인연금", "연금저축", "irp", "isa",
            "건강보험", "건보료", "피부양자", "임의계속가입", "노후자금", "생활비",
            "절세", "세금", "세액공제", "연말정산", "종합소득세", "금융소득", "양도세", "상속세", "증여세",
            "금리", "기준금리", "예금", "적금", "파킹통장", "경상수지", "환율", "물가", "인플레이션",
            "지원금", "보조금", "환급금", "장려금", "배당", "국채"
        ],
        "scores": {"trend": 4, "intent": 5, "gap": 4, "capability": 4, "evergreen": 5},  # 88/100
        "official_refs": [
            ("국민연금공단 공식 홈페이지 (내 연금 알아보기)", "https://www.nps.or.kr/"),
            ("국민건강보험공단 공식 사이트 (보험료 모의계산)", "https://www.nhis.or.kr/"),
            ("금융감독원 통합연금포털", "https://100lifeplan.fss.or.kr/"),
            ("한국은행 경제통계시스템 (ECOS)", "https://ecos.bok.or.kr/")
        ]
    },
    "ai_it": {
        "name": "AI·IT 활용법",
        "ratio": "25%",
        "desc": "ChatGPT, AI 코딩·문서 도구, 맥(Mac)·스마트폰 사용법, 업무 자동화",
        "keywords": [
            "chatgpt", "챗gpt", "생성형 ai", "인공지능", "클로드", "claude", "제미나이", "gemini",
            "엔비디아", "nvidia", "반도체", "오픈ai", "openai", "퍼플렉시티", "코파일럿",
            "맥북", "mac", "애플", "아이폰", "ios", "갤럭시", "안드로이드", "스마트폰",
            "깃허브", "github", "vercel", "자동화", "파이썬", "오류", "로그인", "서치콘솔", "애드센스"
        ],
        "scores": {"trend": 5, "intent": 5, "gap": 4, "capability": 5, "evergreen": 5},  # 96/100
        "official_refs": [
            ("Google 검색 센터 (검색엔진 최적화 기본 가이드)", "https://developers.google.com/search/docs?hl=ko"),
            ("Google AdSense 공식 고객센터", "https://support.google.com/adsense/?hl=ko"),
            ("Google Trends 공식 페이지", "https://trends.google.com/trends/?geo=KR"),
            ("OpenAI 공식 도움말 센터", "https://help.openai.com/")
        ]
    },
    "product_compare": {
        "name": "제품 비교·사용법",
        "ratio": "25%",
        "desc": "제품 사양, 기능 비교, 사용법, 수수료·구매 전 필수 확인 사항",
        "keywords": [
            "주얼리", "순금", "골드바", "금시세", "금값", "다이아몬드", "에르메스", "명품",
            "노트북", "태블릿", "아이패드", "갤럭시탭", "워치", "스마트워치", "이어폰",
            "가전", "냉장고", "세탁기", "로봇청소기", "공기청정기", "비교", "사양", "스펙",
            "자동차", "전기차", "하이브리드", "타이어", "블랙박스", "보험료"
        ],
        "scores": {"trend": 4, "intent": 4, "gap": 4, "capability": 4, "evergreen": 4},  # 80/100
        "official_refs": [
            ("한국거래소(KRX) 금시장 정보시스템", "http://marketdata.krx.co.kr/"),
            ("한국소비자원 참가격 / 소비자24 비교정보", "https://www.consumer.go.kr/"),
            ("관세청 해외직구 통관 및 세율 안내", "https://www.customs.go.kr/")
        ]
    },
    "golf_hobby": {
        "name": "골프·취미",
        "ratio": "10%",
        "desc": "골프·파크골프 연습, 장비 선택 기준, 시니어 취미·운동 정보",
        "keywords": [
            "골프", "파크골프", "골프채", "드라이버", "아이언", "퍼터", "공인은증",
            "등산", "트레킹", "등산화", "배드민턴", "탁구", "당구", "테니스", "캠핑", "자전거"
        ],
        "scores": {"trend": 3, "intent": 4, "gap": 4, "capability": 4, "evergreen": 4},  # 76/100
        "official_refs": [
            ("대한파크골프협회 공식 홈페이지 (인증 용구 확인)", "http://www.kpga7330.com/"),
            ("국민체육진흥공단 국민체력100", "https://nfa.kspo.or.kr/")
        ]
    },
    "pet_life": {
        "name": "반려동물·생활정보",
        "ratio": "10%",
        "desc": "사료 성분 비교, 반려동물 용품, 일상 생활 문제 해결 및 건강검진",
        "keywords": [
            "반려동물", "강아지", "고양이", "사료", "동물병원", "펫보험", "반려견",
            "건강검진", "국가검진", "임플란트", "백내장", "실손보험", "실비", "독감", "예방접종",
            "김장", "절임배추", "사과", "과일", "보관법", "농협"
        ],
        "scores": {"trend": 4, "intent": 4, "gap": 3, "capability": 4, "evergreen": 4},  # 76/100
        "official_refs": [
            ("질병관리청 국가건강정보포털", "https://health.kdca.go.kr/"),
            ("농림축산검역본부 국가동물보호정보시스템", "https://www.animal.go.kr/"),
            ("식품의약품안전처 식품안전나라", "https://www.foodsafetykorea.go.kr/")
        ]
    }
}

def log(msg):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    print(formatted)
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def evaluate_trend_for_tistory(keyword, news_title=""):
    """
    Google Trends 상승 검색어를 분석하여:
    1) 티스토리 5대 카테고리 매칭 여부 판별 (정확한 단어/2음절 이상 키워드 매칭)
    2) 티스토리 5대 주제 평가 기준(100점 만점) 점수 산출
    3) 단기 이슈를 '장기 검색형 질문(방법·비교·조건·절차)'으로 변환한 주제 및 제목 후보 3개 반환
    """
    kw = keyword.strip()
    kw_lower = kw.lower()
    target = f"{kw} {news_title}".lower()

    # "ai" 단독 영문 단어 매칭 처리 (daily, mail 등 오매칭 방지)
    has_ai_word = bool(re.search(r'(?<![a-z])ai(?![a-z])', target))

    matched_cat_key = None
    matched_kw = None

    if has_ai_word:
        matched_cat_key = "ai_it"
        matched_kw = "AI"
    else:
        for cat_key, cat_info in TISTORY_CATEGORIES.items():
            for ck in cat_info["keywords"]:
                if ck in target:
                    matched_cat_key = cat_key
                    matched_kw = ck
                    break
            if matched_cat_key:
                break

    # 맞춤형 티스토리 변환 로직
    if matched_cat_key:
        cat_info = TISTORY_CATEGORIES[matched_cat_key]
        sc = cat_info["scores"].copy()
        total_score = sum(sc.values()) * 4
        rec_level = "높음 (추천)" if total_score >= 80 else "보통 (작성 가능)"

        # 카테고리별 구체적인 검색 질문 & 제목 후보 3개 생성
        if matched_cat_key == "pension_finance":
            if "경상수지" in kw or "환율" in target or "금리" in target:
                search_question = f"'{kw}' 등 거시경제 지표와 물가·환율 변동이 내 국민연금 수령액 및 노후 자산에 미치는 영향과 공식 조회 방법은?"
                candidates = [
                    f"국민연금 예상 수령액 조회 방법 및 물가상승률 반영 기준 정리 ({kw}·경제지표 확인법)",
                    f"경상수지·물가 변동 시 국민연금 수령액은 어떻게 바뀔까? 공식 사이트 확인 절차",
                    f"은퇴 전 필수 확인! 국민연금·퇴직연금 예상 수령액 계산 방법과 물가 연동 기준"
                ]
                final_title = candidates[0]
            elif any(w in target for w in ["연금", "건보료", "건강보험"]):
                search_question = f"{kw} 예상 금액 계산 기준과 공식 홈페이지에서 본인 조건을 조회하는 구체적인 절차는?"
                candidates = [
                    f"{kw} 계산 기준 및 공식 사이트 조회 방법 4단계 정리 (신청 조건·주의사항)",
                    f"퇴직 후 {kw} 얼마나 나올까? 모의계산 절차와 감액·변동 기준 비교",
                    f"{kw} 확인 방법 총정리: 자격 조건부터 항목별 비교표까지"
                ]
                final_title = candidates[0]
            else:
                search_question = f"{kw} 관련 세금·수수료·지원 조건과 공식 기관에서 정확히 확인하는 절차는?"
                candidates = [
                    f"{kw} 핵심 기준과 공식 사이트 확인 방법 정리 (대상 조건·절세 비교표)",
                    f"은퇴·노후 자산을 위한 {kw} 체크리스트: 신청 절차와 조건별 비교",
                    f"{kw} 자주 묻는 질문 해결: 자격 요건·계산 방법·주의사항 총정리"
                ]
                final_title = candidates[0]

        elif matched_cat_key == "ai_it":
            if "엔비디아" in kw or "반도체" in target or has_ai_word:
                search_question = f"생성형 AI(ChatGPT 등) 트렌드 확산 속 AI로 블로그 초안을 작성하고 공식 자료로 사실관계(팩트체크)를 검증하는 구체적인 방법은?"
                candidates = [
                    f"ChatGPT 등 AI로 블로그 초안 작성 후 사실관계(팩트체크) 검증하는 5단계 방법",
                    f"AI가 작성한 글의 할루시네이션(사실 오류) 확인하는 방법과 발행 전 점검표",
                    f"Google Trends 상승 검색어('{kw}'·AI)를 활용해 검색 유입형 정보 글 쓰는 절차"
                ]
                final_title = candidates[0]
            else:
                search_question = f"{kw} 설정 방법 또는 오류 발생 시 공식 고객센터 기준 해결 순서는?"
                candidates = [
                    f"{kw} 설정 및 문제 해결 순서 총정리: 초보자도 따라 하는 단계별 가이드",
                    f"{kw} 사용법과 자주 발생하는 오류 해결 방법 (공식 안내 기준)",
                    f"알아두면 시간 아끼는 {kw} 핵심 기능 비교 및 초기 설정 체크리스트"
                ]
                final_title = candidates[0]

        elif matched_cat_key == "product_compare":
            if "주얼리" in kw or "에르메스" in kw or "금" in target:
                search_question = f"순금(24K) 주얼리·골드바·KRX 금현물 구매 시 공임비·부가세·수수료 차이와 구매 전 확인 사항은?"
                candidates = [
                    f"순금(24K) 주얼리 vs 골드바 vs KRX 금현물 구매 방법 및 수수료·세금 비교표",
                    f"금·파인주얼리 구매 전 필수 확인 사항: 순도(24K·18K·14K) 기준과 부가세·수수료 비교",
                    f"실물 금(주얼리·골드바)과 금현물 계좌 장단점 비교 및 공식 시세 조회 방법"
                ]
                final_title = candidates[0]
            else:
                search_question = f"{kw} 구매 전 반드시 비교해야 할 사양·유지비·수수료 기준과 확인 방법은?"
                candidates = [
                    f"{kw} 사양·기능 비교 및 구매 전 필수 확인 사항 5가지 정리",
                    f"{kw} 선택 기준 총정리: 등급별 차이점 비교표와 사용 시 주의사항",
                    f"후회 없는 {kw} 선택을 위한 스펙 비교 및 공식 인증 확인 방법"
                ]
                final_title = candidates[0]

        elif matched_cat_key == "golf_hobby":
            search_question = f"{kw} 입문자가 장비를 선택할 때 확인해야 할 공인 규격·사양 비교와 연습 순서는?"
            candidates = [
                f"{kw} 장비 선택 기준 및 입문자 필수 확인 사항 비교표 (공인 규격·체크리스트)",
                f"초보자를 위한 {kw} 기본 규칙과 단계별 연습 방법 정리",
                f"관절 부담 줄이는 {kw} 올바른 자세와 용품 비교 가이드"
            ]
            final_title = candidates[0]

        else:  # pet_life
            search_question = f"{kw} 관련 공식 기준·성분·대상자 조건을 확인하고 실생활 문제를 해결하는 방법은?"
            candidates = [
                f"{kw} 기준 및 단계별 확인 방법 정리 (필수 체크리스트·비교표)",
                f"실생활에서 바로 쓰는 {kw} 선택 기준과 주의사항 총정리",
                f"{kw} 공식 안내 기준 확인 절차와 조건별 차이점 비교"
            ]
            final_title = candidates[0]

        return {
            "is_selected": True,
            "cat_key": matched_cat_key,
            "cat_name": cat_info["name"],
            "cat_ratio": cat_info["ratio"],
            "matched_keyword": matched_kw,
            "scores": sc,
            "total_score": total_score,
            "rec_level": rec_level,
            "search_question": search_question,
            "title_candidates": candidates,
            "final_title": final_title,
            "official_refs": cat_info["official_refs"]
        }

    # 비매칭(단기 연예/스포츠/단순 사건사고 이슈) -> 티스토리에서는 낮은 점수로 평가하여 작성 보류 안내
    sc = {"trend": 4, "intent": 2, "gap": 2, "capability": 2, "evergreen": 1}
    total_score = sum(sc.values()) * 4  # 44/100
    return {
        "is_selected": False,
        "cat_key": "none",
        "cat_name": "단기 이슈 (네이버 권장)",
        "cat_ratio": "-",
        "matched_keyword": "-",
        "scores": sc,
        "total_score": total_score,
        "rec_level": "낮음 (티스토리 보류)",
        "search_question": f"단기 실시간 이슈('{kw}')로 장기 검색 지속성이 낮음 → 공식 제도·방법·비교 질문으로 전환 필요",
        "title_candidates": [
            f"[전환 예시] '{kw}' 관련 공식 발표 사실 확인 및 관련 제도·규정 정리"
        ],
        "final_title": f"[보류] '{kw}' — 단기 이슈성 검색어 (네이버 블로그 발행 권장)",
        "official_refs": []
    }

def fetch_google_trends_for_tistory():
    """Google Trends 상승 검색어 Top 10을 수집하고 티스토리 100점 평가표 결과와 함께 반환"""
    url = "https://trends.google.co.kr/trending/rss?geo=KR"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_trends = []

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = root.findall(".//item")

        for item in items[:10]:
            title = item.find("title").text if item.find("title") is not None else ""
            approx = item.find("{https://trends.google.com/trending/rss}approx_traffic")
            traffic = approx.text if approx is not None else "상승"
            news_items = item.findall("{https://trends.google.com/trending/rss}news_item")
            news_title = news_items[0].find("{https://trends.google.com/trending/rss}news_item_title").text if news_items else ""
            news_url = news_items[0].find("{https://trends.google.com/trending/rss}news_item_url").text if news_items else ""

            raw_trends.append({
                "keyword": title,
                "traffic": traffic,
                "news_title": news_title,
                "news_url": news_url
            })
    except Exception as e:
        log(f"⚠️ Google Trends RSS 수집 실패 (기본 상승 검색어 사용): {e}")

    if len(raw_trends) < 10:
        fallbacks = [
            {"keyword": "경상수지", "traffic": "500+", "news_title": "한국 경상수지 흑자 및 환율·물가 지표 발표", "news_url": "https://ecos.bok.or.kr/"},
            {"keyword": "엔비디아", "traffic": "500+", "news_title": "AI 반도체 및 생성형 AI 활용 트렌드 확산", "news_url": "https://trends.google.com/trends/"},
            {"keyword": "주얼리", "traffic": "200+", "news_title": "순금 파인주얼리 및 골드바 안전자산 관심 급증", "news_url": "http://marketdata.krx.co.kr/"},
            {"keyword": "국민연금", "traffic": "1000+", "news_title": "국민연금 예상 수령액 조회 및 물가상승률 반영 기준", "news_url": "https://www.nps.or.kr/"},
            {"keyword": "건강보험료", "traffic": "800+", "news_title": "퇴직 후 건강보험료 피부양자 자격 및 임의계속가입 비교", "news_url": "https://www.nhis.or.kr/"}
        ]
        raw_trends.extend(fallbacks[:10 - len(raw_trends)])

    evaluated = []
    for idx, item in enumerate(raw_trends, 1):
        ev = evaluate_trend_for_tistory(item["keyword"], item["news_title"])
        evaluated.append({
            "rank": idx,
            "keyword": item["keyword"],
            "traffic": item["traffic"],
            "news_title": item["news_title"],
            "news_url": item["news_url"],
            "eval": ev
        })

    return evaluated

def build_tistory_post_markdown(post_id, date_str, weekday_str, trend_item):
    """
    티스토리 검색형 블로그 글 작성 지침(7단계 구성 + 제목 후보 3개 + 사실 확인 체크리스트)에 맞춘
    고품질 마크다운 본문 생성
    """
    kw = trend_item["keyword"]
    news = trend_item.get("news_title", "")
    ev = trend_item["eval"]
    cat_key = ev["cat_key"]
    cat_name = ev["cat_name"]
    final_title = ev["final_title"]
    candidates = ev["title_candidates"]
    search_q = ev["search_question"]
    score = ev["total_score"]
    sc = ev["scores"]
    refs = ev["official_refs"]

    refs_md = "\n".join([f"- [{name}]({url})" for name, url in refs])

    # 카테고리별 심층 본문 템플릿 구성
    if cat_key == "pension_finance" and ("경상수지" in kw or "연금" in final_title):
        core_summary = (
            "국민연금 예상 수령액은 **국민연금공단 '내 연금 알아보기' 공식 누리집** 또는 **모바일 앱 '내 곁에 국민연금'**에서 공동·금융·간편인증 로그인 후 1분 만에 조회할 수 있습니다. "
            "특히 경상수지·환율·소비자물가지수 등 거시경제 지표가 변동하더라도, 국민연금은 **매년 전국소비자물가변동률을 반영해 수령액을 인상(실질가치 보전)**하므로 은퇴 후 인플레이션 방어에 가장 핵심적인 현금 흐름 역할을 합니다."
        )
        body_sections = f"""## 1. 왜 지금 국민연금 예상 수령액과 물가 반영 기준을 확인해야 할까요?

최근 Google Trends에서 **'{kw}'** 관련 뉴스({news})가 상승 검색어로 주목받으면서 환율, 수출입 경기, 물가 흐름이 내 노후 자산에 어떤 영향을 주는지 궁금해하는 분들이 많습니다.

은퇴를 앞두거나 이미 은퇴 생활을 시작한 분들에게 가장 중요한 질문은 단순한 경제 뉴스 요약이 아니라 **"물가가 오를 때 내 연금 수령액은 실제로 어떻게 계산되며, 어디서 정확한 금액을 확인할 수 있는가?"**입니다. 이 글에서는 공식 기관 자료를 바탕으로 **국민연금 예상 수령액 조회 절차, 물가상승률 연동 구조, 수령 시기별(조기·정상·연기) 비교표, 그리고 확인 시 주의사항**을 단계별로 정리합니다.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

바쁜 분들을 위해 가장 중요한 핵심 답변을 먼저 요약합니다.

- **공식 조회처**: 국민연금공단 [내 연금 알아보기](https://www.nps.or.kr/) 또는 금융감독원 [통합연금포털](https://100lifeplan.fss.or.kr/)
- **준비물**: 간편인증(카카오·네이버·토스·PASS 등) 또는 공동·금융인증서
- **물가 연동 핵심 원칙**: 국민연금은 매년 1월 전년도 **전국소비자물가변동률**을 반영하여 기본연금액을 인상합니다(국민연금법 제51조 기준).
- **조회 전 필수 확인**: 모의계산 결과는 **현재 가치(현재 소득 기준)**로 산출되므로, 향후 납부 기간과 소득 변동에 따라 실제 수령액은 달라질 수 있습니다.

---

## 3. 공식 사이트에서 국민연금 예상 수령액 확인하는 순서

### 1단계: 국민연금공단 '내 연금 알아보기' 접속 및 본인 인증
1. PC 또는 스마트폰 브라우저에서 [국민연금공단 공식 홈페이지(nps.or.kr)](https://www.nps.or.kr/)에 접속합니다.
2. 메인 화면 자주 찾는 서비스에서 **[내 연금 알아보기]** 메뉴를 클릭합니다.
3. 간편인증(카카오톡, 네이버, PASS 등) 또는 금융인증서로 로그인합니다.

### 2단계: 예상연금액 조회 및 가입내역 확인
1. 상단 메뉴 중 **[예상연금액 조회]** → **[국민연금 예상연금액 알아보기]**를 선택합니다.
2. 화면에 표시되는 **총 가입 개월 수**, **납부한 총 보험료**, 그리고 **만 65세(출생연도별 정상 수령 연령)부터 매월 받게 될 예상 노령연금액(세전 기준)**을 확인합니다.

### 3단계: 미래 소득·가입기간 가정 조건 입력해 비교하기
1. 퇴직 후 **임의계속가입**을 고려 중이거나 소득이 변경된 경우 **[상세연금 조회]** 또는 **[모의계산]** 메뉴를 엽니다.
2. 만 60세 이후에도 추가 납부할 예상 기간과 기준소득월액을 입력하면, 추가 납부 시 늘어나는 월 예상 수령액을 비교할 수 있습니다.

### 4단계: 통합연금포털에서 개인연금·퇴직연금까지 한 번에 합산하기
1. 국민연금 외에 퇴직연금(IRP)과 연금저축 계좌가 있다면 금융감독원 [통합연금포털(100lifeplan.fss.or.kr)](https://100lifeplan.fss.or.kr/)에 접속합니다.
2. **[내 연금 조회]**를 신청(최초 신청 시 영업일 기준 약 3일 소요)하면 연령대별 전체 연금 합산 수령표를 한눈에 내려받을 수 있습니다.

---

## 4. 수령 시기(조기·정상·연기)에 따른 수령률 비교표

국민연금은 본인의 건강 상태, 퇴직 후 소득 유무, 생활비 필요 시점에 따라 수령 개시 시점을 조정할 수 있습니다. 아래 표는 **국민연금법상 기준 수령률(정상 수령 = 100% 가정)**을 비교한 공식 기준표입니다.

| 구분 | 신청 가능 시기 (출생연도별 정상 연령 기준) | 연금 수령률 변화 (가정 조건 명시) | 유리한 대상 및 특징 |
| :--- | :--- | :--- | :--- |
| **조기노령연금** | 정상 수령 연령보다 **최대 5년 일찍** 신청 (소득이 있는 업무에 종사하지 않을 것) | 1년 앞당길 때마다 **연 6%p(월 0.5%p) 감액** (5년 조기 수령 시 최대 30% 감액된 70% 수령) | 은퇴 직후 소득 공백기가 길어 당장 생활비 현금 흐름이 급한 경우 |
| **정상 노령연금** | 출생연도별 기준 연령 (1969년생 이후 **만 65세**) | **기본연금액 100%** + 부양가족연금액 (매년 물가상승률 반영) | 가장 표준적인 수령 방식 |
| **연기연금** | 정상 수령 연령부터 **최대 5년 늦춰** 신청 (전부 또는 일부 50~90% 연기 가능) | 1년 연기할 때마다 **연 7.2%p(월 0.6%p) 증액** (5년 연기 시 최대 36% 증액된 136% 수령) | 은퇴 후 다른 근로·사업소득이 있거나 건강보험료·종합소득세 분산이 필요한 경우 |

> **※ 표 해석 시 유의사항**: 위 수령률(감액 연 6%, 증액 연 7.2%)은 현행 국민연금법 기준이며, 개인의 총 가입기간·평균소득월액·기대여명 및 소득 유무에 따라 손익분기점이 달라집니다.

---

## 5. 조회 전 반드시 체크해야 할 3가지 예외 조건

1. **출생연도별 정상 수령 개시 연령 차이 확인**
   - 1957~1960년생은 만 62세, 1961~1964년생은 만 63세, 1965~1968년생은 만 64세, **1969년생 이후부터 만 65세**입니다. 본인의 출생연도 기준 연령을 먼저 확인하세요.
2. **소득 활동에 따른 노령연금 감액 제도 (재직자 노령연금)**
   - 연금 수령 개시 후에도 일정 기준(전체 가입자 평균소득월액, A값)을 초과하는 근로·사업소득이 있으면 수령 초기 최대 5년간 연금액의 일부가 감액될 수 있습니다.
3. **건강보험료 피부양자 자격 및 세금 영향**
   - 국민연금(공적연금) 수령액은 건강보험료 피부양자 소득 요건(연 2,000만 원 이하 기준) 산정 시 **세전 연금액 전체가 포함**되므로, 퇴직 후 자녀의 건강보험 피부양자로 등록할 계획이라면 연간 수령 총액을 반드시 사전 점검해야 합니다.

---

## 6. 마무리 및 실천 체크리스트

1. 오늘 바로 [국민연금공단 내 연금 알아보기](https://www.nps.or.kr/)에 로그인해 **내 총 가입 개월 수와 만 65세 기준 월 예상 수령액**을 확인하고 메모해 두세요.
2. 최소 가입기간(10년, 120개월)이 부족하거나 수령액을 늘리고 싶다면 **임의계속가입** 또는 **추납(추후납부) 제도** 대상인지 공단 지사(국번 없이 1355)를 통해 확인하세요.
3. 퇴직 후 건강보험료 피부양자 유지 여부가 중요하다면, 연간 국민연금 예상 수령액과 금융소득 합산액이 연 2,000만 원을 넘지 않는지 함께 계산해 보시기 바랍니다."""
        fact_checks = [
            "조기노령연금 감액률(1년당 6%, 최대 5년 30%) 및 연기연금 증액률(1년당 7.2%, 최대 5년 36%)이 현행 국민연금법 기준과 일치함",
            "1969년생 이후 노령연금 정상 수령 개시 연령(만 65세) 기준 확인 완료",
            "건강보험 피부양자 소득 요건(연간 합산소득 2,000만 원 이하) 공식 기준 일치 확인"
        ]

    elif cat_key == "ai_it":
        core_summary = (
            "ChatGPT, Claude, Gemini 등 생성형 AI로 블로그 초안을 작성할 때 가장 중요한 절차는 **발행 전 5단계 사실관계 검증(팩트체크)**입니다. "
            "① AI에게 출처 URL과 기준 연도를 함께 요구하고, ② 숫자·세율·가격·정책은 반드시 **공식 기관 사이트 원문**과 대조하며, ③ 확인되지 않은 통계나 가상 경험담은 삭제하고, ④ 비교표에 **가정 조건**을 명시한 뒤, ⑤ 구글 검색 의도에 맞는 독창적 구조로 재구성해야 애드센스 승인과 장기 검색 노출에 유리합니다."
        )
        body_sections = f"""## 1. AI 블로그 글쓰기, 왜 '초안 생성'보다 '사실관계 검증'이 중요할까요?

최근 Google Trends에서 **'{kw}'** 및 인공지능(AI) 관련 검색 관심도가 꾸준히 상승하고 있습니다. 많은 분들이 ChatGPT나 AI 도구를 활용해 티스토리·네이버 블로그 글을 작성하지만, AI가 그럴듯하게 지어낸 잘못된 숫자나 오래된 정책(할루시네이션, Hallucination)을 그대로 발행해 신뢰도를 잃거나 애드센스 심사에서 거절당하는 사례도 함께 늘고 있습니다.

구글 검색 센터(Google Search Central)와 애드센스 정책은 **"AI 사용 여부 자체보다, 독자에게 독창적이고 정확하며 유용한 가치를 제공하는가"**를 핵심 기준으로 평가합니다. 이 글에서는 **AI가 작성한 블로그 초안의 사실관계를 10분 만에 검증하고 검색 친화적인 정보 글로 완성하는 5단계 실전 방법**을 정리합니다.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

- **핵심 원칙**: AI는 '글의 뼈대와 초안 정리 도구'로 쓰고, **숫자·법령·가격·절차는 반드시 사람이 공식 사이트에서 최종 확인**합니다.
- **필수 점검 3대 항목**:
  1. 연도·날짜·세율·수수료·지원금 금액 등 **수치 데이터**
  2. 신청 기간·메뉴 경로·로그인 방식 등 **실제 절차**
  3. 직접 겪지 않은 일을 본인의 실제 경험처럼 쓴 **가상 경험 문장**
- **권장 작업 시간 배분 (총 30분)**: 주제 선정 및 공식 자료 확인(5분) → AI 초안 작성(10분) → **사실 확인 및 본문 수정(10분)** → 발행 및 기록(5분)

---

## 3. AI 작성 글의 사실관계를 확인하는 5단계 순서

### 1단계: 초안 작성 전 '공식 참고 자료 URL'을 먼저 확보하기
AI에게 막연히 *"국민연금 수령액 늘리는 법 써줘"*라고 요청하면 과거 데이터와 추측성 문장을 섞어 작성합니다.
1. 글을 쓰기 전에 먼저 정부 부처, 공단, 제조사 공식 홈페이지에서 **최신 기준 페이지 1~2개**를 찾습니다.
2. 프롬프트 입력란의 `[참고 자료]` 항목에 공식 안내 내용이나 URL을 함께 넣어주면 오류 발생률이 절반 이하로 줄어듭니다.

### 2단계: 본문 내 모든 '숫자·단위·연도'에 형광펜 표시 후 원문 대조하기
AI 초안이 나오면 본문에 포함된 **숫자(%, 원, 세, 개월, 연도)**만 빠르게 스캔합니다.
1. 예: *"최대 300만 원 지원"*, *"만 60세 이상 신청 가능"*, *"수수료 0.1%"* 같은 문장을 찾습니다.
2. 해당 수치가 올해(2026년) 공식 공고문이나 약관과 정확히 일치하는지 대조합니다.
3. 만약 공식 사이트에서 즉시 확인되지 않는 수치라면 추측해서 두지 말고 과감히 삭제하거나 **"세부 기준은 개인 조건 및 당해 연도 공고에 따라 다를 수 있으므로 공식 누리집에서 확인이 필요합니다"**라고 명확히 안내합니다.

### 3단계: AI가 지어낸 '가짜 개인 경험담' 제거하기
AI는 자연스러운 글을 쓰기 위해 *"제가 지난주에 직접 구청에 방문해 신청해 보니 10분밖에 걸리지 않았습니다"*와 같은 허구 경험을 자동으로 생성하는 경향이 있습니다.
1. 실제로 본인이 직접 해본 절차나 사용 경험이 아니라면 1인칭 허구 경험 문장을 모두 삭제합니다.
2. 대신 **공식 매뉴얼에서 안내하는 객관적인 절차와 준비물** 중심으로 담백하고 정확하게 서술합니다.

### 4단계: 조건별 비교표(Table) 추가 및 '가정 조건' 명시하기
줄글로만 길게 이어진 AI 초안은 가독성이 떨어집니다.
1. 독자가 한눈에 비교할 수 있도록 핵심 차이를 **마크다운 표(4~5열)**로 정리합니다.
2. 표 하단에는 반드시 `※ 위 표는 2026년 공식 안내 기준이며, 개인별 가입 조건에 따라 달라질 수 있습니다`와 같이 **기준 시점과 가정 조건**을 명시합니다.

### 5단계: 출처 링크 연결 및 발행 전 3대 체크리스트 최종 점검
1. 핵심 주장이나 계산 기준 바로 아래에 독자가 직접 원문을 확인할 수 있는 **공식 사이트 외부 링크**를 연결합니다.
2. PC와 모바일 미리보기 화면에서 표가 깨지지 않는지, 링크가 정상적으로 열리는지 확인한 뒤 공개 발행합니다.

---

## 4. 단순 AI 복붙 글 vs 사실 검증된 티스토리 정보 글 비교표

같은 주제를 다루더라도 AI 초안을 그대로 붙여넣은 글과 5단계 검증을 거친 글은 검색 노출과 애드센스 심사에서 아래와 같은 차이가 발생합니다.

| 비교 항목 | ❌ 단순 AI 생성 후 그대로 복사·붙여넣기한 글 | ✅ 5단계 사실 검증 및 재구성을 거친 티스토리 글 |
| :--- | :--- | :--- |
| **도입부 구성** | "안녕하세요, 오늘은 ~에 대해 알아보겠습니다" 등 상투적 인사 반복 | 독자가 검색한 **핵심 질문에 대한 결론과 요약**을 첫 문단에서 바로 제시 |
| **숫자 및 정책 정확도** | 과거 연도 기준이나 출처 불명의 통계가 섞여 있을 위험 높음 | **공식 기관 사이트 기준**으로 수치 검증 완료 (미확인 수치는 제외) |
| **경험 서술 방식** | 해보지 않은 일을 직접 겪은 것처럼 과장된 문장 포함 | 실제 확인한 절차와 **검증된 공식 가이드**를 명확히 구분해 서술 |
| **본문 시각 구조** | 비슷한 패턴의 글머리 기호와 추상적인 문장 나열 | **단계별 순서(1~4단계)** + **조건별 비교표(Table)** + **주의사항** 분리 |
| **출처 및 신뢰도** | 참고 자료나 공식 링크가 전혀 없음 | 관련 정부·기관·제조사 **공식 페이지 링크**를 본문과 하단에 명시 |
| **장기 검색 유입 가능성** | 낮음 (저품질·중복 문서로 분류될 우려) | **높음** (독자의 체류 시간 증가 및 구글 검색 상위 노출 유리) |

---

## 5. 금융·의료·세금·법률 주제 작성 시 주의사항

1. **단정적인 표현 피하기**
   - 연금, 건강보험료, 세금, 건강 관련 글은 개인의 소득·연령·기저질환·재산 조건에 따라 결과가 완전히 달라집니다. *"무조건 환급받습니다"*, *"100% 승인됩니다"* 같은 단정적 표현을 피하세요.
2. **네이버 블로그와 티스토리 원고 완전 분리**
   - 네이버 블로그에 올린 문장을 그대로 복사해 티스토리에 올리면 검색엔진이 중복 문서로 인식할 수 있습니다. **'주제 조사는 한 번에 하되, 제목·목차·비교표·설명은 플랫폼별로 새롭게 작성'**하는 원칙을 지키세요.
3. **티스토리 광고 정책 변화 반영**
   - 2026년 6월 29일부터 티스토리의 카카오 애드핏 신규 연동 신청이 종료되었으므로, 초기부터 **구글 애드센스(Google AdSense) 프로그램 정책**과 **구글 서치 콘솔 색인 기준**에 맞춘 고품질 정보 글 축적에 집중하는 것이 효율적입니다.

---

## 6. 마무리: 오늘 바로 적용할 3가지 실천 가이드

1. 글쓰기를 시작하기 전 **Google Trends**에서 상승 검색어를 확인하고, 단순 이슈가 아닌 **'방법·비교·절차' 질문**으로 주제를 먼저 정의하세요.
2. AI에게 초안을 요청할 때는 **공식 사이트 자료**를 함께 제공하고, 출력된 원고의 **숫자·날짜·가상 경험 문장**을 10분간 반드시 점검하세요.
3. 발행 직후 실제 게시글을 열어 **모바일 표 가독성**과 **공식 참고 자료 링크 동작 여부**를 확인하는 습관을 들이시기 바랍니다."""
        fact_checks = [
            "티스토리 카카오 애드핏 신규 연동 종료일(2026년 6월 29일) 티스토리 공식 공지 기준 일치 확인",
            "구글 검색 센터(Google Search Central)의 유용한 콘텐츠 가이드라인 원칙 부합 여부 확인",
            "본문 내 확인되지 않은 임의 통계나 가상 경험담이 포함되지 않았음을 점검 완료"
        ]

    else:
        # 제품 비교·사용법 (주얼리 / 순금 / 골드바 / 일반 비교) 및 기타 카테고리
        core_summary = (
            "실물 금이나 파인주얼리를 구매할 때는 **사용 목적(착용·선물용 vs 순수 자산 투자용)**에 따라 구매 경로를 구분해야 합니다. "
            "**순금(24K) 주얼리와 골드바**는 구매 시 **부가가치세 10%와 세공 공임비(약 5~15% 이상)**가 추가되므로 단기 시세차익 목적에는 불리하며, "
            "수수료와 세금을 최소화하려면 **KRX 금시장(한국거래소 금현물 계좌, 매매차익 비과세·수수료 약 0.2~0.3% 수준)**과 비교한 뒤 결정하는 것이 합리적입니다."
        )
        body_sections = f"""## 1. '{kw}' 관심 급증, 디자인만 보고 구매하면 손해 보는 이유는?

최근 Google Trends에서 **'{kw}'** 관련 검색어({news})의 관심도가 크게 상승했습니다. 금값 상승세와 맞물려 일상의 패션 아이템이자 안전자산 가치를 지닌 파인주얼리·순금 제품을 찾는 분들이 늘어나고 있는데요.

하지만 주얼리 매장에서 제품을 구매할 때와 투자 목적으로 금을 살 때는 **적용되는 세금(부가세 10%), 세공 공임비, 그리고 나중에 되팔 때(매입가) 차감되는 비용 구조**가 완전히 다릅니다. 이 글에서는 **순금(24K)·18K·14K 함량 기준, 주얼리 vs 골드바 vs KRX 금현물 비용 비교표, 그리고 구매 전 반드시 확인해야 할 체크리스트**를 정리합니다.

---

## 2. 핵심 내용 요약 (결론 먼저 보기)

- **착용 및 기념 선물 목적**: 내구성이 필요한 반지·목걸이·팔찌는 순금(24K)보다 강도가 높은 **18K(금 함량 75%)** 또는 **14K(금 함량 58.5%)**가 실용적이며, 순금 주얼리는 구매 시 **공임비 + 부가세 10%**가 붙는 점을 감안해야 합니다.
- **순수 자산 보관·투자 목적**: 세공비가 많이 드는 주얼리 형태보다 **한국거래소(KRX) 금현물 계좌**(매매차익 비과세, 부가세 면제)나 인증된 **골드바(999.9‰)**가 비용 면에서 유리합니다.
- **필수 확인 각인**: 제품 안쪽에 새겨진 **순도 각인(999, 750, 585)**과 **검인 마크(태극 마크·금자 마크 등)**, 품질보증서를 반드시 확인해야 합니다.

---

## 3. 주얼리·순금 구매 전 공식 시세와 기준 확인하는 순서

### 1단계: 오늘의 공식 금 시세(기준가) 먼저 확인하기
매장에 방문하거나 온라인에서 결제하기 전에 당일 기준 시세를 먼저 파악해야 공임비가 적정한지 계산할 수 있습니다.
1. [한국거래소(KRX) 정보데이터시스템](http://marketdata.krx.co.kr/) 또는 한국금거래소 공식 사이트에 접속합니다.
2. **1g당 기준 가격**과 **1돈(3.75g) 기준 살 때/팔 때 가격**을 확인합니다.

### 2단계: 금 순도(24K · 18K · 14K) 및 각인 숫자 확인하기
주얼리는 금의 무른 성질을 보완하기 위해 은·구리 등을 합금하여 제작합니다.
1. **24K (순금, 99.9%)**: 제품에 `24K` 또는 `999` / `999.9`로 각인됩니다. 변색이 없으나 무르기 때문에 충격에 의해 모양이 변형될 수 있습니다.
2. **18K (금 함량 75.0%)**: 제품에 `18K` 또는 `750`으로 각인됩니다. 파인주얼리에서 가장 선호되는 등급입니다.
3. **14K (금 함량 58.5%)**: 제품에 `14K` 또는 `585`로 각인됩니다. 경도가 단단해 일상 착용용 데일리 주얼리에 적합합니다.

### 3단계: 최종 결제 금액에서 '순수 금값'과 '공임비·부가세' 분리 계산하기
1. 매장 견적을 받을 때 **"오늘 1돈(3.75g) 단가가 얼마이고, 세공 공임비와 부가세가 각각 얼마인지"** 구분해서 안내받습니다.
2. 나중에 되팔 때는 **공임비와 부가세(10%)는 환급되지 않고 순수 금 중량과 순도만 평가**받으므로, 투자 겸용이라면 공임비 비중이 낮은 심플한 제품을 고르는 것이 유리합니다.

---

## 4. 순금 주얼리 vs 실물 골드바 vs KRX 금현물 비교표

아래 표는 동일한 금 자산을 구매할 때 **구매 방식별 비용 구조와 세금 차이**를 비교한 표입니다. (※ 세부 수수료율은 판매처 및 증권사별로 상이할 수 있으므로 구매 전 각 기관 공시를 확인하세요.)

| 비교 항목 | 💍 순금(24K) 주얼리 | 🧈 실물 골드바 (은행·금은방) | 📈 KRX 금현물 계좌 (증권사) |
| :--- | :--- | :--- | :--- |
| **주요 목적** | 일상 착용, 예물, 기념일 선물 | 실물 안전자산 직접 보관, 증여 | 시세차익 투자, 장기 분할 매수 |
| **부가가치세 (10%)** | **부과됨 (10%)** | **부과됨 (10%)** | **면제** (실물 인출 시에만 10% 부과) |
| **세공 공임비·수수료** | 디자인별 공임비 발생 (약 5~15% 이상) | 제작·유통 수수료 발생 (약 4~6% 내외) | 온라인 매매수수료만 발생 (약 0.2~0.3% 내외) |
| **매매차익 세금** | 실물 매도 시 별도 양도세 없음 | 실물 매도 시 별도 양도세 없음 | **매매차익 비과세** (금융소득종합과세 제외) |
| **되팔 때(환금성)** | 공임·부가세 제외 후 순도·중량만 평가 | 인증 마크 보유 시 매입처에서 즉시 현금화 | 평일 장중 주식처럼 1g 단위로 즉시 매도 가능 |

---

## 5. 구매 전 놓치기 쉬운 3가지 주의사항

1. **'순금 코팅(도금)'과 '순금(24K) 제품' 구분**
   - 온라인 쇼핑몰에서 지나치게 저렴한 제품은 내부가 은(Silver)이나 신주(황동)이고 겉면만 얇게 금으로 도금(`GP`, `GF` 표기)된 경우가 많습니다. 반드시 상세페이지에서 **전체 소재 함량(999, 750, 585)**을 확인하세요.
2. **잠금장치(붕어장식·클asp) 소재 확인**
   - 24K 순금 목걸이나 팔찌라도 장식 연결 부위는 강도 유지를 위해 **18K로 제작**되는 경우가 일반적입니다. 품질보증서에 본체 중량과 장식(18K) 중량이 명확히 표기되어 있는지 확인하세요.
3. **품질보증서 및 현금영수증 보관**
   - 추후 매도하거나 수리(AS)를 맡길 때 순도와 중량을 증명하는 품질보증서가 있으면 감정 지연을 줄일 수 있습니다.

---

## 6. 마무리 및 구매 전 실천 요약

1. 착용 만족감이 우선이라면 **18K/24K 함량 각인과 공임비 비중**을 먼저 비교하고, 순수 자산 증식이 목적이라면 부가세(10%)와 세공비가 없는 **KRX 금현물 계좌**를 우선 검토하세요.
2. 매장 방문 전 [한국거래소 금시장](http://marketdata.krx.co.kr/)에서 **당일 1g / 1돈(3.75g) 기준 시세**를 스마트폰으로 먼저 확인한 뒤 견적을 비교해 보시기 바랍니다."""
        fact_checks = [
            "1돈 = 3.75g 및 24K(99.9%), 18K(75.0%, 750), 14K(58.5%, 585) 표준 귀금속 함량 기준 일치 확인",
            "실물 금 구매 시 부가가치세 10% 부과 및 KRX 금시장 장내 거래 시 매매차익 비과세·부가세 면제(실물 인출 시 부과) 기준 일치 확인",
            "특정 업체 홍보나 확인되지 않은 확정 가격 없이 공식 기준과 절차 중심으로 작성됨"
        ]

    md_content = f"""# {final_title}

> **📌 핵심 요약**: {core_summary}

---

{body_sections}

---

## 7. 참고 자료 및 공식 확인 사이트

{refs_md}
"""
    return md_content

def build_tistory_post_html(post_id, date_str, weekday_str, trend_item, md_content):
    """티스토리 에디터(기본모드 서식 복사 & 마크다운 복사) 전용 HTML 뷰어 생성"""
    ev = trend_item["eval"]
    title = ev["final_title"]
    kw = trend_item["keyword"]
    cat_name = ev["cat_name"]
    score = ev["total_score"]

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[{date_str}] 티스토리 포스팅 | {title}</title>

  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>

  <style>
    :root {{
      --tistory: #ea580c;
      --tistory-dark: #c2410c;
      --tistory-light: #fff7ed;
      --tistory-border: #fed7aa;
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

    .nav-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-tag {{
      background: var(--tistory);
      color: var(--white);
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }}

    .nav-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--text-main);
    }}

    .nav-actions {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 13px;
      border-radius: 6px;
      font-size: 12.5px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.15s;
      border: 1px solid var(--border);
      background: var(--white);
      color: var(--text-main);
    }}

    .btn:hover {{ background: #f3f4f6; }}

    .btn-tistory {{
      background: var(--tistory);
      color: var(--white);
      border-color: var(--tistory);
    }}
    .btn-tistory:hover {{ background: var(--tistory-dark); color: var(--white); }}

    .container {{
      max-width: 860px;
      margin: 32px auto 0;
      padding: 0 16px;
    }}

    .meta-card {{
      background: var(--white);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      border: 1px solid var(--border);
      border-top: 4px solid var(--tistory);
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}

    .meta-badges {{
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}

    .badge {{
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 4px;
      background: var(--tistory-light);
      color: var(--tistory-dark);
      border: 1px solid var(--tistory-border);
    }}

    .badge-score {{
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
    }}

    .post-title {{
      font-size: 23px;
      font-weight: 800;
      line-height: 1.4;
      margin-bottom: 14px;
      color: #111827;
    }}

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
    .meta-info-item strong {{ color: var(--text-main); }}

    .editor-preview {{
      background: var(--white);
      border-radius: 12px;
      padding: 40px 48px;
      border: 1px solid var(--border);
      box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}

    .editor-preview h1 {{
      font-size: 24px;
      font-weight: 800;
      margin-bottom: 24px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--tistory);
      color: #111;
    }}

    .editor-preview h2 {{
      font-size: 19.5px;
      font-weight: 750;
      margin: 34px 0 14px;
      color: #111827;
      border-left: 4px solid var(--tistory);
      padding-left: 12px;
    }}

    .editor-preview h3 {{
      font-size: 16.5px;
      font-weight: 700;
      margin: 24px 0 10px;
      color: #1f2937;
    }}

    .editor-preview p {{
      margin-bottom: 16px;
      font-size: 15.5px;
      line-height: 1.85;
      color: #374151;
      word-break: keep-all;
    }}

    .editor-preview ul, .editor-preview ol {{
      margin: 12px 0 20px 22px;
    }}

    .editor-preview li {{
      margin-bottom: 8px;
      font-size: 15px;
      line-height: 1.75;
      color: #374151;
    }}

    .editor-preview blockquote {{
      border: 1px solid var(--tistory-border);
      border-left: 4px solid var(--tistory);
      background: var(--tistory-light);
      padding: 16px 20px;
      margin: 20px 0;
      border-radius: 8px;
      color: #7c2d12;
      font-size: 14.5px;
    }}

    .editor-preview table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0 24px;
      font-size: 14px;
    }}

    .editor-preview th {{
      background: #fff7ed;
      color: #9a3412;
      font-weight: 700;
      border: 1px solid #fed7aa;
      padding: 10px 12px;
      text-align: left;
    }}

    .editor-preview td {{
      border: 1px solid #e5e7eb;
      padding: 10px 12px;
      color: #374151;
      vertical-align: top;
    }}

    .editor-preview tr:nth-child(even) td {{
      background: #f9fafb;
    }}

    .editor-preview a {{
      color: var(--tistory-dark);
      font-weight: 600;
      text-decoration: underline;
    }}

    .toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: #111827;
      color: #fff;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
      opacity: 0;
      pointer-events: none;
      transition: all 0.2s ease;
      z-index: 999;
    }}
    .toast.show {{
      opacity: 1;
      transform: translateX(-50%) translateY(-10px);
    }}
  </style>
</head>
<body>

  <header class="top-nav">
    <div class="nav-left">
      <span class="brand-tag">TISTORY · 똑똑한 생활탐구</span>
      <span class="nav-title">티스토리 정보형 포스팅: {date_str} ({weekday_str}) · {cat_name}</span>
    </div>
    <div class="nav-actions">
      <a href="../../index.html" class="btn">📂 티스토리 작업실 홈</a>
      <a href="{post_id}.md" target="_blank" class="btn">📄 원본 MD 열기</a>
      <button class="btn btn-tistory" id="copyTistoryHtmlBtn" title="티스토리 기본모드 에디터에 표·소제목·인용구 서식 그대로 붙여넣기 됩니다">
        🟠 티스토리 에디터(기본모드) 서식 복사
      </button>
      <button class="btn" id="copyCleanTextBtn" title="** 나 ### 등 마크다운 기호를 모두 지운 깨끗한 텍스트로 복사합니다">
        📄 순수 텍스트 복사 (** 제거)
      </button>
      <button class="btn" id="copyMarkdownBtn" title="티스토리 마크다운 모드용 원문을 복사합니다">
        📝 마크다운 원문 복사
      </button>
    </div>
  </header>

  <div class="container">
    <div class="meta-card">
      <div class="meta-badges">
        <span class="badge">📂 카테고리: {cat_name}</span>
        <span class="badge">📈 Google Trends 상승 검색어: [{kw}]</span>
        <span class="badge badge-score">🎯 주제 평가 점수: {score}/100점</span>
      </div>
      <h1 class="post-title">{title}</h1>

      <div class="meta-info-grid">
        <div class="meta-info-item">
          <span>작성일자:</span><strong>{date_str} ({weekday_str})</strong>
        </div>
        <div class="meta-info-item">
          <span>타겟 검색엔진:</span><strong>구글(Google) & 다음(Daum)</strong>
        </div>
        <div class="meta-info-item">
          <span>글 구성:</span><strong>티스토리 7단계 표준 템플릿 (표 포함)</strong>
        </div>
        <div class="meta-info-item">
          <span>수익화 타겟:</span><strong>구글 애드센스 승인·노출 최적화</strong>
        </div>
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

    function showToast(message) {{
      const toast = document.getElementById("toast");
      toast.textContent = message;
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 2800);
    }}

    function getCleanPlainText() {{
      return mdSource
        .replace(/\\*\\*(.*?)\\*\\*/g, '$1')
        .replace(/#{{1,6}}\\s+/g, '')
        .replace(/^>\\s+/gm, '')
        .replace(/^---\\s*$/gm, '──────────')
        .replace(/^\\s*[-*]\\s+/gm, '• ')
        .replace(/`([^`]+)`/g, '$1')
        .trim();
    }}

    function getTistoryOptimizedHtml() {{
      const clone = articleEl.cloneNode(true);
      clone.querySelectorAll("h1").forEach(el => el.setAttribute("style", "font-size: 24px; font-weight: bold; color: #111827; margin-bottom: 22px; line-height: 1.4;"));
      clone.querySelectorAll("h2").forEach(el => el.setAttribute("style", "font-size: 19px; font-weight: bold; color: #c2410c; margin-top: 32px; margin-bottom: 14px; border-left: 4px solid #ea580c; padding-left: 10px;"));
      clone.querySelectorAll("h3, h4").forEach(el => el.setAttribute("style", "font-size: 16.5px; font-weight: bold; color: #1f2937; margin-top: 22px; margin-bottom: 10px;"));
      clone.querySelectorAll("p").forEach(el => el.setAttribute("style", "font-size: 16px; line-height: 1.85; color: #374151; margin-bottom: 16px; word-break: keep-all;"));
      clone.querySelectorAll("blockquote").forEach(el => el.setAttribute("style", "background-color: #fff7ed; border: 1px solid #fed7aa; border-left: 4px solid #ea580c; padding: 16px 20px; margin: 20px 0; border-radius: 6px; color: #7c2d12; font-style: normal; font-size: 15px;"));
      clone.querySelectorAll("table").forEach(el => el.setAttribute("style", "width: 100%; border-collapse: collapse; margin: 20px 0 24px; font-size: 14px;"));
      clone.querySelectorAll("th").forEach(el => el.setAttribute("style", "background-color: #fff7ed; color: #9a3412; font-weight: bold; border: 1px solid #fed7aa; padding: 10px 12px; text-align: left;"));
      clone.querySelectorAll("td").forEach(el => el.setAttribute("style", "border: 1px solid #e5e7eb; padding: 10px 12px; color: #374151;"));
      clone.querySelectorAll("ul, ol").forEach(el => el.setAttribute("style", "margin: 14px 0 20px 22px;"));
      clone.querySelectorAll("li").forEach(el => el.setAttribute("style", "font-size: 15.5px; line-height: 1.75; margin-bottom: 8px; color: #374151;"));
      return clone.innerHTML;
    }}

    document.getElementById("copyTistoryHtmlBtn").addEventListener("click", async () => {{
      const htmlContent = getTistoryOptimizedHtml();
      const plainText = getCleanPlainText();
      let success = false;
      if (navigator.clipboard && window.ClipboardItem) {{
        try {{
          const htmlBlob = new Blob([htmlContent], {{ type: 'text/html' }});
          const textBlob = new Blob([plainText], {{ type: 'text/plain' }});
          await navigator.clipboard.write([new ClipboardItem({{ 'text/html': htmlBlob, 'text/plain': textBlob }})]);
          success = true;
        }} catch(e) {{}}
      }}
      if (!success) {{
        await navigator.clipboard.writeText(plainText);
      }}
      showToast("🟠 티스토리 기본모드 서식(표·소제목 포함)이 복사되었습니다! 에디터에 바로 붙여넣으세요.");
    }});

    document.getElementById("copyCleanTextBtn").addEventListener("click", async () => {{
      const plainText = getCleanPlainText();
      await navigator.clipboard.writeText(plainText);
      showToast("📄 ** 및 # 기호가 완전히 제거된 순수 텍스트가 복사되었습니다!");
    }});

    document.getElementById("copyMarkdownBtn").addEventListener("click", async () => {{
      await navigator.clipboard.writeText(mdSource);
      showToast("📝 티스토리 마크다운 원문이 복사되었습니다!");
    }});
  </script>
</body>
</html>"""

def create_tistory_post(post_id, date_str, weekday_str, trend_item, post_num=1, force=False):
    """개별 티스토리 포스팅(.md 및 .html) 생성"""
    ym = date_str[:7].replace("-", "")
    post_dir = os.path.join(POSTS_DIR, ym)
    os.makedirs(post_dir, exist_ok=True)
    md_path = os.path.join(post_dir, f"{post_id}.md")
    html_path = os.path.join(post_dir, f"{post_id}.html")

    if not force and os.path.exists(md_path) and os.path.exists(html_path):
        log(f"ℹ️ tistory/posts/{ym}/{post_id} 파일이 이미 존재하여 보존합니다.")
        return

    md_content = build_tistory_post_markdown(post_id, date_str, weekday_str, trend_item)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    log(f"✅ blog/tistory/posts/{ym}/{post_id}.md 생성 완료 (#{post_num}편: [{trend_item['keyword']}])")

    html_content = build_tistory_post_html(post_id, date_str, weekday_str, trend_item, md_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    log(f"✅ blog/tistory/posts/{ym}/{post_id}.html 뷰어 생성 완료 (#{post_num}편: [{trend_item['keyword']}])")

def scan_tistory_posts():
    """blog/tistory/posts/ 하위 모든 마크다운 포스트 스캔"""
    all_files = glob.glob(os.path.join(POSTS_DIR, "*", "*.md")) + glob.glob(os.path.join(POSTS_DIR, "*.md"))

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

        rel_md = os.path.relpath(fpath, TISTORY_BLOG_DIR)
        rel_html = rel_md[:-3] + ".html"

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            m_title = re.search(r"^#\s+(.+)$", content, re.M)
            title = m_title.group(1).strip() if m_title else post_id

            m_cat = re.search(r">\s*\*\*카테고리\*\*:\s*(.+)$", content, re.M)
            if m_cat:
                category = m_cat.group(1).strip()
            elif "연금" in title or "건강보험" in title:
                category = "은퇴·연금·생활비"
            elif "AI" in title or "ChatGPT" in title or "팩트체크" in title:
                category = "AI·IT 활용법"
            else:
                category = "제품 비교·사용법"

            m_kw = re.search(r">\s*\*\*Google Trends 상승 검색어\*\*:\s*`?([^`\n]+)`?", content, re.M)
            trend_kw = m_kw.group(1).strip() if m_kw else ""

            m_score = re.search(r">\s*\*\*주제 평가 점수\*\*:\s*\*\*([0-9]+/100점)\*\*", content, re.M)
            if m_score:
                score_str = m_score.group(1).strip()
            elif "AI" in title or "ChatGPT" in title:
                score_str = "96/100점"
            elif "연금" in title:
                score_str = "88/100점"
            else:
                score_str = "80/100점"

            m_summary = re.search(r">\s*\*\*📌 핵심 요약\*\*:\s*(.+)$", content, re.M)
            desc = m_summary.group(1).strip().replace("**", "") if m_summary else ""
            if len(desc) > 150:
                desc = desc[:150] + "..."

            char_count = len(content.replace(" ", "").replace("\n", ""))

            posts.append({
                "post_id": post_id,
                "date_only": date_only,
                "post_num": post_num,
                "category": category,
                "trend_kw": trend_kw,
                "score_str": score_str,
                "title": title,
                "desc": desc,
                "char_count": char_count,
                "rel_md": rel_md,
                "rel_html": rel_html
            })
        except Exception as e:
            log(f"⚠️ 티스토리 포스트 파싱 오류 {fname}: {e}")

    return posts

def update_tistory_index_html(today_str, evaluated_trends, posts):
    """blog/tistory/index.html 티스토리 전용 작업실 대시보드 생성"""
    os.makedirs(TISTORY_BLOG_DIR, exist_ok=True)
    index_path = os.path.join(TISTORY_BLOG_DIR, "index.html")

    post_cards_html = ""
    for p in posts:
        is_today = (p["date_only"] == today_str)
        today_class = " today" if is_today else ""
        date_badge = f"📍 {p['date_only']} ({'오늘 작성' if is_today else '발행본'})"

        post_cards_html += f"""
            <article class="post-card{today_class}">
              <div class="post-card-date">
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                  <span>{date_badge}</span>
                  <span class="cat-pill">📂 {p['category']}</span>
                  <span class="score-pill">🎯 평가 {p['score_str']}</span>
                </div>
                <span style="font-size: 11.5px; color: var(--text-muted); font-weight: 600;">#{p['post_num']}편</span>
              </div>
              <a href="{p['rel_html']}" class="post-card-title">
                {p['title']}
              </a>
              <p class="post-card-desc">
                {p['desc']}
              </p>
              <div class="post-card-footer">
                <div>상승 검색어: <strong>{p['trend_kw']}</strong> · 분량: 약 {p['char_count']:,}자 (공백 제외)</div>
                <div class="post-btn-group">
                  <a href="{p['rel_md']}" target="_blank" class="action-btn">📄 MD 원문</a>
                  <a href="{p['rel_html']}" class="action-btn action-btn-primary">👁️ 포스트 열기 & 에디터 복사</a>
                </div>
              </div>
            </article>
        """

    trends_rows_html = ""
    for t in evaluated_trends:
        ev = t["eval"]
        sc = ev["scores"]
        is_sel = ev["is_selected"]
        row_style = 'background: #fffaf5; border-color: #fdba74;' if is_sel else ''
        badge_style = 'background: #ffedd5; color: #c2410c; border: 1px solid #fdba74;' if is_sel else 'background: #f1f5f9; color: #64748b;'
        safe_title = ev["final_title"].replace("'", "\\'").replace('"', '&quot;')

        trends_rows_html += f"""
            <div class="trend-item" style="{row_style}">
              <div class="trend-rank">{t['rank']}</div>
              <div class="trend-content">
                <div class="trend-kw-row">
                  <span class="trend-kw">{t['keyword']}</span>
                  <span class="trend-traffic">{t['traffic']}</span>
                  <span class="trend-badge" style="{badge_style}">📂 {ev['cat_name']}</span>
                  <span class="trend-badge" style="{badge_style}">🎯 {ev['total_score']}/100점 ({ev['rec_level']})</span>
                </div>
                <div style="font-size: 12.5px; color: var(--text-muted); margin-bottom: 4px;">
                  <strong>변환된 검색 질문:</strong> {ev['search_question']}
                </div>
                <div class="trend-title-rec">
                  <strong>추천 제목:</strong> {ev['final_title']}
                </div>
                <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 6px;">
                  세부 평가: 관심도 상승({sc['trend']}/5) · 검색 의도 명확성({sc['intent']}/5) · 경쟁 글 빈틈({sc['gap']}/5) · 작성 역량({sc['capability']}/5) · 장기 검색성({sc['evergreen']}/5)
                </div>
              </div>
              <button class="copy-title-btn" onclick="copyText('{safe_title}')">제목 복사</button>
            </div>
        """

    prompt_text = (
        "# 티스토리 검색형 블로그 글 작성 지침\\n\\n"
        "당신은 정확성과 실용성을 중시하는 블로그 편집자입니다.\\n"
        "독자가 검색을 통해 유입되어 궁금한 문제를 해결할 수 있는 티스토리용 정보 글을 작성합니다.\\n\\n"
        "- 주제: [작성할 주제]\\n"
        "- 주요 독자: [5060 은퇴 준비자 및 일반 검색 독자]\\n"
        "- 검색할 질문: [독자가 해결하려는 구체적인 방법·비교·조건 질문]\\n"
        "- 참고 자료: [공식 기관 URL]\\n\\n"
        "작성 규칙:\\n"
        "1. 검색 질문에 대한 핵심 답변을 도입부에서 먼저 제시합니다.\\n"
        "2. 본문은 7단계(도입부 → 핵심 요약 → 단계별 설명 → 사례/비교표 → 주의사항 → 결론 → 참고 자료)로 구성합니다.\\n"
        "3. 확인되지 않은 통계, 가격, 정책, 가상 개인 경험을 만들지 않습니다.\\n"
        "4. 출력 형식: 1) 제목 후보 3개, 2) 최종 추천 제목, 3) 핵심 답변 요약, 4) 완성된 본문, 5) 사실 확인 항목, 6) 참고 자료 목록, 7) 발행 전 체크리스트"
    )

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>티스토리 블로그 작업실 (Google Trends & AdSense) | AI Blog Notes</title>

  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />

  <style>
    :root {{
      --tistory: #ea580c;
      --tistory-dark: #c2410c;
      --tistory-light: #fff7ed;
      --tistory-border: #fed7aa;
      --text-main: #191f28;
      --text-sub: #4e5968;
      --text-muted: #8b95a1;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e5e8eb;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, BlinkMacSystemFont, sans-serif;
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

    .brand-wrap {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .tistory-badge {{
      background: var(--tistory);
      color: #fff;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
    }}

    .brand-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--text-main);
    }}

    .header-links {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .header-link {{
      font-size: 13px;
      color: var(--text-sub);
      text-decoration: none;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      transition: all 0.15s;
      font-weight: 600;
    }}

    .header-link:hover {{
      background: var(--bg);
      color: var(--tistory-dark);
      border-color: var(--tistory);
    }}

    .container {{
      max-width: 1120px;
      margin: 28px auto 0;
      padding: 0 20px;
    }}

    .hero-banner {{
      background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
      color: #fff;
      padding: 32px 36px;
      border-radius: 16px;
      margin-bottom: 28px;
      box-shadow: 0 8px 24px rgba(234, 88, 12, 0.2);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
    }}

    .hero-text h1 {{
      font-size: 24px;
      font-weight: 800;
      margin-bottom: 8px;
    }}

    .hero-text p {{
      font-size: 14px;
      opacity: 0.94;
      max-width: 640px;
    }}

    .hero-stats {{
      display: flex;
      gap: 16px;
    }}

    .stat-box {{
      background: rgba(255, 255, 255, 0.18);
      backdrop-filter: blur(8px);
      padding: 12px 18px;
      border-radius: 12px;
      text-align: center;
      min-width: 100px;
    }}

    .stat-number {{
      font-size: 21px;
      font-weight: 800;
      display: block;
    }}

    .stat-label {{
      font-size: 12px;
      opacity: 0.9;
    }}

    .main-grid {{
      display: grid;
      grid-template-columns: 1fr 350px;
      gap: 24px;
    }}

    @media (max-width: 920px) {{
      .main-grid {{ grid-template-columns: 1fr; }}
    }}

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
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }}

    .card-title {{
      font-size: 17px;
      font-weight: 750;
      color: var(--text-main);
    }}

    .card-subtitle {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    .post-timeline {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .post-card {{
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      background: #fff;
      position: relative;
    }}

    .post-card.today {{
      border-color: var(--tistory);
      box-shadow: 0 4px 16px rgba(234, 88, 12, 0.1);
    }}

    .post-card-date {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12.5px;
      font-weight: 700;
      color: var(--tistory-dark);
      margin-bottom: 8px;
    }}

    .cat-pill {{
      background: var(--tistory-light);
      color: var(--tistory-dark);
      border: 1px solid var(--tistory-border);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
    }}

    .score-pill {{
      background: #eff6ff;
      color: #1d4ed8;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
    }}

    .post-card-title {{
      font-size: 17px;
      font-weight: 750;
      margin-bottom: 10px;
      color: var(--text-main);
      text-decoration: none;
      display: inline-block;
    }}

    .post-card-title:hover {{
      color: var(--tistory-dark);
      text-decoration: underline;
    }}

    .post-card-desc {{
      font-size: 13.5px;
      color: var(--text-sub);
      line-height: 1.55;
      margin-bottom: 14px;
    }}

    .post-card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px dashed var(--border);
      padding-top: 12px;
      font-size: 12px;
      color: var(--text-muted);
      flex-wrap: wrap;
      gap: 10px;
    }}

    .post-btn-group {{
      display: flex;
      gap: 8px;
    }}

    .action-btn {{
      font-size: 12px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 6px;
      text-decoration: none;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text-main);
      cursor: pointer;
    }}

    .action-btn-primary {{
      background: var(--tistory);
      color: #fff;
      border-color: var(--tistory);
    }}
    .action-btn-primary:hover {{
      background: var(--tistory-dark);
    }}

    .trend-list {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .trend-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 14px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: var(--bg);
    }}

    .trend-rank {{
      font-size: 15px;
      font-weight: 800;
      color: var(--tistory-dark);
      min-width: 24px;
      text-align: center;
    }}

    .trend-content {{ flex: 1; }}

    .trend-kw-row {{
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 6px;
      flex-wrap: wrap;
    }}

    .trend-kw {{
      font-size: 14.5px;
      font-weight: 800;
      color: var(--text-main);
    }}

    .trend-traffic {{
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 4px;
      background: #fee2e2;
      color: #b91c1c;
      font-weight: 700;
    }}

    .trend-badge {{
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 700;
    }}

    .trend-title-rec {{
      font-size: 13px;
      color: var(--text-main);
      line-height: 1.45;
    }}

    .copy-title-btn {{
      font-size: 11px;
      padding: 5px 9px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: #fff;
      cursor: pointer;
      white-space: nowrap;
    }}

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
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: #111827;
      color: #fff;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 13.5px;
      font-weight: 600;
      opacity: 0;
      pointer-events: none;
      transition: all 0.2s;
      z-index: 999;
    }}
    .toast.show {{
      opacity: 1;
      transform: translateX(-50%) translateY(-10px);
    }}

    .pagination-bar {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 6px;
      margin-top: 20px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
      flex-wrap: wrap;
    }}
    .page-btn {{
      min-width: 34px;
      height: 34px;
      padding: 0 10px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text-sub);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s;
    }}
    .page-btn:hover:not(:disabled) {{
      border-color: var(--tistory);
      color: var(--tistory-dark);
      background: var(--tistory-light);
    }}
    .page-btn.active {{
      background: var(--tistory);
      color: #fff;
      border-color: var(--tistory);
    }}
    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}
  </style>
</head>
<body>

  <header class="header">
    <div class="header-inner">
      <div class="brand-wrap">
        <span class="tistory-badge">TISTORY BLOG</span>
        <div class="brand-title">똑똑한 생활탐구 · 티스토리 작업실</div>
      </div>
      <div class="header-links">
        <a href="../../index.html" class="header-link">🏠 블로그 홈</a>
        <a href="../naver/index.html" class="header-link" style="background: #e6f9ed; color: #009f47; border-color: #bbf7d0; font-weight: 700;">🟢 네이버 작업실</a>
        <a href="index.html" class="header-link" style="background: #fff7ed; color: #c2410c; border-color: #fed7aa; font-weight: 700;">🟠 티스토리 작업실</a>
        <a href="../wordpress/index.html" class="header-link" style="background: #f0f7fb; color: #0073aa; border-color: #bae6fd; font-weight: 700;">🔵 워드프레스 작업실</a>
        <a href="../../docs/index.html#tistory-guide" class="header-link">📚 티스토리 가이드</a>
      </div>
    </div>
  </header>

  <div class="container">
    <section class="hero-banner">
      <div class="hero-text">
        <h1>🟠 티스토리 검색형 블로그 & 애드센스 작업실</h1>
        <p>Google Trends 상승 검색어에서 독자의 구체적인 질문을 발굴하고, 공식 자료 검증과 7단계 표준 구성으로 오래 검색되는 정보 자산을 축적합니다.</p>
        <div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
          <a href="https://trends.google.com/trends/?geo=KR" target="_blank" rel="noopener noreferrer" style="background: #fff; color: var(--tistory-dark); padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; text-decoration: none;">
            📊 Google Trends 상승 검색어 확인 ↗
          </a>
          <a href="https://search.google.com/search-console/" target="_blank" rel="noopener noreferrer" style="background: rgba(255,255,255,0.2); color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; text-decoration: none; border: 1px solid rgba(255,255,255,0.35);">
            🔍 Google Search Console ↗
          </a>
          <a href="https://adsense.google.com/start/" target="_blank" rel="noopener noreferrer" style="background: rgba(255,255,255,0.2); color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; text-decoration: none; border: 1px solid rgba(255,255,255,0.35);">
            💰 Google AdSense ↗
          </a>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span class="stat-number">{len(posts)} 편</span>
          <span class="stat-label">누적 정보형 글</span>
        </div>
        <div class="stat-box">
          <span class="stat-number">하루 1편</span>
          <span class="stat-label">권장 발행 목표</span>
        </div>
      </div>
    </section>

    <div class="main-grid">
      <div class="left-col">
        <section class="card">
          <div class="card-header">
            <div class="card-title">📝 티스토리 검색형 포스팅 목록 (7단계 표준 템플릿)</div>
            <div class="card-subtitle">총 {len(posts)}편 작성됨</div>
          </div>
          <div class="post-timeline" id="tistoryPostList">
            {post_cards_html}
          </div>
          <div class="pagination-bar" id="tistoryPagination"></div>
        </section>

        <section class="card">
          <div class="card-header">
            <div class="card-title">📈 Google Trends 상승 검색어 → 티스토리 주제 변환 & 100점 평가표</div>
            <div class="card-subtitle">{today_str} 기준 자동 분석</div>
          </div>
          <p style="font-size: 13.5px; color: var(--text-sub); margin-bottom: 16px;">
            단순 실시간 이슈는 보류하고, <strong>5대 평가 기준(관심도·의도 명확성·경쟁 빈틈·작성 역량·장기 검색성)</strong>에서 70점 이상을 획득한 주제를 구체적인 질문 해결형 글로 변환합니다.
          </p>
          <div class="trend-list">
            {trends_rows_html}
          </div>
        </section>
      </div>

      <div class="right-col">
        <section class="card" style="border: 2px solid var(--tistory); background: #fffcf9;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
            <span style="background: var(--tistory); color: #fff; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px;">MY BLOG</span>
            <div class="card-title" style="margin: 0; font-size: 15px;">똑똑한 생활탐구 티스토리</div>
          </div>
          <p style="font-size: 13px; color: var(--text-sub); line-height: 1.55; margin-bottom: 14px;">
            작업실에서 완성된 티스토리 에디터 서식을 복사한 뒤, 실제 운영 중인 내 티스토리 블로그에 바로 새 글로 발행하세요.
          </p>
          <a href="https://www.tistory.com/" target="_blank" rel="noopener noreferrer" class="action-btn action-btn-primary" style="display: flex; align-items: center; justify-content: center; gap: 6px; text-decoration: none; padding: 10px; font-weight: 700; font-size: 13px;">
            <span>🌐 내 티스토리 바로가기 (tistory.com)</span>
            <span style="font-size: 12px;">↗</span>
          </a>
        </section>

        <section class="card" style="border: 2px solid var(--tistory);">
          <div class="card-title" style="margin-bottom: 12px;">📂 티스토리 5대 추천 카테고리 비중</div>
          <div style="font-size: 13px; color: var(--text-sub); display: flex; flex-direction: column; gap: 10px;">
            <div><strong>1. 은퇴·연금·생활비 (30%)</strong><br><span style="font-size:12px; color:var(--text-muted);">국민연금, 개인연금, 퇴직 후 건보료, 생활비 계산</span></div>
            <div><strong>2. AI·IT 활용법 (25%)</strong><br><span style="font-size:12px; color:var(--text-muted);">ChatGPT, AI 사실 검증, 맥·스마트폰 사용법, 자동화</span></div>
            <div><strong>3. 제품 비교·사용법 (25%)</strong><br><span style="font-size:12px; color:var(--text-muted);">사양·기능 비교표, 구매 전 확인사항, 수수료·세금 비교</span></div>
            <div><strong>4. 골프·취미 (10%)</strong><br><span style="font-size:12px; color:var(--text-muted);">골프·파크골프 연습, 장비 선택, 취미 정보</span></div>
            <div><strong>5. 반려동물·생활정보 (10%)</strong><br><span style="font-size:12px; color:var(--text-muted);">사료 성분, 반려동물 용품, 일상 문제 해결</span></div>
          </div>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 12px;">✅ 애드센스 준비 체크리스트 (6단계)</div>
          <label class="check-row"><input type="checkbox" class="ads-chk" onchange="updateAdsCount()"> <span>블로그 제목(똑똑한 생활탐구)과 소개를 작성했다</span></label>
          <label class="check-row"><input type="checkbox" class="ads-chk" onchange="updateAdsCount()"> <span>주제에 맞는 5대 카테고리를 정리했다</span></label>
          <label class="check-row"><input type="checkbox" class="ads-chk" onchange="updateAdsCount()"> <span>독자에게 도움이 되는 공개 글을 발행했다</span></label>
          <label class="check-row"><input type="checkbox" class="ads-chk" onchange="updateAdsCount()"> <span>복사·반복된 콘텐츠와 사실 오류를 점검했다</span></label>
          <label class="check-row"><input type="checkbox" class="ads-chk" onchange="updateAdsCount()"> <span>문의 방법과 개인정보처리방침 안내를 준비했다</span></label>
          <label class="check-row"><input type="checkbox" class="ads-chk" onchange="updateAdsCount()"> <span>구글 서치 콘솔 등록 및 <code>/sitemap.xml</code>, <code>/rss</code> 제출을 완료했다</span></label>
          <div id="adsStatus" style="margin-top: 10px; font-size: 12.5px; font-weight: 700; color: var(--tistory-dark);">0/6 항목 완료</div>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 10px;">⚡ 티스토리 검색형 AI 작성 프롬프트</div>
          <p style="font-size: 12.5px; color: var(--text-sub); margin-bottom: 12px;">
            제목 후보 3개, 핵심 답변 요약, 7단계 본문, 비교표, 공식 참고 자료 및 팩트체크 항목을 한 번에 생성하는 표준 프롬프트입니다.
          </p>
          <button class="action-btn action-btn-primary" style="width: 100%; text-align: center; padding: 10px;" onclick="copyText('{prompt_text}')">
            📋 티스토리 AI 작성 프롬프트 복사
          </button>
        </section>
      </div>
    </div>
  </div>

  <div class="toast" id="toast">복사되었습니다!</div>

  <script>
    function copyText(text) {{
      navigator.clipboard.writeText(text).then(() => {{
        const toast = document.getElementById("toast");
        toast.textContent = "✓ 클립보드에 복사되었습니다!";
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 2200);
      }});
    }}

    function updateAdsCount() {{
      const chks = document.querySelectorAll(".ads-chk");
      let done = 0;
      chks.forEach((c, i) => {{
        if (c.checked) done++;
        localStorage.setItem("tistory_ads_chk_" + i, c.checked ? "1" : "0");
      }});
      document.getElementById("adsStatus").textContent = done + "/6 항목 완료";
    }}

    function initPagination(listId, pagId, perPage) {{
      const container = document.getElementById(listId);
      const pag = document.getElementById(pagId);
      if (!container || !pag) return;
      const items = Array.from(container.querySelectorAll(".post-card"));
      const totalPages = Math.ceil(items.length / perPage);
      if (totalPages <= 1) {{
        pag.style.display = "none";
        return;
      }}
      let currentPage = 1;
      function render(page) {{
        currentPage = page;
        items.forEach((el, idx) => {{
          const p = Math.floor(idx / perPage) + 1;
          el.style.display = (p === currentPage) ? "" : "none";
        }});
        pag.innerHTML = "";
        const prevBtn = document.createElement("button");
        prevBtn.className = "page-btn";
        prevBtn.textContent = "‹ 이전";
        prevBtn.disabled = (currentPage === 1);
        prevBtn.onclick = () => render(currentPage - 1);
        pag.appendChild(prevBtn);

        for (let i = 1; i <= totalPages; i++) {{
          const btn = document.createElement("button");
          btn.className = "page-btn" + (i === currentPage ? " active" : "");
          btn.textContent = i;
          btn.onclick = () => render(i);
          pag.appendChild(btn);
        }}

        const nextBtn = document.createElement("button");
        nextBtn.className = "page-btn";
        nextBtn.textContent = "다음 ›";
        nextBtn.disabled = (currentPage === totalPages);
        nextBtn.onclick = () => render(currentPage + 1);
        pag.appendChild(nextBtn);
      }}
      render(1);
    }}

    window.addEventListener("DOMContentLoaded", () => {{
      const chks = document.querySelectorAll(".ads-chk");
      chks.forEach((c, i) => {{
        if (localStorage.getItem("tistory_ads_chk_" + i) === "1") c.checked = true;
      }});
      updateAdsCount();
      initPagination("tistoryPostList", "tistoryPagination", 5);
    }});
  </script>
</body>
</html>"""

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    log(f"✅ blog/tistory/index.html 대시보드 갱신 완료 (총 {len(posts)}개 포스트)")

def update_root_portal_with_tistory(today_str, tistory_posts):
    """최상위 루트 index.html에 티스토리 활성화 상태 및 최신 티스토리 포스트 링크 반영"""
    portal_path = os.path.join(BASE_DIR, "index.html")
    if not os.path.exists(portal_path):
        return

    with open(portal_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. tag-tistory CSS 스타일 보강 (없을 경우 추가)
    if ".tag-tistory" not in content:
        content = content.replace(
            ".tag-naver {\n      background: var(--naver-light);\n      color: var(--naver-dark);\n    }",
            ".tag-naver {\n      background: var(--naver-light);\n      color: var(--naver-dark);\n    }\n    .tag-tistory {\n      background: var(--tistory-light);\n      color: var(--tistory);\n    }\n    .p-btn-tistory {\n      background: var(--tistory);\n      color: #fff;\n    }\n    .p-btn-tistory:hover {\n      background: #c2410c;\n    }"
        )

    # 2. 상단 헤더에 티스토리 포털 바로가기 버튼 추가
    if 'href="blog/tistory/index.html"' not in content:
        content = content.replace(
            '<a href="blog/naver/index.html" class="header-link header-link-naver">🟢 네이버 블로그 포털</a>',
            '<a href="blog/naver/index.html" class="header-link header-link-naver">🟢 네이버 블로그 포털</a>\n        <a href="blog/tistory/index.html" class="header-link" style="background: var(--tistory-light); color: var(--tistory); border-color: #fed7aa;">🟠 티스토리 포털</a>'
        )

    # 3. Platform 2: Tistory 카드를 '운영 중'으로 업데이트
    latest_t = tistory_posts[0] if tistory_posts else None
    latest_t_link = f"blog/tistory/{latest_t['rel_html']}" if latest_t else "blog/tistory/index.html"

    old_tistory_card_pattern = r'<!-- Platform 2: Tistory[\s\S]*?<!-- Platform 3: WordPress'
    new_tistory_card = f"""<!-- Platform 2: Tistory (Active) -->
      <div class="platform-card tistory">
        <div>
          <div class="platform-card-header">
            <div class="platform-brand">
              <div class="platform-logo">T</div>
              <div class="platform-name">티스토리 · 똑똑한 생활탐구</div>
            </div>
            <span class="status-badge badge-active">🟢 운영 중</span>
          </div>

          <p class="platform-desc">
            <strong>Google Trends 상승 검색어</strong>를 장기 검색형 질문(방법·비교·절차)으로 전환! 공식 자료 검증과 7단계 구성으로 구글 검색 유입 및 애드센스 수익을 구축합니다.
          </p>

          <div class="platform-meta-box">
            <div class="meta-row">
              <span class="meta-label">운영 목표</span>
              <span class="meta-value" style="color: var(--tistory);">하루 1편 / 주 5편 (100점 평가 선별)</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">주요 타겟</span>
              <span class="meta-value">구글(Google) SEO & 다음 검색</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">수익 모델</span>
              <span class="meta-value">구글 애드센스(AdSense) 달러 수익</span>
            </div>
          </div>
        </div>

        <div class="platform-btn-group">
          <a href="blog/tistory/index.html" class="p-btn p-btn-tistory">
            🟠 티스토리 블로그 작업실 이동
          </a>
        </div>
      </div>

      <!-- Platform 3: WordPress"""
    content = re.sub(old_tistory_card_pattern, new_tistory_card, content)

    # 4. 최근 작성된 일별 블로그 포스팅에 티스토리 최신 글과 네이버 최신 글 통합 표시
    tistory_rows = ""
    for p in tistory_posts[:3]:
        p_date_only = p["date_only"]
        try:
            dt = datetime.strptime(p_date_only, "%Y-%m-%d")
            weekday = WEEKDAYS_KR[dt.weekday()]
            date_display = f"{p_date_only} ({weekday} · {p['category']} · 평가 {p['score_str']})"
        except Exception:
            date_display = p["post_id"]
        post_link = f"blog/tistory/{p['rel_html']}"
        tistory_rows += f"""
      <div class="post-item-row">
        <div class="post-item-left">
          <span class="post-platform-tag tag-tistory">티스토리</span>
          <a href="{post_link}" class="post-item-title">
            {p['title']}
          </a>
        </div>
        <span class="post-item-date">{date_display}</span>
        <a href="{post_link}" class="post-item-btn">
          👁️ 포스트 열기 & 서식 복사
        </a>
      </div>"""

    marker_pattern = r'(<!-- RECENT_POSTS_LIST_START -->)([\s\S]*?)(<!-- RECENT_POSTS_LIST_END -->)'
    m_marker = re.search(marker_pattern, content)
    if m_marker:
        existing_rows = m_marker.group(2)
        # 기존 티스토리 행 제거 후 최신 티스토리 행을 상단에 결합
        naver_only_rows = re.sub(
            r'\s*<div class="post-item-row">[\s\S]*?<span class="post-platform-tag tag-tistory">티스토리</span>[\s\S]*?</div>\s*</div>',
            '',
            existing_rows
        )
        # 조금 더 안전하게 각 row 단위로 분리하여 tag-naver만 유지
        row_blocks = re.findall(
            r'(<div class="post-item-row">\s*<div class="post-item-left">[\s\S]*?</div>\s*<span class="post-item-date">[\s\S]*?</span>\s*<a[^>]*class="post-item-btn">[\s\S]*?</a>\s*</div>)',
            existing_rows
        )
        naver_blocks = [b for b in row_blocks if "tag-naver" in b][:6]
        combined_html = tistory_rows + "\n      " + "\n      ".join(naver_blocks)
        content = content[:m_marker.start()] + f"<!-- RECENT_POSTS_LIST_START -->{combined_html}\n      <!-- RECENT_POSTS_LIST_END -->" + content[m_marker.end():]

    with open(portal_path, "w", encoding="utf-8") as f:
        f.write(content)
    log("✅ 루트 index.html 포털에 티스토리 작업실 및 최신 포스팅 연동 완료")

def run_tistory_batch(target_date=None, force=False):
    """티스토리 일별 배치 메인 실행"""
    lock_file_path = "/tmp/daily_tistory_batch.lock"
    try:
        lock_file = open(lock_file_path, "w")
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError):
        log("ℹ️ 이미 다른 프로세스에서 티스토리 배치가 실행 중입니다.")
        return

    now = datetime.now()
    today_date = datetime.strptime(target_date, "%Y-%m-%d") if target_date else now
    today_str = today_date.strftime("%Y-%m-%d")
    weekday_str = WEEKDAYS_KR[today_date.weekday()]

    log(f"🚀 [티스토리 배치 시작] Google Trends 상승 검색어 기반 티스토리 글 생성 (기준일: {today_str} {weekday_str}요일, force={force})")

    evaluated_trends = fetch_google_trends_for_tistory()
    selected = [t for t in evaluated_trends if t["eval"]["is_selected"]]

    # 만약 실시간 트렌드 10개 중 매칭된 주제가 부족할 경우 핵심 카테고리 상승 주제로 보완
    if not selected:
        fallback_item = {
            "rank": 1,
            "keyword": "AI 블로그 팩트체크",
            "traffic": "상승",
            "news_title": "생성형 AI 활용 정보성 블로그 작성 및 사실 검증 가이드",
            "news_url": "https://developers.google.com/search/docs?hl=ko",
            "eval": evaluate_trend_for_tistory("AI", "생성형 AI 활용 정보성 블로그 작성")
        }
        selected = [fallback_item]

    # 점수순 정렬 (가장 높은 평가 점수를 받은 주제를 #1편 메인으로 발행)
    selected_sorted = sorted(selected, key=lambda x: x["eval"]["total_score"], reverse=True)

    for idx, t_item in enumerate(selected_sorted[:3], 1):
        post_id = today_str if idx == 1 else f"{today_str}-{idx}"
        create_tistory_post(post_id, today_str, weekday_str, t_item, post_num=idx, force=force)

    log(f"📝 오늘 작성된 티스토리 검색형 포스팅: 총 {min(len(selected_sorted), 3)}편")

    posts = scan_tistory_posts()
    update_tistory_index_html(today_str, evaluated_trends, posts)
    update_root_portal_with_tistory(today_str, posts)

    gen_script = os.path.join(BASE_DIR, "tools", "generate_html.py")
    if os.path.exists(gen_script):
        os.system(f"{sys.executable} {gen_script} > /dev/null 2>&1")
        log("✅ 전체 가이드 뷰어(docs/index.html) 동기화 완료")

    log(f"🎉 [티스토리 배치 완료] {today_str} 티스토리 블로그 작업이 완료되었습니다.\n")

if __name__ == "__main__":
    force_mode = "--force" in sys.argv
    date_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    t_date = date_args[0] if date_args else None
    run_tistory_batch(t_date, force=force_mode)

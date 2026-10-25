#!/usr/bin/env python3
"""
Daily Naver Blog Automation Batch
매일 새벽 00시(자정)에 실행되어 실시간 트렌드 키워드를 수집하고,
당일 네이버 블로그 포스팅 초안(.md, .html) 및 블로그 대시보드(index.html)를 자동 생성/갱신합니다.
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
NAVER_BLOG_DIR = os.path.join(BASE_DIR, "blog", "naver")
POSTS_DIR = os.path.join(NAVER_BLOG_DIR, "posts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "daily_batch.log")

# 요일 한글 변환
WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

# 블로그 핵심 테마(품미인생: 자산/건강/음식/취미/인생2막) 정의
BLOG_THEMES = {
    "finance": {
        "name": "노후 자산관리 & 연금·절세",
        "category": "경제 / 시사 / 노후 자산관리",
        "keywords": [
            "국민연금", "기초연금", "퇴직연금", "주택연금", "개인연금", "연금", "irp", "isa", "노후자금",
            "절세", "세금", "세액공제", "상속세", "증여세", "양도세", "취득세", "재산세", "종부세", "건보료", "건강보험료", "연말정산", "환급",
            "금리", "예금", "적금", "특판", "파킹통장", "은행", "시중은행", "저축은행", "이자", "대출",
            "주식", "증시", "코스피", "코스닥", "배당", "배당주", "삼성전자", "삼전", "하이닉스", "삼전닉스", "반도체", "엔비디아", "etf", "펀드", "채권", "국채", "동전주", "테마주", "우량주",
            "금시세", "골드바", "골드", "안전자산", "환율", "달러", "엔화",
            "부동산", "청약", "아파트", "분양", "전세", "월세", "임대", "상가", "경매", "공시지가", "재건축", "재개발",
            "지원금", "보조금", "수당", "기부", "고향사랑"
        ],
        "lead": "은퇴 후 가장 중요한 것은 일확천금을 좇는 무리한 투자가 아니라, 매달 꾸준히 통장에 입금되는 안정적인 현금 흐름과 평생 모은 소중한 원금을 든든히 지키는 자산 관리입니다.",
        "p1_title": "변동성 높은 금융 시장과 은퇴자의 자산 리스크",
        "p1_desc": "시장의 변동성은 젊은 세대보다 은퇴자에게 훨씬 더 치명적입니다. 단기 시세차익보다는 배당 수익과 원금 보존형 포트폴리오를 구성해야 불안감 없이 편안한 노후를 보낼 수 있습니다.",
        "p2_title": "원금 보존과 안정적 현금 흐름을 만드는 실전 분산",
        "p2_desc": "특판 고금리 예적금, 안전한 배당 ETF, 절세 혜택이 큰 IRP/ISA 계좌를 적절히 배분하여 세금 부담은 줄이고 안정적인 현금 파이프라인을 구축해야 합니다.",
        "p3_title": "불필요한 세금과 지출을 막는 절세 체크리스트",
        "p3_desc": "금융소득종합과세와 건강보험료 피부양자 탈락 기준을 미리 숙지하고, 합법적인 비과세·감면 제도를 적극 활용하여 새어 나가는 돈을 원천 차단해야 합니다."
    },
    "health": {
        "name": "시니어 건강 & 웰빙",
        "category": "건강 / 웰빙 / 시니어 헬스케어",
        "keywords": [
            "건강", "병원", "의사", "약국", "치료", "수술", "요양", "간병", "실비", "보험",
            "혈당", "당뇨", "고혈압", "혈압", "고지혈증", "콜레스테롤", "심장", "뇌졸중", "뇌경색", "혈관",
            "관절", "무릎", "연골", "디스크", "허리", "척추", "오십견", "관절염", "통증", "정형외과",
            "치아", "임플란트", "틀니", "치과", "스케일링",
            "눈", "안과", "백내장", "녹내장", "황반변성", "노안", "시력",
            "영양제", "비타민", "오메가", "단백질", "유산균", "보충제", "건기식", "식단", "다이어트",
            "수면", "불면증", "우울증", "치매", "기억력", "인지장애", "대상포진", "갱년기", "노화",
            "건강검진", "암검진", "국가검진", "내시경", "감기", "독감", "백신", "예방접종"
        ],
        "lead": "통장에 수억 원의 잔고가 있어도 내 몸이 아프면 아무 소용이 없습니다. 5060 인생 2막에서 가장 값지고 든든한 1등 자산은 바로 '건강한 몸과 맑은 정신'입니다.",
        "p1_title": "나이 들수록 조용히 찾아오는 만성질환의 위험성",
        "p1_desc": "혈관 건강과 관절, 대사 질환은 초기 증상이 뚜렷하지 않아 방치하기 쉽습니다. 사소한 몸의 신호를 가볍게 넘기지 말고 정기적인 검진과 수치 관리를 생활화해야 합니다.",
        "p2_title": "식후 30분 걷기와 균형 잡힌 시니어 영양 루틴",
        "p2_desc": "무리한 고강도 운동 대신 매일 꾸준한 유산소 걷기와 하체 근력 운동을 병행하고, 단백질과 항산화 영양소를 골고루 섭취하여 근감소증을 예방하는 것이 핵심입니다.",
        "p3_title": "숙면과 스트레스 다스리는 힐링 라이프스타일",
        "p3_desc": "충분한 수면은 면역력 회복과 뇌 건강의 기본입니다. 취침 전 스마트폰 사용을 줄이고, 감사하는 마음과 명상으로 심리적 평온을 유지하는 지혜가 필요합니다."
    },
    "food_lifestyle": {
        "name": "품미인생 & 맛있는 일상",
        "category": "일상 / 맛집 / 푸드 & 라이프",
        "keywords": [
            "맛집", "식당", "음식", "요리", "레시피", "집밥", "반찬", "밥상",
            "김치", "김장", "배추", "절임배추", "고춧가루", "양념", "마늘", "양파", "제철", "보양식",
            "고기", "한우", "삼겹살", "생선", "해산물", "과일", "사과", "배", "감", "쌀", "농협", "하나로마트", "로컬푸드", "전통시장", "오일장",
            "카페", "커피", "베이커리", "빵", "전통차", "와인", "전통주", "막걸리"
        ],
        "lead": "좋은 계절에 사랑하는 가족, 소중한 이웃과 함께 맛있는 밥상을 나누는 것, 그것이야말로 품미인생(品味人生)이 추구하는 노후의 가장 크고 진솔한 행복입니다.",
        "p1_title": "제철 식재료가 주는 보약 같은 자연의 맛",
        "p1_desc": "계절의 흐름을 담은 신선한 제철 채소와 로컬 식재료는 인공 영양제보다 뛰어난 건강의 원천입니다. 식탁 위의 작은 변화가 일상에 활력과 입맛을 되찾아줍니다.",
        "p2_title": "가계부는 가볍게, 밥상은 풍성하게 채우는 장보기 비결",
        "p2_desc": "직거래 장터, 농협 하나로마트, 제철 특판을 현명하게 활용하면 외식비 부담은 대폭 줄이면서도 집밥의 품격을 최고로 끌어올릴 수 있습니다.",
        "p3_title": "추억과 정성이 깃든 시니어의 손맛과 미식 탐방",
        "p3_desc": "오랜 세월 가족을 위해 차려온 손맛 레시피를 정갈하게 기록하고, 전국 곳곳 숨겨진 건강한 노포 맛집을 찾아 떠나는 여정은 삶에 따뜻한 감동을 선사합니다."
    },
    "hobby_sports": {
        "name": "시니어 취미 & 스포츠·여행",
        "category": "취미 / 스포츠 / 시니어 라이프",
        "keywords": [
            "골프", "파크골프", "당구", "탁구", "배드민턴", "테니스", "수영", "걷기", "만보", "트레킹", "등산", "단풍", "캠핑", "차박", "낚시",
            "여행", "국내여행", "기차여행", "ktx", "온천", "힐링", "휴양", "숙소", "호텔", "리조트", "펜션", "축제", "페스티벌",
            "취미", "사진", "카메라", "가드닝", "화초", "텃밭", "원예", "분재", "음악", "악기", "기타", "색소폰", "노래", "트로트"
        ],
        "lead": "은퇴 후 길어진 여유 시간, 땀 흘리며 몰입할 수 있는 운동이나 가슴 뛰는 취미 하나는 노후의 무료함을 없애고 새로운 활력을 불어넣는 최고의 친구입니다.",
        "p1_title": "몸에 무리 없는 저강도·고효율 힐링 레저의 매력",
        "p1_desc": "당구, 파크골프, 가벼운 트레킹처럼 관절에 무리를 주지 않으면서도 집중력과 두뇌 회전, 적당한 신체 활동을 동시에 챙길 수 있는 운동이 시니어에게 최적입니다.",
        "p2_title": "좋은 사람들과 교류하며 사회적 유대감 쌓기",
        "p2_desc": "동호회나 커뮤니티 활동을 통해 비슷한 공감대를 가진 친구들을 사귀고, 건전한 승부와 대화를 나누는 과정에서 은퇴 후 고립감을 자연스럽게 해소할 수 있습니다.",
        "p3_title": "비용 부담 없이 오래 즐기는 스마트한 취미 관리 노하우",
        "p3_desc": "지자체 체육시설이나 공공 레저 공간, 비수기 여행 혜택을 꼼꼼히 챙기면 경제적인 부담 없이도 수준 높은 취미 생활을 평생 이어갈 수 있습니다."
    },
    "career_life2": {
        "name": "인생 2막 & 은퇴 일자리",
        "category": "커리어 / 인생 2막 / 사회공헌",
        "keywords": [
            "은퇴", "퇴직", "정년", "명퇴", "인생2막", "5060", "신중년", "시니어", "노후",
            "일자리", "재취업", "알바", "공공근로", "사회공헌", "노인일자리", "시니어클럽",
            "택시", "개인택시", "운전", "모빌리티", "화물", "배달",
            "자격증", "국가자격증", "조경", "손해평가사", "사회복지사", "경비지도사", "주택관리사",
            "창업", "소자본", "무인매장", "귀농", "귀촌", "전원생활",
            "스마트폰", "갤럭시", "아이폰", "폴더블", "디지털", "ai", "chatgpt", "키오스크", "유튜브"
        ],
        "lead": "평생의 직장을 떠났다고 해서 나의 사회적 가치까지 사라지는 것은 아닙니다. 30~40년간 축적된 경륜과 지혜는 인생 2막에서 새로운 꽃을 피울 준비가 되어 있습니다.",
        "p1_title": "수입보다 보람과 활력을 찾는 신중년의 사회 참여",
        "p1_desc": "젊은 시절처럼 치열한 경쟁에 뛰어들기보다는, 나의 경험을 나누고 사회에 기여할 수 있는 공공 일자리나 멘토링, 사회공헌 활동이 정서적 만족감을 극대화합니다.",
        "p2_title": "정부 지원제도와 시니어 취업 포털 적극 활용하기",
        "p2_desc": "신중년 경력형 일자리, 노인일자리 지원사업, 지자체 시니어클럽 등 은퇴자를 위해 마련된 공공 복지 인프라를 잘 활용하면 안정적인 활동 기회를 얻을 수 있습니다.",
        "p3_title": "디지털 역량 강화와 평생 학습으로 시대에 발맞추기",
        "p3_desc": "스마트폰과 AI 도구를 조금만 익혀두면 일상생활은 물론 새로운 재취업이나 1인 미디어 창작 활동에서도 남들보다 한발 앞서나갈 수 있습니다."
    }
}

def match_blog_theme(keyword, news_title=""):
    """
    트렌드 키워드 및 뉴스가 품미인생 블로그 테마(자산, 건강, 음식, 취미, 인생2막)와
    연관성이 있는지 판별하고 매칭된 테마 정보를 반환.
    연관이 없으면 None 반환.
    """
    target = f"{keyword} {news_title}".lower()
    for theme_key, theme_info in BLOG_THEMES.items():
        for kw in theme_info["keywords"]:
            if kw in target:
                return {
                    "theme_key": theme_key,
                    "theme_name": theme_info["name"],
                    "category": theme_info["category"],
                    "matched_keyword": kw,
                    "lead": theme_info["lead"],
                    "p1_title": theme_info["p1_title"],
                    "p1_desc": theme_info["p1_desc"],
                    "p2_title": theme_info["p2_title"],
                    "p2_desc": theme_info["p2_desc"],
                    "p3_title": theme_info["p3_title"],
                    "p3_desc": theme_info["p3_desc"],
                }
    return None

def log(msg):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    print(formatted)
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def fetch_trending_keywords():
    """Google Trends RSS 및 Fallback을 통한 실시간 검색어 Top 10 수집 (블로그 테마 자동 매칭)"""
    url = "https://trends.google.co.kr/trending/rss?geo=KR"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    trends = []

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = root.findall(".//item")
        
        for item in items[:10]:
            title = item.find("title").text if item.find("title") is not None else ""
            approx = item.find("{https://trends.google.com/trending/rss}approx_traffic")
            traffic = approx.text if approx is not None else ""
            news_items = item.findall("{https://trends.google.com/trending/rss}news_item")
            news_title = news_items[0].find("{https://trends.google.com/trending/rss}news_item_title").text if news_items else ""
            
            trends.append({
                "keyword": title,
                "traffic": traffic,
                "news_title": news_title
            })
    except Exception as e:
        log(f"⚠️ 트렌드 RSS 수집 실패 (Fallback 키워드 사용): {e}")

    # Fallback 키워드 (오프라인/에러 대비)
    if len(trends) < 10:
        fallbacks = [
            {"keyword": "금 (Gold)", "traffic": "2000+", "news_title": "안전자산 금 시세 최고치 경신"},
            {"keyword": "국민연금", "traffic": "1000+", "news_title": "국민연금 수령액 인상 및 개혁안 발표"},
            {"keyword": "기초연금", "traffic": "800+", "news_title": "기초연금 40만원 단계적 인상 및 감액 기준"},
            {"keyword": "건강검진", "traffic": "1500+", "news_title": "올해 국가건강검진 대상자 및 필수 수검 항목"},
            {"keyword": "절세 혜택", "traffic": "600+", "news_title": "은퇴자를 위한 ISA 및 IRP 연말정산 절세 팁"},
            {"keyword": "파크골프", "traffic": "1200+", "news_title": "전국 파크골프장 인기 코스 및 예약 노하우"},
            {"keyword": "임플란트", "traffic": "900+", "news_title": "65세 이상 임플란트 건강보험 적용 기준"},
            {"keyword": "정기예금", "traffic": "2000+", "news_title": "시중은행 특판 고금리 예적금 금리 비교"},
            {"keyword": "시니어 일자리", "traffic": "700+", "news_title": "사회공헌 및 공공 시니어 일자리 신청 방법"},
            {"keyword": "혈당 관리", "traffic": "1100+", "news_title": "식후 30분 걷기와 연속혈당측정기 활용법"}
        ]
        needed = 10 - len(trends)
        trends.extend(fallbacks[:needed])

    # 키워드별 테마 분석 및 블로그 추천 제목 생성
    results = []
    for i, t in enumerate(trends, 1):
        kw = t["keyword"]
        news = t["news_title"]
        theme_info = match_blog_theme(kw, news)
        rec_title = generate_blog_title_for_trend(kw, news, theme_info)
        results.append({
            "rank": i,
            "keyword": kw,
            "badge": t.get("traffic", "실시간"),
            "news": news,
            "recommended_title": rec_title,
            "theme": theme_info
        })

    return results

def generate_blog_title_for_trend(keyword, news_title, theme_info=None):
    """트렌드 키워드를 네이버 블로그 스마트블록 상위노출용 매력적인 제목으로 변환"""
    kw = keyword.strip()
    
    if theme_info:
        theme_key = theme_info["theme_key"]
        if theme_key == "finance":
            if any(w in kw for w in ["연금", "국민연금", "기초연금", "퇴직연금", "주택연금", "개인연금"]):
                return f"{kw} 수령액 개편 뉴스 총정리! 내 노후 통장에 미치는 영향과 꿀팁 3가지"
            elif any(w in kw for w in ["주식", "삼전", "하이닉스", "반도체", "증시", "코스피", "코스닥"]):
                return f"흔들리는 증시 속 '{kw}' 주목! 5060 은퇴자 배당·안전 자산관리 관점 대응법 3가지"
            elif any(w in kw for w in ["기부", "고향사랑", "세금", "절세", "연말정산", "환급"]):
                return f"13월의 월급 늘리는 '{kw}' 절세 비결! 은퇴자가 꼭 챙겨야 할 세액공제 알짜 혜택 총정리"
            elif any(w in kw for w in ["금시세", "골드바", "골드"]) or kw == "금":
                return f"지금이라도 금 사둘까? 사상 최고가 속 은퇴자 실전 금 투자법 3가지"
            elif any(w in kw for w in ["예금", "적금", "금리", "파킹통장", "은행"]):
                return f"{kw} 금리 비교와 만기 재예치 노하우, 이자 세금 아끼는 3대 절세 비결"
            elif any(w in kw for w in ["부동산", "아파트", "청약", "전세", "월세"]):
                return f"변화하는 부동산 시장 속 '{kw}' 체크포인트! 은퇴자 주거 안정과 자산 방어 전략"
            else:
                return f"노후 자산 지키는 '{kw}' 핵심 체크포인트! 은퇴 전후 꼭 알아야 할 자산관리 팁 3가지"
        elif theme_key == "health":
            if any(w in kw for w in ["치아", "임플란트", "틀니", "치과"]):
                return f"65세 이상 임플란트 건강보험 혜택과 '{kw}' 주의사항! 씹는 즐거움 되찾는 치아 관리법"
            elif any(w in kw for w in ["혈당", "당뇨", "혈압", "고혈압", "고지혈증"]):
                return f"식후 30분 혈당 스파이크 잡는 '{kw}' 관리법! 5060 건강 지키는 실전 식단 루틴"
            elif any(w in kw for w in ["관절", "무릎", "오십견", "디스크", "척추", "관절염"]):
                return f"지긋지긋한 관절 통증 줄이는 '{kw}' 관리 노하우! 매일 10분 스트레칭과 습관 3가지"
            elif any(w in kw for w in ["눈", "안과", "백내장", "녹내장", "노안", "황반변성"]):
                return f"침침한 눈 건강 되살리는 '{kw}' 예방 및 관리법! 5060 시니어 필수 안과 상식"
            elif any(w in kw for w in ["검진", "건강검진", "암검진", "내시경"]):
                return f"올해 놓치면 손해인 국가건강검진과 '{kw}' 필수 체크리스트 3가지"
            else:
                return f"내 몸 살리는 '{kw}' 핵심 가이드! 5060 세대가 꼭 알아야 할 건강 수칙 3가지"
        elif theme_key == "food_lifestyle":
            if any(w in kw for w in ["김장", "배추", "김치", "절임배추"]):
                return f"올해 {kw} 비용 부담 줄이는 실전 비법! 맛과 가성비 다 잡는 품미인생 김장 노하우"
            elif any(w in kw for w in ["맛집", "식당", "음식", "노포"]):
                return f"입맛 돋우는 전국 숨은 '{kw}' 탐방기! 든든하고 건강한 품미인생 미식 가이드"
            else:
                return f"맛있는 인생 2막을 위한 '{kw}' 식도락 가이드! 제철 밥상과 건강 챙기는 꿀팁"
        elif theme_key == "hobby_sports":
            if "당구" in kw:
                return f"은퇴 후 최고의 힐링 스포츠 '당구'! 5060 세대가 다시 당구장에 모이는 이유와 건강 효과 3가지"
            elif any(w in kw for w in ["골프", "파크골프"]):
                return f"요즘 대세 '{kw}' 완벽 입문 가이드! 관절에 무리 없이 즐기는 실전 꿀팁 베스트 5"
            elif any(w in kw for w in ["등산", "트레킹", "걷기", "만보"]):
                return f"무릎 부담 없는 '{kw}' 명코스 추천! 은퇴 후 몸과 마음을 채우는 힐링 로드"
            else:
                return f"인생 2막을 풍요롭게 채우는 취미 '{kw}'! 건강과 즐거움을 함께 잡는 3가지 노하우"
        elif theme_key == "career_life2":
            if any(w in kw for w in ["택시", "개인택시", "운전", "모빌리티"]):
                return f"은퇴 후 자유로운 인생 2막! '{kw}' 취업 및 부업 노하우와 실제 수입 체크포인트"
            elif any(w in kw for w in ["스마트폰", "폰", "폴더블", "디지털", "ai", "chatgpt"]):
                return f"5060을 위한 스마트 라이프! '{kw}' 최신 트렌드와 일상을 편리하게 바꾸는 핵심 기능"
            elif any(w in kw for w in ["일자리", "재취업", "알바", "공공근로", "노인일자리"]):
                return f"은퇴 후 활력 찾는 '{kw}' 지원제도 총정리! 5060 신중년 맞춤형 일자리 신청 노하우"
            elif any(w in kw for w in ["자격증", "국가자격증"]):
                return f"은퇴 후 평생 쓸 수 있는 '{kw}' 유망 자격증 3선! 취득 전략과 실전 활용처"
            else:
                return f"경륜과 지혜로 꽃피우는 인생 2막! '{kw}' 소식 속 은퇴자가 발견한 새로운 가능성"

    # 일반/시사 기본 제목 생성 (Rank 1 및 비테마)
    if news_title:
        clean_news = re.sub(r"\[.*?\]", "", news_title).strip()
        if len(clean_news) > 28:
            clean_news = clean_news[:28] + "..."
        return f"{kw} 이슈 주목! {clean_news} - 은퇴자 관점에서 본 핵심 체크포인트"
    else:
        return f"실시간 핫이슈 '{kw}' 총정리! 우리가 꼭 알아야 할 핵심 내용과 일상 꿀팁"

def create_post(post_id, date_str, weekday_str, trend, theme_info=None, post_num=1, force=False):
    """
    개별 네이버 블로그 포스팅(.md 및 .html) 자동 생성
    - post_id: '2026-10-20' (1편 메인) 또는 '2026-10-20-2' (추가 테마 글)
    - post_num: 글 순번 (1, 2, 3...)
    - force: 기존 파일 존재 시에도 강제 재생성 여부
    - 년월(YYYYMM) 폴더 하위에 파일 생성 (예: blog/naver/posts/202610/)
    """
    ym = date_str[:7].replace("-", "")  # YYYYMM 형식 (예: 202610)
    post_dir = os.path.join(POSTS_DIR, ym)
    os.makedirs(post_dir, exist_ok=True)
    md_path = os.path.join(post_dir, f"{post_id}.md")
    html_path = os.path.join(post_dir, f"{post_id}.html")

    # 이미 포스팅 파일이 존재하면 force가 아닐 때 보존
    if not force and os.path.exists(md_path) and os.path.exists(html_path):
        log(f"ℹ️ posts/{ym}/{post_id} 포스팅 파일이 이미 존재하여 보존합니다.")
        return

    kw = trend["keyword"]
    title = trend["recommended_title"]
    news = trend.get("news", "")

    if theme_info:
        theme_name = theme_info["theme_name"]
        category = theme_info["category"]
        matched_kw = theme_info["matched_keyword"]
        lead_text = theme_info["lead"]
        p1_title = theme_info["p1_title"]
        p1_desc = theme_info["p1_desc"]
        p2_title = theme_info["p2_title"]
        p2_desc = theme_info["p2_desc"]
        p3_title = theme_info["p3_title"]
        p3_desc = theme_info["p3_desc"]
        theme_badge_line = f"> **테마 분류**: {theme_name} (연관 키워드: {matched_kw})  \n"
        tags_line = f"#{kw.replace(' ', '')} #{matched_kw.replace(' ', '')} #인생2막 #품미인생 #노후자산관리 #생활꿀팁 #스마트블록 #디지털연금"
    else:
        theme_name = "실시간 트렌드"
        category = "경제 / 시사 / 노후 자산관리 & 라이프"
        matched_kw = kw
        lead_text = f"오늘 아침 실시간 검색어와 주요 뉴스에서 가장 뜨겁게 화제가 되고 있는 주제는 바로 '{kw}'입니다. 관련 소식({news})을 접하시고 많은 분들이 큰 관심을 갖고 계실 텐데요."
        p1_title = "오늘 이슈가 대중의 주목을 받는 배경"
        p1_desc = "단순한 단기 이슈가 아니라, 우리 생활과 소비, 자산 관리에 직간접적인 영향을 주는 중요한 계기가 되고 있습니다."
        p2_title = "내 상황에 맞는 분산과 안전성 최우선하기"
        p2_desc = "무리한 선택이나 급작스러운 변화보다는, 현재 내가 가지고 있는 자원(건강, 시간, 자산)을 안정적으로 지키는 수비적 관점을 유지해야 합니다."
        p3_title = "작은 것부터 오늘 바로 실천해보기"
        p3_desc = "아무리 좋은 정보라도 행동하지 않으면 내 것이 되지 않습니다. 오늘 소개해 드린 체크리스트 중 하나라도 즉시 내 삶에 적용해 보세요."
        theme_badge_line = ""
        tags_line = f"#{kw.replace(' ', '')} #{kw.replace(' ', '')}전망 #인생2막 #품미인생 #노후자산관리 #생활꿀팁 #실시간트렌드 #디지털연금"

    # 네이버 스마트블록 친화적 마크다운 본문 템플릿 (최종 발행용 내용만 구성)
    md_content = f"""# {title}

안녕하세요, 든든한 노후 자산과 맛있는 일상을 가꾸는 블로그 지기 **'품미인생(品味人生)'**입니다.

{lead_text}

> **"이 소식이 내 일상과 노후 준비에 어떤 영향을 미칠까?"**  
> **"우리가 미리 알고 준비해야 할 핵심 포인트는 무엇일까?"**

오늘은 5060 세대와 은퇴자의 관점에서 **'{kw}' 관련 핵심 쟁점과 실생활에 바로 적용할 수 있는 3가지 실천 팁**을 알기 쉽게 정리해 드립니다.

---

## 1. {p1_title}

최근 관련 트렌드와 뉴스를 살펴보면 많은 분들이 궁금해하시는 핵심 요인이 드러납니다.

* **변화하는 사회적 흐름**: {p1_desc}
* **시니어 세대의 현명한 대응 필요성**: 뉴스를 그저 스쳐 지나치지 않고, 나의 건강이나 가계부에 긍정적인 방향으로 접목하는 지혜가 필요한 시점입니다.

---

## 2. 우리가 꼭 기억해야 할 실천 포인트 3가지

### ① 팩트 기반으로 냉정하게 상황 파악하기
자극적인 제목이나 주변의 소문에 휩쓸리기보다는, 공신력 있는 기관의 발표와 정확한 수치를 기준으로 판단하는 것이 중요합니다.

### ② {p2_title}
{p2_desc}

### ③ {p3_title}
{p3_desc}

---

## 3. 실패를 줄이는 은퇴자의 지혜 한마디

제가 인생의 여러 굴곡을 겪으며 배운 가장 큰 교훈은 **"남들이 우르르 몰려갈 때 한 박자 쉬어가는 여유"**였습니다.  
오늘의 핫이슈 '{kw}' 역시 조급해하지 마시고, 차분히 본질을 들여다보신다면 분명 좋은 기회와 인생의 깊은 인사이트를 발견하실 수 있을 것입니다.

---

## 맺음말 & 소통 한마디

> "매일 마주하는 새로운 뉴스 속에서 나만의 가치를 발견하는 것,  
> 그것이 바로 인생 2막을 풍요롭게 만드는 최고의 습관입니다."

여러분은 오늘 '{kw}' 소식을 보며 어떤 생각이 드셨나요? 여러분만의 생각이나 궁금하신 점이 있다면 편하게 댓글로 남겨주세요.

글이 도움 되셨다면 **이웃 추가**와 **공감(❤️)** 꾹 부탁드립니다. 내일도 유익한 자산 정보와 맛있는 이야기로 찾아뵙겠습니다!

{tags_line}
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    log(f"✅ posts/{ym}/{post_id}.md 마크다운 파일 생성 완료 (#{post_num}편: [{kw}])")

    # HTML 뷰어 페이지 생성
    html_content = build_post_html(post_id, date_str, weekday_str, title, kw, md_content, theme_name=theme_name, category=category)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    log(f"✅ posts/{ym}/{post_id}.html 네이버 스마트에디터 전용 뷰어 생성 완료 (#{post_num}편: [{kw}])")

def create_daily_post(date_str, weekday_str, main_trend):
    """하위 호환 래퍼: 실시간 1위 트렌드 포스트 생성"""
    theme_info = match_blog_theme(main_trend["keyword"], main_trend.get("news", ""))
    create_post(date_str, date_str, weekday_str, main_trend, theme_info=theme_info, post_num=1)

def build_post_html(post_id, date_str, weekday_str, title, keyword, md_content, theme_name=None, category=None):
    """HTML 뷰어 템플릿 생성"""
    escaped_md = md_content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[{date_str}] 네이버 블로그 포스팅 | {title}</title>
  
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>

  <style>
    :root {{
      --naver-green: #03c75a;
      --naver-green-dark: #02b14f;
      --naver-light: #f4fbf7;
      --text-main: #222222;
      --text-muted: #666666;
      --border: #e6e6e6;
      --bg: #f5f6f8;
      --white: #ffffff;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.7;
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
    }}

    .nav-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-tag {{
      background: var(--naver-green);
      color: var(--white);
      font-size: 11px;
      font-weight: 800;
      padding: 3px 8px;
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
      gap: 10px;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.15s;
      border: 1px solid var(--border);
      background: var(--white);
      color: var(--text-main);
    }}

    .btn:hover {{ background: #f0f0f0; }}

    .btn-naver {{
      background: var(--naver-green);
      color: var(--white);
      border-color: var(--naver-green);
    }}
    .btn-naver:hover {{ background: var(--naver-green-dark); color: var(--white); }}

    .container {{
      max-width: 820px;
      margin: 32px auto 0;
      padding: 0 16px;
    }}

    .meta-card {{
      background: var(--white);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      border: 1px solid var(--border);
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}

    .meta-badges {{
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
    }}

    .badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background: #eef2ff;
      color: #4f46e5;
    }}

    .badge-trend {{
      background: #fef3c7;
      color: #b45309;
    }}

    .post-title {{
      font-size: 24px;
      font-weight: 800;
      line-height: 1.4;
      margin-bottom: 14px;
      color: #111;
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

    .smarteditor-preview {{
      background: var(--white);
      border-radius: 12px;
      padding: 40px 48px;
      border: 1px solid var(--border);
      box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}

    .smarteditor-preview h1 {{
      font-size: 24px;
      font-weight: 800;
      margin-bottom: 24px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--naver-green);
    }}

    .smarteditor-preview h2 {{
      font-size: 19px;
      font-weight: 700;
      margin: 32px 0 14px;
      color: #222;
      border-left: 4px solid var(--naver-green);
      padding-left: 10px;
    }}

    .smarteditor-preview h3 {{
      font-size: 17px;
      font-weight: 700;
      margin: 24px 0 10px;
      color: #333;
    }}

    .smarteditor-preview p {{
      margin-bottom: 18px;
      font-size: 15.5px;
      line-height: 1.85;
      color: #333;
      word-break: keep-all;
    }}

    .smarteditor-preview blockquote {{
      border: 1px solid #d9f3e4;
      background: var(--naver-light);
      padding: 16px 20px;
      margin: 22px 0;
      border-radius: 8px;
      color: #2b593f;
      font-weight: 500;
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
      transition: opacity 0.2s ease, transform 0.2s ease;
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
      <span class="brand-tag">NAVER BLOG · 품미인생</span>
      <span class="nav-title">일별 포스팅: {date_str} ({weekday_str}){f" · {theme_name}" if theme_name else ""}</span>
    </div>
    <div class="nav-actions">
      <a href="../../index.html" class="btn">📂 네이버 블로그 홈</a>
      <a href="{post_id}.md" target="_blank" class="btn">📄 원본 MD 열기</a>
      <button class="btn btn-naver" id="copyNaverBtn" title="네이버 스마트에디터에 붙여넣을 때 ** 없이 볼드 및 서식이 유지됩니다">
        🟢 네이버 스마트에디터 서식 복사
      </button>
      <button class="btn" id="copyCleanTextBtn" title="** 나 ### 등 마크다운 기호를 모두 지운 깨끗한 텍스트로 복사합니다">
        📄 순수 텍스트 복사 (** 제거)
      </button>
    </div>
  </header>

  <div class="container">
    <div class="meta-card">
      <div class="meta-badges">
        <span class="badge">{category or "시사 / 라이프"}</span>
        <span class="badge badge-trend">🔥 실시간 트렌드: [{keyword}]{f" · {theme_name}" if theme_name else ""}</span>
      </div>
      <h1 class="post-title">{title}</h1>
      
      <div class="meta-info-grid">
        <div class="meta-info-item">
          <span>작성일자:</span><strong>{date_str} ({weekday_str})</strong>
        </div>
        <div class="meta-info-item">
          <span>글자수:</span><strong>약 1,800자 (공백 포함)</strong>
        </div>
        <div class="meta-info-item">
          <span>예상 소요시간:</span><strong>3분 30초</strong>
        </div>
        <div class="meta-info-item">
          <span>스마트블록 타겟:</span><strong>{keyword}, {theme_name or "시니어 라이프"}</strong>
        </div>
      </div>
    </div>

    <article class="smarteditor-preview" id="postArticle"></article>
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
        .replace(/^\\s*\\*\\s+/gm, '• ')
        .trim();
    }}

    function getNaverOptimizedHtml() {{
      const clone = articleEl.cloneNode(true);
      clone.querySelectorAll("h1").forEach(el => el.setAttribute("style", "font-size: 24px; font-weight: bold; color: #111; margin-bottom: 24px; line-height: 1.4;"));
      clone.querySelectorAll("h2").forEach(el => el.setAttribute("style", "font-size: 19px; font-weight: bold; color: #03c75a; margin-top: 32px; margin-bottom: 14px; border-left: 4px solid #03c75a; padding-left: 10px;"));
      clone.querySelectorAll("h3, h4").forEach(el => el.setAttribute("style", "font-size: 16px; font-weight: bold; color: #222; margin-top: 22px; margin-bottom: 10px;"));
      clone.querySelectorAll("strong, b").forEach(el => el.setAttribute("style", "font-weight: bold; color: #111;"));
      clone.querySelectorAll("p").forEach(el => el.setAttribute("style", "font-size: 16px; line-height: 1.85; color: #333; margin-bottom: 18px; word-break: keep-all;"));
      clone.querySelectorAll("blockquote").forEach(el => el.setAttribute("style", "background-color: #f4fbf7; border: 1px solid #d9f3e4; border-left: 4px solid #03c75a; padding: 16px 20px; margin: 22px 0; border-radius: 6px; color: #235438; font-style: normal; font-size: 15px;"));
      clone.querySelectorAll("hr").forEach(el => el.setAttribute("style", "border: 0; height: 1px; background-color: #e6e6e6; margin: 36px 0;"));
      clone.querySelectorAll("ul, ol").forEach(el => el.setAttribute("style", "margin: 16px 0 20px 20px; padding: 0;"));
      clone.querySelectorAll("li").forEach(el => el.setAttribute("style", "font-size: 15.5px; line-height: 1.75; margin-bottom: 8px; color: #333;"));
      return clone.innerHTML;
    }}

    document.getElementById("copyNaverBtn").addEventListener("click", async () => {{
      const htmlContent = getNaverOptimizedHtml();
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
        try {{
          const tempEl = document.createElement("div");
          tempEl.contentEditable = "true";
          tempEl.innerHTML = htmlContent;
          tempEl.style.position = "fixed";
          tempEl.style.left = "-9999px";
          document.body.appendChild(tempEl);
          const range = document.createRange();
          range.selectNodeContents(tempEl);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
          document.execCommand("copy");
          document.body.removeChild(tempEl);
          success = true;
        }} catch(e) {{
          await navigator.clipboard.writeText(plainText);
        }}
      }}
      showToast("🟢 네이버 에디터 맞춤 서식이 복사되었습니다! (에디터에 바로 붙여넣기 하세요 - ** 기호 없음)");
    }});

    document.getElementById("copyCleanTextBtn").addEventListener("click", async () => {{
      const plainText = getCleanPlainText();
      await navigator.clipboard.writeText(plainText);
      showToast("📄 ** 및 # 기호가 완전히 제거된 순수 텍스트가 복사되었습니다!");
    }});
  </script>
</body>
</html>"""

def scan_all_posts():
    """posts/ 디렉토리(YYYYMM 서브폴더 포함)의 모든 일별 글 목록을 스캔하여 메타데이터 리스트 반환"""
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

        # 상대 경로 계산 (blog/naver 기준)
        # 예: fpath가 blog/naver/posts/202610/2026-10-20.md 이면 rel_md는 'posts/202610/2026-10-20.md'
        rel_md = os.path.relpath(fpath, NAVER_BLOG_DIR)
        rel_html = rel_md[:-3] + ".html"
        html_fpath = fpath[:-3] + ".html"
        
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 제목 추출 (# ...)
            m_title = re.search(r"^#\s+(.+)$", content, re.M)
            title = m_title.group(1).strip() if m_title else post_id

            # 카테고리 추출
            m_cat = re.search(r">\s*\*\*카테고리\*\*:\s*(.+)$", content, re.M)
            if m_cat:
                category = m_cat.group(1).strip()
            else:
                matched_t = match_blog_theme(title, "")
                category = matched_t["category"] if matched_t else "경제 / 시사 / 노후 자산관리 & 라이프"

            # 테마 분류 추출
            m_theme = re.search(r">\s*\*\*테마 분류\*\*:\s*(.+)$", content, re.M)
            if m_theme:
                theme_name = m_theme.group(1).strip()
            else:
                matched_t = match_blog_theme(title, "")
                theme_name = f"{matched_t['theme_name']} (연관 키워드: {matched_t['matched_keyword']})" if matched_t else ""
            
            # 설명/요약 추출 (첫 번째 본문 단락)
            desc = ""
            paragraphs = content.split("\n\n")
            for p in paragraphs:
                p_clean = p.strip()
                if p_clean and not p_clean.startswith("#") and not p_clean.startswith(">") and not p_clean.startswith("---"):
                    desc = p_clean.replace("**", "").replace("\n", " ")
                    if len(desc) > 130:
                        desc = desc[:130] + "..."
                    break
            
            # 태그 추출
            m_tags = re.findall(r"#([a-zA-Z0-9가-힣]+)", content)
            tags = [f"#{t}" for t in m_tags[:5]]
            
            # 글자수
            char_count = len(content.replace(" ", "").replace("\n", ""))

            posts.append({
                "post_id": post_id,
                "date": post_id,           # 하위 호환용 (기존 링크 참조 유지)
                "date_only": date_only,
                "post_num": post_num,
                "category": category,
                "theme_name": theme_name,
                "title": title,
                "desc": desc,
                "tags": tags,
                "char_count": char_count,
                "rel_md": rel_md,
                "rel_html": rel_html,
                "has_html": os.path.exists(html_fpath)
            })
        except Exception as e:
            log(f"포스트 파싱 오류 {fname}: {e}")

    return posts

def update_naver_index_html(today_str, trends, posts):
    """blog/naver/index.html 대시보드 재생성"""
    index_path = os.path.join(NAVER_BLOG_DIR, "index.html")

    # 포스트 타임라인 HTML 조립
    post_cards_html = ""
    for p in posts:
        is_today = (p["date_only"] == today_str)
        today_class = " today" if is_today else ""
        
        # 뱃지 텍스트
        if p["post_num"] == 1:
            badge_suffix = " (오늘 · 실시간 1위)" if is_today else " (실시간 1위)"
        else:
            theme_label = f"테마: {p['theme_name']}" if p['theme_name'] else f"테마 #{p['post_num']}"
            badge_suffix = f" (오늘 · {theme_label})" if is_today else f" ({theme_label})"
            
        date_badge = f"📍 {p['date_only']}{badge_suffix}"
        
        cat_badge = f'<span style="font-size: 11px; background: #e8f9f0; color: #02b14f; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-left: 8px;">{p["category"].split("/")[0].strip()}</span>' if p.get("category") else ""
        
        tags_html = "".join([f'<span class="post-tag">{t}</span>' for t in p["tags"]])
        
        post_cards_html += f"""
            <article class="post-card{today_class}">
              <div class="post-card-date" style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                  <span>{date_badge}</span>
                  {cat_badge}
                </div>
                <span style="font-size: 11.5px; color: var(--text-muted); font-weight: 600;">#{p['post_num']}편</span>
              </div>
              <a href="{p['rel_html']}" class="post-card-title">
                {p['title']}
              </a>
              <p class="post-card-desc">
                {p['desc']}
              </p>
              <div class="post-card-tags">
                {tags_html}
              </div>
              <div class="post-card-footer">
                <div>작성 분량: 약 {p['char_count']:,}자 (공백 제외)</div>
                <div class="post-btn-group">
                  <a href="{p['rel_md']}" target="_blank" class="action-btn">📄 MD 원문</a>
                  <a href="{p['rel_html']}" class="action-btn action-btn-primary">👁️ 포스트 열기 & 복사</a>
                </div>
              </div>
            </article>
        """

    # 실시간 트렌드 Top 10 HTML 조립
    trends_html = ""
    for t in trends:
        safe_title = t["recommended_title"].replace("'", "\\'").replace('"', '&quot;')
        theme_badge_html = ""
        if t.get("theme"):
            theme_badge_html = f'<span class="trend-badge" style="background:#e8f9f0; color:#02b14f; font-weight:700; border:1px solid #c3eed6;">★ {t["theme"]["theme_name"]}</span>'

        trends_html += f"""
            <div class="trend-item">
              <div class="trend-rank">{t['rank']}</div>
              <div class="trend-content">
                <div class="trend-kw-row">
                  <span class="trend-kw">{t['keyword']}</span>
                  <span class="trend-badge">{t['badge']}</span>
                  {theme_badge_html}
                </div>
                <div class="trend-title-rec">
                  <strong>추천 제목:</strong> {t['recommended_title']}
                </div>
              </div>
              <button class="copy-title-btn" onclick="copyText('{safe_title}')">제목 복사</button>
            </div>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>네이버 블로그 일별 포스팅 워크스페이스 | AI Blog Notes</title>

  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />

  <style>
    :root {{
      --naver-green: #03c75a;
      --naver-green-dark: #02b14f;
      --naver-light: #e8f9f0;
      --naver-light-border: #c3eed6;
      --text-main: #191f28;
      --text-sub: #4e5968;
      --text-muted: #8b95a1;
      --bg: #f7f9fa;
      --card-bg: #ffffff;
      --border: #e5e8eb;
      --badge-trend: #ffefe5;
      --badge-trend-text: #ff5e00;
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
      max-width: 1080px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .brand-wrap {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .naver-badge {{
      background: var(--naver-green);
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
      gap: 10px;
    }}

    .header-link {{
      font-size: 13px;
      color: var(--text-sub);
      text-decoration: none;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      transition: all 0.15s;
    }}

    .header-link:hover {{
      background: var(--bg);
      color: var(--naver-green-dark);
      border-color: var(--naver-green);
    }}

    .container {{
      max-width: 1080px;
      margin: 28px auto 0;
      padding: 0 20px;
    }}

    .hero-banner {{
      background: linear-gradient(135deg, #03c75a 0%, #009e45 100%);
      color: #fff;
      padding: 32px 36px;
      border-radius: 16px;
      margin-bottom: 28px;
      box-shadow: 0 8px 24px rgba(3, 199, 90, 0.2);
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
      opacity: 0.92;
      max-width: 600px;
    }}

    .hero-stats {{
      display: flex;
      gap: 20px;
    }}

    .stat-box {{
      background: rgba(255, 255, 255, 0.18);
      backdrop-filter: blur(8px);
      padding: 12px 20px;
      border-radius: 12px;
      text-align: center;
      min-width: 100px;
    }}

    .stat-number {{
      font-size: 22px;
      font-weight: 800;
      display: block;
    }}

    .stat-label {{
      font-size: 12px;
      opacity: 0.85;
    }}

    .main-grid {{
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 24px;
    }}

    @media (max-width: 900px) {{
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
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .card-subtitle {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    .trend-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .trend-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px 14px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: var(--bg);
      transition: all 0.15s;
    }}

    .trend-item:hover {{
      border-color: var(--naver-green);
      background: #fff;
    }}

    .trend-rank {{
      font-size: 15px;
      font-weight: 800;
      color: var(--naver-green-dark);
      min-width: 24px;
      text-align: center;
      padding-top: 2px;
    }}

    .trend-content {{ flex: 1; }}

    .trend-kw-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }}

    .trend-kw {{
      font-size: 14.5px;
      font-weight: 700;
      color: var(--text-main);
    }}

    .trend-badge {{
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--badge-trend);
      color: var(--badge-trend-text);
      font-weight: 600;
    }}

    .trend-title-rec {{
      font-size: 13px;
      color: var(--text-sub);
      line-height: 1.45;
    }}

    .copy-title-btn {{
      font-size: 11px;
      padding: 4px 8px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text-sub);
      cursor: pointer;
    }}

    .copy-title-btn:hover {{
      border-color: var(--naver-green);
      color: var(--naver-green-dark);
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
      border-color: var(--naver-green);
      box-shadow: 0 4px 16px rgba(3, 199, 90, 0.12);
    }}

    .post-card.today::before {{
      content: "TODAY";
      position: absolute;
      top: -10px;
      right: 20px;
      background: var(--naver-green);
      color: #fff;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 10px;
    }}

    .post-card-date {{
      font-size: 12.5px;
      font-weight: 600;
      color: var(--naver-green-dark);
      margin-bottom: 6px;
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
      color: var(--naver-green-dark);
      text-decoration: underline;
    }}

    .post-card-desc {{
      font-size: 13.5px;
      color: var(--text-sub);
      line-height: 1.55;
      margin-bottom: 14px;
    }}

    .post-card-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 16px;
    }}

    .post-tag {{
      font-size: 11.5px;
      background: var(--bg);
      color: var(--text-muted);
      padding: 2px 8px;
      border-radius: 4px;
    }}

    .post-card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px dashed var(--border);
      padding-top: 12px;
      font-size: 12px;
      color: var(--text-muted);
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
    }}

    .action-btn:hover {{ background: var(--bg); }}

    .action-btn-primary {{
      background: var(--naver-green);
      color: #fff;
      border-color: var(--naver-green);
    }}

    .action-btn-primary:hover {{
      background: var(--naver-green-dark);
      color: #fff;
    }}

    .check-item {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      margin-bottom: 12px;
      font-size: 13px;
      color: var(--text-sub);
    }}

    .check-icon {{
      color: var(--naver-green-dark);
      font-weight: bold;
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
      border-color: var(--naver-green);
      color: var(--naver-green-dark);
      background: var(--naver-light);
    }}
    .page-btn.active {{
      background: var(--naver-green);
      color: #fff;
      border-color: var(--naver-green);
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
        <span class="naver-badge">NAVER BLOG</span>
        <div class="brand-title">품미인생의 블로그 작업실</div>
      </div>
      <div class="header-links">
        <a href="../../index.html" class="header-link">🏠 블로그 홈</a>
        <a href="../tistory/index.html" class="header-link" style="background: #fff7ed; color: #c2410c; border-color: #fed7aa; font-weight: 700;">🟠 티스토리 작업실</a>
        <a href="../wordpress/index.html" class="header-link" style="background: #f0f7fb; color: #0073aa; border-color: #bae6fd; font-weight: 700;">🔵 워드프레스 작업실</a>
        <a href="../../docs/index.html" class="header-link">📚 지침서 & 가이드 뷰어</a>
      </div>
    </div>
  </header>

  <div class="container">
    <section class="hero-banner">
      <div class="hero-text">
        <h1>🟢 품미인생(品味人生)의 네이버 블로그 작업실</h1>
        <p>통장은 든든하게, 입맛은 풍요롭게! 실시간 트렌드와 노후 자산관리, 맛있는 일상을 스마트에디터 ONE 서식으로 매일 완성합니다.</p>
        <div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
          <a href="https://datalab.naver.com/" target="_blank" rel="noopener noreferrer" style="background: #fff; color: var(--naver-green-dark); padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; text-decoration: none;">
            📊 네이버 데이터랩 (검색어 트렌드) ↗
          </a>
          <a href="https://creator-advisor.naver.com/" target="_blank" rel="noopener noreferrer" style="background: rgba(255,255,255,0.2); color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; text-decoration: none; border: 1px solid rgba(255,255,255,0.35);">
            📈 네이버 크리에이터 어드바이저 ↗
          </a>
          <a href="https://adpost.naver.com/" target="_blank" rel="noopener noreferrer" style="background: rgba(255,255,255,0.2); color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; text-decoration: none; border: 1px solid rgba(255,255,255,0.35);">
            💰 네이버 애드포스트 ↗
          </a>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span class="stat-number">{len(posts)} 편</span>
          <span class="stat-label">누적 발행 글</span>
        </div>
        <div class="stat-box">
          <span class="stat-number">10 개</span>
          <span class="stat-label">실시간 트렌드</span>
        </div>
      </div>
    </section>

    <div class="main-grid">
      <div class="left-col">
        <section class="card">
          <div class="card-header">
            <div class="card-title">
              📅 일별 포스팅 캘린더 / 목록
            </div>
            <div class="card-subtitle">총 {len(posts)}개의 일별 포스팅 작성됨</div>
          </div>
          <div class="post-timeline" id="naverPostList">
            {post_cards_html}
          </div>
          <div class="pagination-bar" id="naverPagination"></div>
        </section>

        <section class="card">
          <div class="card-header">
            <div class="card-title">
              🔥 네이버 블로그 제목 추천: 실시간 검색어 & 트렌드 Top 10
            </div>
            <div class="card-subtitle">{today_str} 자동 집계 기준</div>
          </div>
          <p style="font-size: 13.5px; color: var(--text-sub); margin-bottom: 16px;">
            현재 실시간으로 대중의 관심이 집중된 키워드를 시니어/은퇴자 및 정보성 네이버 블로그 스마트블록 노출에 최적화된 매력적인 제목으로 변환한 추천안입니다.
          </p>
          <div class="trend-list" id="trendList">
            {trends_html}
          </div>
        </section>
      </div>

      <div class="right-col">
        <section class="card" style="border: 2px solid var(--naver-green); background: #fdfefe;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
            <span style="background: var(--naver-green); color: #fff; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px;">MY BLOG</span>
            <div class="card-title" style="margin: 0; font-size: 15px;">품미인생 네이버 블로그</div>
          </div>
          <p style="font-size: 13px; color: var(--text-sub); line-height: 1.55; margin-bottom: 14px;">
            작업실에서 완성된 스마트에디터 서식을 복사한 뒤, 실제 운영 중인 내 네이버 블로그에 바로 새 글로 발행하세요.
          </p>
          <a href="https://blog.naver.com/ms7park" target="_blank" rel="noopener noreferrer" class="action-btn action-btn-primary" style="display: flex; align-items: center; justify-content: center; gap: 6px; text-decoration: none; padding: 10px; font-weight: 700; font-size: 13px;">
            <span>🌐 내 블로그 바로가기 (ms7park)</span>
            <span style="font-size: 12px;">↗</span>
          </a>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 14px;">
            ✅ 네이버 C-Rank & D.I.A 체크리스트
          </div>
          <div class="check-item"><span class="check-icon">✓</span><div><strong>제목 키워드 앞배치</strong>: 메인 키워드를 제목 앞쪽 15자 내에 자연스럽게 배치</div></div>
          <div class="check-item"><span class="check-icon">✓</span><div><strong>글자수 1,500~2,000자</strong>: 스마트블록 상위 노출 체류시간 확보</div></div>
          <div class="check-item"><span class="check-icon">✓</span><div><strong>소제목(H2/H3) 3~4개</strong>: 네이버 요약 봇 친화적 구조</div></div>
          <div class="check-item"><span class="check-icon">✓</span><div><strong>진솔한 경험담 1스푼</strong>: D.I.A 로직 가산점 핵심 요소</div></div>
          <div class="check-item"><span class="check-icon">✓</span><div><strong>이미지 4~6장 권장</strong>: 직접 촬영한 사진이나 캡처 권장</div></div>
        </section>

        <section class="card" style="border-left: 4px solid var(--naver-green); background: #fcfdfd;">
          <div class="card-title" style="color: var(--naver-green-dark); margin-bottom: 10px;">
            💡 스마트에디터 서식 복사 팁
          </div>
          <p style="font-size: 13px; color: var(--text-sub); line-height: 1.6;">
            네이버 블로그 에디터(SmartEditor ONE)는 마크다운(<code>**</code>, <code>###</code>)을 직접 해석하지 않는 위지윅 에디터입니다.<br><br>
            포스트 뷰어에서 <strong>[🟢 네이버 스마트에디터 서식 복사]</strong> 버튼을 누르면 <code>**</code> 기호 없이 <strong>진짜 굵은 글씨와 소제목</strong>으로 스마트에디터에 바로 붙여넣기됩니다.
          </p>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 14px;">
            ⚡ AI 원클릭 글쓰기 프롬프트
          </div>
          <div style="background: var(--naver-light); border: 1px solid var(--naver-light-border); border-radius: 8px; padding: 12px; font-size: 12.5px; color: #1f5135; margin-bottom: 10px;">
            "선택한 제목과 키워드로 50대 은퇴자의 경험이 담긴 친절한 네이버 블로그 초안 1,800자를 작성해줘."
          </div>
          <button class="action-btn" style="width: 100%; text-align: center;" onclick="copyText('선택한 제목과 키워드로 50대 은퇴자의 진솔한 경험이 담긴 친절하고 가독성 높은 네이버 블로그 포스팅 초안 1,800자를 작성해줘. 소제목 3개와 결론, 스마트블록 태그 10개를 포함해줘.')">
            프롬프트 복사하기
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
        toast.textContent = `✓ 클립보드에 복사되었습니다!`;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 2000);
      }});
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
      initPagination("naverPostList", "naverPagination", 5);
    }});
  </script>
</body>
</html>"""

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    log(f"✅ blog/naver/index.html 대시보드 갱신 완료 (총 {len(posts)}개 포스트)")

def update_portal_index_html(today_str, posts):
    """최상위 루트 index.html 포털의 '오늘자 글 보기' 링크 및 '최근 작성된 일별 블로그 포스팅' 목록 자동 갱신"""
    portal_path = os.path.join(BASE_DIR, "index.html")
    if not os.path.exists(portal_path):
        return

    try:
        with open(portal_path, "r", encoding="utf-8") as f:
            content = f.read()

        latest_post = posts[0] if posts else None
        latest_date = latest_post["date"] if latest_post else today_str
        latest_rel_html = latest_post.get("rel_html", f"posts/{today_str[:7].replace('-', '')}/{latest_date}.html") if latest_post else f"posts/{today_str[:7].replace('-', '')}/{today_str}.html"

        # 1. '오늘자 글 보기 & 서식 복사' 링크 최신화
        content = re.sub(
            r'<a href="blog/naver/posts/[0-9a-zA-Z/_\-]+\.html" class="p-btn p-btn-sub">\s*👁️ 오늘자 글 보기 & 서식 복사\s*</a>',
            f'<a href="blog/naver/{latest_rel_html}" class="p-btn p-btn-sub">\n            👁️ 오늘자 글 보기 & 서식 복사\n          </a>',
            content
        )

        # 2. 최근 작성된 일별 블로그 포스팅 섹션 갱신 (최근 8개)
        recent_rows_html = ""
        for p in posts[:8]:
            p_date_only = p.get("date_only", p["date"][:10])
            try:
                dt = datetime.strptime(p_date_only, "%Y-%m-%d")
                weekday = WEEKDAYS_KR[dt.weekday()]
                theme_tag = f" · {p['theme_name']}" if p.get("theme_name") else ""
                date_display = f"{p_date_only} ({weekday}{theme_tag})"
            except Exception:
                date_display = p["post_id"]

            p_rel = p.get('rel_html') or f"posts/{p['post_id']}.html"
            post_link = f"blog/naver/{p_rel}"
            recent_rows_html += f"""
      <div class="post-item-row">
        <div class="post-item-left">
          <span class="post-platform-tag tag-naver">네이버</span>
          <a href="{post_link}" class="post-item-title">
            {p['title']}
          </a>
        </div>
        <span class="post-item-date">{date_display}</span>
        <a href="{post_link}" class="post-item-btn">
          👁️ 포스트 열기 & 서식 복사
        </a>
      </div>"""

        # Section 2의 post-item-row 들을 마커 기준으로 안전하게 교체
        marker_pattern = r'(<!-- RECENT_POSTS_LIST_START -->)([\s\S]*?)(<!-- RECENT_POSTS_LIST_END -->)'
        m_marker = re.search(marker_pattern, content)
        if m_marker:
            content = content[:m_marker.start()] + f"<!-- RECENT_POSTS_LIST_START -->{recent_rows_html}\n      <!-- RECENT_POSTS_LIST_END -->" + content[m_marker.end():]
        else:
            # 마커가 없을 때 fallback
            section_pattern = r'(<!-- Section 2: Recent Posts Hub -->[\s\S]*?</div>\s*)([\s\S]*?)(</section>)'
            m = re.search(section_pattern, content)
            if m:
                content = content[:m.start(2)] + f"\n      <!-- RECENT_POSTS_LIST_START -->{recent_rows_html}\n      <!-- RECENT_POSTS_LIST_END -->\n    " + content[m.end(2):]

        with open(portal_path, "w", encoding="utf-8") as f:
            f.write(content)
        log("✅ 루트 index.html 포털 최근 포스팅 목록 동기화 완료")
    except Exception as e:
        log(f"⚠️ 루트 index.html 포털 동기화 오류: {e}")

def git_commit_and_push(today_str, title):
    """배치 생성 파일들을 Git에 자동 커밋하고 origin으로 푸시"""
    try:
        # 1. 상태 확인
        status_res = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
        if not status_res.stdout.strip():
            log("ℹ️ Git 변경 사항이 없어 커밋을 건너뜁니다.")
            return

        # 2. 관련 파일 staging
        add_res = subprocess.run(["git", "add", "."], cwd=BASE_DIR, capture_output=True, text=True)
        if add_res.returncode != 0:
            log(f"⚠️ git add 실패: {add_res.stderr.strip()}")
            return

        # 3. 커밋 메시지 구성 및 커밋
        clean_title = re.sub(r'[\r\n"\'`]', ' ', title).strip() if title else ""
        if len(clean_title) > 40:
            clean_title = clean_title[:40] + "..."
        commit_msg = f"feat(auto): {today_str} 네이버 블로그 포스팅 자동 생성"
        if clean_title:
            commit_msg += f" ({clean_title})"

        commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True, text=True)
        if commit_res.returncode != 0:
            log(f"⚠️ git commit 실패: {commit_res.stderr.strip()}")
            return
        log(f"✅ Git 커밋 완료: {commit_msg}")

        # 4. 현재 활성 브랜치 확인
        branch_res = subprocess.run(["git", "branch", "--show-current"], cwd=BASE_DIR, capture_output=True, text=True)
        current_branch = branch_res.stdout.strip() or "develop"

        # 5. 원격 푸시
        push_res = subprocess.run(["git", "push", "origin", current_branch], cwd=BASE_DIR, capture_output=True, text=True)
        if push_res.returncode == 0:
            log(f"🚀 Git 원격 저장소 푸시 완료 (origin/{current_branch})")
        else:
            log(f"⚠️ git push 실패: {push_res.stderr.strip()}")
    except Exception as e:
        log(f"⚠️ Git 자동 커밋 및 푸시 중 오류 발생: {e}")

def run_batch(target_date=None, force=False):
    """배치 메인 실행 함수"""
    # 동시 실행 방지 파일 락 (LaunchAgent + Cron 이중 구동 시 상호 배타 보장)
    lock_file_path = "/tmp/daily_naver_batch.lock"
    try:
        lock_file = open(lock_file_path, "w")
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError):
        log("ℹ️ 이미 다른 프로세스에서 일별 배치가 실행 중입니다. 중복 실행을 방지하고 종료합니다.")
        return

    now = datetime.now()
    if target_date:
        today_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        today_date = now

    today_str = today_date.strftime("%Y-%m-%d")
    weekday_str = WEEKDAYS_KR[today_date.weekday()]

    log(f"🚀 [배치 시작] 네이버 블로그 일별 자동화 배치 실행 (기준일: {today_str} {weekday_str}요일, force={force})")

    # force 모드일 경우 당일자 기존 추가 포스팅 파일 정리 (새로운 트렌드 결과에 맞춰 정확히 재작성)
    ym = today_str[:7].replace("-", "")
    target_ym_dir = os.path.join(POSTS_DIR, ym)
    if force and os.path.exists(target_ym_dir):
        for f in os.listdir(target_ym_dir):
            if f.startswith(f"{today_str}-") and (f.endswith(".md") or f.endswith(".html")):
                try:
                    os.remove(os.path.join(target_ym_dir, f))
                except OSError:
                    pass

    # 1. 실시간 트렌드 키워드 수집
    trends = fetch_trending_keywords()
    log(f"📊 실시간 트렌드 {len(trends)}개 수집 완료: 1위 [{trends[0]['keyword']}] - {trends[0]['recommended_title']}")

    # 2. 당일 메인 포스팅 생성 (실시간 검색어 1위)
    main_theme = match_blog_theme(trends[0]["keyword"], trends[0].get("news", ""))
    create_post(today_str, today_str, weekday_str, trends[0], theme_info=main_theme, post_num=1, force=force)

    # 3. 실시간 검색어 Top 10 중 블로그 테마와 연관된 키워드 추가 포스팅 생성
    theme_posts_count = 0
    for t in trends[1:]:
        theme_info = match_blog_theme(t["keyword"], t.get("news", ""))
        if theme_info:
            theme_posts_count += 1
            post_id = f"{today_str}-{theme_posts_count + 1}"
            log(f"🎯 블로그 테마 연관 키워드 발굴 (#{t['rank']}위 [{t['keyword']}] - 테마: {theme_info['theme_name']})")
            create_post(post_id, today_str, weekday_str, t, theme_info=theme_info, post_num=theme_posts_count + 1, force=force)

    log(f"📝 오늘 작성된 총 포스팅: 메인 1편 + 테마 연관 {theme_posts_count}편 = 총 {theme_posts_count + 1}편")

    # 4. 전체 포스트 스캔 및 블로그 대시보드 갱신
    posts = scan_all_posts()
    update_naver_index_html(today_str, trends, posts)

    # 5. 루트 index.html 멀티 블로그 포털 최근 포스트 갱신
    update_portal_index_html(today_str, posts)

    # 5-2. 티스토리 일별 자동화 배치 연동 실행 (Google Trends 상승 검색어 기반)
    tistory_script = os.path.join(BASE_DIR, "tools", "daily_tistory_batch.py")
    if os.path.exists(tistory_script):
        force_arg = " --force" if force else ""
        os.system(f"{sys.executable} {tistory_script} {today_str}{force_arg}")

    # 5-3. 워드프레스(WordPress) 코너스톤 SEO 작업실 배치 연동 실행
    wp_script = os.path.join(BASE_DIR, "tools", "daily_wordpress_batch.py")
    if os.path.exists(wp_script):
        os.system(f"{sys.executable} {wp_script} {today_str}")

    # 6. docs/index.html 전체 가이드 뷰어 동기화
    gen_script = os.path.join(BASE_DIR, "tools", "generate_html.py")
    if os.path.exists(gen_script):
        os.system(f"{sys.executable} {gen_script} > /dev/null 2>&1")
        log("✅ 전체 가이드 뷰어(docs/index.html) 동기화 완료")

    # 7. 변경 사항 Git 자동 커밋 및 원격 푸시
    latest_title = posts[0]["title"] if posts else trends[0]["recommended_title"]
    git_commit_and_push(today_str, latest_title)

    log(f"🎉 [배치 완료] {today_str} 네이버 블로그 일별 작업이 성공적으로 끝났습니다.\n")

if __name__ == "__main__":
    force_mode = "--force" in sys.argv
    date_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    t_date = date_args[0] if date_args else None
    run_batch(t_date, force=force_mode)


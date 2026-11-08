#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
daily_naver_tattoo_batch.py

타투이스트 전용 네이버 블로그 작업실(blog/naver-tatto/) 일일 포스팅 자동 생성 및 대시보드 갱신 배치 스크립트.

특징 및 원칙:
1. 스토리텔링 페르소나:
   - 현직 전문 타투이스트(INK/NOIR 아티스트)의 1인칭 전문 시점.
   - 철저한 1회용 멸균 위생 수칙, 1:1 맞춤 커스텀 도안 디자인, 섬세한 파인라인/블랙워크 지향.
   - 신뢰도 높은 포트폴리오 및 예약 상담 웹사이트(https://tattoostudio-flax.vercel.app/) 연계 카드 포함.
2. 타투 인기 검색 주제 풀 (15선):
   - 미니타투, 레터링, 부위별 통증, 비판텐 애프터케어, 도안 가격 및 견적 산정,
     반려동물 타투, 커버업, 쇄골/손목/발목 타투, 위생 체크리스트 등 상록수/트렌드 주제 내장.
3. 대시보드(blog/naver-tatto/index.html) 자동 갱신:
   - 작성일 오름차순 고유 번호(No. 1, No. 2, ...) 자동 넘버링.
   - 10건 페이징, 최근 30일 통계 위젯, 공식 사이트 링크 배너 완비.
"""

import os
import sys
import glob
import re
import html
from datetime import datetime, timedelta

# 기본 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TATTOO_BLOG_DIR = os.path.join(BASE_DIR, "blog", "naver-tatto")
TATTOO_POSTS_DIR = os.path.join(TATTOO_BLOG_DIR, "posts")
STUDIO_URL = "https://tattoostudio-flax.vercel.app/"
STUDIO_NAME = "INK/NOIR Tattoo Studio"
NAVER_BLOG_URL = "https://blog.naver.com/applepark03"
KAKAO_CHAT_URL = "https://open.kakao.com/o/spg2Vnvh"

# 엄선된 타투 인기 검색 주제 풀 (15선)
TATTOO_TOPIC_POOL = [
    {
        "id": "mini-tattoo-recommend",
        "category": "도안 추천",
        "badge": "미니타투",
        "keywords": ["미니타투", "손목타투", "발목타투", "쇄골타투", "첫타투"],
        "title": "2026 미니타투 도안 추천 BEST 5! 손목·발목·쇄골 첫 타투 위치별 통증과 관리 꿀팁",
        "subtitle": "작지만 온전한 나만의 감성을 담아내는 미니멀 커스텀 타투 가이드",
        "score": 96,
        "lead": "안녕하세요. 세상에 단 하나뿐인 온전한 나만의 이야기를 피부에 섬세하게 새겨드리는 타투이스트입니다. 첫 타투를 고민할 때 가장 부담 없이 접근할 수 있는 것이 바로 '미니 타투'인데요. 오늘은 실패 없는 미니타투 인기 위치와 도안 추천, 그리고 통증 관리 노하우를 솔직하게 정리해 드립니다.",
        "p1_title": "1. 첫 타투로 가장 사랑받는 BEST 3 포인트 부위",
        "p1_desc": "손목 안쪽, 쇄골 라인 끝자락, 복사뼈 뒷라인은 일상에서 살짝 드러나며 가장 자연스러운 감성을 주는 부위입니다. 노출 조절이 쉽고 단정한 옷차림에서도 감각적인 포인트가 되어줍니다.",
        "p2_title": "2. 유행을 타지 않는 5가지 감성 미니멀 모티브",
        "p2_desc": "한 줄 드로잉 라인워크, 미니멀 레터링, 탄생화·잎사귀 모티브, 밤하늘 천체(달과 별), 그리고 기하학적인 심볼은 10년이 지나도 질리지 않는 클래식한 매력을 가집니다.",
        "p3_title": "3. 부위별 통증 체감과 멸균 위생 체크포인트",
        "p3_desc": "미니타투는 시술 시간이 20~40분 내외로 매우 짧아 통증 부담이 적습니다. 다만 뼈와 밀접한 부위는 진동감이 느껴질 수 있으니 시술 전 컨디션 조절이 중요하며, 모든 과정에서 1회용 멸균 니들과 비닐 래핑이 적용되는지 반드시 확인해야 합니다."
    },
    {
        "id": "bepanthen-aftercare-guide",
        "category": "애프터케어",
        "badge": "타투관리",
        "keywords": ["비판텐", "타투관리", "타투연고", "애프터케어", "바세린"],
        "title": "타투 후 비판텐 연고 언제 어떻게 바를까? 시기별 애프터케어 완벽 가이드",
        "subtitle": "시술 후 딱지 앉기 전 첫 2주가 평생의 발색과 선명도를 결정합니다",
        "score": 98,
        "lead": "멋진 도안을 정교하게 작업받았더라도, 사후 관리를 소홀히 하면 잉크가 번지거나 색이 빠질 수 있습니다. 타투의 완성은 아티스트의 작업 50%와 손님의 애프터케어 50%로 완성된다고 해도 과언이 아닙니다. 비판텐 연고의 올바른 도포 요령과 시기별 관리법을 안내해 드립니다.",
        "p1_title": "1. 시술 당일 방수필름(더마이즈) 부착 및 세안 주의사항",
        "p1_desc": "시술 직후 부착해 드리는 의료용 방수필름은 진물과 잉크가 자연스럽게 피부를 보호하도록 돕습니다. 2~3일간 유지한 뒤 미온수로 조심스럽게 떼어내고, 무향 약산성 비누로 거품을 내어 가볍게 씻어내세요.",
        "p2_title": "2. 비판텐 연고는 '얇고 투명하게' 펴 바르는 것이 핵심",
        "p2_desc": "비판텐을 너무 두껍게 바르면 피부가 숨을 쉬지 못해 뾰루지나 모낭염이 생길 수 있습니다. 쌀알 크기만큼 덜어 윤기만 살짝 돌 정도로 아주 얇게 펴 바르고, 하루 2~3회 건조할 때마다 덧발라주세요.",
        "p3_title": "3. 시술 후 2주 동안 절대 피해야 할 금기사항 3가지",
        "p3_desc": "음주(염증 유발), 사우나 및 대중목욕탕 입욕(감염 및 색 빠짐 위험), 땀이 흠뻑 나는 격렬한 운동은 최소 2주간 반드시 피해야 합니다. 가려울 때는 긁지 말고 얼음팩을 수건에 감싸 냉찜질해 주세요."
    },
    {
        "id": "tattoo-pain-guide",
        "category": "통증 가이드",
        "badge": "통증비교",
        "keywords": ["타투통증", "타투아픔", "손목타투통증", "갈비뼈타투", "첫타투"],
        "title": "첫 타투 부위별 통증 솔직 비교 가이드! 손목, 팔, 쇄골, 발목 아픔 정도 총정리",
        "subtitle": "덜 아프게 잘 받는 프로 타투이스트의 사전 컨디션 조절 꿀팁",
        "score": 94,
        "lead": "첫 타투를 결심하고 방문하시는 고객님들께서 가장 많이 물어보시는 질문 1위는 단연 '얼마나 아픈가요?'입니다. 통증은 개인차가 있지만, 부위별 신경 분포와 피부 두께에 따라 확실한 차이가 있습니다. 솔직하고 투명하게 통증 등급을 비교해 드립니다.",
        "p1_title": "1. 통증 난이도 '하(★☆☆)': 팔 바깥쪽, 어깨, 종아리",
        "p1_desc": "근육과 지방층이 적당히 두텁고 신경이 덜 밀집된 부위입니다. 살짝 긁히는 듯한 따끔거림 수준으로, 휴대폰을 보거나 음악을 들으며 편안하게 시술받을 수 있는 가장 무난한 부위입니다.",
        "p2_title": "2. 통증 난이도 '중(★★☆)': 손목 안쪽, 발목, 쇄골 라인",
        "p2_desc": "피부가 다소 얇고 뼈와 가까워 기계의 진동이 뼈로 전해지는 느낌이 듭니다. 긴장하면 근육이 굳어 더 아프게 느껴질 수 있으므로, 천천히 복식호흡을 하며 릴랙스하는 것이 요령입니다.",
        "p3_title": "3. 통증 난이도 '상(★★★)': 갈비뼈(옆구리), 복사뼈, 목 뒤",
        "p3_desc": "피부가 매우 얇고 말초신경이 예민한 곳으로 인내심이 필요합니다. 다만 숙련된 아티스트의 일정한 텐션 조절과 신속하고 정밀한 핸들링으로 통증 시간을 최소화할 수 있습니다."
    },
    {
        "id": "lettering-quotes-recommend",
        "category": "도안 추천",
        "badge": "레터링",
        "keywords": ["레터링타투", "타투문구", "라틴어명언", "영어레터링", "감성타투"],
        "title": "영문 & 라틴어 레터링 타투 문구 추천! 의미 있고 촌스럽지 않은 인생 명언 BEST",
        "subtitle": "폰트 서체 선택부터 줄바꿈 비율까지 세련된 레터링 완성 공식",
        "score": 95,
        "lead": "평생 내 몸에 새겨지는 글귀는 볼 때마다 마음에 잔잔한 용기와 위로를 주는 특별한 힘이 있습니다. 하지만 너무 흔하거나 철자 오타가 나면 후회할 수 있죠. 뜻이 깊고 시각적으로도 아름다운 레터링 문구와 폰트 매칭 팁을 제안합니다.",
        "p1_title": "1. 시대를 초월해 사랑받는 라틴어 인생 명언 BEST",
        "p1_desc": "'Luce sicut stella(별처럼 밝게 빛나라)', 'Tempus edax rerum(세월은 모든 것을 삼킨다)', 'Amor fati(자신의 운명을 사랑하라)' 등 간결하면서도 묵직한 울림을 주는 라틴어 문구를 추천합니다.",
        "p2_title": "2. 자연스러운 감성의 모던 영문 프레이즈",
        "p2_desc": "'Still with you', 'In every wave', 'Present over perfect'처럼 너무 길지 않으면서 일상의 태도를 나타내는 영문 구절은 필기체(Script) 또는 산세리프(San-serif) 폰트와 찰떡궁합을 이룹니다.",
        "p3_title": "3. 폰트 선택과 신체 곡선에 맞춘 줄바꿈 밸런스",
        "p3_desc": "레터링은 글자 자체의 아름다움뿐 아니라 팔이나 쇄골의 굴곡을 따라 자연스럽게 흐르도록 배치(Flow)하는 것이 핵심입니다. 피부에 전사(스텐실) 후 거울로 서 있는 자세를 꼼꼼히 체크해 드립니다."
    },
    {
        "id": "tattoo-price-cost-guide",
        "category": "견적 가이드",
        "badge": "타투견적",
        "keywords": ["타투가격", "타투견적", "타투비용", "레터링가격", "도안의뢰"],
        "title": "타투 가격 책정 기준과 견적 산정 방식 완벽 정리! 크기·디테일·작업 시간별 비교",
        "subtitle": "바가지 쓰지 않고 합리적으로 1:1 커스텀 도안 의뢰하는 요령",
        "score": 93,
        "lead": "타투 샵마다 견적이 천차만별이라 처음 의뢰할 때 막막하셨던 경험이 있으실 겁니다. 타투 가격은 단순히 센티미터(cm) 크기뿐 아니라 도안의 정밀도, 명암 밀도, 소요 시간, 1회용 소모품 비용이 복합적으로 산정됩니다. 투명한 가격 책정 기준을 알려드립니다.",
        "p1_title": "1. 미니타투 & 심플 레터링의 기본 견적대",
        "p1_desc": "5cm 미만의 미니멀 심볼이나 짧은 1줄 레터링은 보통 기본 세팅비(멸균 위생 소모품 및 정품 잉크 세팅)를 포함해 5만~10만 원 안팎으로 책정됩니다.",
        "p2_title": "2. 커스텀 드로잉 및 디테일 밀도에 따른 시간당 견적",
        "p2_desc": "단순 기성 도안이 아닌 손님의 스토리를 바탕으로 직접 스케치하는 커스텀 도안이나, 촘촘한 도트 명암(Dot-work), 블랙앤그레이 쉐이딩이 들어갈수록 작업 소요 시간에 비례해 견적이 형성됩니다.",
        "p3_title": "3. 과도하게 저렴한 샵을 주의해야 하는 이유",
        "p3_desc": "비정상적으로 싼 가격의 작업은 검증되지 않은 저가 잉크, 바늘 재사용, 비위생적인 환경의 위험이 있습니다. 피부에 평생 남는 작업인 만큼 위생 설비와 포트폴리오의 선명도를 우선시해야 합니다."
    },
    {
        "id": "pre-tattoo-precautions",
        "category": "주의사항",
        "badge": "시술준비",
        "keywords": ["타투전날", "타투주의사항", "타투음주", "시술전준비", "컨디션관리"],
        "title": "타투 시술 전날 절대 하면 안 되는 주의사항 3가지! (음주·수면부족·아스피린 금지)",
        "subtitle": "출혈과 붓기를 줄이고 선명한 발색을 얻기 위한 필수 사전 준비",
        "score": 95,
        "lead": "타투 당일 최상의 잉크 발색과 적은 통증을 위해서는 시술 전날의 컨디션 관리가 무엇보다 중요합니다. 전날 과음을 하거나 잠을 설친 상태로 오시면 통증 민감도가 배로 뛰고 출혈이 늘어 도안 착색이 방해받을 수 있습니다. 전날 꼭 지켜주셔야 할 수칙을 정리했습니다.",
        "p1_title": "1. 전날 음주는 절대 금물! 혈액 순환 과다로 잉크 밀림 현상 발생",
        "p1_desc": "알코올은 혈액을 묽게 만들어 시술 중 피와 진물이 과도하게 분비되게 합니다. 이는 바늘이 들어갈 때 잉크를 밖으로 밀어내어 선이 흐려지고 착색률을 크게 떨어뜨립니다.",
        "p2_title": "2. 충분한 숙면(최소 7시간)과 든든한 식사 필수",
        "p2_desc": "빈속에 시술을 받으면 저혈당 쇼크나 어지럼증(바소베갈 반응)이 올 수 있습니다. 시술 1~2시간 전에 탄수화물이 포함된 든든한 식사를 챙겨 드시고, 편안한 복장으로 방문해 주세요.",
        "p3_title": "3. 시술 부위의 각질 케어와 수분 보습",
        "p3_desc": "시술 부위 피부가 극도로 건조하거나 각질이 두꺼우면 라인이 깔끔하게 나오지 않습니다. 2~3일 전부터 바디로션을 발라 피부 결을 촉촉하고 유연하게 정돈해 주시면 좋습니다."
    },
    {
        "id": "pet-portrait-tattoo",
        "category": "도안 추천",
        "badge": "반려동물",
        "keywords": ["반려동물타투", "강아지타투", "고양이타투", "라인타투", "추억타투"],
        "title": "반려동물(강아지·고양이) 감성 라인 타투 도안 제작기! 소중한 아이를 평생 간직하는 법",
        "subtitle": "실제 사진 기반 1:1 맞춤 커스텀 드로잉과 디테일 살리기",
        "score": 97,
        "lead": "세상에서 가장 순수한 눈망울로 나를 바라보던 우리 집 강아지, 고양이. 그 소중한 순간과 따스한 온기를 피부에 예술로 남기는 반려동물 타투는 작업할 때마다 가슴 뭉클한 감동이 있습니다. 실제 사진을 감각적인 도안으로 구현하는 과정을 소개합니다.",
        "p1_title": "1. 아이의 특징이 가장 잘 드러난 사진 선별하기",
        "p1_desc": "귓바퀴의 모양, 특유의 점이나 털 패턴, 반짝이는 눈동자의 하이라이트가 선명하게 찍힌 고화질 원본 사진이 좋습니다. 여러 장을 보내주시면 가장 구도가 좋은 컷을 골라 상담해 드립니다.",
        "p2_title": "2. 1:1 맞춤 커스텀: 파인라인 vs 블랙워크 명암",
        "p2_desc": "털의 결 하나하나를 얇은 바늘로 섬세하게 묘사하는 파인라인 스타일과, 이목구비만 뚜렷하게 따내는 미니멀 라인드로잉 중 손님의 취향과 시술 부위에 맞게 도안을 스케치합니다.",
        "p3_title": "3. 아이의 이름이나 생일 레터링과 조화로운 결합",
        "p3_desc": "반려동물 일러스트 하단에 작은 필기체로 아이의 이름이나 함께한 날짜를 자연스럽게 얹어주면 완성도 높은 나만의 감성 시그니처 바디아트가 탄생합니다."
    },
    {
        "id": "blackwork-vs-linework",
        "category": "스타일 비교",
        "badge": "장르비교",
        "keywords": ["블랙워크", "라인워크", "타투장르", "타투스타일", "타투추천"],
        "title": "블랙워크 vs 라인워크 타투 차이점 총정리! 나에게 딱 맞는 타투 스타일 고르는 법",
        "subtitle": "선의 굵기와 명암 표현의 미학, 도안 감성에 따른 장르 완벽 가이드",
        "score": 92,
        "lead": "타투 인스타그램이나 핀터레스트를 보다 보면 '라인워크(Linework)'와 '블랙워크(Blackwork)'라는 단어를 자주 마주칩니다. 흑백의 잉크를 사용한다는 공통점이 있지만, 표현 기법과 시각적 무게감에서 큰 차이가 있습니다. 두 장르의 매력을 비교 분석해 드립니다.",
        "p1_title": "1. 섬세함과 여백의 미, 라인워크(Linework)",
        "p1_desc": "다양한 두께의 바늘을 이용해 정교한 선(Line) 위주로 형태를 구성하는 장르입니다. 불필요한 명암을 배제하고 드로잉 느낌을 극대화하여 미니멀하고 단정한 감성을 선호하시는 분들께 적합합니다.",
        "p2_title": "2. 강렬한 대비와 묵직한 존재감, 블랙워크(Blackwork)",
        "p2_desc": "진한 블랙 잉크의 솔리드 면과 점묘(Dot), 거친 쉐이딩을 혼합해 깊이감과 입체감을 주는 장르입니다. 어두운 명암의 대비가 뚜렷해 남성적인 무드나 무게감 있는 아트워크에 제격입니다.",
        "p3_title": "3. 나에게 맞는 스타일 선택 기준",
        "p3_desc": "작고 은은하게 포인트를 주고 싶다면 파인 라인워크를, 팔이나 허벅지 등 넓은 면적에 뚜렷한 존재감을 새기고 싶다면 블랙워크를 추천해 드립니다."
    },
    {
        "id": "finger-hand-tattoo-longevity",
        "category": "부위별 가이드",
        "badge": "손가락타투",
        "keywords": ["손가락타투", "손등타투", "타투번짐", "타투색빠짐", "타투리터치"],
        "title": "손가락·손등 타투 번짐과 색 빠짐 왜 생길까? 시술 전 반드시 알아야 할 현실적인 유지력",
        "subtitle": "마찰과 물 접촉이 잦은 손 부위의 리터치 주기와 관리 노하우",
        "score": 94,
        "lead": "유명 연예인들의 손가락 마디나 손등 타투를 보고 매료되어 문의하시는 분들이 많습니다. 손은 매우 매력적인 위치이지만, 피부 특성상 착색 난이도가 가장 높은 부위이기도 합니다. 시술 전 반드시 짚고 넘어가야 할 손가락 타투의 현실을 가감 없이 밝혀드립니다.",
        "p1_title": "1. 손 부위 피부의 해부학적 특성과 잦은 각질 탈락",
        "p1_desc": "손바닥과 손가락 안쪽은 피부 턴오버(각질 탈락 주기)가 몸의 다른 부위보다 몇 배나 빠릅니다. 또한 피하지방이 얇아 잉크가 진피층에 안착하지 못하고 쉽게 날아갈 수 있습니다.",
        "p2_title": "2. 손가락 타투에서 흔히 발생하는 '번짐(Blowout)' 현상",
        "p2_desc": "손가락 피부는 얇기 때문에 바늘이 0.1mm만 깊게 들어가도 피하지방층으로 잉크가 번져 뿌옇게 퍼질 수 있습니다. 고도의 섬세한 압력 조절이 가능한 숙련된 아티스트에게 받아야 합니다.",
        "p3_title": "3. 1~2회 이상의 주기적인 리터치는 선택이 아닌 필수",
        "p3_desc": "손가락 타투는 첫 시술 후 일부 선이 끊기거나 연해질 확률이 80% 이상입니다. 발색이 완전히 자리 잡은 4~6주 뒤 리터치를 통해 선을 보강해 주어야 오래 선명함을 유지할 수 있습니다."
    },
    {
        "id": "coverup-tattoo-guide",
        "category": "커버업",
        "badge": "커버업",
        "keywords": ["커버업타투", "타투커버업", "흉터커버업", "망한타투", "타투수정"],
        "title": "옛날 타투 후회된다면? 커버업(Cover-up) 타투 성공 조건과 도안 상담 꿀팁",
        "subtitle": "바래진 잉크와 흉터를 새로운 예술 작품으로 탈바꿈하는 마법",
        "score": 96,
        "lead": "20대 초반에 멋모르고 받았던 유행 지난 문신이나, 수술 흉터, 색이 바랜 바디아트 때문에 스트레스를 받는 분들이 많습니다. 기존 타투를 완벽하게 가리면서도 아름다운 새 도안으로 덮는 '커버업'은 고난도의 설계가 필요합니다. 성공적인 커버업을 위한 핵심 조건을 알려드립니다.",
        "p1_title": "1. 커버업 도안은 기존 문신보다 1.5~2배 커져야 하는 이유",
        "p1_desc": "어두운 기존 잉크 흔적을 자연스럽게 분산시키고 시선을 분산(Distraction)시키기 위해서는 주변 여백을 활용해 도안의 스케일을 키워야 부자연스럽지 않습니다.",
        "p2_title": "2. 명암 대비와 텍스처를 활용한 은폐 테크닉",
        "p2_desc": "무작정 검은색으로 칠해버리면 답답한 덩어리가 됩니다. 깃털, 용의 비늘, 꽃잎의 겹침, 블랙워크 기하학 패턴 등 복잡한 결(Texture)을 지닌 도안을 활용해 기존 라인을 감쪽같이 숨깁니다.",
        "p3_title": "3. 레이저 토닝 1~2회 병행 시 드라마틱한 결과물",
        "p3_desc": "기존 타투가 너무 짙은 검은색이라면 레이저 시술을 1~2회 받아 살짝 연하게 뺀 뒤 커버업을 진행하면 도안 선택의 폭이 훨씬 넓어지고 환상적인 퀄리티가 나옵니다."
    },
    {
        "id": "clavicle-shoulder-tattoo",
        "category": "부위별 가이드",
        "badge": "쇄골타투",
        "keywords": ["쇄골타투", "어깨타투", "여성타투", "감성타투", "쇄골레터링"],
        "title": "쇄골 타투 & 어깨 라인 타투 도안 추천! 은은하고 매력적인 감성 포인트",
        "subtitle": "신체의 부드러운 곡선에 완벽히 녹아드는 감각적인 라인 배치 공식",
        "score": 93,
        "lead": "쇄골과 어깨선은 옷깃 사이로 은은하게 드러나며 가장 여성스럽고 세련된 분위기를 연출할 수 있는 명당 부위입니다. 신체의 유려한 곡선을 따라 흐르듯 디자인된 도안은 그 자체로 하나의 쥬얼리 같은 역할을 하죠. 쇄골과 어깨에 찰떡인 도안 디자인을 추천합니다.",
        "p1_title": "1. 쇄골 뼈 라인을 타고 흐르는 원라인 레터링",
        "p1_desc": "직선 형태가 아닌 쇄골 뼈의 완만한 호(Arc)를 따라 부드럽게 커브를 준 얇은 필기체 레터링은 목선과 어깨선을 훨씬 길고 날씬해 보이게 만들어 줍니다.",
        "p2_title": "2. 어깨 둥근 면을 감싸는 꽃과 덩굴 모티브",
        "p2_desc": "어깨 봉우리 쪽에서 쇄골 앞쪽으로 흘러내리는 들꽃, 은방울꽃, 올리브 잎사귀 디자인은 자연스러운 볼륨감과 함께 싱그러운 감성을 더해줍니다.",
        "p3_title": "3. 오프숄더와 셔츠 핏에 따른 위치 시뮬레이션",
        "p3_desc": "평소 즐겨 입으시는 옷 스타일(셔츠, 브이넥, 오프숄더)에 맞춰 일상에서 어느 정도 노출되길 원하는지 1:1 상담 시 스텐실을 부착하고 거울로 다각도 체크를 진행합니다."
    },
    {
        "id": "birth-flower-tattoo",
        "category": "도안 추천",
        "badge": "탄생화타투",
        "keywords": ["탄생화타투", "꽃타투", "감성타투", "파인라인", "의미있는타투"],
        "title": "탄생화 타투 & 꽃 모티브 감성 도안 추천! 꽃말과 함께 새기는 나만의 시그니처",
        "subtitle": "파인라인으로 여리여리하게 피어나는 나만의 수채화 감성 바디아트",
        "score": 95,
        "lead": "자신이 태어난 달과 날의 '탄생화'를 몸에 새기는 것은 나 자신을 사랑하고 아끼는 가장 아름다운 표현 중 하나입니다. 각 꽃이 품고 있는 고유한 꽃말까지 함께 어우러지면 세상에 하나뿐인 상징이 완성됩니다. 섬세한 파인라인 꽃 타투의 매력을 알아봅니다.",
        "p1_title": "1. 1년 12달 대표 탄생화와 아름다운 꽃말의 조화",
        "p1_desc": "1월 수선화(자존심), 4월 스위트피(우아한 추억), 6월 장미(사랑과 열정), 9월 다알리아(감사) 등 나에게 특별한 날의 꽃말을 도안 속에 녹여냅니다.",
        "p2_title": "2. 얇은 니들(Single Needle)로 살려내는 꽃잎의 투명함",
        "p2_desc": "두꺼운 윤곽선 대신 0.25mm 초미세 바늘을 사용해 바람에 흩날리는 듯한 꽃잎의 얇은 결을 섬세하게 표현하여 여리여리한 수채화 같은 느낌을 연출합니다.",
        "p3_title": "3. 가족, 연인, 소중한 사람의 탄생화 부케 조합",
        "p3_desc": "나 혼자의 탄생화뿐 아니라 부모님, 자녀, 배우자의 탄생화를 하나의 조화로운 작은 부케 형태로 엮어 디자인하는 커스텀 패밀리 도안도 큰 인기를 얻고 있습니다."
    },
    {
        "id": "tattoo-touchup-retouch",
        "category": "애프터케어",
        "badge": "리터치",
        "keywords": ["타투리터치", "타투보수", "타투색빠짐", "리터치시기", "착색관리"],
        "title": "타투 리터치는 언제, 왜 받아야 할까? 첫 시술 후 4~6주 차 리터치 시기 총정리",
        "subtitle": "완벽한 착색과 도안의 디테일 완성도를 끌어올리는 필수 코스",
        "score": 93,
        "lead": "타투 시술 후 딱지가 떨어지고 나면 어떤 부위는 선이 살짝 옅어지거나 미세하게 끊겨 보이는 경우가 있습니다. 이는 피부의 자연스러운 재생 과정에서 생기는 정상적인 현상입니다. 이때 필요한 것이 바로 '리터치(Retouch)'입니다. 리터치의 중요성과 적절한 시기를 짚어드립니다.",
        "p1_title": "1. 리터치가 필요한 이유: 피부 재생과 잉크 안착의 차이",
        "p1_desc": "사람마다 피부의 유분기, 두께, 면역 반응이 달라 잉크의 흡수율에 미세한 차이가 납니다. 특히 관절 부위나 움직임이 많은 곳은 첫 시술 후 5~10% 정도의 색 빠짐이 발생할 수 있습니다.",
        "p2_title": "2. 가장 이상적인 리터치 방문 시기: 4주~8주 사이",
        "p2_desc": "겉 피부(표피)가 아문 것처럼 보여도 속 피부(진피)까지 완전히 안정화되는 데는 최소 4주가 걸립니다. 진피가 완전히 회복되기 전에 바늘을 대면 피부 손상이 오므로 4~8주 사이가 최적기입니다.",
        "p3_title": "3. 리터치 시술 시 보완되는 디테일 요소들",
        "p3_desc": "끊어진 라인의 연결, 옅어진 쉐이딩 명암의 보강, 테두리의 날카로움 복원 등 전체적인 완성도를 100%로 끌어올리는 마무리 작업이 진행됩니다."
    },
    {
        "id": "tattoo-studio-hygiene-guide",
        "category": "위생 가이드",
        "badge": "안전위생",
        "keywords": ["타투위생", "타투샵추천", "멸균바늘", "타투부작용", "안전한타투"],
        "title": "타투이스트가 알려주는 타투 샵 위생 체크리스트! 안전하고 깨끗한 스튜디오 구별법",
        "subtitle": "멸균 1회용 니들, 교차오염 방지 래핑, 정품 인증 잉크 확인 필수",
        "score": 97,
        "lead": "피부에 직접 잉크를 주입하는 바디아트는 미적인 디자인만큼이나 '위생과 안전'이 생명입니다. 청결하지 못한 작업 환경은 세균 감염이나 염증의 주원인이 될 수 있죠. 손님의 입장에서 작업실에 들어섰을 때 반드시 눈으로 확인해야 할 위생 4대 수칙을 공개합니다.",
        "p1_title": "1. 1회용 멸균 니들 카트리지의 눈앞 개봉 여부",
        "p1_desc": "모든 바늘은 EO가스 멸균 처리된 밀봉 팩에 담겨 있어야 하며, 반드시 고객님이 보는 눈앞에서 즉석으로 개봉하여 머신에 결합해야 안전합니다. 재사용은 절대 있을 수 없습니다.",
        "p2_title": "2. 교차 오염을 완벽 차단하는 비닐 래핑(Barrier Film)",
        "p2_desc": "시술 베드, 베개, 머신 그립, 클립코드, 전원 공급기 등 작업자의 손이나 신체가 닿는 모든 장비는 1회용 위생 랩과 커버로 꼼꼼하게 감싸져 있어야 교차 감염을 막을 수 있습니다.",
        "p3_title": "3. 의료용 알코올 소독 및 글로벌 안전 인증 정품 잉크 사용",
        "p3_desc": "피부 소독은 물론 시술 전후 알코올 스왑 소독, 그리고 중금속 및 유해 물질 검사를 통과한 정품 비건 잉크(Dynamic, Kuro Sumi 등)를 사용하는지 확인하는 것이 현명합니다."
    },
    {
        "id": "ankle-bone-tattoo-guide",
        "category": "부위별 가이드",
        "badge": "발목타투",
        "keywords": ["발목타투", "복사뼈타투", "감성타투", "미니타투", "스니커즈포인트"],
        "title": "발목 & 복사뼈 타투 도안과 통증 가이드! 슬랙스·스니커즈에 살짝 드러나는 멋진 포인트",
        "subtitle": "뼈에 가까운 부위의 시술 감각과 양말 마찰 방지 회복 요령",
        "score": 93,
        "lead": "슬랙스를 롤업하거나 로우탑 스니커즈를 신었을 때 복사뼈 주변으로 살짝 엿보이는 타투는 무심한 듯 시크한 매력을 뿜어냅니다. 남녀 모두에게 인기가 높은 발목 타투의 특징과 통증, 그리고 양말 마찰을 피하는 관리법을 안내해 드립니다.",
        "p1_title": "1. 복사뼈 라인을 감싸는 미니멀 도안 추천",
        "p1_desc": "복사뼈 둥근 뼈를 살짝 비껴가는 나침반, 달의 주기, 파도 라인, 심플한 레터링 밴드는 발목의 가늘고 긴 라인을 돋보이게 해주는 최고의 디자인입니다.",
        "p2_title": "2. 뼈와 밀접한 부위의 찌릿한 진동 통증",
        "p2_desc": "복사뼈 바로 위는 뼈막과 신경이 가까워 바늘의 진동이 뼈 전체로 울리는 듯한 독특한 감각이 있습니다. 크기가 작다면 15~30분이면 충분히 마무리되므로 크게 겁먹으실 필요는 없습니다.",
        "p3_title": "3. 회복기 동안 조이는 양말과 신발 마찰 주의",
        "p3_desc": "시술 후 2주 동안은 밴딩이 짱짱한 스포츠 양말이나 발목을 조이는 부츠는 피하고, 부드러운 면양말을 헐렁하게 착용하여 딱지가 쓸리지 않도록 보호해야 합니다."
    }
]


def generate_post_markdown(topic_data, post_no, date_str):
    """타투 전문 포스팅 마크다운 생성"""
    post_date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")
    
    md_content = f"""# {topic_data['title']}

> **INK/NOIR Tattoo Studio | 현직 타투이스트가 전하는 바디아트 가이드**  
> **발행일**: {post_date_formatted} | **카테고리**: {topic_data['category']} | **글 번호**: No. {post_no}  
> **핵심 키워드**: {', '.join(topic_data['keywords'])}

---

## 🎨 아티스트의 여는 글

{topic_data['lead']}

단순한 유행을 좇기보다는, 고객님 한 분 한 분의 소중한 추억과 삶의 가치관을 충분한 대화를 통해 1:1 맞춤 커스텀 디자인으로 빚어내는 것이 제 작업의 가장 큰 보람입니다.

---

## 💡 {topic_data['p1_title']}

{topic_data['p1_desc']}

작업 전 충분한 시각 자료와 신체 비율 시뮬레이션을 통해 가장 안정적이고 세련된 위치를 함께 찾아갑니다.

---

## 🔍 {topic_data['p2_title']}

{topic_data['p2_desc']}

모든 도안은 기성 핀터레스트 이미지를 그대로 복제하지 않고, 고객님의 개성과 감성에 어우러지도록 디테일한 선의 굵기와 음영 톤을 섬세하게 재해석합니다.

---

## 🛡️ {topic_data['p3_title']}

{topic_data['p3_desc']}

---

## 📋 프로 타투이스트의 1:1 체크리스트

| 점검 항목 | 상세 체크 포인트 | 권장 수칙 |
| :--- | :--- | :--- |
| **위생 환경** | 1회용 멸균 니들 & 랩핑 소독 | 눈앞 개봉 및 시술 후 즉시 폐기 |
| **도안 맞춤** | 1:1 프라이빗 커스텀 상담 | 전사 스텐실 부착 후 자세별 다각도 확인 |
| **사후 케어** | 방수필름 & 비판텐 도포 주기 | 시술 2주간 음주·사우나 금지 및 얇게 도포 |
| **리터치** | 착색 안정화 후 디테일 보강 | 첫 시술 후 4~8주 차에 최적 진행 |

---

## 💬 자주 묻는 질문 (Q&A)

**Q. 첫 타투인데 혼자 방문하기 망설여져요. 친구와 함께 와도 되나요?**  
A. 편안한 마음으로 1:1 상담을 받으실 수 있도록 동반 1인까지 편안한 대기 공간을 제공합니다. 다만 집중도 높은 멸균 작업을 위해 실제 시술 구역에는 작업자와 고객님만 입장합니다.

**Q. 도안 제작 상담은 어떻게 진행되나요?**  
A. 원하시는 느낌의 참고 사진이나 생각하고 계신 문구, 상징하고 싶은 키워드를 전달해 주시면 1차 드로잉 시안을 제작하여 피드백을 주고받으며 완성해 나갑니다.

---

## 🔗 INK/NOIR 공식 스튜디오 안내 및 예약

평생 간직할 나만의 소중한 예술, 타투이스트와 함께 가장 안전하고 아름답게 완성해 보세요.

- **💬 카카오톡 1:1 상담**: [{KAKAO_CHAT_URL}]({KAKAO_CHAT_URL}) (견적 및 도안 실시간 문의)
- **🟢 네이버 공식 블로그**: [{NAVER_BLOG_URL}]({NAVER_BLOG_URL}) (스튜디오 일상 및 포스팅)
- **🌐 공식 포트폴리오 웹사이트**: [{STUDIO_NAME}]({STUDIO_URL})
- **작업 원칙**: 100% 예약제 프라이빗 세션 / 철저한 1회용 멸균 위생 준수 / 1:1 커스텀 디자인
"""
    return md_content


def generate_post_html(topic_data, post_no, date_str, md_path_relative):
    """네이버 친화적인 고품질 타투 포스팅 HTML 생성"""
    post_date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")
    keywords_tags = "".join([f'<span class="tag">#{kw}</span>' for kw in topic_data['keywords']])
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(topic_data['title'])} | {STUDIO_NAME}</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <style>
    :root {{
      --primary: #18181b;
      --primary-accent: #6366f1;
      --primary-light: #f4f4f5;
      --tattoo-gold: #d97706;
      --text-main: #18181b;
      --text-sub: #52525b;
      --text-muted: #a1a1aa;
      --bg: #fafafa;
      --card-bg: #ffffff;
      --border: #e4e4e7;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.75;
      padding-bottom: 80px;
    }}
    .header {{
      background: #09090b;
      color: #fafafa;
      border-bottom: 1px solid #27272a;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-inner {{
      max-width: 860px;
      margin: 0 auto;
      padding: 14px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .brand-wrap {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .brand-badge {{
      background: #fafafa;
      color: #09090b;
      font-size: 11px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }}
    .brand-title {{
      font-size: 16px;
      font-weight: 700;
      color: #fafafa;
      text-decoration: none;
    }}
    .header-link {{
      font-size: 13px;
      color: #a1a1aa;
      text-decoration: none;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid #3f3f46;
      transition: all 0.15s;
    }}
    .header-link:hover {{
      color: #fff;
      border-color: #71717a;
      background: #27272a;
    }}
    .container {{
      max-width: 860px;
      margin: 32px auto 0;
      padding: 0 20px;
    }}
    .post-header {{
      background: var(--card-bg);
      border-radius: 16px;
      border: 1px solid var(--border);
      padding: 36px 32px;
      margin-bottom: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .post-meta {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }}
    .post-no-badge {{
      background: #09090b;
      color: #fff;
      font-size: 12px;
      font-weight: 800;
      padding: 3px 9px;
      border-radius: 6px;
    }}
    .category-badge {{
      background: var(--primary-light);
      color: var(--primary);
      font-size: 12px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 6px;
    }}
    .date-text {{
      font-size: 13px;
      color: var(--text-muted);
    }}
    .post-title {{
      font-size: 26px;
      font-weight: 800;
      line-height: 1.35;
      margin-bottom: 12px;
      color: #09090b;
      letter-spacing: -0.5px;
    }}
    .post-subtitle {{
      font-size: 15px;
      color: var(--text-sub);
      margin-bottom: 18px;
    }}
    .tags-wrap {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .tag {{
      font-size: 12px;
      color: var(--primary-accent);
      background: #eef2ff;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 600;
    }}
    .post-body {{
      background: var(--card-bg);
      border-radius: 16px;
      border: 1px solid var(--border);
      padding: 40px 32px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .lead-box {{
      background: #f8fafc;
      border-left: 4px solid #09090b;
      padding: 20px 24px;
      border-radius: 0 12px 12px 0;
      margin-bottom: 36px;
      font-size: 15.5px;
      color: #334155;
      line-height: 1.8;
    }}
    .section-title {{
      font-size: 20px;
      font-weight: 800;
      color: #09090b;
      margin: 40px 0 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid #f4f4f5;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .section-desc {{
      font-size: 15px;
      color: var(--text-sub);
      line-height: 1.85;
      margin-bottom: 24px;
    }}
    .table-wrap {{
      overflow-x: auto;
      margin: 28px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th {{
      background: #f4f4f5;
      color: #18181b;
      font-weight: 700;
      padding: 12px 16px;
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      text-align: left;
    }}
    td {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
      color: var(--text-sub);
    }}
    .qa-card {{
      background: #fafafa;
      border-radius: 10px;
      padding: 18px 20px;
      margin-bottom: 14px;
      border: 1px solid var(--border);
    }}
    .qa-q {{
      font-size: 15px;
      font-weight: 700;
      color: #09090b;
      margin-bottom: 8px;
    }}
    .qa-a {{
      font-size: 14px;
      color: var(--text-sub);
      line-height: 1.7;
    }}
    .studio-cta-card {{
      background: linear-gradient(135deg, #09090b 0%, #18181b 100%);
      color: #fff;
      border-radius: 14px;
      padding: 28px 24px;
      margin-top: 48px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      align-items: center;
      text-align: center;
    }}
    .studio-cta-badge {{
      background: rgba(255,255,255,0.15);
      color: #fafafa;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 20px;
      letter-spacing: 0.5px;
    }}
    .studio-cta-title {{
      font-size: 20px;
      font-weight: 800;
      color: #fff;
    }}
    .studio-cta-desc {{
      font-size: 14px;
      color: #d4d4d8;
      max-width: 580px;
      line-height: 1.6;
    }}
    .studio-cta-btn-group {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: center;
    }}
    .studio-cta-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #fff;
      color: #09090b;
      font-size: 13.5px;
      font-weight: 700;
      padding: 10px 22px;
      border-radius: 24px;
      text-decoration: none;
      transition: all 0.2s;
    }}
    .studio-cta-btn:hover {{
      transform: translateY(-2px);
      background: #f4f4f5;
    }}
    .studio-cta-btn-kakao {{
      background: #fee500;
      color: #191919;
      font-weight: 800;
    }}
    .studio-cta-btn-kakao:hover {{
      background: #fada0a;
    }}
    .studio-cta-btn-naver {{
      background: #03c75a;
      color: #fff;
      font-weight: 700;
    }}
    .studio-cta-btn-naver:hover {{
      background: #02b14f;
    }}
    .nav-bottom {{
      display: flex;
      justify-content: space-between;
      margin-top: 24px;
    }}
    .btn-outline {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 10px 18px;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-main);
      text-decoration: none;
      font-size: 13.5px;
      font-weight: 600;
      transition: all 0.15s;
    }}
    .btn-outline:hover {{
      background: var(--bg);
      border-color: #a1a1aa;
    }}
  </style>
</head>
<body>

  <header class="header">
    <div class="header-inner">
      <div class="brand-wrap">
        <span class="brand-badge">INK/NOIR</span>
        <a href="../../index.html" class="brand-title">타투 아티스트 블로그 작업실</a>
      </div>
      <div>
        <a href="../../index.html" class="header-link">목록으로</a>
      </div>
    </div>
  </header>

  <main class="container">
    <article class="post-header">
      <div class="post-meta">
        <span class="post-no-badge">No. {post_no}</span>
        <span class="category-badge">{html.escape(topic_data['category'])}</span>
        <span class="date-text">📍 {post_date_formatted}</span>
      </div>
      <h1 class="post-title">{html.escape(topic_data['title'])}</h1>
      <p class="post-subtitle">{html.escape(topic_data['subtitle'])}</p>
      <div class="tags-wrap">
        {keywords_tags}
      </div>
    </article>

    <div class="post-body">
      <div class="lead-box">
        <strong>🎨 아티스트의 여는 글</strong><br><br>
        {html.escape(topic_data['lead'])}
      </div>

      <h2 class="section-title">{html.escape(topic_data['p1_title'])}</h2>
      <p class="section-desc">{html.escape(topic_data['p1_desc'])}</p>

      <h2 class="section-title">{html.escape(topic_data['p2_title'])}</h2>
      <p class="section-desc">{html.escape(topic_data['p2_desc'])}</p>

      <h2 class="section-title">{html.escape(topic_data['p3_title'])}</h2>
      <p class="section-desc">{html.escape(topic_data['p3_desc'])}</p>

      <h2 class="section-title">📋 프로 타투이스트의 1:1 체크리스트</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>점검 항목</th>
              <th>상세 체크 포인트</th>
              <th>권장 수칙</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>위생 환경</strong></td>
              <td>1회용 멸균 니들 & 랩핑 소독</td>
              <td>눈앞 개봉 및 시술 후 즉시 폐기</td>
            </tr>
            <tr>
              <td><strong>도안 맞춤</strong></td>
              <td>1:1 프라이빗 커스텀 상담</td>
              <td>전사 스텐실 부착 후 자세별 다각도 확인</td>
            </tr>
            <tr>
              <td><strong>사후 케어</strong></td>
              <td>방수필름 & 비판텐 도포 주기</td>
              <td>시술 2주간 음주·사우나 금지 및 얇게 도포</td>
            </tr>
            <tr>
              <td><strong>리터치</strong></td>
              <td>착색 안정화 후 디테일 보강</td>
              <td>첫 시술 후 4~8주 차에 최적 진행</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 class="section-title">💬 자주 묻는 질문 (Q&A)</h2>
      <div class="qa-card">
        <div class="qa-q">Q. 첫 타투인데 혼자 방문하기 망설여져요. 친구와 함께 와도 되나요?</div>
        <div class="qa-a">A. 편안한 마음으로 1:1 상담을 받으실 수 있도록 동반 1인까지 편안한 대기 공간을 제공합니다. 다만 집중도 높은 멸균 작업을 위해 실제 시술 구역에는 작업자와 고객님만 입장합니다.</div>
      </div>
      <div class="qa-card">
        <div class="qa-q">Q. 도안 제작 상담은 어떻게 진행되나요?</div>
        <div class="qa-a">A. 원하시는 느낌의 참고 사진이나 생각하고 계신 문구, 상징하고 싶은 키워드를 전달해 주시면 1차 드로잉 시안을 제작하여 피드백을 주고받으며 완성해 나갑니다.</div>
      </div>

      <div class="studio-cta-card">
        <span class="studio-cta-badge">{STUDIO_NAME} OFFICIAL</span>
        <h3 class="studio-cta-title">세상에 단 하나뿐인 나만의 바디아트를 완성하세요</h3>
        <p class="studio-cta-desc">
          공장형 도안이 아닌 1:1 맞춤 커스텀 디자인과 철저한 1회용 멸균 위생으로 안전하고 품격 있는 타투를 약속드립니다.<br>
          도안 상담 및 견적 문의는 카카오톡 오픈채팅으로 편하게 남겨주시면 친절히 안내해 드립니다.
        </p>
        <div class="studio-cta-btn-group">
          <a href="{KAKAO_CHAT_URL}" target="_blank" rel="noopener noreferrer" class="studio-cta-btn studio-cta-btn-kakao">
            💬 카카오톡 1:1 오픈채팅 문의 ↗
          </a>
          <a href="{STUDIO_URL}" target="_blank" rel="noopener noreferrer" class="studio-cta-btn">
            🌐 포트폴리오 웹사이트 ↗
          </a>
          <a href="{NAVER_BLOG_URL}" target="_blank" rel="noopener noreferrer" class="studio-cta-btn studio-cta-btn-naver">
            🟢 공식 네이버 블로그 ↗
          </a>
        </div>
      </div>
    </div>

    <div class="nav-bottom">
      <a href="../../index.html" class="btn-outline">← 전체 포스팅 목록</a>
      <a href="{md_path_relative}" class="btn-outline" download>📥 마크다운(.md) 다운로드</a>
    </div>
  </main>

</body>
</html>
"""
    return html_content


def scan_existing_posts():
    """기존 naver-tatto 포스트 목록 스캔 및 정렬 (날짜 오름차순)"""
    files = glob.glob(os.path.join(TATTOO_POSTS_DIR, "*", "*.html"))
    posts = []
    
    for fpath in files:
        fname = os.path.basename(fpath)
        # 2026-11-09.html 또는 2026-11-09-2.html
        m = re.match(r"^(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.html$", fname)
        if not m:
            continue
        date_str = m.group(1)
        sub_idx = int(m.group(2)) if m.group(2) else 1
        
        # 파일에서 제목과 메타정보 추출
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            title_m = re.search(r'<h1 class="post-title">(.*?)</h1>', content)
            title = title_m.group(1) if title_m else fname
            
            category_m = re.search(r'<span class="category-badge">(.*?)</span>', content)
            category = category_m.group(1) if category_m else "타투 가이드"
            
            rel_path = os.path.relpath(fpath, TATTOO_BLOG_DIR)
        except Exception:
            title = fname
            category = "타투"
            rel_path = os.path.relpath(fpath, TATTOO_BLOG_DIR)
            
        posts.append({
            "date": date_str,
            "sub_idx": sub_idx,
            "title": html.unescape(title),
            "category": html.unescape(category),
            "html_path": rel_path,
            "full_path": fpath
        })
        
    # 날짜 오름차순, sub_idx 오름차순 정렬 (고유 글 번호 No. 1, 2, 3... 부여용)
    posts.sort(key=lambda x: (x["date"], x["sub_idx"]))
    for idx, p in enumerate(posts, 1):
        p["post_no"] = idx
        
    return posts


def rebuild_index(posts, today_str):
    """blog/naver-tatto/index.html 대시보드 재생성"""
    # 글 목록 표시용 (최신순 내림차순)
    posts_desc = sorted(posts, key=lambda x: (x["date"], x["sub_idx"]), reverse=True)
    total_posts = len(posts_desc)
    
    # 최근 30일 통계 계산
    today_dt = datetime.strptime(today_str, "%Y-%m-%d")
    date_counts = {}
    for i in range(29, -1, -1):
        d_str = (today_dt - timedelta(days=i)).strftime("%Y-%m-%d")
        date_counts[d_str] = 0
        
    for p in posts:
        if p["date"] in date_counts:
            date_counts[p["date"]] += 1
            
    recent_30_sum = sum(date_counts.values())
    
    # 30일 위젯 바 생성
    stat_bars_html = []
    for d_str, cnt in date_counts.items():
        is_today = (d_str == today_str)
        height_px = min(60, cnt * 28 + 6) if cnt > 0 else 6
        bg_color = "#6366f1" if is_today else ("#18181b" if cnt > 0 else "#e4e4e7")
        d_short = d_str[5:]
        bar_html = f"""
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 16px;">
          <span style="font-size: 10px; font-weight: 700; color: {'#6366f1' if is_today else '#71717a'};">{cnt if cnt > 0 else ''}</span>
          <div style="width: 100%; max-width: 18px; height: {height_px}px; background: {bg_color}; border-radius: 4px 4px 0 0;" title="{d_str}: {cnt}건"></div>
          <span style="font-size: 9px; color: {'#6366f1' if is_today else '#a1a1aa'}; writing-mode: vertical-rl; transform: rotate(180deg); margin-top: 2px;">{d_short}</span>
        </div>
        """
        stat_bars_html.append(bar_html)
        
    stat_bars_rendered = "".join(stat_bars_html)
    
    # 포스트 카드 렌더링
    cards_html = []
    for p in posts_desc:
        is_today = (p["date"] == today_str)
        today_badge = '<span style="font-size: 11px; background: #eef2ff; color: #4f46e5; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-left: 6px;">오늘</span>' if is_today else ''
        card = f"""
        <article class="post-card {'today' if is_today else ''}">
          <div class="post-card-date">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="post-no">No. {p['post_no']}</span>
              <span>📍 {p['date']} ({p['category']})</span>
              {today_badge}
            </div>
            <span style="font-size: 12px; color: #a1a1aa; font-weight: 600;">#{p['sub_idx']}편</span>
          </div>
          <a href="{p['html_path']}" class="post-card-title">
            {html.escape(p['title'])}
          </a>
        </article>
        """
        cards_html.append(card)
        
    cards_rendered = "\n".join(cards_html)
    
    index_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>타투이스트 네이버 블로그 작업실 | {STUDIO_NAME}</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <style>
    :root {{
      --primary: #09090b;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --text-main: #0f172a;
      --text-sub: #475569;
      --text-muted: #94a3b8;
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
      background: #09090b;
      border-bottom: 1px solid #27272a;
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
    .brand-badge {{
      background: #ffffff;
      color: #09090b;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
      letter-spacing: 0.5px;
    }}
    .brand-title {{
      font-size: 18px;
      font-weight: 800;
      color: #fafafa;
    }}
    .header-link {{
      font-size: 13px;
      color: #a1a1aa;
      text-decoration: none;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid #3f3f46;
      transition: all 0.15s;
    }}
    .header-link:hover {{
      background: #27272a;
      color: #fff;
    }}
    .container {{
      max-width: 1080px;
      margin: 28px auto 0;
      padding: 0 20px;
    }}
    .hero-banner {{
      background: linear-gradient(135deg, #09090b 0%, #1e1b4b 100%);
      color: #fff;
      border-radius: 16px;
      padding: 32px 28px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    .hero-text h1 {{
      font-size: 24px;
      font-weight: 800;
      margin-bottom: 8px;
    }}
    .hero-text p {{
      font-size: 14px;
      color: #cbd5e1;
      max-width: 620px;
      line-height: 1.6;
    }}
    .hero-actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .btn-site {{
      background: #ffffff;
      color: #09090b;
      font-size: 13.5px;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: 8px;
      text-decoration: none;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .btn-site:hover {{
      background: #f1f5f9;
      transform: translateY(-1px);
    }}
    .btn-kakao {{
      background: #fee500;
      color: #191919;
      font-size: 13.5px;
      font-weight: 800;
      padding: 10px 18px;
      border-radius: 8px;
      text-decoration: none;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .btn-kakao:hover {{
      background: #fada0a;
      transform: translateY(-1px);
    }}
    .btn-naver {{
      background: #03c75a;
      color: #fff;
      font-size: 13.5px;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: 8px;
      text-decoration: none;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .btn-naver:hover {{
      background: #02b14f;
      transform: translateY(-1px);
    }}
    .btn-sub {{
      background: rgba(255,255,255,0.1);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.2);
      font-size: 13.5px;
      font-weight: 600;
      padding: 10px 18px;
      border-radius: 8px;
      text-decoration: none;
      transition: all 0.15s;
    }}
    .btn-sub:hover {{
      background: rgba(255,255,255,0.2);
    }}
    .stat-widget {{
      background: #fff;
      border-radius: 12px;
      border: 1px solid var(--border);
      padding: 20px 24px;
      margin-bottom: 24px;
    }}
    .stat-widget-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}
    .stat-widget-title {{
      font-size: 15px;
      font-weight: 700;
      color: #0f172a;
    }}
    .stat-bars-container {{
      display: flex;
      align-items: flex-end;
      gap: 4px;
      height: 90px;
      padding-top: 10px;
      border-bottom: 1px solid #f1f5f9;
      overflow-x: auto;
    }}
    .post-list-card {{
      background: #fff;
      border-radius: 12px;
      border: 1px solid var(--border);
      padding: 24px;
    }}
    .list-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }}
    .list-title {{
      font-size: 16px;
      font-weight: 700;
    }}
    .post-card {{
      padding: 16px 0;
      border-bottom: 1px solid #f1f5f9;
      transition: all 0.15s;
    }}
    .post-card:last-child {{
      border-bottom: none;
    }}
    .post-card.today {{
      background: #fbfbfe;
      margin: 0 -12px;
      padding: 16px 12px;
      border-radius: 8px;
    }}
    .post-card-date {{
      font-size: 12px;
      color: var(--text-sub);
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}
    .post-no {{
      font-size: 11px;
      font-weight: 800;
      background: #09090b;
      color: #fff;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .post-card-title {{
      font-size: 16px;
      font-weight: 700;
      color: #0f172a;
      text-decoration: none;
      display: block;
      line-height: 1.45;
    }}
    .post-card-title:hover {{
      color: var(--accent);
    }}
    .pagination-bar {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 6px;
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
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
      border-color: #09090b;
      color: #09090b;
      background: #f8fafc;
    }}
    .page-btn.active {{
      background: #09090b;
      color: #fff;
      border-color: #09090b;
    }}
    .page-btn:disabled {{
      opacity: 0.35;
      cursor: not-allowed;
    }}
  </style>
</head>
<body>

  <header class="header">
    <div class="header-inner">
      <div class="brand-wrap">
        <span class="brand-badge">INK/NOIR</span>
        <div class="brand-title">타투이스트 네이버 블로그 작업실</div>
      </div>
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <a href="{KAKAO_CHAT_URL}" target="_blank" rel="noopener noreferrer" class="header-link" style="background: #fee500; color: #191919; font-weight: 700; border-color: #fada0a;">💬 카톡 상담</a>
        <a href="{NAVER_BLOG_URL}" target="_blank" rel="noopener noreferrer" class="header-link" style="background: #03c75a; color: #fff; font-weight: 700; border-color: #02b14f;">🟢 네이버 블로그</a>
        <a href="{STUDIO_URL}" target="_blank" rel="noopener noreferrer" class="header-link">🌐 공식 사이트</a>
        <a href="../../index.html" class="header-link">← 포털 홈</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero-banner">
      <div class="hero-text">
        <h1>{STUDIO_NAME} 공식 블로그 작업실</h1>
        <p>
          국내 법적 규제로 포털 검색광고 집행이 어려운 타투 스튜디오를 위해, 
          실시간 상위 검색 주제 및 1:1 커스텀 감성 도안, 철저한 멸균 위생 수칙 중심의 고품질 블로그 콘텐츠를 매일 1~2건씩 자동 발행합니다.<br>
          제작된 글은 공식 네이버 블로그(<strong>applepark03</strong>)에 즉시 복사하여 포스팅할 수 있으며, 카카오톡 오픈채팅과 공식 사이트를 통해 실시간 견적 상담 및 예약으로 연결됩니다.
        </p>
      </div>
      <div class="hero-actions">
        <a href="{KAKAO_CHAT_URL}" target="_blank" rel="noopener noreferrer" class="btn-kakao">
          💬 카카오톡 오픈채팅 상담 ↗
        </a>
        <a href="{NAVER_BLOG_URL}" target="_blank" rel="noopener noreferrer" class="btn-naver">
          🟢 공식 네이버 블로그 ↗
        </a>
        <a href="{STUDIO_URL}" target="_blank" rel="noopener noreferrer" class="btn-site">
          🌐 포트폴리오 웹사이트 ↗
        </a>
        <a href="../../index.html" class="btn-sub">
          전체 작업실 목록
        </a>
      </div>
    </section>

    <section class="stat-widget">
      <div class="stat-widget-header">
        <div class="stat-widget-title">📊 최근 30일 포스팅 현황 (총 {recent_30_sum}건 / 전체 누적 {total_posts}건)</div>
        <span style="font-size: 12px; color: #64748b;">기준일: {today_str}</span>
      </div>
      <div class="stat-bars-container">
        {stat_bars_rendered}
      </div>
    </section>

    <section class="post-list-card">
      <div class="list-header">
        <div class="list-title">📝 전체 포스팅 목록 (총 {total_posts}편)</div>
        <div style="font-size: 13px; color: var(--text-sub);">
          페이지당 10개씩 표시
        </div>
      </div>

      <div id="post-items-wrap">
        {cards_rendered}
      </div>

      <div class="pagination-bar" id="pagination-controls">
        <!-- JS 페이징 동적 렌더링 -->
      </div>
    </section>
  </main>

  <script>
    // 10건 단위 페이징 로직
    const ITEMS_PER_PAGE = 10;
    let currentPage = 1;

    function renderPagination() {{
      const itemsWrap = document.getElementById("post-items-wrap");
      const cards = itemsWrap.querySelectorAll(".post-card");
      const totalItems = cards.length;
      const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE) || 1;

      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;

      // 카드 가시성 토글
      cards.forEach((card, index) => {{
        const start = (currentPage - 1) * ITEMS_PER_PAGE;
        const end = start + ITEMS_PER_PAGE;
        if (index >= start && index < end) {{
          card.style.display = "block";
        }} else {{
          card.style.display = "none";
        }}
      }});

      // 컨트롤 바 렌더링
      const controls = document.getElementById("pagination-controls");
      if (totalPages <= 1) {{
        controls.innerHTML = "";
        return;
      }}

      let html = '';
      html += `<button class="page-btn" onclick="goToPage(${{currentPage - 1}})" ${{currentPage === 1 ? 'disabled' : ''}}>‹ 이전</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        html += `<button class="page-btn ${{i === currentPage ? 'active' : ''}}" onclick="goToPage(${{i}})">${{i}}</button>`;
      }}

      html += `<button class="page-btn" onclick="goToPage(${{currentPage + 1}})" ${{currentPage === totalPages ? 'disabled' : ''}}>다음 ›</button>`;
      controls.innerHTML = html;
    }}

    function goToPage(page) {{
      currentPage = page;
      renderPagination();
      window.scrollTo({{ top: 380, behavior: 'smooth' }});
    }}

    document.addEventListener("DOMContentLoaded", () => {{
      renderPagination();
    }});
  </script>

</body>
</html>
"""
    index_file = os.path.join(TATTOO_BLOG_DIR, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"✅ 대시보드 갱신 완료: {index_file} (총 {total_posts}편 인덱싱)")


def run_batch(target_date_str=None, count=2, force=False):
    """지정된 날짜의 타투 포스팅 생성 및 대시보드 갱신"""
    if not target_date_str:
        target_date_str = datetime.now().strftime("%Y-%m-%d")
        
    date_obj = datetime.strptime(target_date_str, "%Y-%m-%d")
    month_dir = date_obj.strftime("%Y%m")
    target_posts_dir = os.path.join(TATTOO_POSTS_DIR, month_dir)
    os.makedirs(target_posts_dir, exist_ok=True)
    
    # 기존 글 스캔
    existing_posts = scan_existing_posts()
    existing_today_files = [p for p in existing_posts if p["date"] == target_date_str]
    
    if len(existing_today_files) >= count and not force:
        print(f"ℹ️ {target_date_str} 타투 글이 이미 {len(existing_today_files)}편 존재합니다. (--force 옵션으로 강제 재생성 가능)")
        rebuild_index(existing_posts, target_date_str)
        return
        
    # 날짜 기반 시드 및 토픽 선택
    day_int = int(date_obj.strftime("%Y%m%d"))
    pool_len = len(TATTOO_TOPIC_POOL)
    
    created_items = []
    # 이전 날짜 포스트 개수 기준으로 글 번호 산정
    prior_posts = [p for p in existing_posts if p["date"] < target_date_str]
    current_post_count = len(prior_posts)
    
    for i in range(count):
        sub_idx = i + 1
        topic_idx = (day_int * 2 + i) % pool_len
        topic = TATTOO_TOPIC_POOL[topic_idx]
        
        # 파일명 결정
        if sub_idx == 1:
            file_base = target_date_str
        else:
            file_base = f"{target_date_str}-{sub_idx}"
            
        md_filename = f"{file_base}.md"
        html_filename = f"{file_base}.html"
        
        md_path = os.path.join(target_posts_dir, md_filename)
        html_path = os.path.join(target_posts_dir, html_filename)
        
        # 고유 글 번호
        post_no = current_post_count + i + 1
        
        # 마크다운 및 HTML 생성
        md_text = generate_post_markdown(topic, post_no, target_date_str)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
            
        html_text = generate_post_html(topic, post_no, target_date_str, md_filename)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_text)
            
        print(f"✨ [No. {post_no}] 타투 포스트 생성: {html_filename} - {topic['title']}")
        created_items.append(html_filename)
        
    # 인덱스 전체 재스캔 및 대시보드 갱신
    all_posts = scan_existing_posts()
    rebuild_index(all_posts, target_date_str)
    print(f"🎉 {target_date_str}자 타투 포스팅 {len(created_items)}건 생성 완료!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="타투이스트 네이버 블로그 일일 배치")
    parser.add_argument("date", nargs="?", default=None, help="대상 날짜 (YYYY-MM-DD)")
    parser.add_argument("--count", type=int, default=2, help="생성할 포스트 수 (기본: 2)")
    parser.add_argument("--force", action="store_true", help="기존 포스트 덮어쓰기")
    args = parser.parse_args()
    
    run_batch(args.date, count=args.count, force=args.force)

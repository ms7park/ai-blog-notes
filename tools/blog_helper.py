#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blog_helper.py - AI 블로그 글 품질 및 SEO 분석 도구
사용법: python tools/blog_helper.py <마크다운파일경로> [타겟키워드]
"""

import sys
import re
from collections import Counter
from pathlib import Path

def analyze_blog_file(file_path: str, target_keyword: str = ""):
    path = Path(file_path)
    if not path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return

    content = path.read_text(encoding="utf-8")

    # 1. 헤더 추출
    headers = re.findall(r'^(#{1,4})\s+(.+)$', content, flags=re.MULTILINE)

    # 2. 텍스트 정제 (마크다운 기호 제거)
    plain_text = re.sub(r'#+\s+', '', content)
    plain_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', plain_text)  # 링크
    plain_text = re.sub(r'[*_~`>|-]', ' ', plain_text)                # 서식 기호
    
    char_count_with_spaces = len(plain_text)
    char_count_no_spaces = len(re.sub(r'\s+', '', plain_text))
    word_count = len(plain_text.split())
    reading_time_min = max(1, round(char_count_no_spaces / 500))  # 분당 약 500자 독서 기준

    # 3. 키워드 분석
    korean_words = re.findall(r'[가-힣]{2,}', plain_text)
    word_freq = Counter(korean_words).most_common(10)

    print("=" * 60)
    print(f"📊 블로그 글 품질 & SEO 분석 리포트: {path.name}")
    print("=" * 60)

    # 기본 통계
    print("\n[1] 분량 및 가독성 지표")
    print(f" • 총 글자수 (공백 포함) : {char_count_with_spaces:,} 자")
    print(f" • 순수 글자수 (공백 제외): {char_count_no_spaces:,} 자")
    print(f" • 총 단어수            : {word_count:,} 개")
    print(f" • 예상 독서 시간        : 약 {reading_time_min} 분")

    # 권장 분량 평가
    if char_count_no_spaces < 1000:
        length_status = "⚠️ 다소 짧음 (1,500자 이상 권장)"
    elif 1000 <= char_count_no_spaces <= 3500:
        length_status = "✅ 최적 분량 (체류 시간 및 검색 상위 노출에 이상적)"
    else:
        length_status = "💡 긴 글 (소제목과 요약 박스를 적극 활용하세요)"
    print(f" • 분량 진단            : {length_status}")

    # 헤더 구조 분석
    print("\n[2] 소제목(H2, H3) 구조")
    if not headers:
        print(" ⚠️ 소제목이 없습니다. H2(##), H3(###)를 활용해 글을 구조화해 주세요.")
    else:
        h2_count = sum(1 for h in headers if h[0] == '##')
        h3_count = sum(1 for h in headers if h[0] == '###')
        print(f" • H2(##): {h2_count}개 | H3(###): {h3_count}개")
        for tag, title in headers:
            indent = "  " * (len(tag) - 1)
            print(f"   {indent}• {tag} {title}")

    # 키워드 빈도 분석
    print("\n[3] 본문 주요 빈출 단어 (TOP 10)")
    for word, count in word_freq:
        print(f" • {word:<8} : {count:>2}회")

    # 타겟 키워드 점검
    if target_keyword:
        kw_count = plain_text.count(target_keyword)
        print(f"\n[4] 타겟 키워드 점검: '{target_keyword}'")
        print(f" • 등장 횟수 : {kw_count} 회")
        if kw_count == 0:
            print(" ❌ 본문에 타겟 키워드가 없습니다. 제목과 소제목, 본문에 자연스럽게 배치하세요.")
        elif 3 <= kw_count <= 8:
            print(" ✅ 적정 키워드 밀도 (과도하지 않고 자연스러움)")
        elif kw_count > 8:
            print(" ⚠️ 키워드가 다소 많습니다. 검색엔진 어뷰징(도배)으로 오인되지 않게 조절하세요.")
        else:
            print(" 💡 1~2회 등장. 3~5회 정도 자연스럽게 추가하면 SEO에 좋습니다.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python tools/blog_helper.py <마크다운파일경로> [타겟키워드]")
        print("예시  : python tools/blog_helper.py docs/05-templates/01-blog-templates.md 국민연금")
        sys.exit(1)

    file_arg = sys.argv[1]
    kw_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    analyze_blog_file(file_arg, kw_arg)

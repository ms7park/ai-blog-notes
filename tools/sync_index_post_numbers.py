#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버, 티스토리, 워드프레스 작업실 대시보드(index.html)의 글 카드 목록을
생성일 기준 오름차순 글번호(No. 1 ~ No. N) 및 화면 표시 최신순(내림차순)으로 완전 동기화하는 유틸리티 스크립트.
"""

import os
import re
import sys
from datetime import datetime

# BASE_DIR 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from tools.daily_naver_batch import scan_all_posts
from tools.daily_tistory_batch import scan_tistory_posts
from tools.daily_wordpress_batch import scan_wp_posts, WEEKDAYS_KR

def update_naver():
    index_path = os.path.join(BASE_DIR, "blog", "naver", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    posts = scan_all_posts()
    today_str = posts[0]["date_only"] if posts else datetime.now().strftime("%Y-%m-%d")
    cards = []
    for p in posts:
        is_today = (p["date_only"] == today_str)
        today_class = " today" if is_today else ""
        if p["post_num"] == 1:
            badge_suffix = " (오늘 · 실시간 1위)" if is_today else " (실시간 1위)"
        else:
            t_name = p.get("theme_name")
            theme_label = f"테마: {t_name}" if t_name else f"테마 #{p['post_num']}"
            badge_suffix = f" (오늘 · {theme_label})" if is_today else f" ({theme_label})"
        date_badge = f"📍 {p['date_only']}{badge_suffix}"
        cat_badge = f'<span style="font-size: 11px; background: #e8f9f0; color: #02b14f; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-left: 8px;">{p["category"].split("/")[0].strip()}</span>' if p.get("category") else ""
        score_badge = f'<span class="score-pill">🎯 {p.get("score_str", "95/100점")}</span>'

        cards.append(f"""            <article class="post-card{today_class}">
              <div class="post-card-date" style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                  <span class="post-no">No. {p['post_no']}</span>
                  <span>{date_badge}</span>
                  {cat_badge}
                  {score_badge}
                </div>
                <span style="font-size: 11.5px; color: var(--text-muted); font-weight: 600;">#{p['post_num']}편</span>
              </div>
              <a href="{p['rel_html']}" class="post-card-title">
                {p['title']}
              </a>
            </article>""")

    new_cards_str = "\n".join(cards)
    pattern = r'(<div [^>]*id="naverPostList"[^>]*>)(.*?)(</div>\s*<div class="pagination-bar" id="naverPagination">)'
    new_html, count = re.subn(pattern, r'\1\n' + new_cards_str + r'\n          \3', html, flags=re.DOTALL)
    if count == 0:
        raise RuntimeError("naverPostList 영역을 찾을 수 없습니다.")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"✅ 네이버 index.html 갱신 완료: 총 {len(cards)}개 포스트 (상단 No. {posts[0]['post_no']} ~ 하단 No. {posts[-1]['post_no']})")

def update_tistory():
    index_path = os.path.join(BASE_DIR, "blog", "tistory", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    posts = scan_tistory_posts()
    today_str = posts[0]["date_only"] if posts else datetime.now().strftime("%Y-%m-%d")
    cards = []
    for p in posts:
        is_today = (p["date_only"] == today_str)
        today_class = " today" if is_today else ""
        date_badge = f"📍 {p['date_only']} ({'오늘 작성' if is_today else '발행본'})"

        cards.append(f"""            <article class="post-card{today_class}">
              <div class="post-card-date">
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                  <span class="post-no">No. {p['post_no']}</span>
                  <span>{date_badge}</span>
                  <span class="cat-pill">📂 {p['category']}</span>
                  <span class="score-pill">🎯 평가 {p['score_str']}</span>
                </div>
                <span style="font-size: 11.5px; color: var(--text-muted); font-weight: 600;">#{p['post_num']}편</span>
              </div>
              <a href="{p['rel_html']}" class="post-card-title">
                {p['title']}
              </a>
            </article>""")

    new_cards_str = "\n".join(cards)
    pattern = r'(<div [^>]*id="tistoryPostList"[^>]*>)(.*?)(</div>\s*<div class="pagination-bar" id="tistoryPagination">)'
    new_html, count = re.subn(pattern, r'\1\n' + new_cards_str + r'\n          \3', html, flags=re.DOTALL)
    if count == 0:
        raise RuntimeError("tistoryPostList 영역을 찾을 수 없습니다.")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"✅ 티스토리 index.html 갱신 완료: 총 {len(cards)}개 포스트 (상단 No. {posts[0]['post_no']} ~ 하단 No. {posts[-1]['post_no']})")

def update_wordpress():
    index_path = os.path.join(BASE_DIR, "blog", "wordpress", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    posts = scan_wp_posts()
    today_str = posts[0]["date_only"] if posts else datetime.now().strftime("%Y-%m-%d")
    cards = []
    for p in posts:
        is_today = (p["date_only"] == today_str)
        today_class = " today" if is_today else ""
        try:
            p_weekday = WEEKDAYS_KR[datetime.strptime(p["date_only"], "%Y-%m-%d").weekday()]
        except Exception:
            p_weekday = "금"

        cards.append(f"""            <article class="post-card{today_class}">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                  <span class="post-no">No. {p['post_no']}</span>
                  <span style="font-size:12.5px; font-weight:700; color:var(--wp-dark);">📍 {p['date_only']} ({p_weekday})</span>
                  <span class="cat-pill">📂 {p['category']}</span>
                  <span class="score-pill">🎯 {p['score_str']}</span>
                </div>
                <span style="font-size:11.5px; color:var(--text-muted); font-weight:600;">#{p['post_num']}편</span>
              </div>
              <a href="{p['rel_html']}" class="post-card-title">{p['title']}</a>
            </article>""")

    new_cards_str = "\n".join(cards)
    pattern = r'(<div [^>]*id="wpPostList"[^>]*>)(.*?)(</div>\s*<div class="pagination-bar" id="wpPagination">)'
    new_html, count = re.subn(pattern, r'\1\n' + new_cards_str + r'\n          \3', html, flags=re.DOTALL)
    if count == 0:
        raise RuntimeError("wpPostList 영역을 찾을 수 없습니다.")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"✅ 워드프레스 index.html 갱신 완료: 총 {len(cards)}개 포스트 (상단 No. {posts[0]['post_no']} ~ 하단 No. {posts[-1]['post_no']})")

if __name__ == "__main__":
    update_naver()
    update_tistory()
    update_wordpress()

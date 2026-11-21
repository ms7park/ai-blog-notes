#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
온디맨드(수시) 블로그 포스팅 생성 엔진 (tools/write_ondemand.py)

사용자가 시간이 있을 때 언제든 터미널 또는 CLI에서 원하는 플랫폼에
키워드 지정 또는 실시간 최신 트렌드를 반영하여 1편~수 편의 글을 즉시 생성합니다.
생성 후 대시보드(blog/*/index.html) 및 메인 포털(index.html)까지 자동으로 동기화합니다.

사용 예시:
  python3 tools/write_ondemand.py --platform=tistory --keyword="국민연금 개혁안"
  python3 tools/write_ondemand.py --platform=wordpress --auto-trend
  python3 tools/write_ondemand.py --platform=all --keyword="AI 챗봇 활용법"
  python3 tools/write_ondemand.py --platform=naver --count=2
"""

import os
import sys
import argparse
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

import daily_tistory_batch as tis
import daily_wordpress_batch as wp
import daily_naver_batch as nav

WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

def get_next_post_index(platform, date_str):
    """당일자 마지막 포스트 번호를 확인하여 다음 번호(post_id, index) 반환"""
    ym = date_str[:7].replace("-", "")
    posts_dir = os.path.join(BASE_DIR, "blog", platform, "posts", ym)
    if not os.path.exists(posts_dir):
        return (date_str, 1)

    matching_files = glob.glob(os.path.join(posts_dir, f"{date_str}*.md"))
    if not matching_files:
        return (date_str, 1)

    max_idx = 1
    for f in matching_files:
        base = os.path.basename(f).replace(".md", "")
        parts = base.split("-")
        if len(parts) > 3 and parts[3].isdigit():
            max_idx = max(max_idx, int(parts[3]))
        elif len(parts) == 3:
            max_idx = max(max_idx, 1)

    next_idx = max_idx + 1
    return (f"{date_str}-{next_idx}", next_idx)

def write_tistory_ondemand(date_str, weekday_str, keyword=None, news_title=""):
    """티스토리에 온디맨드 1편 작성"""
    post_id, post_num = get_next_post_index("tistory", date_str)
    existing_sigs = tis.get_existing_tistory_signatures()

    if not keyword:
        trends = tis.fetch_google_trends_for_tistory(existing_sigs)
        chosen = None
        for t in trends:
            if t["keyword"].strip().lower() not in existing_sigs["keywords"]:
                chosen = t
                break
        if not chosen and trends:
            chosen = trends[0]
        if not chosen:
            chosen = {
                "rank": post_num,
                "keyword": "ChatGPT 실무 활용법",
                "traffic": "실시간 핫토픽",
                "news_title": "AI 생산성 도구 실전 활용 가이드",
                "eval": tis.evaluate_trend_for_tistory("ChatGPT 실무 활용법", "AI 생산성 도구 실전 활용 가이드")
            }
        trend_item = chosen
    else:
        eval_data = tis.evaluate_trend_for_tistory(keyword, news_title or f"{keyword} 핵심 가이드 및 체크포인트")
        trend_item = {
            "rank": post_num,
            "keyword": keyword,
            "traffic": "온디맨드 추천",
            "news_title": news_title or f"{keyword} 최신 주요 이슈",
            "news_url": "",
            "eval": eval_data,
            "is_top3": True
        }

    success = tis.create_tistory_post(post_id, date_str, weekday_str, trend_item, post_num=post_num, force=True, is_top3=True)
    if success:
        posts = tis.scan_tistory_posts()
        tis.update_tistory_index_html(date_str, [trend_item], posts)
        tis.update_root_portal_with_tistory(date_str, posts)
        print(f"✅ [티스토리 온디맨드 생성 완료] #{post_num}편: {trend_item['eval']['final_title']}")
        return True
    return False

def write_wordpress_ondemand(date_str, weekday_str, keyword=None, news_title=""):
    """워드프레스에 온디맨드 1편 작성"""
    post_id, post_num = get_next_post_index("wordpress", date_str)
    ym = date_str[:7].replace("-", "")
    wp_post_dir = os.path.join(wp.POSTS_DIR, ym)
    os.makedirs(wp_post_dir, exist_ok=True)

    if not keyword:
        trends = wp.fetch_trending_keywords_for_wp()
        existing_titles = wp.get_existing_wp_titles()
        chosen_t = None
        for t in trends:
            th = wp.match_wp_theme(t["keyword"], t.get("news_title", ""))
            item = wp.create_wp_item_from_trend(t, post_num, theme_info=th)
            if item["final_title"] not in existing_titles:
                chosen_t = item
                break
        if not chosen_t and wp.WP_ARTICLES:
            p_item = wp.WP_ARTICLES[(post_num - 1) % len(wp.WP_ARTICLES)].copy()
            p_item["seq"] = post_num
            p_item["final_title"] = f"{p_item['final_title']} (온디맨드 특별판)"
            chosen_t = p_item
        wp_item = chosen_t
    else:
        th = wp.match_wp_theme(keyword, news_title)
        wp_item = wp.create_wp_item_from_trend({
            "rank": post_num,
            "keyword": keyword,
            "badge": "온디맨드",
            "news_title": news_title or f"{keyword} 핵심 이슈"
        }, post_num, theme_info=th)

    md_path = os.path.join(wp_post_dir, f"{post_id}.md")
    html_path = os.path.join(wp_post_dir, f"{post_id}.html")
    md_content = wp.format_wp_markdown(date_str, weekday_str, wp_item)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    html_content = wp.build_wp_post_html(post_id, date_str, weekday_str, wp_item, md_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    posts = wp.scan_wp_posts()
    with open(os.path.join(wp.WP_BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(wp.build_wp_index_html(date_str, weekday_str, posts))
    wp.update_root_portal_with_wordpress(date_str, posts)
    print(f"✅ [워드프레스 온디맨드 생성 완료] #{post_num}편: {wp_item['final_title']}")
    return True

def write_naver_ondemand(date_str, weekday_str, keyword=None, news_title=""):
    """네이버 블로그에 온디맨드 1편 작성"""
    post_id, post_num = get_next_post_index("naver", date_str)
    existing_sigs = nav.get_existing_naver_signatures()

    if not keyword:
        trends = nav.fetch_trending_keywords()
        chosen = None
        for t in trends:
            if t["keyword"].lower() not in existing_sigs["keywords"]:
                chosen = t
                break
        if not chosen and trends:
            chosen = trends[0]
        t_obj = chosen
        th_info = t_obj.get("theme") or nav.match_blog_theme(t_obj["keyword"], t_obj.get("news", ""))
    else:
        th_info = nav.match_blog_theme(keyword, news_title)
        rec_title = nav.generate_blog_title_for_trend(keyword, news_title, th_info, rank=post_num)
        t_obj = {
            "rank": post_num,
            "keyword": keyword,
            "badge": "온디맨드",
            "news": news_title or f"{keyword} 이슈 안내",
            "recommended_title": rec_title,
            "theme": th_info
        }

    nav.create_post(post_id, date_str, weekday_str, t_obj, th_info, post_num=post_num, force=True)
    posts = nav.scan_all_posts()
    nav.update_naver_index_html(date_str, [t_obj], posts)
    nav.update_portal_index_html(date_str, posts)
    print(f"✅ [네이버 블로그 온디맨드 생성 완료] #{post_num}편: {t_obj['recommended_title']}")
    return True

def main():
    parser = argparse.ArgumentParser(description="온디맨드 블로그 포스팅 즉시 생성 도구")
    parser.add_argument("--platform", "-p", choices=["naver", "tistory", "wordpress", "all"], default="all",
                        help="작성할 플랫폼 (naver, tistory, wordpress, all)")
    parser.add_argument("--keyword", "-k", type=str, default=None,
                        help="작성할 키워드 (생략 시 실시간 트렌드에서 미작성 키워드 자동 선정)")
    parser.add_argument("--count", "-c", type=int, default=1,
                        help="플랫폼당 작성할 글 수 (기본: 1편)")
    parser.add_argument("--date", "-d", type=str, default=None,
                        help="기준 날짜 (YYYY-MM-DD, 기본: 오늘)")

    args = parser.parse_args()

    now = datetime.now()
    today_date = datetime.strptime(args.date, "%Y-%m-%d") if args.date else now
    today_str = today_date.strftime("%Y-%m-%d")
    weekday_str = WEEKDAYS_KR[today_date.weekday()]

    platforms = ["naver", "tistory", "wordpress"] if args.platform == "all" else [args.platform]

    print(f"\n🚀 [온디맨드 포스팅 시작] 기준일: {today_str} ({weekday_str}), 대상 플랫폼: {platforms}, 편수: {args.count}편")
    if args.keyword:
        print(f"🎯 지정 키워드: [{args.keyword}]")
    else:
        print(f"⚡ 모드: 실시간 트렌드 & 핫토픽 자동 선별 모드")

    for p in platforms:
        for i in range(args.count):
            if p == "tistory":
                write_tistory_ondemand(today_str, weekday_str, keyword=args.keyword)
            elif p == "wordpress":
                write_wordpress_ondemand(today_str, weekday_str, keyword=args.keyword)
            elif p == "naver":
                write_naver_ondemand(today_str, weekday_str, keyword=args.keyword)

    # 전체 가이드 뷰어 동기화
    gen_script = os.path.join(BASE_DIR, "tools", "generate_html.py")
    if os.path.exists(gen_script):
        os.system(f"{sys.executable} {gen_script} > /dev/null 2>&1")
        print("✅ 전체 가이드 뷰어(docs/index.html) 동기화 완료")

    print("\n🎉 모든 온디맨드 포스팅 및 대시보드 갱신이 완료되었습니다!\n")

if __name__ == "__main__":
    main()

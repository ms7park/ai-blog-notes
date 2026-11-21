#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드프레스 구텐베르크 자동 업로더 (tools/upload_wordpress_playwright.py)

로컬 HTTP 데몬(127.0.0.1)을 띄워 HTML 뷰어를 열고,
'워드프레스 에디터 서식 복사' 기능(getWordPressOptimizedHtml)을 호출하여
중간제목(H3 ▍), 파란 요약박스(Callout Box), 표(Table), 볼드 서식을 추출한 후,
워드프레스 Gutenberg 공식 API(wp.data & wp.blocks)를 통해 네이티브 블록으로 변환 주입하고
즉시 정식 발행(PUBLISH)합니다.

마크다운 기호(**, --- 등)가 일체 노출되지 않으며 워드프레스 구텐베르크 정식 블록으로 등록됩니다.
"""

import os
import sys
import glob
import time
import re
import argparse
import http.server
import threading
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "wordpress")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
POSTS_DIR = os.path.join(BASE_DIR, "blog", "wordpress", "posts")
DEFAULT_SITE = "smartlife70.wordpress.com"

class LocalServerHandler(http.server.SimpleHTTPRequestHandler):
    """로컬 파일 서빙 핸들러 (로그 억제)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
        
    def log_message(self, format, *args):
        pass

def start_local_server(port=9996):
    """localhost에 임시 HTTP 서버를 백그라운드로 실행"""
    server = http.server.HTTPServer(("127.0.0.1", port), LocalServerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

def get_wp_post_data_via_server(viewer_page, server_port, rel_path):
    """
    http://127.0.0.1:{server_port}/{rel_path} 를 열고
    제목과 구텐베르크 최적화 리치 서식 HTML을 추출
    """
    url = f"http://127.0.0.1:{server_port}/{rel_path}"
    viewer_page.goto(url, wait_until="domcontentloaded")
    time.sleep(0.5)

    title = viewer_page.evaluate("""() => {
        const titleEl = document.querySelector('.post-title, #postArticle h1, article h1');
        if (titleEl) return titleEl.innerText.trim();
        const parts = document.title.split('|');
        return parts.length > 1 ? parts.slice(1).join('|').trim() : document.title.trim();
    }""")

    html_content = viewer_page.evaluate("() => typeof getWordPressOptimizedHtml === 'function' ? getWordPressOptimizedHtml(false) : document.querySelector('#postArticle')?.innerHTML || ''")

    return title.strip(), html_content

def upload_post_to_wordpress(page, site, title, html_content, mode="publish"):
    """워드프레스 Gutenberg API에 접속하여 제목 및 서식 블록 주입 후 발행"""
    print(f"\n📝 워드프레스 포스팅 작업: [{title[:35]}...]", flush=True)
    
    # 1. 새 글 작성 페이지 진입
    write_url = f"https://{site}/wp-admin/post-new.php"
    page.goto(write_url, wait_until="domcontentloaded")
    time.sleep(4)

    # 2. 구텐베르크 네이티브 블록 주입 및 저장/발행 실행
    target_status = "publish" if mode == "publish" else "draft"
    print(f"  ✍️ 구텐베르크 블록 변환 및 주입 중 (모드: {target_status.upper()})...", flush=True)

    try:
        res = page.evaluate("""async ([title, html, status]) => {
            // Gutenberg API 검증
            if (!window.wp || !window.wp.data || !window.wp.blocks) {
                return { success: false, error: 'WP Gutenberg API not available' };
            }

            // 1. 제목 설정
            wp.data.dispatch('core/editor').editPost({ title: title });

            // 2. HTML을 네이티브 구텐베르크 블록으로 자동 파싱
            const blocks = wp.blocks.rawHandler({ HTML: html });
            wp.data.dispatch('core/editor').resetBlocks(blocks);

            // 3. 상태 설정 (publish 또는 draft)
            wp.data.dispatch('core/editor').editPost({ status: status });

            // 4. 저장/발행 실행
            await wp.data.dispatch('core/editor').savePost();

            return {
                success: true,
                blocksCount: blocks.length,
                status: status
            };
        }""", [title, html_content, target_status])

        if not res or not res.get("success"):
            print(f"  ❌ 구텐베르크 주입 실패: {res.get('error', 'unknown error')}", flush=True)
            return False

        time.sleep(3.5)

        # 3. 발행 결과 확인
        post_info = page.evaluate("""() => {
            const post = wp.data.select('core/editor').getCurrentPost();
            return {
                id: post.id,
                status: post.status,
                link: post.link
            };
        }""")

        blocks_cnt = res.get("blocksCount", 0)
        print(f"  ✅ 본문 구텐베르크 서식(요약박스/소제목/표) 블록 생성 완료 (총 {blocks_cnt}개 블록)", flush=True)
        print(f"  🎉 [{target_status.upper()} 성공] 워드프레스 정식 등록 완료! (ID: {post_info.get('id')}, 상태: {post_info.get('status')})", flush=True)
        if post_info.get("link"):
            print(f"  🔗 글 링크: {post_info.get('link')}", flush=True)
        return True

    except Exception as e:
        print(f"  ❌ 워드프레스 발행 처리 오류: {e}", flush=True)
        return False

def main():
    parser = argparse.ArgumentParser(description="워드프레스 Playwright 자동 등록 도구")
    parser.add_argument("--single", type=int, default=None, help="등록할 특정 포스트 번호 (예: 1이면 2026-11-21.html)")
    parser.add_argument("--all", action="store_true", help="오늘 작성된 모든 포스트 등록")
    parser.add_argument("--date", type=str, default=None, help="대상 날짜 (기본: 오늘)")
    parser.add_argument("--mode", choices=["draft", "publish"], default="publish", help="저장 모드 (기본: publish)")
    parser.add_argument("--headless", action="store_true", default=True, help="화면 없이 백그라운드 실행")
    parser.add_argument("--show-browser", action="store_true", help="화면 브라우저 표시 모드")
    parser.add_argument("--site", type=str, default=DEFAULT_SITE, help="대상 워드프레스 사이트 도메인")

    args = parser.parse_args()
    headless_mode = not args.show_browser

    today_str = args.date or datetime.now().strftime("%Y-%m-%d")
    ym = today_str[:7].replace("-", "")
    target_dir = os.path.join(POSTS_DIR, ym)

    if not os.path.exists(STATE_FILE):
        print("❌ 워드프레스 로그인 세션 파일(state.json)이 없습니다!", flush=True)
        print("먼저 `./scripts/upload-wordpress.sh --login`을 실행하여 1회 로그인을 완료해 주세요.", flush=True)
        sys.exit(1)

    def sort_key(path):
        m = re.search(r'(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.', path)
        if m:
            date_part = m.group(1)
            num = int(m.group(2)) if m.group(2) else 1
            return (date_part, num)
        return (path, 0)

    if args.single is not None:
        idx_suffix = "" if args.single == 1 else f"-{args.single}"
        target_file = os.path.join(target_dir, f"{today_str}{idx_suffix}.html")
        if not os.path.exists(target_file):
            target_file = os.path.join(target_dir, f"{today_str}{idx_suffix}.md")
        if not os.path.exists(target_file):
            print(f"❌ 대상 파일이 존재하지 않습니다: {target_file}", flush=True)
            sys.exit(1)
        files_to_upload = [target_file]
    else:
        pattern_html = os.path.join(target_dir, f"{today_str}*.html")
        all_today = sorted(glob.glob(pattern_html), key=sort_key)
        if not all_today:
            pattern_md = os.path.join(target_dir, f"{today_str}*.md")
            all_today = sorted(glob.glob(pattern_md), key=sort_key)
        if not all_today:
            print(f"❌ 오늘({today_str}) 작성된 워드프레스 포스트가 없습니다.", flush=True)
            sys.exit(1)
        files_to_upload = all_today

    print("==========================================================", flush=True)
    print(f" 🚀 워드프레스 서식복사 자동 등록기 (대상: {len(files_to_upload)}편, 모드: {args.mode.upper()})", flush=True)
    print("==========================================================", flush=True)

    # 로컬 HTTP 데몬 서버 시작
    server_port = 9996
    server = start_local_server(server_port)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless_mode,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
                ]
            )

            context = browser.new_context(
                storage_state=STATE_FILE,
                viewport={"width": 1280, "height": 900}
            )

            viewer_page = context.new_page()
            page = context.new_page()

            print("🔍 워드프레스 로그인 상태 확인 중...", flush=True)
            page.goto(f"https://{args.site}/wp-admin/post-new.php")
            time.sleep(4)

            if "log-in" in page.url or "wp-login" in page.url:
                print("⚠️ 워드프레스 로그인이 만료되었거나 세션이 없습니다.", flush=True)
                print("`./scripts/upload-wordpress.sh --login`을 다시 실행해 주세요.", flush=True)
                browser.close()
                sys.exit(1)

            print("✅ 워드프레스 로그인 세션 확인 완료! (에디터 진입 성공)", flush=True)

            success_count = 0
            for i, fpath in enumerate(files_to_upload, 1):
                html_path = fpath if fpath.endswith(".html") else fpath[:-3] + ".html"
                rel_path = os.path.relpath(html_path, BASE_DIR).replace("\\", "/")
                
                title, html_content = get_wp_post_data_via_server(viewer_page, server_port, rel_path)
                
                print(f"\n[{i}/{len(files_to_upload)}] {os.path.basename(fpath)}", flush=True)
                ok = upload_post_to_wordpress(page, args.site, title, html_content, mode=args.mode)
                if ok:
                    success_count += 1
                
                if i < len(files_to_upload):
                    delay = 3 if args.mode == "publish" else 1.5
                    print(f"  ⏳ 다음 글 등록 대기 중 ({delay}초)...", flush=True)
                    time.sleep(delay)

            browser.close()
    finally:
        server.shutdown()

    print("\n==========================================================", flush=True)
    print(f" 🎉 등록 완료: 총 {len(files_to_upload)}편 중 {success_count}편 {args.mode.upper()} 성공!", flush=True)
    print("==========================================================", flush=True)

if __name__ == "__main__":
    main()

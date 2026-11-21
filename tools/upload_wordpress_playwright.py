#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드프레스 구텐베르크 자동 업로더 (tools/upload_wordpress_playwright.py)

로컬 HTTP 데몬(127.0.0.1)을 띄워 HTML 뷰어를 열고,
'워드프레스 에디터 서식 복사(#copyWpBtn)' 기능을 실행하여
중간제목(H3 ▍), 파란 요약박스(Callout Box), 표(Table), 볼드 서식을
클립보드에 완벽하게 복사한 후, 워드프레스 구텐베르크 에디터에 붙여넣어 정식 발행(PUBLISH)합니다.
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

def start_local_server(port=9997):
    """localhost에 임시 HTTP 서버를 백그라운드로 실행하여 isSecureContext 보장"""
    server = http.server.HTTPServer(("127.0.0.1", port), LocalServerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

def copy_wp_post_via_server(viewer_page, server_port, rel_path):
    """
    http://127.0.0.1:{server_port}/{rel_path} 를 열고
    #copyWpBtn 을 클릭하여 브라우저 클립보드에 구텐베르크 리치 서식 복사
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

    try:
        copy_btn = viewer_page.locator("#copyWpBtn").first
        copy_btn.click()
        time.sleep(0.5)
        print("  📋 [에디터 서식 복사] 버튼 클릭 완료 (구텐베르크 요약박스·소제목·볼드 서식 복사)", flush=True)
    except Exception as e:
        print(f"  ⚠️ 서식 복사 버튼 클릭 오류: {e}", flush=True)

    return title.strip()

def dismiss_gutenberg_dialogs(page):
    """구텐베르크 시작 가이드 팝업 닫기"""
    try:
        close_btn = page.locator('button[aria-label="대화 상자 닫기"], button[aria-label="Close dialog"], button.components-modal__close-button').first
        if close_btn.is_visible(timeout=2000):
            close_btn.click()
            time.sleep(0.5)
            print("  ℹ️ 구텐베르크 안내 팝업 닫기 완료", flush=True)
    except Exception:
        pass

def upload_post_to_wordpress(page, site, title, mode="publish"):
    """워드프레스 구텐베르크 에디터에 접속하여 제목 및 서식 본문 주입 후 발행"""
    print(f"\n📝 워드프레스 포스팅 작업: [{title[:35]}...]", flush=True)
    
    # 1. 새 글 작성 페이지 진입
    write_url = f"https://{site}/wp-admin/post-new.php"
    page.goto(write_url, wait_until="domcontentloaded")
    time.sleep(4)
    
    # 2. 팝업 닫기
    dismiss_gutenberg_dialogs(page)

    # 3. 제목 입력
    print("  ✍️ 제목 입력 중...", flush=True)
    try:
        title_el = page.locator('h1.editor-post-title__input, textarea.editor-post-title__input, .wp-block-post-title').first
        title_el.wait_for(state="visible", timeout=8000)
        title_el.click()
        time.sleep(0.2)
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        page.keyboard.insert_text(title)
        time.sleep(0.4)
        print("  ✅ 제목 입력 완료", flush=True)
    except Exception as e:
        print(f"  ⚠️ 제목 입력 오류: {e}", flush=True)
        return False

    # 4. 본문 서식 붙여넣기 (Meta+v / Control+v)
    print("  📄 에디터 서식 붙여넣기(Cmd+V) 실행 중...", flush=True)
    try:
        # 제목에서 아래로 내려가거나 첫 블록 선택
        page.keyboard.press("Enter")
        time.sleep(0.3)
        
        body_appender = page.locator('.block-editor-default-block-appender__content, p.wp-block-paragraph, .is-root-container p').first
        if body_appender.is_visible(timeout=3000):
            body_appender.click()
            time.sleep(0.2)
            
        page.keyboard.press("Meta+v")
        time.sleep(0.5)
        page.keyboard.press("Control+v")
        time.sleep(2.5)
        print("  ✅ 본문 서식(요약박스/소제목/표) 붙여넣기 완료", flush=True)
    except Exception as e:
        print(f"  ⚠️ 본문 붙여넣기 오류: {e}", flush=True)
        return False

    # 5. 모드에 따른 저장 (draft: 임시글 저장, publish: 정식 발행)
    if mode == "draft":
        print("  💾 [임시글로 저장] 버튼 클릭 중...", flush=True)
        try:
            save_draft_btn = page.locator('button.editor-post-save-draft, button:has-text("임시글로 저장"), button:has-text("Save draft")').first
            save_draft_btn.click()
            time.sleep(3)
            print("  🎉 [임시저장 성공] 워드프레스 임시글 저장 완료!", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 임시저장 실패: {e}", flush=True)
            return False

    elif mode == "publish":
        print("  🚀 [정식 발행] 버튼 클릭 중...", flush=True)
        try:
            # 1단계: 상단 발행 패널 토글 버튼 클릭
            publish_toggle = page.locator('button.editor-post-publish-panel__toggle, button:has-text("공개…"), button:has-text("발행…"), button:has-text("Publish…")').first
            publish_toggle.click()
            time.sleep(1.5)

            # 2단계: 패널 내 최종 발행 확인 버튼 클릭
            final_publish = page.locator('button.editor-post-publish-button, button:has-text("공개"), button:has-text("발행"), button:has-text("Publish")').first
            final_publish.click()
            time.sleep(5)
            print("  🎉 [발행 성공] 워드프레스에 포스팅이 실제 정식 발행되었습니다!", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 발행 버튼 클릭 실패: {e}", flush=True)
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
    server_port = 9997
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
                viewport={"width": 1280, "height": 900},
                permissions=["clipboard-read", "clipboard-write"]
            )

            viewer_page = context.new_page()
            page = context.new_page()

            print("🔍 워드프레스 로그인 상태 확인 중...", flush=True)
            page.goto(f"https://{args.site}/wp-admin/post-new.php")
            time.sleep(3)

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
                
                title = copy_wp_post_via_server(viewer_page, server_port, rel_path)
                
                print(f"\n[{i}/{len(files_to_upload)}] {os.path.basename(fpath)}", flush=True)
                ok = upload_post_to_wordpress(page, args.site, title, mode=args.mode)
                if ok:
                    success_count += 1
                
                if i < len(files_to_upload):
                    delay = 4 if args.mode == "publish" else 2
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

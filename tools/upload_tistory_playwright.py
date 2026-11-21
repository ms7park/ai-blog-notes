#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
티스토리 블로그 Playwright 자동 업로더 (tools/upload_tistory_playwright.py)

1. 로컬 뷰어 HTML의 '🟠 티스토리 에디터(기본모드) 서식 복사' 버튼(#copyTistoryHtmlBtn)을 클릭
2. 티스토리 에디터에 제목 입력 및 본문에 Cmd+V로 스타일(표, 요약박스, 소제목) 그대로 주입
3. 즉시 정식 공개 발행(Publish)합니다.
"""

import os
import sys
import glob
import time
import re
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "tistory")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
POSTS_DIR = os.path.join(BASE_DIR, "blog", "tistory", "posts")
DEFAULT_BLOG = "essay30497"

def copy_post_via_viewer(viewer_page, html_path):
    """
    로컬 HTML 뷰어를 열고 '에디터 서식 복사' 버튼(#copyTistoryHtmlBtn)을 클릭하여
    클립보드에 표, 요약박스, 소제목 서식을 복사하고 제목 반환
    """
    file_url = f"file://{os.path.abspath(html_path)}"
    viewer_page.goto(file_url, wait_until="domcontentloaded")
    time.sleep(0.5)

    title = viewer_page.evaluate("""() => {
        const titleEl = document.querySelector('.post-title, #postArticle h1, article h1');
        if (titleEl) return titleEl.innerText.trim();
        const parts = document.title.split('|');
        return parts.length > 1 ? parts.slice(1).join('|').trim() : document.title.trim();
    }""")

    try:
        copy_btn = viewer_page.locator("#copyTistoryHtmlBtn").first
        copy_btn.click()
        time.sleep(0.5)
        print("  📋 [에디터 서식 복사] 버튼 클릭 완료 (표·요약박스·소제목 스타일 클립보드 복사)", flush=True)
    except Exception as e:
        print(f"  ⚠️ 서식 복사 버튼 클릭 오류: {e}", flush=True)

    return title.strip()

def upload_post_to_tistory(page, blog_name, title, mode="publish"):
    """
    티스토리 새 에디터에 제목 입력 후 클립보드 서식(Cmd+V) 붙여넣기 및 정식 발행
    """
    print(f"\n📝 포스팅 등록 시작: [{title[:35]}...]", flush=True)
    write_url = f"https://{blog_name}.tistory.com/manage/newpost"

    # 1. 글쓰기 페이지 진입
    try:
        page.goto(write_url, wait_until="domcontentloaded")
        time.sleep(3)
    except Exception as e:
        print(f"  ⚠️ 글쓰기 페이지 로딩 오류: {e}", flush=True)
        return False

    # 2. 임시저장 이어쓰기 팝업 취소
    try:
        dialog_cancel = page.locator("button:has-text('취소'), .btn-cancel, .layer_body button:has-text('취소')").first
        if dialog_cancel.is_visible(timeout=2000):
            dialog_cancel.click()
            print("  ℹ️ 기존 임시저장 이어쓰기 안내창 취소 완료", flush=True)
            time.sleep(0.5)
    except Exception:
        pass

    # 3. 닫기/안내창 처리
    try:
        close_btn = page.locator("button:has-text('닫기'), .btn_close").first
        if close_btn.is_visible(timeout=1000):
            close_btn.click()
            time.sleep(0.3)
    except Exception:
        pass

    # 4. 제목 입력
    print("  ✍️ 제목 입력 중...", flush=True)
    try:
        title_loc = page.locator("#post-title-inp, #post-title, textarea.textarea_tit").first
        title_loc.wait_for(state="visible", timeout=6000)
        title_loc.click()
        time.sleep(0.2)
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        page.keyboard.insert_text(title)
        time.sleep(0.5)
        print("  ✅ 제목 입력 완료", flush=True)
    except Exception as e:
        print(f"  ⚠️ 제목 입력 실패 (JS 대체 시도): {e}", flush=True)
        try:
            page.evaluate("""(t) => {
                const el = document.querySelector('#post-title-inp, #post-title, textarea.textarea_tit');
                if (el) {
                    el.value = t;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", title)
        except Exception:
            pass

    # 5. 본문 포커스 및 클립보드 서식 붙여넣기 (Meta+V)
    print("  📄 에디터 서식 붙여넣기(Cmd+V) 실행 중...", flush=True)
    try:
        body_frame = page.frame(name="editor-tistory_ifr")
        if body_frame:
            body_el = body_frame.locator("body#tinymce").first
        else:
            body_el = page.locator("#editor-root [contenteditable='true'], div[contenteditable='true']").first
            
        body_el.wait_for(state="visible", timeout=6000)
        body_el.click()
        time.sleep(0.4)
        page.keyboard.press("Meta+v")
        time.sleep(2)
        print("  ✅ 본문 서식(표/요약박스/소제목) 붙여넣기 완료", flush=True)
    except Exception as e:
        print(f"  ⚠️ 본문 붙여넣기 오류: {e}", flush=True)
        return False

    time.sleep(1)

    # 6. 저장 및 발행
    if mode == "draft":
        print("  💾 [임시저장] 버튼 클릭 중...", flush=True)
        try:
            save_btn = page.locator("button.btn-save, button:has-text('저장'), .btn_save").first
            save_btn.click()
            time.sleep(2)
            print("  🎉 [임시저장 성공] 티스토리 임시저장함에 등록되었습니다!", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 임시저장 실패: {e}", flush=True)
            return False

    else:
        # 정식 공개 발행 (기본값)
        print(f"  🚀 [정식 {mode.upper()} 발행] 진행 중...", flush=True)
        try:
            # 1단계: 우측 하단 [완료] 버튼 클릭 (#publish-layer-btn)
            complete_btn = page.locator("#publish-layer-btn, button:has-text('완료')").first
            complete_btn.click()
            time.sleep(1.5)

            # 2단계: 공개/비공개 옵션
            if mode == "private":
                priv_opt = page.locator("label:has-text('비공개'), input[value='private']").first
                if priv_opt.is_visible(timeout=2000):
                    priv_opt.click()
            else:
                pub_opt = page.locator("label:has-text('공개'), input[value='public']").first
                if pub_opt.is_visible(timeout=2000):
                    pub_opt.click()
            time.sleep(0.5)

            # 3단계: 최종 [공개 발행] 버튼 (#publish-btn)
            submit_btn = page.locator("#publish-btn, button:has-text('공개 발행')").first
            submit_btn.click()
            time.sleep(4)
            print(f"  🎉 [발행 성공] 티스토리 블로그에 실제 정식 글이 등록되었습니다!", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 발행 버튼 클릭 실패: {e}", flush=True)
            return False

def sort_key_for_posts(filepath):
    fname = os.path.basename(filepath)
    m = re.search(r'(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.html$', fname)
    if m:
        idx = int(m.group(2)) if m.group(2) else 1
        return (m.group(1), idx)
    return (fname, 0)

def main():
    parser = argparse.ArgumentParser(description="티스토리 블로그 Playwright 자동 등록 도구")
    parser.add_argument("--single", type=int, default=None, help="등록할 특정 포스트 번호")
    parser.add_argument("--all", action="store_true", help="오늘 작성된 30편 전체 등록")
    parser.add_argument("--date", type=str, default=None, help="대상 날짜 (기본: 오늘 YYYY-MM-DD)")
    parser.add_argument("--blog", type=str, default=DEFAULT_BLOG, help=f"티스토리 서브도메인 (기본: {DEFAULT_BLOG})")
    parser.add_argument("--mode", choices=["draft", "publish", "private"], default="publish", help="저장 모드 (기본: publish [정식 공개발행])")
    parser.add_argument("--headless", action="store_true", default=True, help="화면 없이 백그라운드 브라우저 실행")
    parser.add_argument("--show-browser", action="store_true", help="화면 브라우저 표시 모드")
    parser.add_argument("--delay", type=int, default=4, help="글 등록 사이 대기 시간(초, 기본 4초)")

    args = parser.parse_args()
    headless_mode = not args.show_browser

    today_str = args.date or datetime.now().strftime("%Y-%m-%d")
    ym = today_str[:7].replace("-", "")
    target_dir = os.path.join(POSTS_DIR, ym)

    if not os.path.exists(STATE_FILE) and not os.path.exists(SESSION_DIR):
        print("❌ 티스토리 로그인 세션이 없습니다!", flush=True)
        print("먼저 `./scripts/upload-tistory.sh --login`을 실행하여 1회 카카오 로그인을 완료해 주세요.", flush=True)
        sys.exit(1)

    if args.single is not None:
        idx_suffix = "" if args.single == 1 else f"-{args.single}"
        html_file = os.path.join(target_dir, f"{today_str}{idx_suffix}.html")
        if not os.path.exists(html_file):
            print(f"❌ 대상 파일이 존재하지 않습니다: {html_file}", flush=True)
            sys.exit(1)
        files_to_upload = [html_file]
    else:
        pattern = os.path.join(target_dir, f"{today_str}*.html")
        all_today = sorted(glob.glob(pattern), key=sort_key_for_posts)
        if not all_today:
            print(f"❌ 오늘({today_str}) 작성된 티스토리 포스트가 없습니다.", flush=True)
            sys.exit(1)
        files_to_upload = all_today

    print("==========================================================", flush=True)
    print(f" 🚀 티스토리 블로그 자동 등록기 (대상: {len(files_to_upload)}편, 모드: {args.mode.upper()})", flush=True)
    print(f" 🎯 블로그 주소: https://{args.blog}.tistory.com/", flush=True)
    print(" 📋 방식: 로컬 뷰어 '에디터 서식복사' 버튼 활용 서식 주입", flush=True)
    print("==========================================================", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless_mode,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context_kwargs = {
            "viewport": {"width": 1280, "height": 900},
            "permissions": ["clipboard-read", "clipboard-write"]
        }
        if os.path.exists(STATE_FILE):
            context_kwargs["storage_state"] = STATE_FILE

        context = browser.new_context(**context_kwargs)

        page = context.new_page()
        viewer_page = context.new_page()

        print("🔍 티스토리 로그인 세션 유효성 확인 중...", flush=True)
        test_write_url = f"https://{args.blog}.tistory.com/manage/newpost"
        page.goto(test_write_url)
        
        logged_in = False
        for _ in range(10):
            time.sleep(1)
            if "manage/newpost" in page.url or "manage/post" in page.url:
                logged_in = True
                break

        if not logged_in and ("auth/login" in page.url or "accounts.kakao.com" in page.url):
            print("⚠️ 티스토리 로그인이 풀려있거나 세션이 만료되었습니다.", flush=True)
            print("👉 `./scripts/upload-tistory.sh --login`을 먼저 실행해 주세요.", flush=True)
            browser.close()
            sys.exit(1)

        print(f"✅ 티스토리 로그인 세션 확인 완료! (에디터 진입 성공: {page.url})", flush=True)

        success_count = 0
        total_files = len(files_to_upload)

        for i, fpath in enumerate(files_to_upload, 1):
            fname = os.path.basename(fpath)
            print(f"\n[{i}/{total_files}] 진행 중: {fname}", flush=True)

            # 1. 뷰어 페이지에서 '에디터 서식 복사' 버튼 클릭 및 제목 추출
            title = copy_post_via_viewer(viewer_page, fpath)
            if not title:
                print(f"  ❌ 글 내용 추출 실패: {fpath}", flush=True)
                continue

            # 2. 티스토리 에디터에 주입 및 발행
            ok = upload_post_to_tistory(page, args.blog, title, mode=args.mode)
            if ok:
                success_count += 1

            if i < total_files:
                delay_sec = args.delay
                print(f"  ⏳ 다음 글 등록 대기 중 ({delay_sec}초 대기)...", flush=True)
                time.sleep(delay_sec)

        try:
            viewer_page.close()
        except Exception:
            pass
        browser.close()

    print("\n==========================================================", flush=True)
    print(f" 🎉 작업 완료: 총 {len(files_to_upload)}편 중 {success_count}편 {args.mode.upper()} 완료!", flush=True)
    print("==========================================================", flush=True)

if __name__ == "__main__":
    main()

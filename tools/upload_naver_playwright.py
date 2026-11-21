#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 블로그 스마트에디터 ONE 자동 업로더 (tools/upload_naver_playwright.py)

Playwright의 저장된 브라우저 세션(.browser_session/naver/state.json)을 사용하여
오늘 작성된 네이버 블로그 포스트를 로컬 뷰어의 '에디터 서식복사(#copyNaverBtn)' 기능을 통해
초록 요약박스, 소제목, 표, 볼드 서식을 클립보드에 복사한 뒤,
스마트에디터 ONE에 Cmd+V로 깔끔하게 붙여넣고 정식 발행(PUBLISH)합니다.
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
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "naver")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
POSTS_DIR = os.path.join(BASE_DIR, "blog", "naver", "posts")

def copy_naver_post_via_viewer(viewer_page, html_path):
    """
    로컬 네이버 HTML 뷰어를 열고 '네이버 서식 복사' 버튼(#copyNaverBtn)을 클릭하여
    클립보드에 초록 요약박스, 소제목, 볼드, 줄간격 서식을 복사하고 제목 반환
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
        copy_btn = viewer_page.locator("#copyNaverBtn").first
        copy_btn.click()
        time.sleep(0.5)
        print("  📋 [에디터 서식 복사] 버튼 클릭 완료 (초록 요약박스·소제목·볼드 서식 클립보드 복사)", flush=True)
    except Exception as e:
        print(f"  ⚠️ 서식 복사 버튼 클릭 오류: {e}", flush=True)

    return title.strip()

def dismiss_popups(frame):
    """작성 중인 글 이어쓰기 팝업 및 도움말 팝업을 안전하게 닫기"""
    # 1. '작성 중인 글이 있습니다' 팝업의 취소 버튼 (정확한 클래스 매칭)
    try:
        cancel_btn = frame.locator('button.se-popup-button-cancel, button:text-is("취소")').first
        if cancel_btn.is_visible(timeout=2500):
            cancel_btn.click()
            print("  ℹ️ 기존 임시저장 글 이어쓰기 팝업 [취소] 완료", flush=True)
            time.sleep(0.5)
    except Exception:
        pass

    # 2. 도움말/튜토리얼 팝업 닫기
    try:
        help_btn = frame.locator('button.se-help-panel-close-button, button.se-popup-button-close').first
        if help_btn.is_visible(timeout=1000):
            help_btn.click()
            time.sleep(0.5)
    except Exception:
        pass

    # 3. 팝업 dim 오버레이 확인
    try:
        dim = frame.locator('.se-popup-dim').first
        if dim.is_visible(timeout=1000):
            dim.wait_for(state="hidden", timeout=2000)
    except Exception:
        pass

def upload_post_to_naver(page, title, mode="publish"):
    """스마트에디터 ONE에 접속하여 제목 입력 및 클립보드 서식(Cmd+V) 붙여넣기 후 정식 발행"""
    print(f"\n📝 네이버 포스팅 작업: [{title[:35]}...]", flush=True)
    
    # 1. 스마트에디터 ONE 진입
    page.goto("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(3.5)
    
    # 2. mainFrame 획득
    frame = page.frame(name="mainFrame") or page
    
    # 3. 팝업 처리
    dismiss_popups(frame)

    # 4. 제목 입력
    print("  ✍️ 제목 입력 중...", flush=True)
    try:
        title_el = frame.locator('.se-documentTitle .se-text-paragraph').first
        title_el.wait_for(state="visible", timeout=6000)
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

    # 5. 본문 에디터 서식 붙여넣기 (Meta+v)
    print("  📄 에디터 서식 붙여넣기(Cmd+V) 실행 중...", flush=True)
    try:
        body_el = frame.locator('.se-main-container .se-text-paragraph, .se-content .se-text-paragraph').first
        body_el.wait_for(state="visible", timeout=6000)
        body_el.click()
        time.sleep(0.4)
        page.keyboard.press("Meta+v")
        time.sleep(2)
        page.keyboard.press("Enter")
        time.sleep(0.5)
        print("  ✅ 본문 서식(요약박스/소제목/표) 붙여넣기 완료", flush=True)
    except Exception as e:
        print(f"  ⚠️ 본문 붙여넣기 오류: {e}", flush=True)
        return False

    # 6. 모드에 따른 저장 (draft: 임시저장, publish: 정식발행)
    if mode == "draft":
        print("  💾 [임시저장] 버튼 클릭 중...", flush=True)
        try:
            save_btn = frame.locator('button:has-text("저장"), button[class*="save_btn"]').first
            save_btn.click()
            time.sleep(2)
            
            count_btn = frame.locator('button[class*="save_count_btn"]').first
            count_val = count_btn.inner_text() if count_btn.is_visible() else "저장완료"
            print(f"  🎉 [임시저장 성공] 네이버 블로그 임시저장 완료! (현재 저장 수: {count_val})", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 임시저장 버튼 클릭 실패: {e}", flush=True)
            return False
            
    elif mode == "publish":
        print("  🚀 [정식 발행] 버튼 클릭 중...", flush=True)
        try:
            # 1. 상단 [발행] 버튼 클릭하여 발행 설정 패널 열기
            publish_btn = frame.locator('button[data-click-area="tpb.publish"]').first
            publish_btn.click()
            time.sleep(1.5)
            
            # 2. 발행 설정 패널 내의 최종 초록색 [발행] 확인 버튼 클릭
            final_btn = frame.locator('button[data-testid="seOnePublishBtn"]').first
            final_btn.click()
            time.sleep(4)
            print("  🎉 [발행 성공] 네이버 블로그에 포스팅이 실제 정식 발행되었습니다!", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 발행 버튼 클릭 실패: {e}", flush=True)
            return False

def main():
    parser = argparse.ArgumentParser(description="네이버 블로그 Playwright 자동 등록 도구")
    parser.add_argument("--single", type=int, default=None, help="등록할 특정 포스트 번호 (예: 1이면 2026-11-21.html)")
    parser.add_argument("--all", action="store_true", help="오늘 작성된 모든 포스트 등록")
    parser.add_argument("--date", type=str, default=None, help="대상 날짜 (기본: 오늘)")
    parser.add_argument("--mode", choices=["draft", "publish"], default="publish", help="저장 모드 (draft: 임시저장, publish: 정식발행 - 기본: publish)")
    parser.add_argument("--headless", action="store_true", default=True, help="화면 없이 백그라운드 실행")
    parser.add_argument("--show-browser", action="store_true", help="화면 브라우저 표시 모드")

    args = parser.parse_args()
    headless_mode = not args.show_browser

    today_str = args.date or datetime.now().strftime("%Y-%m-%d")
    ym = today_str[:7].replace("-", "")
    target_dir = os.path.join(POSTS_DIR, ym)

    if not os.path.exists(STATE_FILE):
        print("❌ 네이버 로그인 세션 파일(state.json)이 없습니다!", flush=True)
        print("먼저 `./scripts/upload-naver.sh --login`을 실행하여 1회 로그인을 완료해 주세요.", flush=True)
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
            print(f"❌ 오늘({today_str}) 작성된 네이버 포스트가 없습니다.", flush=True)
            sys.exit(1)
        files_to_upload = all_today

    print("==========================================================", flush=True)
    print(f" 🚀 네이버 블로그 서식복사 자동 등록기 (대상: {len(files_to_upload)}편, 모드: {args.mode.upper()})", flush=True)
    print("==========================================================", flush=True)

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

        print("🔍 네이버 로그인 상태 확인 중...", flush=True)
        page.goto("https://blog.naver.com/GoBlogWrite.naver")
        time.sleep(3)

        if "nidlogin" in page.url:
            print("⚠️ 네이버 로그인이 풀려있거나 세션이 만료되었습니다.", flush=True)
            print("`./scripts/upload-naver.sh --login`을 다시 실행해 주세요.", flush=True)
            browser.close()
            sys.exit(1)

        print("✅ 네이버 로그인 세션 확인 완료! (스마트에디터 ONE 진입 성공)", flush=True)

        success_count = 0
        for i, fpath in enumerate(files_to_upload, 1):
            html_path = fpath if fpath.endswith(".html") else fpath[:-3] + ".html"
            if os.path.exists(html_path):
                title = copy_naver_post_via_viewer(viewer_page, html_path)
            else:
                from tools.upload_tistory_playwright import extract_title_and_body
                title, _ = extract_title_and_body(fpath)
            
            print(f"\n[{i}/{len(files_to_upload)}] {os.path.basename(fpath)}", flush=True)
            ok = upload_post_to_naver(page, title, mode=args.mode)
            if ok:
                success_count += 1
            
            if i < len(files_to_upload):
                delay = 4 if args.mode == "publish" else 2
                print(f"  ⏳ 다음 글 등록 대기 중 ({delay}초)...", flush=True)
                time.sleep(delay)

        browser.close()

    print("\n==========================================================", flush=True)
    print(f" 🎉 등록 완료: 총 {len(files_to_upload)}편 중 {success_count}편 {args.mode.upper()} 성공!", flush=True)
    print("==========================================================", flush=True)

if __name__ == "__main__":
    main()

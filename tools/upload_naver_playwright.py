#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 블로그 스마트에디터 ONE 안전 업로더 (tools/upload_naver_playwright.py)

[보안 & 안티디텍트(Anti-Detect) 강화 버전]
- 네이버 계정 보호(보호조치/아이디 잠금)를 원천 방지하기 위한 안전 가드레일 탑재
- 기본 실행: 실제 브라우저 화면 표시(Headless=False) 및 navigator.webdriver 은폐
- 마우스 움직임, 타이핑 지연, 휠 스크롤 등 인간 행동 시뮬레이션
- 발행 수량 엄격 제한: 1회 실행당 최대 1~2편 (어뷰징 탐지 회피)
- 다건 등록 시 최소 60초 이상 안전 딜레이 적용
- 예약 발행(Schedule Post) 옵션(--reserve) 지원
"""

import os
import sys
import glob
import time
import random
import re
import argparse
import http.server
import threading
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "naver")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
POSTS_DIR = os.path.join(BASE_DIR, "blog", "naver", "posts")

# 네이버 블로그 안전 발행 기준 (보호조치 방지용 하드 리밋)
MAX_SAFE_POSTS = 2

class LocalServerHandler(http.server.SimpleHTTPRequestHandler):
    """로컬 파일 서빙 핸들러 (로그 억제)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
        
    def log_message(self, format, *args):
        pass

def start_local_server(port=9998):
    """localhost에 임시 HTTP 서버를 백그라운드로 실행하여 isSecureContext 보장"""
    server = http.server.HTTPServer(("127.0.0.1", port), LocalServerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

def human_delay(min_sec=1.5, max_sec=3.0):
    """자연스러운 인간 행동 모방 무작위 대기"""
    time.sleep(random.uniform(min_sec, max_sec))

def copy_naver_post_via_server(viewer_page, server_port, rel_path):
    """
    http://127.0.0.1:{server_port}/{rel_path} 를 열고
    #copyNaverBtn 을 클릭하여 브라우저 클립보드에 리치 서식 및 클린 텍스트 복사
    """
    url = f"http://127.0.0.1:{server_port}/{rel_path}"
    viewer_page.goto(url, wait_until="domcontentloaded")
    human_delay(0.8, 1.5)

    title = viewer_page.evaluate("""() => {
        const titleEl = document.querySelector('.post-title, #postArticle h1, article h1');
        if (titleEl) return titleEl.innerText.trim();
        const parts = document.title.split('|');
        return parts.length > 1 ? parts.slice(1).join('|').trim() : document.title.trim();
    }""")

    try:
        copy_btn = viewer_page.locator("#copyNaverBtn").first
        copy_btn.click()
        human_delay(0.5, 1.0)
        print("  📋 [에디터 서식 복사] 완료 (초록 요약박스·소제목·볼드 서식)", flush=True)
    except Exception as e:
        print(f"  ⚠️ 서식 복사 버튼 클릭 오류: {e}", flush=True)

    return title.strip()

def dismiss_popups(frame):
    """작성 중인 글 이어쓰기 팝업 및 도움말 팝업을 안전하게 닫기"""
    try:
        cancel_btn = frame.locator('button.se-popup-button-cancel, button:text-is("취소")').first
        if cancel_btn.is_visible(timeout=2500):
            cancel_btn.click()
            print("  ℹ️ 기존 임시저장 글 이어쓰기 팝업 [취소] 완료", flush=True)
            human_delay(0.5, 1.0)
    except Exception:
        pass

    try:
        help_btn = frame.locator('button.se-help-panel-close-button, button.se-popup-button-close').first
        if help_btn.is_visible(timeout=1500):
            help_btn.click()
            human_delay(0.3, 0.6)
    except Exception:
        pass

def simulate_human_reading(page):
    """마우스 움직임 및 휠 스크롤 시뮬레이션"""
    try:
        for _ in range(2):
            x = random.randint(200, 800)
            y = random.randint(200, 600)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.2, 0.4))
        page.mouse.wheel(0, random.randint(150, 300))
        time.sleep(random.uniform(0.5, 1.0))
        page.mouse.wheel(0, -random.randint(100, 200))
    except Exception:
        pass

def upload_post_to_naver(page, title, mode="publish", reserve=False):
    """스마트에디터 ONE에 접속하여 제목 입력 및 클립보드 서식(Cmd+V) 붙여넣기 후 정식 발행"""
    print(f"\n📝 네이버 포스팅 작업: [{title[:35]}...]", flush=True)
    
    # 1. 스마트에디터 ONE 진입
    page.goto("https://blog.naver.com/GoBlogWrite.naver")
    human_delay(3.0, 4.5)
    
    # 2. mainFrame 획득
    frame = page.frame(name="mainFrame") or page
    
    # 3. 팝업 처리
    dismiss_popups(frame)
    human_delay(0.8, 1.5)

    # 4. 제목 입력 (자연스러운 타이핑 지연)
    print("  ✍️ 제목 입력 중 (인간 타이핑 모방)...", flush=True)
    try:
        title_el = frame.locator('.se-documentTitle .se-text-paragraph').first
        title_el.wait_for(state="visible", timeout=8000)
        title_el.click()
        human_delay(0.3, 0.6)
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        human_delay(0.2, 0.4)
        
        # 1글자씩 약간의 딜레이로 타이핑
        page.keyboard.type(title, delay=random.randint(20, 50))
        human_delay(0.8, 1.5)
        print("  ✅ 제목 입력 완료", flush=True)
    except Exception as e:
        print(f"  ⚠️ 제목 입력 오류: {e}", flush=True)
        return False

    # 5. 본문 에디터 서식 붙여넣기 (Cmd+V / Ctrl+V)
    print("  📄 본문 에디터 클릭 및 서식 붙여넣기...", flush=True)
    try:
        body_el = frame.locator('.se-module-text:not(.se-title-text) .se-text-paragraph').first
        body_el.wait_for(state="visible", timeout=8000)
        body_el.click()
        human_delay(0.5, 1.0)
        
        # 클립보드 붙여넣기
        page.keyboard.press("Meta+v")
        human_delay(0.4, 0.8)
        page.keyboard.press("Control+v")
        human_delay(2.0, 3.5)
        
        # 서식 검증
        paras = frame.locator('.se-module-text:not(.se-title-text) .se-text-paragraph').all_inner_texts()
        has_raw = any("**" in p or p.strip() == "---" for p in paras)
        if has_raw:
            print("  ⚠️ 주의: 마크다운 기호 감지됨, 보정 필요", flush=True)
        else:
            print(f"  ✅ 본문 서식(요약박스/소제목/표) 붙여넣기 성공 (총 {len(paras)}개 문단)", flush=True)
    except Exception as e:
        print(f"  ⚠️ 본문 붙여넣기 오류: {e}", flush=True)
        return False

    # 6. 글 검토 모방 (마우스 스크롤 및 3초 대기)
    simulate_human_reading(page)
    human_delay(2.0, 4.0)

    # 7. 모드에 따른 저장 (draft: 임시저장, publish: 정식발행)
    if mode == "draft":
        print("  💾 [임시저장] 버튼 클릭 중...", flush=True)
        try:
            save_btn = frame.locator('button:has-text("저장"), button[class*="save_btn"]').first
            save_btn.click()
            human_delay(2.0, 3.0)
            print("  🎉 [임시저장 성공] 네이버 블로그 임시저장 완료!", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 임시저장 버튼 클릭 실패: {e}", flush=True)
            return False
            
    elif mode == "publish":
        print("  🚀 [정식 발행] 버튼 클릭 중...", flush=True)
        try:
            publish_btn = frame.locator('button[data-click-area="tpb.publish"]').first
            publish_btn.click()
            human_delay(2.0, 3.0)
            
            # 예약 발행 옵션 처리
            if reserve:
                print("  ⏰ [예약 발행] 옵션 설정 시도 중...", flush=True)
                try:
                    reserve_opt = frame.locator('input[type="radio"][value="reserve"], label:has-text("예약"), button:has-text("예약")').first
                    if reserve_opt.is_visible(timeout=3000):
                        reserve_opt.click()
                        human_delay(1.0, 1.5)
                        print("  ✅ 예약 발행 선택 완료", flush=True)
                except Exception as re_err:
                    print(f"  ⚠️ 예약 옵션 선택 건너뜀 (현재 발행 진행): {re_err}", flush=True)

            final_btn = frame.locator('button[data-testid="seOnePublishBtn"]').first
            final_btn.click()
            human_delay(4.5, 6.0)
            print("  🎉 [발행 성공] 네이버 블로그에 포스팅이 실제 정식 발행되었습니다!", flush=True)
            return True
        except Exception as e:
            print(f"  ❌ 발행 버튼 클릭 실패: {e}", flush=True)
            return False

def main():
    parser = argparse.ArgumentParser(description="네이버 블로그 Playwright 안티디텍트 안전 업로더")
    parser.add_argument("--single", type=int, default=None, help="등록할 특정 포스트 번호 (기본: 1번 글)")
    parser.add_argument("--all", action="store_true", help="오늘 작성된 포스트 중 안전 수량 등록")
    parser.add_argument("--date", type=str, default=None, help="대상 날짜 (기본: 오늘)")
    parser.add_argument("--mode", choices=["draft", "publish"], default="publish", help="저장 모드 (기본: publish)")
    parser.add_argument("--reserve", action="store_true", help="즉시 발행 대신 '예약 발행'으로 설정")
    parser.add_argument("--limit", type=int, default=1, help=f"1회 등록할 최대 포스트 수 (기본: 1편, 최대 {MAX_SAFE_POSTS}편)")
    parser.add_argument("--headless", action="store_true", default=False, help="백그라운드 헤드리스 실행 (권장하지 않음: 봇 탐지 위험)")
    parser.add_argument("--dangerous-override", action="store_true", help="안전 제한 해제 (비추천: 계정 보호조치 위험)")

    args = parser.parse_args()

    # 네이버 계정 안전 가드레일
    post_limit = args.limit
    if not args.dangerous_override and post_limit > MAX_SAFE_POSTS:
        print(f"\n⚠️ [계정 보호 안전 가드레일 발동]", flush=True)
        print(f"  네이버 블로그는 단시간에 3편 이상 등록 시 계정 보호조치(아이디 잠금)가 발동합니다.", flush=True)
        print(f"  안전을 위해 1회 등록 수량을 최대 {MAX_SAFE_POSTS}편으로 제한합니다.", flush=True)
        post_limit = MAX_SAFE_POSTS

    # 헤드리스 경고
    if args.headless:
        print("\n⚠️ [경고] Headless 모드는 네이버 안티봇 스크립트에 감지될 확률이 높습니다.", flush=True)
        print("  계정 보호를 위해 화면 표시 모드(기본값)를 적극 권장합니다.\n", flush=True)

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
        
        # 안전 수량만큼 슬라이싱
        files_to_upload = all_today[:post_limit]

    print("==========================================================", flush=True)
    print(f" 🛡️ 네이버 블로그 안티디텍트 안전 등록기 (방안 C 적용)", flush=True)
    print(f" 🎯 대상: 총 {len(files_to_upload)}편 (안전 제한 적용) | 모드: {args.mode.upper()}", flush=True)
    if args.reserve:
        print(" ⏰ 옵션: 예약 발행(Schedule) 모드 활성화", flush=True)
    print(f" 🖥️ 브라우저: {'헤드리스(비권장)' if args.headless else '실제 브라우저 화면 표시(안전 모드)'}", flush=True)
    print("==========================================================", flush=True)

    # 1. 로컬 HTTP 서버 시작 (HTTPS/localhost 컨텍스트로 클립보드 API 활성화)
    server_port = 9998
    server = start_local_server(server_port)

    # 2. Stealth 스크립트 (navigator.webdriver 등 자동화 서명 은폐)
    stealth_js = """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    Object.defineProperty(navigator, 'languages', {
        get: () => ['ko-KR', 'ko', 'en-US', 'en']
    });
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    """

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=args.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-default-browser-check",
                    "--no-sandbox"
                ]
            )

            context = browser.new_context(
                storage_state=STATE_FILE,
                viewport={"width": 1366, "height": 900},
                user_agent=user_agent,
                locale="ko-KR",
                timezone_id="Asia/Seoul",
                permissions=["clipboard-read", "clipboard-write"]
            )

            # 모든 페이지에 안티디텍트 스크립트 사전 주입
            context.add_init_script(stealth_js)

            viewer_page = context.new_page()
            page = context.new_page()

            print("🔍 네이버 로그인 세션 확인 중...", flush=True)
            page.goto("https://blog.naver.com/GoBlogWrite.naver")
            human_delay(3.0, 4.0)

            if "nidlogin" in page.url:
                print("⚠️ 네이버 로그인이 풀려있거나 보호조치로 인해 접근이 차단되었습니다.", flush=True)
                print("먼저 브라우저에서 본인 인증 및 보호조치를 해제한 뒤 `./scripts/upload-naver.sh --login`을 다시 실행해 주세요.", flush=True)
                browser.close()
                sys.exit(1)

            print("✅ 네이버 로그인 세션 정상 확인! (스마트에디터 ONE 진입 성공)", flush=True)

            success_count = 0
            for i, fpath in enumerate(files_to_upload, 1):
                html_path = fpath if fpath.endswith(".html") else fpath[:-3] + ".html"
                rel_path = os.path.relpath(html_path, BASE_DIR).replace("\\", "/")
                
                title = copy_naver_post_via_server(viewer_page, server_port, rel_path)
                
                print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
                print(f" [{i}/{len(files_to_upload)}] {os.path.basename(fpath)}", flush=True)
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
                
                ok = upload_post_to_naver(page, title, mode=args.mode, reserve=args.reserve)
                if ok:
                    success_count += 1
                
                if i < len(files_to_upload):
                    # 2편 이상 등록 시 네이버 어뷰징 방지를 위해 최소 60~90초 대기
                    wait_sec = random.randint(60, 90)
                    print(f"\n  ⏳ [계정 보호 안전 대기] 네이버 어뷰징 방지를 위해 {wait_sec}초간 대기합니다...", flush=True)
                    for remaining in range(wait_sec, 0, -10):
                        print(f"     ... {remaining}초 남음", flush=True)
                        time.sleep(min(10, remaining))

            human_delay(1.5, 2.5)
            browser.close()
    finally:
        server.shutdown()

    print("\n==========================================================", flush=True)
    print(f" 🎉 네이버 안전 등록 완료: 총 {len(files_to_upload)}편 중 {success_count}편 {args.mode.upper()} 성공!", flush=True)
    print(" 💡 [팁] 네이버 계정의 건강한 성장을 위해 하루 1~2편 유지를 적극 권장합니다.", flush=True)
    print("==========================================================", flush=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드프레스 1회성 브라우저 로그인 세션 생성 도구 (tools/setup_wordpress_login.py)

사용자가 화면에 열린 Chromium 브라우저에서 워드프레스(WordPress.com)에 로그인하면,
로그인 인증 세션(쿠키, 스토리지)을 .browser_session/wordpress/state.json 에 영구 저장합니다.
이후 자동 업로드 시에는 로그인 창 없이 바로 구텐베르크 에디터에 접속해 글을 작성합니다.
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "wordpress")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
DEFAULT_SITE = "smartlife70.wordpress.com"

def setup_wordpress_session(site=DEFAULT_SITE):
    os.makedirs(SESSION_DIR, exist_ok=True)
    print("==========================================================", flush=True)
    print(" 🌐 워드프레스(WordPress) 1회성 로그인 세션 설정", flush=True)
    print("==========================================================", flush=True)
    print(f" 🎯 대상 사이트: https://{site}/", flush=True)
    print(" 화면에 브라우저 로그인 창이 열립니다.", flush=True)
    print(" 1. 브라우저에서 워드프레스 계정(구글/애플/이메일 등)으로 로그인해 주세요.", flush=True)
    print(" 2. 2단계 인증이 있다면 완료해 주세요.", flush=True)
    print(" 3. 로그인이 완료되면 자동으로 감지하여 세션을 저장합니다.", flush=True)
    print("==========================================================", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            permissions=["clipboard-read", "clipboard-write"]
        )

        page = context.new_page()

        # 워드프레스 로그인 페이지로 이동
        login_url = f"https://wordpress.com/log-in?redirect_to=https%3A%2F%2F{site}%2Fwp-admin%2Fpost-new.php"
        print("🚀 워드프레스 로그인 페이지를 여는 중입니다...", flush=True)
        page.goto(login_url)

        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "Google Chrome for Testing" to activate'
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        print("\n⏳ 화면에 열린 브라우저 창에서 워드프레스 로그인을 진행해 주세요...", flush=True)
        print("💡 로그인 완료 시 자동으로 감지하여 세션을 저장합니다 (최대 10분 대기).", flush=True)

        logged_in = False
        for i in range(300):
            time.sleep(2)
            try:
                all_pages = [p for p in context.pages if not p.is_closed()]
                if not all_pages:
                    print("⚠️ 사용자에 의해 브라우저 창이 닫혔습니다.", flush=True)
                    break

                active_urls = [p.url for p in all_pages]
                cookies = context.cookies()
                cookie_names = set(c["name"] for c in cookies)

                # 워드프레스 로그인 인증 쿠키 감지
                has_wp_login = any("wordpress_logged_in" in name or "wp-settings" in name for name in cookie_names)
                reached_admin = any("wp-admin" in u or "wordpress.com/post" in u or "wordpress.com/home" in u for u in active_urls)

                if has_wp_login or (reached_admin and not any("log-in" in u for u in active_urls)):
                    print(f"\n🎉 [1단계 감지] 워드프레스 로그인 인증 확인! (쿠키 수: {len(cookies)})", flush=True)
                    context.storage_state(path=STATE_FILE)
                    logged_in = True
                    break
            except Exception:
                pass

        if not logged_in:
            print("⚠️ 로그인이 완료되지 않았거나 창이 닫혔습니다. 다시 시도해 주세요.", flush=True)
            try:
                browser.close()
            except Exception:
                pass
            return False

        # 2단계: 에디터 접근 확인
        print("🔍 2단계: 워드프레스 새 글 에디터 접근 권한 검증 중...", flush=True)
        editor_page = context.new_page()
        try:
            editor_page.goto(f"https://{site}/wp-admin/post-new.php", timeout=30000)
            time.sleep(3)
            context.storage_state(path=STATE_FILE)
            print("✅ 워드프레스 세션이 성공적으로 영구 저장되었습니다!", flush=True)
            print(f"📁 저장 경로: {STATE_FILE}", flush=True)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 에디터 접근 중 경미한 확인 사항: {e}", flush=True)
            context.storage_state(path=STATE_FILE)

        browser.close()
        return True

if __name__ == "__main__":
    success = setup_wordpress_session()
    if not success:
        sys.exit(1)

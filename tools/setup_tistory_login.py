#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
티스토리 블로그 1회성 브라우저 로그인 세션 생성 도구 (tools/setup_tistory_login.py)

사용자가 화면에 열린 Chromium 브라우저에서 카카오/티스토리에 직접 로그인하면,
로그인 인증 세션을 .browser_session/tistory/state.json 에 영구 저장합니다.
이후 자동 업로드 시에는 재로그인 없이 바로 글쓰기가 가능해집니다.
"""

import os
import sys
import time
import argparse
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "tistory")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
DEFAULT_BLOG = "essay30497"

def setup_tistory_session(blog_name=DEFAULT_BLOG):
    os.makedirs(SESSION_DIR, exist_ok=True)
    print("==========================================================", flush=True)
    print(" 🌐 티스토리(카카오) 블로그 1회성 로그인 세션 설정", flush=True)
    print("==========================================================", flush=True)
    print(f" 🎯 대상 블로그: https://{blog_name}.tistory.com/", flush=True)
    print(" 화면에 브라우저 로그인 창이 열립니다.", flush=True)
    print(" 1. 열린 브라우저에서 [카카오계정으로 로그인]을 클릭합니다.", flush=True)
    print(" 2. 카카오 계정 아이디/비밀번호 입력 및 2단계 인증을 완료합니다.", flush=True)
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

        # 티스토리 로그인 페이지로 이동
        print("🚀 티스토리 로그인 페이지를 여는 중입니다...", flush=True)
        login_url = f"https://www.tistory.com/auth/login?redirectUrl=https%3A%2F%2F{blog_name}.tistory.com%2Fmanage%2Fnewpost"
        page.goto(login_url)

        # macOS에서 브라우저 창을 화면 맨 앞으로 활성화
        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "Google Chrome for Testing" to activate'
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        print("\n⏳ 화면에 열린 브라우저 창에서 카카오 로그인을 완료해 주세요...", flush=True)
        print("💡 로그인 완료 시 자동으로 감지하여 세션을 저장합니다 (최대 10분 대기).", flush=True)

        logged_in = False
        for i in range(300):
            time.sleep(2)
            try:
                if page.is_closed():
                    print("⚠️ 사용자에 의해 브라우저 창이 닫혔습니다.", flush=True)
                    break

                curr_url = page.url
                # 카카오 로그인 완료 후 티스토리나 서브도메인으로 리다이렉트되었는지 확인
                if "manage/newpost" in curr_url or "manage/post" in curr_url or ("tistory.com" in curr_url and "auth/login" not in curr_url and "accounts.kakao.com" not in curr_url):
                    cookies = context.cookies()
                    cookie_names = [c["name"] for c in cookies]
                    if any(k in cookie_names for k in ["TSSESSION", "_karmas", "TIARA"]):
                        print("\n🎉 [1단계 감지] 카카오/티스토리 로그인 토큰 확인 완료!", flush=True)
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

        # 2단계: 블로그 글쓰기 에디터 진입 권한 검증
        print(f"🔍 [2단계 검증] 티스토리 글쓰기 에디터 진입 확인 중 (https://{blog_name}.tistory.com/manage/newpost)...", flush=True)
        try:
            page.goto(f"https://{blog_name}.tistory.com/manage/newpost")
            time.sleep(3)
            if "auth/login" in page.url or "accounts.kakao.com" in page.url:
                print("⚠️ 글쓰기 페이지 진입 실패 (세션 만료 또는 로그인 권한 필요)", flush=True)
                logged_in = False
            else:
                print(f"✅ 티스토리 글쓰기 에디터 진입 성공! (URL: {page.url})", flush=True)
                context.storage_state(path=STATE_FILE)
                logged_in = True
        except Exception as e:
            print(f"ℹ️ 확인 중 안내: {e}", flush=True)

        if logged_in:
            print(f"\n✅ 티스토리 로그인 세션이 안전하게 저장되었습니다: {STATE_FILE}", flush=True)
            print("5초 후 로그인 창이 자동으로 닫히며 등록 준비가 완료됩니다...", flush=True)
            time.sleep(5)

        browser.close()
        return logged_in

def main():
    parser = argparse.ArgumentParser(description="티스토리 Playwright 1회성 로그인 세션 도구")
    parser.add_argument("--blog", type=str, default=DEFAULT_BLOG, help=f"티스토리 서브도메인 (기본: {DEFAULT_BLOG})")
    args = parser.parse_args()
    setup_tistory_session(args.blog)

if __name__ == "__main__":
    main()
